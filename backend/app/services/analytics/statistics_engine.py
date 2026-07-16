import numpy as np
import pandas as pd
from typing import Dict
from app.schemas.analytics import DescriptiveStats

class StatisticsEngine:
    @staticmethod
    def calculate_stats(df: pd.DataFrame) -> Dict[str, DescriptiveStats]:
        stats_map = {}
        
        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if col_data.empty:
                continue
                
            mean = float(col_data.mean())
            median = float(col_data.median())
            mode = float(col_data.mode()[0]) if not col_data.mode().empty else mean
            variance = float(col_data.var()) if len(col_data) > 1 else 0.0
            std_dev = float(col_data.std()) if len(col_data) > 1 else 0.0
            min_val = float(col_data.min())
            max_val = float(col_data.max())
            
            # Skewness & Kurtosis
            skew = float(col_data.skew()) if len(col_data) > 2 else 0.0
            kurt = float(col_data.kurt()) if len(col_data) > 3 else 0.0
            
            coef_var = (std_dev / mean) if mean != 0 else 0.0
            
            stats_map[str(col)] = DescriptiveStats(
                mean=round(mean, 2),
                median=round(median, 2),
                mode=round(mode, 2),
                variance=round(variance, 2),
                std_dev=round(std_dev, 2),
                min_value=round(min_val, 2),
                max_value=round(max_val, 2),
                skewness=round(skew, 2),
                kurtosis=round(kurt, 2),
                coefficient_of_variation=round(coef_var, 4)
            )
            
        return stats_map
