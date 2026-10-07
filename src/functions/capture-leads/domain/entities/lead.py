from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Lead:
    id: str
    name: str
    email: str
    phone: str
    graduation: str
    occupation: str
    createdAt: str
    updatedAt: str

    def to_dict(self):
        return asdict(self)
