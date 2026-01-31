import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def db_connection():
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        db=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

def initialize_database():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SHOW TABLES LIKE 'users'")
    result = cur.fetchone()

    if not result:
        print("Initializing database from init.sql...")
        with open('init.sql', 'r') as f:
            sql_commands = f.read()

        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                cur.execute(command)
        conn.commit()
        print("Database initialized.")
    else:
        print("Database already initialized. Skipping init.sql.")

    cur.close()
    conn.close()
