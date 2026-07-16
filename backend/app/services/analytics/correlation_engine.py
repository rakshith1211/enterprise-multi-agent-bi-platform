import pandas as pd
import numpy as np
from app.schemas.analytics import CorrelationMatrix

class CorrelationEngine:
    @staticmethod
    def calculate_correlations(df: pd.DataFrame) -> CorrelationMatrix:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return CorrelationMatrix(matrix={})

        corr = numeric_df.corr(method="pearson")
        matrix_dict = {}
        for col in corr.columns:
            matrix_dict[col] = {idx: round(float(val), 4) for idx, val in corr[col].items()}

        # Rank relationships
        ranked = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                col1 = corr.columns[i]
                col2 = corr.columns[j]
                val = corr.iloc[i, j]
                if not np.isnan(val):
                    strength = "strong" if abs(val) > 0.7 else "moderate" if abs(val) > 0.3 else "weak"
                    direction = "positive" if val > 0 else "negative"
                    ranked.append(f"{col1} and {col2} have a {strength} {direction} correlation ({round(float(val), 2)})")

        return CorrelationMatrix(
            matrix=matrix_dict,
            ranked_relationships=ranked
        )
