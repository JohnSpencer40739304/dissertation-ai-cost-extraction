


# second trial and building column mapping
# written directly in final normalisation service srcipt 

COLUMN_NORMALISATION = {
    "qty": "quantity",
    "quantité": "quantity",
    "qte": "quantity",
    "unit price": "unit_price",
    "price per unit": "unit_price",
    "pu": "unit_price",
}

def normalise_column_name(col: str) -> str:
    col = col.lower().strip()
    return COLUMN_NORMALISATION.get(col, col.replace(" ", "_"))




"""
First Trial below

COLUMN_NORMALISATION = {
    "unit price": "unit_price",
    "price per unit": "unit_price",
    "pu": "unit_price",
    "tarif unitaire": "unit_price",

    "qty": "quantity",
    "quantité": "quantity",
    "qte": "quantity",

    "description": "description",
    "item": "description",
    "designation": "description",

    "material": "material",
    "matière": "material",

    "category": "category",
    "catégorie": "category",

    "total": "total_price",
    "montant": "total_price",
    "prix total": "total_price",

    "discount": "discount",
    "remise": "discount"
}

def normalise_column_name(col: str) -> str:
    col = col.lower().strip()
    return COLUMN_NORMALISATION.get(col, col.replace(" ", "_"))

"""