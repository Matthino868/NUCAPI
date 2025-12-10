from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel

class MachineAdapterType(Enum):
    SERIAL = 1
    COMPRESSION = 2
    SCALE = 3
    CALIPER = 4


class Machine(BaseModel):
    # machineId: int
    name: str
    comType: MachineAdapterType
    comAddress: str
    nucId: int

class MachineAdapter(ABC):
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
