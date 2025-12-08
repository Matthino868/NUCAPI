from enum import Enum
from pydantic import BaseModel
from typing import Literal, Dict

from Parsers import caliperParser, scaleParser

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

# class NucModel(BaseModel):
#     name: str
#     description: str
#     machines: Dict[str, Machine]
