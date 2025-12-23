from Models import MachineAdapter
from serial import Serial
import threading

class SerialPortHandler(MachineAdapter):
    def __init__(self, device_id,comAddress, name, parser=None):
        super().__init__(device_id=device_id, comAddress=comAddress, name=name)
        self.comPort = "COM"+str(comAddress)
        # Synchronization primitives to prevent concurrent serial access
        self._serial_lock = threading.Lock()
        self._streaming_flag = threading.Event()
        self.parser = parser
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
        """
        Sends '0' over the serial connection and reads a response.
        Returns the parsed float value.
        """
        if not self.serialConnection or not self.serialConnection.is_open:
            raise Exception("Serial connection not established.")

        with self._serial_lock:
            # Send command
            self.serialConnection.write(b'1\r\n')
            print("serial flushed")

            # Read response
            response = self.serialConnection.readline()
            print(f"Raw response from {self.name}: {response}")

        if not response:
            raise Exception("No data received from serial device.")

        try:
            decoded = response.decode('utf-8').strip()
        except UnicodeDecodeError as e:
            raise Exception(f"Failed to decode serial response: {e}")

        # Use parser if provided
        if self.parser:
            return float(self.parser(decoded))

        # Default behavior: direct float conversion
        try:
            return float(decoded)
        except ValueError as e:
            raise Exception(f"Invalid numeric data received: '{decoded}'") from e
        