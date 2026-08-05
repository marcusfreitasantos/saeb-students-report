from dataclasses import asdict, dataclass


@dataclass
class ReportResult:
    success: bool
    message: str

    def to_dict(self):
        return asdict(self)
