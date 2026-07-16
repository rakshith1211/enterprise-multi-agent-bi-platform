import pandas as pd
import numpy as np
from typing import Dict
from app.schemas.analytics import TrendResult

class TrendEngine:
    @staticmethod
    def calculate_trends(df: pd.DataFrame) -> Dict[str, TrendResult]:
        trends = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) < 2:
                continue
                
            # Simple trend direction using slope of linear regression
            x = np.arange(len(col_data))
            y = col_data.values
            slope, _ = np.polyfit(x, y, 1)
            
            direction = "Flat"
            if slope > 0.05:
                direction = "Upward"
            elif slope < -0.05:
                direction = "Downward"
                
            # Moving averages (window size 3)
            ma = col_data.rolling(window=min(3, len(col_data)), min_periods=1).mean().tolist()
            
            # CAGR (Compound Annual Growth Rate) approximation
            cagr = 0.0
            first_val = float(col_data.iloc[0])
            last_val = float(col_data.iloc[-1])
            if first_val > 0 and last_val > 0:
                cagr = ((last_val / first_val) ** (1 / max(1, len(col_data) - 1)) - 1) * 100

            trends[str(col)] = TrendResult(
                direction=direction,
                strength=round(float(abs(slope)), 4),
                cagr=round(cagr, 2),
                moving_averages=[round(v, 2) for v in ma]
            )
            
        return trends
