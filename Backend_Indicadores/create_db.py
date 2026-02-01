import MySQLdb
import sys

try:
    # Try to connect without specifying a database to create it
    db = MySQLdb.connect(host="localhost", user="root", passwd="12345")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS incidencias_db")
    db.close()
    print("Database created or already exists.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
