
from enum import Enum
from dataclasses import dataclass, asdict

class StatusType(Enum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

@dataclass
class Event:
    id: str
    filekey: str
    status: StatusType
    downloadUrl: str
    createdAt: str
    error: str = None

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("id cannot be empty and must be a string")
        if not self.filekey or not isinstance(self.filekey, str):
            raise ValueError("filekey cannot be empty and must be a string")
        if not self.status or not isinstance(self.status, StatusType):
            raise ValueError("status cannot be empty and must be a StatusType type")
        if not self.createdAt or not isinstance(self.createdAt, str):
            raise ValueError("createdAt cannot be empty and must be a string")

    def to_dict(self):
        item = asdict(self)
        item["status"] = self.status.value
        return item