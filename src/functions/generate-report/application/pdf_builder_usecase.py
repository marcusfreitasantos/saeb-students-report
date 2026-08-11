import io
from collections.abc import Callable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class ReportPdfBuilder:
    margin = 1.2 * cm

    def build(
        self,
        diagnosis,
        descriptors: list[str],
        selected_questions: dict[str, dict | None],
        selected_interventions: dict[str, dict | None],
        chart: bytes,
        strip_image_tags: Callable[[str], str],
    ) -> bytes:
        output = io.BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=LETTER,
            topMargin=self.margin,
            bottomMargin=self.margin,
            leftMargin=self.margin,
            rightMargin=self.margin,
            title="RELATORIO PEDAGÓGICO SAEB",
        )

        styles = self._styles()
        story = [
            Paragraph("RELATORIO PEDAGÓGICO SAEB", styles["Title"]),
            Spacer(1, 0.25 * inch),
            Paragraph("1. Indice de Prioridade Pedagogica (IPP)", styles["Heading1"]),
            Spacer(1, 0.12 * inch),
            Image(io.BytesIO(chart), width=6 * inch, height=2.67 * inch),
            Spacer(1, 0.25 * inch),
            Paragraph("2. Desempenho por Estudante", styles["Heading1"]),
            Spacer(1, 0.12 * inch),
            self._students_table(diagnosis),
            PageBreak(),
            Paragraph("3. Simulado de Reforco", styles["Heading1"]),
        ]

        question_number = 1
        for descriptor in descriptors:
            question = selected_questions.get(descriptor.upper())
            if not question:
                story.append(
                    Paragraph(
                        f"Nenhuma questao cadastrada para o descritor {descriptor}.",
                        styles["Body"],
                    )
                )
                continue

            question_items = [
                Paragraph(
                    f"<b>Questao {question_number} (Descritor {descriptor}):</b> "
                    f"{self._escape(strip_image_tags(question.get('description', '')))}",
                    styles["ReportBody"],
                )
            ]
            for option in question.get("options", []):
                question_items.append(Paragraph(f"- {self._escape(str(option))}", styles["ReportBullet"]))

            story.append(KeepTogether(question_items + [Spacer(1, 0.15 * inch)]))
            question_number += 1

        story.extend(
            [
                PageBreak(),
                Paragraph("4. Intervencoes de Robotica e IA", styles["Heading1"]),
            ]
        )

        for descriptor in descriptors:
            intervention = selected_interventions.get(descriptor.upper())
            if not intervention:
                story.append(
                    Paragraph(
                        f"<i>Sugestao de robotica nao cadastrada para o descritor {descriptor}.</i>",
                        styles["ReportBody"],
                    )
                )
                continue

            story.append(Paragraph(f"Estrategia para {descriptor}", styles["Heading2"]))
            if intervention.get("skill"):
                story.append(
                    Paragraph(
                        f"Habilidade: {self._escape(str(intervention.get('skill')))}",
                        styles["ReportBody"],
                    )
                )

            for detail in intervention.get("intervention_data", []):
                title = self._escape(str(detail.get("title", "Sem titulo")))
                challenge = self._escape(str(detail.get("challenge", "N/A")))
                integration = self._escape(str(detail.get("integration", "N/A")))
                story.extend(
                    [
                        Paragraph(f"<b>{title}</b>", styles["ReportBody"]),
                        Paragraph(f"Desafio: {challenge}", styles["ReportBody"]),
                        Paragraph(f"IA: {integration}", styles["ReportBody"]),
                        Spacer(1, 0.12 * inch),
                    ]
                )

        document.build(story)
        return output.getvalue()

    def _styles(self):
        sample = getSampleStyleSheet()
        sample["Title"].alignment = TA_CENTER
        sample["Title"].fontName = "Helvetica-Bold"
        sample["Title"].fontSize = 18
        sample["Title"].leading = 22

        sample["Heading1"].fontName = "Helvetica-Bold"
        sample["Heading1"].fontSize = 14
        sample["Heading1"].leading = 18
        sample["Heading1"].spaceAfter = 8

        sample["Heading2"].fontName = "Helvetica-Bold"
        sample["Heading2"].fontSize = 12
        sample["Heading2"].leading = 16
        sample["Heading2"].spaceBefore = 10
        sample["Heading2"].spaceAfter = 6

        sample.add(
            ParagraphStyle(
                name="ReportBody",
                parent=sample["BodyText"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                spaceAfter=6,
            )
        )
        sample.add(
            ParagraphStyle(
                name="ReportBullet",
                parent=sample["ReportBody"],
                leftIndent=14,
                firstLineIndent=-8,
                spaceAfter=3,
            )
        )
        if "Body" not in sample:
            sample.add(
                ParagraphStyle(
                    name="Body",
                    parent=sample["BodyText"],
                    fontName="Helvetica",
                    fontSize=10,
                    leading=14,
                    spaceAfter=6,
                )
            )
        return sample

    def _students_table(self, diagnosis) -> Table:
        rows = [["STATUS", "ESTUDANTE", "MEDIA %"]]
        rows.extend(
            [
                [student.status, student.name, f"{student.average}%"]
                for student in sorted(
                    diagnosis.students,
                    key=lambda item: item.average,
                    reverse=True,
                )
            ]
        )

        table = Table(rows, colWidths=[1.25 * inch, 3.8 * inch, 1.0 * inch], repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF3")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return table

    def _escape(self, value: str) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
