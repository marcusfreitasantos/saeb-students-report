from dataclasses import dataclass

@dataclass
class Student:
    name: str
    average: float

    def status(self) -> str:
        if self.average >= 70:
            return "🟢 GOOD"
        elif self.average >= 50:
            return "🟡 REGULAR"
        return "🔴 CRITICAL"