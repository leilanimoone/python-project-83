import os
from dotenv import load_dotenv
from psycopg2 import connect


load_dotenv()


def get_connection():
    return connect(os.getenv('DATABASE_URL'))
