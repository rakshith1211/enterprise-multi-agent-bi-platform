import pandas as pd
import numpy as np
from typing import List
from app.schemas.analytics import AnomalyItem

class AnomalyEngine:
    @staticmethod
    def detect_anomalies(df: pd.DataFrame) -> List[AnomalyItem]:
        anomalies = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) < 4:
                continue
                
            # Method 1: Z-score (Threshold = 2.5)
            mean = col_data.mean()
            std = col_data.std()
            if std == 0:
                continue
                
            z_scores = (col_data - mean) / std
            
            for idx, val in col_data.items():
                z = z_scores[idx]
                if abs(z) > 2.2:
                    severity = "High" if abs(z) > 3.0 else "Medium"
                    anomalies.append(AnomalyItem(
                        index=int(idx),
                        column=str(col),
                        value=float(val),
                        reason=f"Z-score {round(float(z), 2)} exceeded outlier boundary limits.",
                        severity=severity,
                        confidence=round(1.0 - (1.0 / (abs(z) + 1.0)), 2)
                    ))
                    
        return anomalies
