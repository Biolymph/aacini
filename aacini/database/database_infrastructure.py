import sqlite3

# Connect to database
connect_db = sqlite3.connect('aacini.db')

# Create a cursor
cursor = connect_db.cursor()

# Create tables
# File type table
# cursor.execute("""CREATE TABLE filetype_table (
#         patient_id text,
#         filename text,
#         extension text,
#         size real,
#         hash_sha256 text,
#         file_location text,
#         hts text
#         )""")

# # File content table
# cursor.execute("""CREATE TABLE filecontent_table (
#     patient_id text,
#     file_name text,
#     file_type text,
#     feature_count integer,
#     feature_type text
#     )""")

cursor.execute("DELETE FROM filetype_table")

# Commit tables
connect_db.commit()

# Close connection
connect_db.close()

# # Show all records
# def show_all(table):
#     # Query the database and select all
#     cursor.execute("SELECT rowid, * FROM table")
#     items = cursor.fetchall()

#     for item in items:
#         print(item)