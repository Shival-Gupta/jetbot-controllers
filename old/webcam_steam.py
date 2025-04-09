#!/usr/bin/env python3
"""
webcam_steam.py
Version: 1.0

Description: OpenCV-based webcam streaming server for Mecanum robot
remote monitoring. Provides a web interface to view the robot's camera feed.

Compatible with:
  - All Mecanum robot Arduino firmware files
  - Can be used alongside any controller
"""

import cv2
import threading
import socket
import logging
import time
import argparse
import sys
import signal
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self, device=0, video_size=(640, 480), fps=30):
        self.device = device
        self.video_size = video_size
        self.fps = fps
        self.is_running = False
        self.lock = threading.Lock()
        self.frame = None
        self.camera = None
        self.thread = None

    def start(self):
        if self.is_running:
            logger.warning("Camera is already running")
            return

        try:
            self.camera = cv2.VideoCapture(self.device)
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera device {self.device}")
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size[1])
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_running = True
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
            logger.info(f"Camera started on device {self.device}")
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            if self.camera is not None and self.camera.isOpened():
                self.camera.release()
            self.is_running = False
            raise

    def _update_frame(self):
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    logger.warning("Failed to get frame from camera")
                    time.sleep(0.1)
                    continue
                    
                with self.lock:
                    self.frame = frame
            except Exception as e:
                logger.error(f"Error in camera loop: {e}")
                time.sleep(0.1)

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            # Create a jpeg from the frame
            _, jpeg = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            return jpeg.tobytes()

    def stop(self):
        self.is_running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
        logger.info("Camera stopped")

class StreamingHandler(BaseHTTPRequestHandler):
    def __init__(self, camera_handler, *args, **kwargs):
        self.camera_handler = camera_handler
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f'''
            <html>
            <head>
                <title>Live Camera Feed</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        text-align: center;
                    }}
                    h1 {{
                        color: #333;
                    }}
                    img {{
                        max-width: 100%;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 5px;
                    }}
                </style>
            </head>
            <body>
                <h1>Live Camera Feed</h1>
                <img src="/stream" alt="Live Video Stream">
            </body>
            </html>
            '''.encode('utf-8')
            self.wfile.write(html)
            
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = self.camera_handler.get_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue
                        
                    self.wfile.write(b'--FRAME\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(frame)}\r\n\r\n'.encode())
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                logger.info("Client disconnected")
            except Exception as e:
                logger.error(f"Error streaming: {e}")
        else:
            self.send_error(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class WebcamStreamer:
    def __init__(self, port=8000, device=0, width=640, height=480, fps=30):
        self.port = port
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_handler = None
        self.server = None
        self.server_thread = None

    def start(self):
        try:
            # Find available port
            self.port = self._find_available_port(self.port)
            
            # Start camera
            self.camera_handler = CameraHandler(
                device=self.device,
                video_size=(self.width, self.height),
                fps=self.fps
            )
            self.camera_handler.start()
            
            # Create a custom handler with access to the camera handler
            handler = lambda *args: StreamingHandler(self.camera_handler, *args)
            
            # Start server
            self.server = ThreadedHTTPServer(('0.0.0.0', self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"Server started at http://0.0.0.0:{self.port}")
            logger.info("Press Ctrl+C to stop the server")
            
            return self.port
        except Exception as e:
            logger.error(f"Error starting streamer: {e}")
            self.stop()
            raise

    def _find_available_port(self, start_port):
        port = start_port
        max_port = start_port + 100  # Try up to 100 ports
        
        while port < max_port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    logger.warning(f"Port {port} is in use, trying next...")
                    port += 1
        
        raise RuntimeError(f"Could not find available port in range {start_port}-{max_port}")

    def stop(self):
        if self.camera_handler:
            self.camera_handler.stop()
            
        if self.server:
            logger.info("Shutting down server...")
            self.server.shutdown()
            self.server.server_close()
            
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
            
        logger.info("Server stopped")

def parse_args():
    parser = argparse.ArgumentParser(description="Stream camera feed over HTTP")
    parser.add_argument('--port', type=int, default=8000, help="Starting port number (default: 8000)")
    parser.add_argument('--device', type=int, default=0, help="Camera device index (default: 0)")
    parser.add_argument('--width', type=int, default=640, help="Video width (default: 640)")
    parser.add_argument('--height', type=int, default=480, help="Video height (default: 480)")
    parser.add_argument('--fps', type=int, default=30, help="Frames per second (default: 30)")
    return parser.parse_args()

def main():
    args = parse_args()
    streamer = WebcamStreamer(
        port=args.port,
        device=args.device,
        width=args.width,
        height=args.height,
        fps=args.fps
    )
    
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal, shutting down...")
        streamer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        port = streamer.start()
        logger.info(f"Access the stream at: http://localhost:{port}")
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        streamer.stop()
        sys.exit(1)

if __name__ == "__main__":
    main() 