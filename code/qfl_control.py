#!/usr/bin/env python3
"""
QFL Control System - Python Interface
Quantum-Flux Lab - Advanced Control & Monitoring

Version: 1.0
Date: 2026-01-31
License: MIT

This module provides:
- Serial communication with Arduino controller
- Gamepad (Xbox/PS4) interface for real-time control
- Data logging and visualization
- Safety monitoring and alerting
- Web interface for remote monitoring

Requirements:
    pip install pyserial pygame matplotlib numpy flask

Open Source References:
    - Corona physics: Riba et al., Sensors 21(19):6676 (2021)
    - EHD thrust: Ianconescu et al., J. Electrostatics 69 (2011)
    - NASA HDBK-4007 for safety protocols
"""

import serial
import serial.tools.list_ports
import threading
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, asdict
import numpy as np

# Optional imports with graceful degradation
try:
    import pygame
    from pygame import joystick
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available - gamepad control disabled")

try:
    from flask import Flask, jsonify, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: flask not available - web interface disabled")

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """System configuration"""
    serial_port: str = "auto"  # "auto" for auto-detect
    baud_rate: int = 115200
    data_log_path: str = "logs/sensor_data.csv"
    command_log_path: str = "logs/commands.log"
    web_port: int = 8080
    update_interval: float = 0.1  # seconds
    
    # Safety thresholds (match Arduino settings)
    temp_warning: float = 40.0
    temp_critical: float = 50.0
    ozone_warning: float = 0.05
    ozone_critical: float = 0.08
    current_warning: float = 0.8
    current_critical: float = 1.2

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SensorData:
    """Sensor readings from device"""
    timestamp: int
    temperature1: float
    temperature2: float
    ozone: float
    uv: float
    current: float
    voltage: float
    spl: float
    state: str
    
    @classmethod
    def from_csv(cls, csv_line: str) -> Optional['SensorData']:
        """Parse CSV data from Arduino"""
        try:
            parts = csv_line.strip().split(',')
            if len(parts) >= 9 and parts[0] == "DATA":
                return cls(
                    timestamp=int(parts[1]),
                    temperature1=float(parts[2]),
                    temperature2=float(parts[3]),
                    ozone=float(parts[4]),
                    uv=float(parts[5]),
                    current=float(parts[6]),
                    voltage=float(parts[7]),
                    spl=float(parts[8]),
                    state=parts[9] if len(parts) > 9 else "UNKNOWN"
                )
        except (ValueError, IndexError):
            pass
        return None

@dataclass
class ControlParams:
    """Control parameters for device"""
    hv_amplitude: int = 128  # 0-255
    hv_frequency: int = 400  # Hz
    audio_frequency: int = 20  # Hz
    audio_amplitude: int = 100  # 0-255
    enable_hv: bool = False
    enable_audio: bool = False

# =============================================================================
# SERIAL COMMUNICATION
# =============================================================================

