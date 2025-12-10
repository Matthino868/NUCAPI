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
        raise NotImplementedError("get_data method is not implemented for SerialPortHandler.")
