import re
from datetime import datetime
import pandas as pd

# 1 -  detect a possible date pattern

DATE_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}$",                     # 2026-05-10 (ISO)
    r"^\d{2}/\d{2}/\d{4}$",                     # 10/05/2026 or 05/10/2026
    r"^\d{2}-\d{2}-\d{4}$",                     # 10-05-2026
    r"^\d{2}/\d{2}/\d{2}$",                     # 10/05/26
    r"^\d{1,2} [A-Za-z]{3,9} \d{4}$",           # 10 May 2026
    r"^[A-Za-z]{3,9} \d{1,2}, \d{4}$",          # May 10, 2026
    r"^\d{8}$",                                 # 20260515 legacy
]

def looks_like_date(value: str) -> bool:
    if value is None:
        return False
    s = str(value).strip()
    for pattern in DATE_PATTERNS:
        if re.match(pattern, s):
            return True
    return False

# 2 parse the date to determine what type of format

def parse_date(value: str):
    if value is None:
        return None

    s = str(value).strip()

    # legacy system formats YYYYMMDD
    if re.match(r"^\d{8}$", s):
        try:
            return datetime.strptime(s, "%Y%m%d").date()
        except:
            pass

    # ISO format YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except:
            pass

    # European DD/MM/YYYY
    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        try:
            return datetime.strptime(s, "%d/%m/%Y").date()
        except:
            pass

    # American MM/DD/YYYY
    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        try:
            return datetime.strptime(s, "%m/%d/%Y").date()
        except:
            pass

    # various Textual formats
    try:
        return datetime.strptime(s, "%d %B %Y").date()
    except:
        pass

    try:
        return datetime.strptime(s, "%B %d, %Y").date()
    except:
        pass

    # if the above fails then Pandas will try
    try:
        return pd.to_datetime(s, errors="coerce").date()
    except:
        return None



# 3 return a value in ISO format

def normalise_date(value: str):
    dt = parse_date(value)
    return dt.isoformat() if dt else None
