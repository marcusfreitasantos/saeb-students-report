import pandas as pd

class IPPCalculator:
    def calculate(self, df_grades: pd.DataFrame) -> pd.DataFrame:
        hit_rate = df_grades.mean(skipna=True)
        error_rate = (df_grades == 0).sum() / df_grades.count()
        ipp = (100 - (hit_rate * 100)) * error_rate
        return pd.DataFrame({"IPP": ipp}).sort_values("IPP", ascending=False)