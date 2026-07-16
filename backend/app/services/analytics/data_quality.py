import pandas as pd
from app.schemas.analytics import DataQualityResult

class DataQualityEngine:
    @staticmethod
    def evaluate(df: pd.DataFrame) -> DataQualityResult:
        total_cells = df.size
        if total_cells == 0:
            return DataQualityResult()

        missing_count = int(df.isnull().sum().sum())
        null_percent = (missing_count / total_cells) * 100
        
        duplicate_rows = int(df.duplicated().sum())
        
        completeness = 1.0 - (missing_count / total_cells)
        
        # Uniqueness score: ratio of unique rows to total rows
        uniqueness = 1.0
        if len(df) > 0:
            uniqueness = len(df.drop_duplicates()) / len(df)

        return DataQualityResult(
            missing_count=missing_count,
            null_percentage=round(null_percent, 2),
            duplicate_rows=duplicate_rows,
            completeness_score=round(completeness, 4),
            uniqueness_score=round(uniqueness, 4)
        )
