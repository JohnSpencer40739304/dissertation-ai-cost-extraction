

# Trials with cleaning numbers and text 

"""
second trial just below
eventually included directly within the normalisation service script

"""

import re

def clean_text(value):
    if value is None:
        return None
    text = str(value)
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def clean_number(value):
    if value is None:
        return None
    text = str(value).replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)
    try:
        return float(text)
    except:
        return None



#def clean_numeric(value):
    """
    Convert US‑style numeric strings like '1,137.14' into floats.
    Leaves non-numeric values untouched.
    """
#    if value is None:
#        return None

#    if isinstance(value, (int, float)):
#        return value

#    if isinstance(value, str):
#        v = value.replace(",", "").strip()
#        try:
#            return float(v)
#        except ValueError:
#            return value

#    return value

def clean_numeric(v):
    if v is None:
        return None

    # Already numeric
    if isinstance(v, (int, float)):
        return v

    # Strings that might contain numbers
    if isinstance(v, str):
        cleaned = (
            v.strip()
             .replace(",", "")        # remove thousand separators
             .replace("\u00A0", "")   # remove non-breaking spaces
             .replace(" ", "")        # remove stray spaces
             .replace("$", "")
             .replace("€", "")
             .replace("£", "")
        )

        # Try float conversion
        try:
            return float(cleaned)
        except:
            return v  # return original if not numeric

    return v




"""
First trial

import re

def clean_text(value):
    if value is None:
        return None
    text = str(value)
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def clean_number(value):
    if value is None:
        return None

    text = str(value).replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)

    try:
        return float(text)
    except ValueError:
        return None
"""