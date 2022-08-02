import sqlite3

# Connect to database
connect_db = sqlite3.connect('file_log.db')

# Create a cursor
cursor = connect_db.cursor()

# Create tables
# File type table
cursor.execute("""CREATE TABLE filetype_table (
        patient_id text,
        sample_id text,
        file_name text,
        file_type text,
        size real,
        hash_sha256 text,
        file_location text,
        index_file text,
        index_file_size,
        index_file_sha256 text,
        hts_file text
    )""")

# File content table
cursor.execute("""CREATE TABLE filecontent_table (
    patient_id text,
    file_name text,
    file_type text,
    feature_count integer,
    feature_type text
    )""")

# Show all records
def show_all(table):
    # Query the database and select all
    cursor.execute("SELECT rowid, * FROM table")
    items = cursor.fetchall()

    for item in items:
        print(item)

# Close connection
connect_db.close()