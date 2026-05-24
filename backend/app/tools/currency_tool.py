import re

class CurrencyTool:

    CURRENCY_SYMBOLS = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY",
        "₽": "RUB",
        "₹": "INR",
        "₩": "KRW",
        "₫": "VND",
        "₺": "TRY",
        "R": "ZAR"
    }

    CURRENCY_CODES = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF",
        "SEK", "NOK", "DKK", "CNY", "INR", "BRL"
    }

    @staticmethod
    def detect_currency_from_cell(value):
        if not value:
            return None
        text = str(value)
        # Symbol detection
        for symbol, code in CurrencyTool.CURRENCY_SYMBOLS.items():
            if symbol in text:
                return code
        # Code detection
        for code in CurrencyTool.CURRENCY_CODES:
            if code.lower() in text.lower():
                return code
        return None

    @staticmethod
    def detect_currency_from_header(header):
        if not header:
            return None
        text = header.lower()
        for code in CurrencyTool.CURRENCY_CODES:
            if code.lower() in text:
                return code
        for symbol, code in CurrencyTool.CURRENCY_SYMBOLS.items():
            if symbol in text:
                return code
        return None

    @staticmethod
    def strip_currency_symbols(value):
        if value is None:
            return None
        text = str(value)
        # Remove currency symbols
        for symbol in CurrencyTool.CURRENCY_SYMBOLS.keys():
            text = text.replace(symbol, "")
        # Remove currency codes
        for code in CurrencyTool.CURRENCY_CODES:
            text = text.replace(code, "")
        # Remove spaces
        text = text.strip()
        return text

    @staticmethod
    def normalise_numeric(value):
        if value is None:
            return None
        text = str(value).strip()
        # Detect EU format: last separator is a comma
        if "," in text and text.rfind(",") > text.rfind("."):
            # EU format: 1.234,56 → 1234.56
            text = text.replace(".", "") 
            text = text.replace(",", ".") 
        else:
            # US format: 1,234.56 → 1234.56
            text = text.replace(",", "") 
        # Remove spaces
        text = text.replace(" ", "")
        try:
            return float(text)
        except:
            return None


    @staticmethod
    def process_cell(value):
        #    Returns (clean_numeric_value, detected_currency)
        currency = CurrencyTool.detect_currency_from_cell(value)
        stripped = CurrencyTool.strip_currency_symbols(value)
        numeric = CurrencyTool.normalise_numeric(stripped)
        return numeric, currency
    
    @staticmethod
    def process_table(headers, rows, surrounding_text=""):
        """
        Cleans all cells in a table and extracts currency context.
        Returns:
            cleaned_rows: list of cleaned rows
            currency_context: {
                "cell_level": [...],
                "header_level": [...],
                "document_level": "...",
                "default": "USD"
            }
        """

        cleaned_rows = []
        cell_level = []
        header_level = []
        document_level = None

        # 1. Detect currency in headers
        for h in headers:
            _, cur = CurrencyTool.process_cell(h)
            if cur:
                header_level.append(cur)

        # 2. Detect currency in surrounding text
        if surrounding_text:
            _, cur = CurrencyTool.process_cell(surrounding_text)
            if cur:
                document_level = cur

        # 3. Clean each row
        for row in rows:
            cleaned_row = []
            for cell in row:
                numeric, cur = CurrencyTool.process_cell(cell)
                cleaned_row.append(numeric if numeric is not None else cell)

                if cur:
                    cell_level.append(cur)

            cleaned_rows.append(cleaned_row)

        currency_context = {
            "cell_level": cell_level,
            "header_level": header_level,
            "document_level": document_level,
            "default": "USD"
        }

        return cleaned_rows, currency_context


