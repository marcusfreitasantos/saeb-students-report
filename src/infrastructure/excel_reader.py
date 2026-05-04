import pandas as pd

class ExcelReader:
    def read(self, path: str) -> pd.DataFrame:
        df = pd.read_excel(path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df