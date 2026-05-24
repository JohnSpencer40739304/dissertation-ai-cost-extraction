"""
Matrix Normaliser
Detects matrix-style pricing tables and explodes them into atomic rows.
A matrix table is defined structurally as:
- One or more descriptive columns on the left (text-dominant)
- Followed by one or more price columns on the right (numeric-dominant)
- Optional comment/notes columns on the far right (text-dominant)
- Rows representing the same entity across multiple price attributes

It assumes currency was dealt with previously by the currency tool so that only numeric values remain.
"""

class MatrixNormaliser:

    @staticmethod
    def is_numeric(value):
        if value is None:
            return False
        try:
            float(value)
            return True
        except:
            return False

    # Detects the split point between descriptive columns and price columns and returns the index where price columns start, or None if not a matrix.
    @staticmethod
    def detect_matrix_structure(headers, rows):
    

        col_count = len(headers)
        # A matric cannot be less than 3 columns
        if col_count < 3:
            return None  
        # Determine numeric ratio per column
        numeric_ratios = []
        for col_idx in range(col_count):
            column_values = [row[col_idx] for row in rows]
            numeric_count = sum(
                1 for v in column_values
                if MatrixNormaliser.is_numeric(v) or v in (None, "", "null")
            )
            ratio = numeric_count / len(column_values)
            numeric_ratios.append(ratio)

        # Identify first numeric-dominant column (>= 70% numeric/null)
        price_start = None
        for idx, ratio in enumerate(numeric_ratios):
            if ratio >= 0.7:
                price_start = idx
                break

        if price_start is None:
            return None

        # looks to see if there are several numeric columns togethor
        if price_start >= col_count - 1:
            return None
        for idx in range(price_start, col_count):
            if numeric_ratios[idx] < 0.7:
                # Allow trailing comment columns (text-dominant)
                # but only AFTER at least 2 numeric columns otherwise it's a normal table
                if idx - price_start < 2:
                    return None
                break

        return price_start

    @staticmethod         # Detects total and summery rows that should be ignored.
    def is_total_row(row):
        if not row:
            return False

        first_cell = str(row[0]).lower()
        if any(keyword in first_cell for keyword in ["total", "sum", "grand total"]):
            return True

        return False

    @staticmethod
    def explode(headers, rows, metadata, price_start):
        # Unpivots the matrix into single  rows.


        exploded = []

        descriptive_headers = headers[:price_start]
        price_headers = headers[price_start:]

        for row in rows:

            # Skip total rows
            if MatrixNormaliser.is_total_row(row):
                continue

            descriptive_values = row[:price_start]

            for idx, price_header in enumerate(price_headers):
                price_value = row[price_start + idx]

                # Skip empty/null price cells
                if price_value in (None, "", "null"):
                    continue

                exploded.append({
                    "cells": descriptive_values + [price_header, price_value],
                    "attributes": {
                        "entity": descriptive_values[0],
                        "rating_attribute_name": price_header,
                        "rating_attribute_value": price_header,
                        "unit_price": price_value
                    },
                    "page": metadata.get("page"),
                    "sheet": metadata.get("sheet"),
                    "source_format": "matrix_exploded"
                })

        return exploded



    """
    Full matrix normalisation pipeline:
    - Detect structure
    - Explode if matrix
    - Return None if not a matrix
    """
    @staticmethod
    def normalise(headers, rows, metadata):
        price_start = MatrixNormaliser.detect_matrix_structure(headers, rows)
        if price_start is None:
            return None  # not a matrix
        return MatrixNormaliser.explode(headers, rows, metadata, price_start)
