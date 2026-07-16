from typing import List, Dict, Any

class SpecCompilers:
    COLOR_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

    @classmethod
    def compile_plotly(cls, chart_type: str, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Extract X and Y axes
        x_col = columns[0]
        y_cols = columns[1:] if len(columns) > 1 else [columns[0]]
        
        # Simple trace data mapping
        data = []
        for idx, y in enumerate(y_cols):
            x_vals = [r.get(x_col) for r in rows]
            y_vals = [r.get(y) for r in rows]
            
            trace = {
                "x": x_vals,
                "y": y_vals,
                "name": y,
                "type": chart_type.lower() if chart_type.lower() in ["bar", "scatter", "heatmap"] else "scatter",
                "mode": "lines+markers" if chart_type.lower() == "line" else None
            }
            if chart_type.lower() == "pie":
                trace = {
                    "labels": x_vals,
                    "values": y_vals,
                    "type": "pie"
                }
            data.append(trace)

        layout = {
            "title": f"{chart_type} Spec Visualization",
            "xaxis": {"title": x_col},
            "yaxis": {"title": y_cols[0]},
            "colorway": cls.COLOR_PALETTE
        }
        return {"data": data, "layout": layout}

    @classmethod
    def compile_recharts(cls, chart_type: str, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Recharts expects raw data rows directly
        x_col = columns[0]
        y_cols = columns[1:] if len(columns) > 1 else [columns[0]]
        
        return {
            "chartType": chart_type,
            "data": rows,
            "xAxisKey": x_col,
            "yAxisKeys": y_cols,
            "colors": cls.COLOR_PALETTE
        }

    @classmethod
    def compile_vega_lite(cls, chart_type: str, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        x_col = columns[0]
        y_col = columns[1] if len(columns) > 1 else columns[0]
        
        mark = "line"
        if chart_type.lower() == "bar":
            mark = "bar"
        elif chart_type.lower() == "scatter":
            mark = "point"

        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"A simple {chart_type} chart.",
            "data": {"values": rows},
            "mark": mark,
            "encoding": {
                "x": {"field": x_col, "type": "nominal"},
                "y": {"field": y_col, "type": "quantitative"}
            }
        }

    @classmethod
    def compile_echarts(cls, chart_type: str, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        x_col = columns[0]
        y_cols = columns[1:] if len(columns) > 1 else [columns[0]]
        
        x_vals = [r.get(x_col) for r in rows]
        
        series = []
        for y in y_cols:
            y_vals = [r.get(y) for r in rows]
            series.append({
                "name": y,
                "type": "bar" if chart_type.lower() == "bar" else "line",
                "data": y_vals
            })

        return {
            "title": {"text": f"{chart_type} Chart"},
            "tooltip": {},
            "legend": {"data": y_cols},
            "xAxis": {"data": x_vals},
            "yAxis": {},
            "series": series
        }
