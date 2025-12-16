from dataclasses import dataclass
from typing import Optional

@dataclass
class Request:
    requestID: int
    startDate: str
    climateTechType: str
    climateTechModel: str
    problemDescryption: str
    requestStatus: str
    completionDate: Optional[str]
    repairParts: Optional[str]
    masterID: Optional[int]
    clientID: int