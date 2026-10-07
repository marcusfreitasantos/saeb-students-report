import re
import unicodedata
from datetime import datetime, timezone
from uuid import uuid4

from domain.entities.lead import Lead
from infrastructure.config.settings import settings


ALLOWED_GRADUATIONS = (
    "sem escolaridade",
    "ensino fundamental incompleto",
    "ensino fundamental completo",
    "ensino médio incompleto",
    "ensino médio completo",
    "ensino superior incompleto",
    "ensino superior completo",
    "pós-graduação",
    "mestrado",
    "doutorado e phd",
)

GRADUATION_ALIASES = {
    "pos graduacao": "pós-graduação",
    "pos-graduacao": "pós-graduação",
    "doutorado e ph.d": "doutorado e phd",
    "doutorado e ph.d.": "doutorado e phd",
}

NORMALIZED_GRADUATIONS = {
    unicodedata.normalize("NFKD", graduation)
    .encode("ascii", "ignore")
    .decode("ascii"): graduation
    for graduation in ALLOWED_GRADUATIONS
}

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x1f\x7f]")
MULTIPLE_SPACES_REGEX = re.compile(r"\s+")
PHONE_REGEX = re.compile(r"^\+?[0-9]{10,15}$")


class ValidationError(Exception):
    pass


class LeadUseCase:
    def __init__(self, dynamodb_client):
        self.dynamodb_client = dynamodb_client

    def create(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValidationError("Payload must be a JSON object")

        sanitized_payload = {
            "name": self._sanitize_text(payload.get("name"), "name", max_length=120),
            "email": self._sanitize_email(payload.get("email")),
            "phone": self._sanitize_phone(payload.get("phone")),
            "graduation": self._sanitize_graduation(payload.get("graduation")),
            "occupation": self._sanitize_text(
                payload.get("occupation"),
                "occupation",
                max_length=120,
            ),
        }

        now = datetime.now(timezone.utc).isoformat()
        lead = Lead(
            id=str(uuid4()),
            createdAt=now,
            updatedAt=now,
            **sanitized_payload,
        )

        self.dynamodb_client.save(settings.DYNAMO_LEADS_TABLE, lead.to_dict())

        return lead.to_dict()

    def _sanitize_text(self, value, field_name: str, max_length: int):
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} is required and must be a string")

        sanitized = CONTROL_CHARS_REGEX.sub("", value)
        sanitized = MULTIPLE_SPACES_REGEX.sub(" ", sanitized).strip()

        if not sanitized:
            raise ValidationError(f"{field_name} is required")

        if len(sanitized) > max_length:
            raise ValidationError(f"{field_name} must contain at most {max_length} characters")

        return sanitized

    def _sanitize_email(self, value):
        email = self._sanitize_text(value, "email", max_length=254).lower()

        if not EMAIL_REGEX.match(email):
            raise ValidationError("email must be a valid email address")

        return email

    def _sanitize_phone(self, value):
        if not isinstance(value, str):
            raise ValidationError("phone is required and must be a string")

        value = value.strip()
        has_plus_prefix = value.startswith("+")
        digits = re.sub(r"\D", "", value)
        phone = f"+{digits}" if has_plus_prefix else digits

        if not PHONE_REGEX.match(phone):
            raise ValidationError("phone must contain 10 to 15 digits")

        return phone

    def _sanitize_graduation(self, value):
        graduation = self._sanitize_text(value, "graduation", max_length=80).lower()
        normalized_graduation = self._strip_accents(graduation)
        graduation = GRADUATION_ALIASES.get(
            normalized_graduation,
            NORMALIZED_GRADUATIONS.get(normalized_graduation),
        )

        if graduation not in ALLOWED_GRADUATIONS:
            allowed_values = ", ".join(ALLOWED_GRADUATIONS)
            raise ValidationError(f"graduation must be one of: {allowed_values}")

        return graduation

    def _strip_accents(self, value: str):
        normalized = unicodedata.normalize("NFKD", value)
        return "".join(char for char in normalized if not unicodedata.combining(char))
