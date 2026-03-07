from fastapi import FastAPI
from modules.db import get_connection   # week 1 database connection test 20260307
from pydantic import BaseModel # week 1 insert data into DB using fastAPI from python
class CostItem(BaseModel):
    category: str
    amount: float
    year: int

app = FastAPI()

# Original root point
@app.get("/")
def root():
    return {"message": "TEST from the dissertation backend to check that the API works"}

# Week 1 database test endpoint from 20260307
@app.get("/db-test")
def db_test():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return {"db_response": result}

# week 1 test to add data very python using fastAPI
@app.post("/add-cost")
def add_cost(item: CostItem):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cost_items (category, amount, year) VALUES (%s, %s, %s) RETURNING id;",
        (item.category, item.amount, item.year)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"inserted_id": new_id}



