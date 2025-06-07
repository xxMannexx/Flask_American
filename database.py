import mysql.connector
import os

database = mysql.connector.connect(
    host=os.getenv('host'),
    user=os.getenv('user'),
    passwd=os.getenv('passwd'),
    port=os.getenv('port'),
    database=os.getenv('database')
)
