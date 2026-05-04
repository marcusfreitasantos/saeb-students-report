from application.process_student_data import ProcessStudentData
from infrastructure.report_generator import ReportGenerator

def main():
    processor = ProcessStudentData()
    students, diagnosis = processor.execute("student_spreadsheet.xlsx")

    report = ReportGenerator()
    report.generate(students, diagnosis)

if __name__ == "__main__":
    main()