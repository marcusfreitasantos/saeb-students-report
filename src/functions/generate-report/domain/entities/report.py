from dataclasses import asdict, dataclass


@dataclass
class ReportResult:
    success: bool
    message: str
    pdf_download_url: str | None = None
    docx_download_url: str | None = None
    html_url: str | None = None

    def to_dict(self):
        return asdict(self)
