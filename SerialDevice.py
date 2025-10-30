from MachineInterface import MachineInterface
from serial import Serial
import threading
import re

class SerialDevice(MachineInterface):
    def __init__(self, device_id, execCommand, comAddress, name):
        super().__init__(device_id=device_id, execCommand=execCommand, comAddress=comAddress, name=name)
        self.comPort = "COM"+comAddress
        # Synchronization primitives to prevent concurrent serial access
        self._serial_lock = threading.Lock()
        self._streaming_flag = threading.Event()
        try:
            self.serialConnection = Serial(self.comPort, baudrate=9600, timeout=1)
            if self.serialConnection and self.serialConnection.is_open:
                print(f"Serial device {self.name} connected on {self.comPort}")
        except Exception as e:
            print(f"Failed to connect to serial port {self.comPort}: {e}")
            self.serialConnection = None
    
    def begin_stream(self) -> bool:
        """Claim exclusive streaming ownership. Returns False if already streaming."""
        if self._streaming_flag.is_set():
            return False
        self._streaming_flag.set()
        return True

    def end_stream(self) -> None:
        """Release streaming ownership."""
        self._streaming_flag.clear()

    def read_line(self) -> bytes:
        """Thread-safe single readline from the serial connection."""
        if not self.serialConnection:
            raise Exception("Serial connection not established.")
        with self._serial_lock:
            return self.serialConnection.readline()
        
    def get_status(self) -> str:
        if self.serialConnection and self.serialConnection.is_open:
            return "Connected"
        else:
            return "Not connected"

    def get_data(self) -> float:
        if not self.serialConnection:
            print("Serial connection not established.")
            raise Exception("Serial connection not established.")
        if self._streaming_flag.is_set():
            raise Exception("Device busy: streaming over WebSocket")
        command = self.execCommand.encode()+b'\r\n'
        with self._serial_lock:
            print(f"Sending command to {self.name} ({self.comPort}): {command}")
            self.serialConnection.write(command)
            response = self.serialConnection.readline().decode().strip()
        try:
            match = re.search(r'[-+]?\d*\.\d+', response)
            if match:
                response = match.group()
            print(f"Response from {self.name} ({self.comPort}): {response}")
            return float(response)
        except ValueError:
            print(f"Could not convert response to float: {response}")
            raise Exception(f"Invalid data received: {response}")
        
