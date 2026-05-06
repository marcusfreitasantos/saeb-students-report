import pandas as pd
from functions.manage_report_questions.domain.entities.student import Student
from src.services.ipp_calculator import IPPCalculator
from infrastructure.excel_reader import ExcelReader

class ProcessStudentData:
    def __init__(self):
        self.reader = ExcelReader()
        self.calculator = IPPCalculator()

    def execute(self, path):
        df = self.reader.read(path)

        descriptor_cols = [c for c in df.columns if c.startswith("D")]
        name_col = next((c for c in df.columns if "NOME" in c), "NOME")

        df_grades = df[descriptor_cols].apply(pd.to_numeric, errors="coerce")
        averages = df_grades.mean(axis=1, skipna=True) * 100

        students = []
        for i in df.index:
            m = averages[i]
            if pd.isna(m):
                continue

            name = str(df.loc[i, name_col]).strip().upper()
            students.append(Student(name=name, average=round(float(m), 1)))

        diagnosis = self.calculator.calculate(df_grades)

        return students, diagnosis