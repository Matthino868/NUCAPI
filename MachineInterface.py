from abc import ABC, abstractmethod

class MachineInterface(ABC):
    def __init__(self, device_id: str, execCommand: str, name: str, comAddress: str):
        self.device_id = device_id
        self.execCommand = execCommand
        self.name = name
        self.comAddress = comAddress 
        
    @abstractmethod
    def get_status(self) -> str:
        """Return the current status of the machine."""
        pass

    @abstractmethod
    def get_data(self) -> float:
        """Return the latest data from the machine."""
        pass