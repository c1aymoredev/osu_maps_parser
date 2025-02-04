"""Utility functions for the parser."""
from datetime import datetime, timedelta
from typing import List, Tuple

def generate_date_ranges(start_date: str = "2007-01-01") -> List[Tuple[str, str]]:
    # generates 3 month intervals from start_date to current date
    ranges = []
    current_date = datetime.now()
    start = datetime.strptime(start_date, "%Y-%m-%d")
    
    while start < current_date:
        end = min(start + timedelta(days=90), current_date)
        ranges.append((
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        ))
        start = end + timedelta(days=1)
    
    return ranges