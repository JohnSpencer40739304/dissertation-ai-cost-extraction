import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cost_dissertation_db",
        user="postgres",
        password="postgres"
    )
