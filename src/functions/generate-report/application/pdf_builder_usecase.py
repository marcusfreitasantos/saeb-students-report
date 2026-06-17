import io

class SimplePdfBuilder:
    max_lines_per_page = 44

    def build(self, lines: list[str]) -> bytes:
        pages = [
            lines[index : index + self.max_lines_per_page]
            for index in range(0, len(lines), self.max_lines_per_page)
        ] or [["RELATORIO PEDAGOGICO SAEB"]]

        objects: list[bytes] = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [] /Count 0 >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]

        page_ids: list[int] = []
        for page_lines in pages:
            content_id = len(objects) + 2
            page_id = len(objects) + 1
            page_ids.append(page_id)
            objects.append(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>".encode(
                    "latin-1"
                )
            )
            content = self._page_content(page_lines)
            objects.append(
                f"<< /Length {len(content)} >>\nstream\n".encode("latin-1")
                + content
                + b"\nendstream"
            )

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode(
            "latin-1"
        )

        return self._serialize(objects)

    def _page_content(self, lines: list[str]) -> bytes:
        commands = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
        for line in lines:
            commands.append(f"({self._escape(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        return "\n".join(commands).encode("latin-1", errors="replace")

    def _escape(self, value: str) -> str:
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

    def _serialize(self, objects: list[bytes]) -> bytes:
        output = io.BytesIO()
        output.write(b"%PDF-1.4\n")
        offsets = [0]

        for index, payload in enumerate(objects, start=1):
            offsets.append(output.tell())
            output.write(f"{index} 0 obj\n".encode("latin-1"))
            output.write(payload)
            output.write(b"\nendobj\n")

        xref_offset = output.tell()
        output.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        output.write(b"0000000000 65535 f \n")

        for offset in offsets[1:]:
            output.write(f"{offset:010d} 00000 n \n".encode("latin-1"))

        output.write(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode(
                "latin-1"
            )
        )
        return output.getvalue()
