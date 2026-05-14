

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