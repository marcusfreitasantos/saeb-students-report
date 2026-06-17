import io
from dataclasses import dataclass
import pandas as pd
from report_builder import StudentPerformance, Diagnosis

class SpreadsheetReportProcessor:
    def process(self, spreadsheet_data: bytes) -> Diagnosis:
        dataframe = pd.read_excel(io.BytesIO(spreadsheet_data))
        dataframe.columns = [str(column).strip().upper() for column in dataframe.columns]

        descriptor_columns = [
            column
            for column in dataframe.columns
            if column.startswith("D") and any(char.isdigit() for char in column)
        ]
        name_column = next((column for column in dataframe.columns if "NOME" in column), "NOME")

        if not descriptor_columns:
            raise ValueError("Nenhuma coluna de descritor encontrada. Use colunas como D1, D2, D3.")

        if name_column not in dataframe.columns:
            raise ValueError("Coluna de nome nao encontrada na planilha.")

        grades = dataframe[descriptor_columns].apply(pd.to_numeric, errors="coerce")
        averages = grades.mean(axis=1, skipna=True) * 100

        students: list[StudentPerformance] = []
        for index in grades.index:
            average = averages[index]
            if pd.isna(average):
                continue

            student_name = str(dataframe.loc[index, name_column]).strip().upper()
            if student_name in ["NAN", ""] or "UNNAMED" in student_name:
                continue

            rounded_average = round(float(average), 1)
            students.append(
                StudentPerformance(
                    name=student_name,
                    average=rounded_average,
                    status=self._student_status(rounded_average),
                )
            )

        if not students:
            raise ValueError("Nenhum aluno com respostas validas foi encontrado.")

        hit_rate = grades.mean(skipna=True)
        error_rate = (grades == 0).sum() / grades.count()
        priority_index = (100 - (hit_rate * 100)) * error_rate
        descriptor_priority = pd.DataFrame({"IPP": priority_index}).sort_values(
            "IPP", ascending=False
        )

        return Diagnosis(descriptor_priority=descriptor_priority, students=students)

    def _student_status(self, average: float) -> str:
        if average >= 70:
            return "BOM"
        if average >= 50:
            return "REGULAR"
        return "CRITICO"