class ArduinoInterface:
    """Handles serial communication with Arduino controller"""
    
    def __init__(self, config: Config):
        self.config = config
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.data_buffer: List[SensorData] = []
        self.callbacks: List[Callable[[SensorData], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
    def find_port(self) -> Optional[str]:
        """Auto-detect Arduino port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Common Arduino identifiers
            if any(id in port.description.lower() for id in 
                   ['arduino', 'ch340', 'ft232', 'usb-serial']):
                return port.device
        # Fallback to first available port
        if ports:
            return ports[0].device
        return None
    
    def connect(self) -> bool:
        """Establish serial connection"""
        port = self.config.serial_port
        if port == "auto":
            port = self.find_port()
            if not port:
                print("ERROR: Could not find Arduino port")
                return False
        
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=self.config.baud_rate,
                timeout=1
            )
            time.sleep(2)  # Wait for Arduino reset
            self.connected = True
            print(f"Connected to Arduino on {port}")
            
            # Start reading thread
            self._running = True
            self._thread = threading.Thread(target=self._read_loop)
            self._thread.daemon = True
            self._thread.start()
            
            return True
        except serial.SerialException as e:
            print(f"ERROR: Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self.serial:
            self.serial.close()
        self.connected = False
        print("Disconnected from Arduino")
    
    def _read_loop(self):
        """Background thread for reading serial data"""
        while self._running and self.serial:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='ignore')
                    data = SensorData.from_csv(line)
                    if data:
                        with self._lock:
                            self.data_buffer.append(data)
                            # Keep last 1000 readings
                            if len(self.data_buffer) > 1000:
                                self.data_buffer.pop(0)
                        # Notify callbacks
                        for callback in self.callbacks:
                            try:
                                callback(data)
                            except Exception:
                                pass
                    else:
                        # Print non-data lines
                        line = line.strip()
                        if line:
                            print(f"[Arduino] {line}")
            except serial.SerialException:
                break
            time.sleep(0.001)
    
    def send_command(self, command: str) -> bool:
        """Send command to Arduino"""
        if not self.connected or not self.serial:
            return False
        try:
            self.serial.write(f"{command}\n".encode())
            return True
        except serial.SerialException:
            return False
    
    def get_latest_data(self) -> Optional[SensorData]:
        """Get most recent sensor data"""
        with self._lock:
            return self.data_buffer[-1] if self.data_buffer else None
    
    def get_data_history(self, n: int = 100) -> List[SensorData]:
        """Get last n sensor readings"""
        with self._lock:
            return self.data_buffer[-n:]

# =============================================================================
# GAMEPAD INTERFACE
# =============================================================================

class GamepadInterface:
    """Handles Xbox/PS4 controller input"""
    
    def __init__(self):
        self.initialized = False
        self.joystick = None
        self.control_callback: Optional[Callable[[ControlParams], None]] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.params = ControlParams()
        
    def init(self) -> bool:
        """Initialize gamepad"""
        if not PYGAME_AVAILABLE:
            print("Pygame not available - gamepad disabled")
            return False
        
        pygame.init()
        joystick.init()
        
        if joystick.get_count() == 0:
            print("No gamepad found")
            return False
        
        self.joystick = joystick.Joystick(0)
        self.joystick.init()
        self.initialized = True
        
        print(f"Gamepad initialized: {self.joystick.get_name()}")
        print("Controls:")
        print("  Left Stick Y: HV Amplitude")
        print("  Right Stick Y: Audio Amplitude")
        print("  D-Pad Up/Down: HV Frequency")
        print("  Button A/Cross: Toggle HV")
        print("  Button B/Circle: Toggle Audio")
        print("  Button X/Square: Emergency Stop")
        
        return True
    
    def start(self):
        """Start gamepad polling"""
        if not self.initialized:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        """Stop gamepad polling"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
    
    def _poll_loop(self):
        """Poll gamepad state"""
        clock = pygame.time.Clock()
        
        while self._running:
            pygame.event.pump()
            
            # Read axes
            left_y = -self.joystick.get_axis(1)  # Invert (up is positive)
            right_y = -self.joystick.get_axis(3)
            
            # Map to control parameters
            self.params.hv_amplitude = int((left_y + 1) * 127.5)  # 0-255
            self.params.audio_amplitude = int((right_y + 1) * 127.5)
            
            # D-pad for frequency
            hat = self.joystick.get_hat(0)
            if hat[1] > 0:
                self.params.hv_frequency = min(2000, self.params.hv_frequency + 10)
            elif hat[1] < 0:
                self.params.hv_frequency = max(100, self.params.hv_frequency - 10)
            
            # Buttons
            if self.joystick.get_button(0):  # A/Cross
                self.params.enable_hv = not self.params.enable_hv
                time.sleep(0.3)  # Debounce
            if self.joystick.get_button(1):  # B/Circle
                self.params.enable_audio = not self.params.enable_audio
                time.sleep(0.3)
            if self.joystick.get_button(2):  # X/Square - Emergency stop
                self.params.enable_hv = False
                self.params.enable_audio = False
            
            # Notify callback
            if self.control_callback:
                self.control_callback(self.params)
            
            clock.tick(30)  # 30 Hz polling
    
    def get_params(self) -> ControlParams:
        """Get current control parameters"""
        return self.params

# =============================================================================
# DATA LOGGER
# =============================================================================

class DataLogger:
    """Logs sensor data to file"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_file: Optional[Path] = None
        self.command_file: Optional[Path] = None
        
    def init(self):
        """Initialize log files"""
        # Create directories
        Path(self.config.data_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.config.command_log_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Data log
        self.data_file = Path(self.config.data_log_path)
        if not self.data_file.exists():
            with open(self.data_file, 'w') as f:
                f.write("timestamp,temperature1,temperature2,ozone,uv,current,voltage,spl,state\n")
        
        # Command log
        self.command_file = Path(self.config.command_log_path)
        
    def log_data(self, data: SensorData):
        """Log sensor reading"""
        if not self.data_file:
            return
        with open(self.data_file, 'a') as f:
            f.write(f"{data.timestamp},{data.temperature1},{data.temperature2},"
                   f"{data.ozone},{data.uv},{data.current},{data.voltage},"
                   f"{data.spl},{data.state}\n")
    
    def log_command(self, command: str):
        """Log command sent to device"""
        if not self.command_file:
            return
        with open(self.command_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()},{command}\n")

# =============================================================================
# SAFETY MONITOR
# =============================================================================

class SafetyMonitor:
    """Monitors safety parameters and alerts"""
    
    def __init__(self, config: Config):
        self.config = config
        self.alert_handlers: List[Callable[[str, str], None]] = []
        self._last_alert = ""
        self._alert_cooldown = 0
    
    def check_data(self, data: SensorData) -> bool:
        """Check if data is within safety limits"""
        alerts = []
        
        # Temperature
        if data.temperature1 > self.config.temp_critical or \
           data.temperature2 > self.config.temp_critical:
            alerts.append(("CRITICAL", f"Overtemperature: {data.temperature1:.1f}C"))
        elif data.temperature1 > self.config.temp_warning or \
             data.temperature2 > self.config.temp_warning:
            alerts.append(("WARNING", f"High temperature: {data.temperature1:.1f}C"))
        
        # Ozone
        if data.ozone > self.config.ozone_critical:
            alerts.append(("CRITICAL", f"Ozone level: {data.ozone:.3f} ppm"))
        elif data.ozone > self.config.ozone_warning:
            alerts.append(("WARNING", f"Elevated ozone: {data.ozone:.3f} ppm"))
        
        # Current
        if data.current > self.config.current_critical:
            alerts.append(("CRITICAL", f"Overcurrent: {data.current:.2f}A"))
        elif data.current > self.config.current_warning:
            alerts.append(("WARNING", f"High current: {data.current:.2f}A"))
        
        # State-based alerts
        if data.state == "EMERGENCY_STOP":
            alerts.append(("CRITICAL", "Emergency stop active"))
        elif data.state == "CRITICAL":
            alerts.append(("CRITICAL", "System in critical state"))
        
        # Send alerts (with cooldown)
        if alerts and time.time() > self._alert_cooldown:
            for level, message in alerts:
                alert_key = f"{level}:{message}"
                if alert_key != self._last_alert:
                    self._trigger_alert(level, message)
                    self._last_alert = alert_key
                    self._alert_cooldown = time.time() + 5  # 5 second cooldown
        
        return len(alerts) == 0
    
    def _trigger_alert(self, level: str, message: str):
        """Trigger alert handlers"""
        print(f"\n!!! {level}: {message} !!!\n")
        for handler in self.alert_handlers:
            try:
                handler(level, message)
            except Exception as e:
                print(f"Alert handler error: {e}")

# =============================================================================
# WEB INTERFACE
# =============================================================================

if FLASK_AVAILABLE:
    app = Flask(__name__)
    
    class WebInterface:
        """Flask web server for remote monitoring"""
        
        def __init__(self, arduino: ArduinoInterface, config: Config):
            self.arduino = arduino
            self.config = config
            self.server_thread: Optional[threading.Thread] = None
        
        def start(self):
            """Start web server in background"""
            self.server_thread = threading.Thread(
                target=lambda: app.run(
                    host='0.0.0.0',
                    port=self.config.web_port,
                    debug=False,
                    use_reloader=False
                )
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"Web interface started on http://localhost:{self.config.web_port}")
        
        def register_routes(self):
            """Register Flask routes"""
            
            @app.route('/')
            def index():
                return render_template_string(HTML_TEMPLATE)
            
            @app.route('/api/status')
            def api_status():
                data = self.arduino.get_latest_data()
                if data:
                    return jsonify(asdict(data))
                return jsonify({"error": "No data available"})
            
            @app.route('/api/history/<int:n>')
            def api_history(n):
                data = self.arduino.get_data_history(n)
                return jsonify([asdict(d) for d in data])
            
            @app.route('/api/command/<cmd>')
            def api_command(cmd):
                success = self.arduino.send_command(cmd)
                return jsonify({"success": success})

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>QFL Control</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .panel { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .value { font-size: 24px; font-weight: bold; color: #4CAF50; }
        .label { font-size: 12px; color: #888; }
        .warning { color: #ff9800; }
        .critical { color: #f44336; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        .controls { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🧲 RPAT Control Interface</h1>
    <div class="panel">
        <h2>Real-time Data</h2>
        <div id="data">Loading...</div>
    </div>
    <div class="panel controls">
        <h2>Controls</h2>
        <button onclick="cmd('start')">Start</button>
        <button onclick="cmd('stop')">Stop</button>
        <button onclick="cmd('status')">Refresh Status</button>
    </div>
    <script>
        async function updateData() {
            try {
                const r = await fetch('/api/status');
                const d = await r.json();
                document.getElementById('data').innerHTML = `
                    <div class="metric"><div class="value ${d.state === 'RUNNING' ? '' : 'warning'}">${d.state}</div><div class="label">State</div></div>
                    <div class="metric"><div class="value ${d.temperature1 > 40 ? 'warning' : ''}">${d.temperature1.toFixed(1)}°C</div><div class="label">Temperature 1</div></div>
                    <div class="metric"><div class="value ${d.temperature2 > 40 ? 'warning' : ''}">${d.temperature2.toFixed(1)}°C</div><div class="label">Temperature 2</div></div>
                    <div class="metric"><div class="value ${d.ozone > 0.05 ? 'warning' : ''}">${d.ozone.toFixed(3)}</div><div class="label">Ozone (ppm)</div></div>
                    <div class="metric"><div class="value ${d.current > 0.8 ? 'warning' : ''}">${d.current.toFixed(2)}A</div><div class="label">Current</div></div>
                    <div class="metric"><div class="value">${d.spl.toFixed(1)}dB</div><div class="label">SPL</div></div>
                `;
            } catch(e) { document.getElementById('data').innerText = 'Connection error'; }
        }
        async function cmd(c) { await fetch('/api/command/' + c); updateData(); }
        updateData();
        setInterval(updateData, 2000);
    </script>
</body>
</html>
"""

# =============================================================================
# MAIN APPLICATION
# =============================================================================

class RPATController:
    """Main application controller"""
    
    def __init__(self):
        self.config = Config()
        self.arduino = ArduinoInterface(self.config)
        self.gamepad = GamepadInterface()
        self.logger = DataLogger(self.config)
        self.safety = SafetyMonitor(self.config)
        self.web: Optional['WebInterface'] = None
        self._running = False
        
    def init(self) -> bool:
        """Initialize all components"""
        print("=" * 50)
        print("RPAT Control System v1.0")
        print("Resonant Plasma Acoustic Trap")
        print("=" * 50)
        
        # Initialize logger
        self.logger.init()
        print("✓ Logger initialized")
        
        # Connect to Arduino
        if not self.arduino.connect():
            print("Failed to connect to Arduino")
            return False
        print("✓ Arduino connected")
        
        # Set up data callback
        self.arduino.callbacks.append(self._on_data)
        
        # Initialize gamepad
        if self.gamepad.init():
            self.gamepad.control_callback = self._on_gamepad
            self.gamepad.start()
            print("✓ Gamepad initialized")
        
        # Initialize web interface
        if FLASK_AVAILABLE:
            self.web = WebInterface(self.arduino, self.config)
            self.web.register_routes()
            self.web.start()
            print("✓ Web interface started")
        
        return True
    
    def _on_data(self, data: SensorData):
        """Handle new sensor data"""
        self.logger.log_data(data)
        self.safety.check_data(data)
    
    def _on_gamepad(self, params: ControlParams):
        """Handle gamepad input"""
        # Send commands to Arduino based on parameter changes
        if params.enable_hv:
            self.arduino.send_command(f"hv {params.hv_amplitude}")
            self.arduino.send_command(f"freq {params.hv_frequency}")
    
    def run(self):
        """Main application loop"""
        self._running = True
        
        print("\nSystem ready. Commands:")
        print("  start  - Begin operation")
        print("  stop   - Emergency stop")
        print("  status - Show current status")
        print("  quit   - Exit program")
        print()
        
        while self._running:
            try:
                cmd = input("QFL> ").strip().lower()
                
                if cmd == "quit" or cmd == "exit":
                    self._running = False
                elif cmd in ["start", "stop", "status", "help", "reset"]:
                    self.arduino.send_command(cmd)
                    self.logger.log_command(cmd)
                else:
                    print("Unknown command. Try: start, stop, status, help, quit")
                    
            except KeyboardInterrupt:
                self._running = False
        
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        print("\nShutting down...")
        self.arduino.send_command("stop")
        self.gamepad.stop()
        self.arduino.disconnect()
        print("Goodbye!")

# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    controller = RPATController()
    if controller.init():
        controller.run()
    else:
        print("Initialization failed")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
