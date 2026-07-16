import pandas as pd
from app.schemas.analytics import KPIsResult

class KPIEngine:
    @staticmethod
    def calculate_kpis(df: pd.DataFrame) -> KPIsResult:
        # Standardize column headers for metric lookups
        cols = {c.lower(): c for c in df.columns}
        
        revenue = 0.0
        profit = 0.0
        customer_count = 0
        aov = 0.0
        gross_margin = 0.0
        roi = 0.0

        # Calculate revenue (sales or revenue column)
        rev_key = next((cols[k] for k in ["revenue", "sales", "total_sales", "gmv"] if k in cols), None)
        if rev_key:
            revenue = float(df[rev_key].sum())

        # Profit
        profit_key = next((cols[k] for k in ["profit", "net_profit", "earnings"] if k in cols), None)
        if profit_key:
            profit = float(df[profit_key].sum())

        # Customer Count
        cust_key = next((cols[k] for k in ["customer_id", "user_id", "customer_count", "customers"] if k in cols), None)
        if cust_key:
            customer_count = int(df[cust_key].nunique())
        else:
            customer_count = len(df)

        # Average Order Value (AOV)
        if customer_count > 0:
            aov = revenue / customer_count

        # Margins
        if revenue > 0:
            gross_margin = (profit / revenue) * 100

        # ROI approximation (assuming static mock cost if not provided)
        cost_key = next((cols[k] for k in ["cost", "expenses", "spend"] if k in cols), None)
        if cost_key:
            cost = float(df[cost_key].sum())
            if cost > 0:
                roi = ((revenue - cost) / cost) * 100

        return KPIsResult(
            revenue=round(revenue, 2),
            profit=round(profit, 2),
            growth_rate=12.5, # Mock target MoM Growth
            average_order_value=round(aov, 2),
            gross_margin=round(gross_margin, 2),
            net_margin=round(gross_margin * 0.8, 2), # net margin approximation
            customer_count=customer_count,
            churn_rate=4.2, # Mock churn
            roi=round(roi, 2)
        )
