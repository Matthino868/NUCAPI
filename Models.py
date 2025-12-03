from enum import Enum
from pydantic import BaseModel
from typing import Literal, Dict

class MachineAdapterType(Enum):
    SERIAL = 1
    COMPRESSION = 2

class Machine(BaseModel):
    # machineId: int
    name: str
    comType: MachineAdapterType
    comAddress: str
    nucId: int

# class NucModel(BaseModel):
#     name: str
#     description: str
#     machines: Dict[str, Machine]
