import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

class TimeIntelligence:
    @staticmethod
    def parse_time_range(query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        now = datetime.now(timezone.utc)
        
        result = {
            "raw_time_expression": "None",
            "start_date": None,
            "end_date": None,
            "sql_filter": None
        }

        # Last N Months
        match = re.search(r"last (\d+) month", query_lower)
        if match:
            months = int(match.group(1))
            result["raw_time_expression"] = f"Last {months} Months"
            # Approx 30 days per month
            result["start_date"] = (now - timedelta(days=months * 30)).isoformat()
            result["end_date"] = now.isoformat()
            result["sql_filter"] = f"sale_date >= date_sub(now(), interval {months} month)"
            return result

        # Last Year
        if "last year" in query_lower:
            result["raw_time_expression"] = "Last Year"
            result["start_date"] = datetime(now.year - 1, 1, 1, tzinfo=timezone.utc).isoformat()
            result["end_date"] = datetime(now.year - 1, 12, 31, 23, 59, 59, tzinfo=timezone.utc).isoformat()
            result["sql_filter"] = f"sale_date BETWEEN '{result['start_date']}' AND '{result['end_date']}'"
            return result

        # Year to Date (YTD)
        if "ytd" in query_lower or "year to date" in query_lower:
            result["raw_time_expression"] = "Year-to-Date"
            result["start_date"] = datetime(now.year, 1, 1, tzinfo=timezone.utc).isoformat()
            result["end_date"] = now.isoformat()
            result["sql_filter"] = f"sale_date >= '{result['start_date']}'"
            return result

        # Today
        if "today" in query_lower:
            result["raw_time_expression"] = "Today"
            result["start_date"] = datetime(now.year, now.month, now.day, tzinfo=timezone.utc).isoformat()
            result["end_date"] = now.isoformat()
            result["sql_filter"] = f"sale_date >= '{result['start_date']}'"
            return result

        return result
