#!/usr/bin/env python3
"""
webcam-streamer.py
Version: 1.0

Description: Advanced webcam streaming server using FFmpeg for Mecanum robot
remote monitoring. Provides a web interface to view the robot's camera feed.

Compatible with:
  - All Mecanum robot Arduino firmware files
  - Can be used alongside any controller

Original content follows:
"""

import subprocess
import http.server
import socketserver
import threading
import signal
import sys
import socket
import logging
import time
import argparse
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FFmpegStreamer:
    def __init__(self, port, device='/dev/video0', framerate='25', video_size='640x480'):
        self.port = port
        self.device = device
        self.framerate = framerate
        self.video_size = video_size
        self.process = None
        self.running = False

    def get_ffmpeg_command(self):
        return [
            'ffmpeg',
            '-f', 'v4l2',
            '-i', self.device,
            '-framerate', self.framerate,
            '-video_size', self.video_size,
            '-f', 'mjpeg',
            f'http://127.0.0.1:{self.port}/feed.mjpg'
        ]

    def start(self):
        if self.running:
            logger.warning("FFmpeg is already running.")
            return
        logger.info(f"Starting FFmpeg stream on port {self.port}...")
        try:
            self.process = subprocess.Popen(
                self.get_ffmpeg_command(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=subprocess.os.setsid
            )
            self.running = True
            threading.Thread(target=self._check_ffmpeg_output, daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to start FFmpeg: {e}")
            self.running = False

    def _check_ffmpeg_output(self):
        stdout, stderr = self.process.communicate()
        if self.process.returncode != 0:
            logger.error(f"FFmpeg error: {stderr.decode().strip()}")
            self.running = False
        else:
            logger.info("FFmpeg exited cleanly.")

    def stop(self):
        if self.running and self.process:
            logger.info("Stopping FFmpeg...")
            try:
                subprocess.os.killpg(subprocess.os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg did not terminate with SIGTERM, sending SIGKILL...")
                subprocess.os.killpg(subprocess.os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()
            self.running = False
            logger.info("FFmpeg stopped.")

class StreamHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.stream_queue = kwargs.pop('stream_queue', None)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f'''
            <html>
            <head>
                <title>Live Webcam Feed</title>
            </head>
            <body>
                <h1>Live Webcam Feed</h1>
                <img src="/feed.mjpg" alt="Live Video Stream">
            </body>
            </html>
            '''.encode('utf-8')
            self.wfile.write(html)
        elif self.path == '/feed.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    data = self.stream_queue.get(timeout=5)  # Wait for data from FFmpeg
                    if not data:
                        break
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                except Queue.Empty:
                    logger.warning("No stream data available, waiting...")
                    continue
                except BrokenPipeError:
                    logger.info("Client disconnected from stream.")
                    break
                except Exception as e:
                    logger.error(f"Error streaming to client: {e}")
                    break
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/feed.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    data = self.rfile.read(1024)
                    if not data:
                        break
                    self.stream_queue.put(data)  # Share data with GET clients
                except BrokenPipeError:
                    logger.info("FFmpeg disconnected from server.")
                    break
                except Exception as e:
                    logger.error(f"Error receiving FFmpeg stream: {e}")
                    break
        else:
            self.send_error(501, "Unsupported method")

class WebcamServer:
    def __init__(self, start_port):
        self.start_port = start_port
        self.port = None
        self.httpd = None
        self.streamer = None
        self.server_thread = None
        self.stream_queue = Queue()

    def find_available_port(self):
        port = self.start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    logger.warning(f"Port {port} is in use, trying {port + 1}...")
                    port += 1

    def start(self):
        self.port = self.find_available_port()
        
        # Start HTTP server
        try:
            handler = lambda *args, **kwargs: StreamHandler(*args, stream_queue=self.stream_queue, **kwargs)
            self.httpd = socketserver.ThreadingTCPServer(("", self.port), handler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
            logger.info(f"Serving webpage at http://0.0.0.0:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")
            sys.exit(1)

        # Start FFmpeg after HTTP server is running
        self.streamer = FFmpegStreamer(self.port)
        time.sleep(1)  # Ensure server is ready
        self.streamer.start()

    def stop(self):
        if self.streamer:
            self.streamer.stop()
        if self.httpd:
            logger.info("Shutting down HTTP server...")
            self.httpd.shutdown()
            self.httpd.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=5)
                if self.server_thread.is_alive():
                    logger.warning("Server thread did not terminate, forcing exit.")
            logger.info("HTTP server stopped.")

def signal_handler(sig, frame, server):
    logger.info("Received Ctrl+C, shutting down...")
    server.stop()
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream webcam feed over the web.")
    parser.add_argument('--port', type=int, default=6000, help="Starting port number (default: 6000)")
    args = parser.parse_args()

    server = WebcamServer(start_port=args.port)
    
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, server))
    
    try:
        server.start()
        while True:
            threading.Event().wait()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        server.stop()
        sys.exit(1) 