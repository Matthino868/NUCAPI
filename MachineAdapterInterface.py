from abc import ABC, abstractmethod

class MachineAdapterInterface(ABC):
    def __init__(self, device_id: int, name: str, comAddress: str):
        self.device_id: int = device_id
        self.name: str = name
        self.comAddress: str = comAddress 
        
    @abstractmethod
    def get_status(self) -> str:
        """Return the current status of the machine."""
        pass

    @abstractmethod
    def get_data(self) -> float:
        """Return the latest data from the machine."""
        pass