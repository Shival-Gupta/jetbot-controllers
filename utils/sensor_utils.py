#!/usr/bin/env python3
"""
Sensor utility functions for Mecanum robot
This module provides calibration and testing functions for sensors
"""

import time
import sys
import json
import os
try:
    import serial
    import numpy as np
except ImportError:
    print("Missing dependencies. Run: pip install pyserial numpy")
    sys.exit(1)

def calibrate_ir_sensors(port, baud_rate=9600, samples=50):
    """
    Calibrates infrared line sensors by measuring surfaces and calculating thresholds
    
    Args:
        port (str): Serial port connected to Arduino
        baud_rate (int): Baud rate for serial communication
        samples (int): Number of samples to collect for each surface
        
    Returns:
        dict: Calibration values for IR sensors
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")
        time.sleep(2)  # Wait for Arduino to reset
        
        print("\nIR Sensor Calibration")
        print("====================")
        print("This utility helps calibrate IR sensors for line following.")
        print(f"Place the robot on each surface as prompted and {samples} readings will be taken.")
        
        # Collect data for the line (dark surface)
        input("\nPlace sensors over the LINE (dark surface) and press Enter...")
        dark_values = _collect_sensor_readings(ser, samples)
        
        # Collect data for the background (light surface)
        input("\nPlace sensors over the BACKGROUND (light surface) and press Enter...")
        light_values = _collect_sensor_readings(ser, samples)
        
        # Calculate thresholds
        calibration = {
            "left": {
                "dark_avg": dark_values["left"]["mean"],
                "light_avg": light_values["left"]["mean"],
                "threshold": (dark_values["left"]["mean"] + light_values["left"]["mean"]) / 2
            },
            "center": {
                "dark_avg": dark_values["center"]["mean"],
                "light_avg": light_values["center"]["mean"],
                "threshold": (dark_values["center"]["mean"] + light_values["center"]["mean"]) / 2
            },
            "right": {
                "dark_avg": dark_values["right"]["mean"],
                "light_avg": light_values["right"]["mean"],
                "threshold": (dark_values["right"]["mean"] + light_values["right"]["mean"]) / 2
            }
        }
        
        # Determine if line is darker or lighter than background
        avg_dark = (dark_values["left"]["mean"] + dark_values["center"]["mean"] + dark_values["right"]["mean"]) / 3
        avg_light = (light_values["left"]["mean"] + light_values["center"]["mean"] + light_values["right"]["mean"]) / 3
        calibration["line_is_darker"] = avg_dark < avg_light
        
        ser.close()
        print("\nCalibration completed.")
        print(f"Line is {'darker' if calibration['line_is_darker'] else 'lighter'} than background.")
        print("Sensor thresholds:")
        print(f"  Left: {calibration['left']['threshold']:.1f}")
        print(f"  Center: {calibration['center']['threshold']:.1f}")
        print(f"  Right: {calibration['right']['threshold']:.1f}")
        
        return calibration
        
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None

def _collect_sensor_readings(ser, samples):
    """
    Helper function to collect sensor readings from Arduino
    
    Args:
        ser (serial.Serial): Open serial connection
        samples (int): Number of samples to collect
        
    Returns:
        dict: Sensor data with statistics
    """
    print(f"Collecting {samples} samples...")
    
    left_values = []
    center_values = []
    right_values = []
    
    # Request sensor readings from Arduino (assuming it responds with "L,C,R" format)
    for i in range(samples):
        ser.write(b"GET_SENSORS\n")
        response = ser.readline().decode('utf-8').strip()
        try:
            l, c, r = map(int, response.split(','))
            left_values.append(l)
            center_values.append(c)
            right_values.append(r)
            sys.stdout.write(f"\rProgress: {i+1}/{samples}")
            sys.stdout.flush()
            time.sleep(0.1)
        except (ValueError, AttributeError):
            # Skip invalid readings
            pass
    
    print()  # New line after progress
    
    # Calculate statistics
    results = {
        "left": {
            "mean": np.mean(left_values),
            "std": np.std(left_values),
            "min": np.min(left_values),
            "max": np.max(left_values)
        },
        "center": {
            "mean": np.mean(center_values),
            "std": np.std(center_values),
            "min": np.min(center_values),
            "max": np.max(center_values)
        },
        "right": {
            "mean": np.mean(right_values),
            "std": np.std(right_values),
            "min": np.min(right_values),
            "max": np.max(right_values)
        }
    }
    
    return results

def calibrate_mpu6050(port, baud_rate=9600, duration=10):
    """
    Calibrates the MPU6050 IMU sensor by collecting data at rest
    
    Args:
        port (str): Serial port connected to Arduino
        baud_rate (int): Baud rate for serial communication
        duration (int): Duration in seconds to collect calibration data
        
    Returns:
        dict: Calibration offsets for gyroscope and accelerometer
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")
        time.sleep(2)  # Wait for Arduino to reset
        
        print("\nMPU6050 IMU Calibration")
        print("======================")
        print("This utility helps calibrate the MPU6050 IMU sensor.")
        print("Place the robot on a flat, level surface and keep it still.")
        
        input(f"\nReady to begin {duration}-second calibration? Press Enter...")
        
        # Request IMU calibration from Arduino
        ser.write(f"CALIBRATE_IMU,{duration}\n".encode())
        
        # Show progress
        for i in range(duration):
            sys.stdout.write(f"\rCalibrating: {i+1}/{duration}s")
            sys.stdout.flush()
            time.sleep(1)
            
        print("\nProcessing calibration data...")
        
        # Read calibration results
        ser.write(b"GET_IMU_CALIBRATION\n")
        response = ser.readline().decode('utf-8').strip()
        
        try:
            # Parse response (format: "gx,gy,gz,ax,ay,az")
            values = list(map(int, response.split(',')))
            calibration = {
                "gyro_offset": {
                    "x": values[0],
                    "y": values[1],
                    "z": values[2]
                },
                "accel_offset": {
                    "x": values[3],
                    "y": values[4],
                    "z": values[5]
                }
            }
            
            ser.close()
            print("\nCalibration completed.")
            print("Gyroscope offsets:")
            print(f"  X: {calibration['gyro_offset']['x']}")
            print(f"  Y: {calibration['gyro_offset']['y']}")
            print(f"  Z: {calibration['gyro_offset']['z']}")
            print("Accelerometer offsets:")
            print(f"  X: {calibration['accel_offset']['x']}")
            print(f"  Y: {calibration['accel_offset']['y']}")
            print(f"  Z: {calibration['accel_offset']['z']}")
            
            return calibration
            
        except (ValueError, IndexError):
            print(f"Error parsing calibration data: {response}")
            return None
            
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None

def save_calibration(calibration, filename):
    """
    Save calibration data to a JSON file
    
    Args:
        calibration (dict): Calibration data
        filename (str): Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            json.dump(calibration, f, indent=2)
        print(f"Calibration data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving calibration: {e}")
        return False

def load_calibration(filename):
    """
    Load calibration data from a JSON file
    
    Args:
        filename (str): Path to the calibration file
        
    Returns:
        dict: Calibration data or None if error
    """
    try:
        with open(filename, 'r') as f:
            calibration = json.load(f)
        print(f"Calibration data loaded from {filename}")
        return calibration
    except Exception as e:
        print(f"Error loading calibration: {e}")
        return None

if __name__ == "__main__":
    # Example usage when run as script
    if len(sys.argv) < 2:
        print("Usage: python sensor_utils.py <serial_port> [ir|imu]")
        sys.exit(1)
        
    port = sys.argv[1]
    action = "ir" if len(sys.argv) < 3 else sys.argv[2]
    
    if action == "ir":
        calibration = calibrate_ir_sensors(port)
        if calibration:
            save_calibration(calibration, "ir_calibration.json")
    elif action == "imu":
        calibration = calibrate_mpu6050(port)
        if calibration:
            save_calibration(calibration, "imu_calibration.json")
    else:
        print(f"Unknown action: {action}")
        print("Valid actions: ir, imu") 