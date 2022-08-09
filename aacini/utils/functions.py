import hashlib
import json
from numpy import var
import pandas as pd
import fnmatch
import pathlib
import os
import sqlite3
import pysam

from datetime import datetime
from aacini.utils.constants import extensions_list
from aacini.utils.constants import extensions_categories


######################################################################
######################################################################
### File information extraction functions
######################################################################

def return_json_as_pydict(file: str) -> str:
    """
    Function that returns a json file containing multiple 
    objects as a python dictionary.

    Use case: files with multi samples.

    Args:
        File name or absolute path.

    Returns:
        Python dictionary with the names of the samples 
        within the multi-sample file.
    """
    # Open JSON file
    opened_file = open(file)
  
    # Return JSON object as a dictionary
    data = json.load(opened_file)

    # Extract samples names
    for sample in data['samples']:
        print(sample['name'])

    # Close file
    opened_file.close()


def get_file_name(file: str) -> str:
    """
    This function gets the original file name.

    Args:
        File name or absolute path.

    Returns:
        Final component of a file path (file name).
    """
    filename = pathlib.PurePath(file).name
    return filename

def get_extension(file: str) -> str:
    """
    This function gets the file extension name of files with
    matching patterns to that of a list instantiated 
    in the file "constants.py". It is usefull when the extension
    format has more than 2 suffixes or when '.' is used to 
    separate the file name. Hence, if other file 
    extensions are required, the list needs to be updated.

    Args:
        File name or absolute path.

    Returns:
        File extension.
    """
    for extension in extensions_list:
        if fnmatch.fnmatch(file, "*"+extension):
            file_extension = extension
            return file_extension

def get_absolute_path(file: str) -> str:
    """
    This function gets the original absolute path of the file.

    Args:
        File name or absolute path..
    
    Returns:
        Absolute path where the file is located.
    """
    absolute_path = os.path.abspath(file)
    return absolute_path


def get_patient_id(directory: str) -> str:
    """
    This function gets the unique string used to identify 
    a patient from the name of the directory were the 
    patient's files are stored.

    Args:
        Directory name or absolute path.

    Returns:
        Unique string used to identify a patient.
    """
    patient_ID = os.path.basename(directory)
    return patient_ID

def get_file_size(file: str) -> str:
    """
    This function gets the size of the file.

    Args:
        File name or absolute path.

    Returns:
        File size.
    """
    # Get size in bytes
    size = os.path.getsize(file)
    
    # Convert to human readable depending on the size
    if size < 1024:
        return f"{size} bytes"

    elif size < 1024*1024:
        return f"{round(size/1024, 2)} KB"

    elif size < 1024*1024*1024:
        return f"{round(size/(1024*1024), 2)} MB"

    elif size < 1024*1024*1024*1024:
        return f"{round(size/(1024*1024*1024), 2)} GB"


def create_sha256(file: str) -> str:
    """
    This function creates a 32-byte hash or message digest 
    using the sha256 algorithm.

    Args:
        File name or absolute path.

    Returns:
        Hexadecimal 32-byte hash of the file using the sha256 algorithm.
    """
    with open(file, "rb") as opened_file:
        # Read file content
        content = opened_file.read()

        # Instantiate sha256 algorithm
        sha256 = hashlib.sha256()

        # Create hash for the file
        sha256.update(content)

        # Close file
        opened_file.close()

        return sha256.hexdigest()

def get_hts(file: str) -> str:
    """
    Detect file format via pysamtools using htsfile functionality.

    Args: 
        file: file name or absolute path.

    Returns:
        File format.
    """
    # For now it takes the category based on the dictionary
    for extension, category in extensions_categories.items():
        if fnmatch.fnmatch(file, "*"+extension):
            file_category = category
            return file_category

    # with open(file, "rt") as opened_file:
    #     # Read file content
    #     content = opened_file.read()

    #     # Extract file format
    #     file_format = pysam.HTSFile(content).format
    #     return file_format

######################################################################
######################################################################
### Database functions
######################################################################

def create_filetype_table(connection, cursor):
    """
    Creates table to store 'File type' information per file per 
    patient if it does not exist already.

    Args:
        connection: sqlite3 connection to database using the connect 
            function. 
            E.g.: connection = sqlite3.connect('database_name.db')
        cursor: sqlite3 cursor created in the connection using the 
            cursor method.
            E.g.: cursor = connection.cursor()
    
    Returns:
        Commited 'File type' table into the database.
    """ 
    cursor.execute("""CREATE TABLE if not exists filetype_table (
            patient_id text,
            filename text,
            extension text,
            size real,
            hash_sha256 text,
            file_location text,
            hts text,
            
            UNIQUE(patient_id, filename, size, hash_sha256)
            )""")
    connection.commit()

def create_filecontent_table(connection, cursor):
    """
    Creates table to store 'File content' information per file per 
    patient if it does not exist already.

    Args:
        connection: sqlite3 connection to database using the connect 
            function. 
            E.g.: connection = sqlite3.connect('database_name.db')
        cursor: sqlite3 cursor created in the connection using the 
            cursor method. 
            E.g.: cursor = connection.cursor()
    
    Returns:
        Commited 'File type' table into the database.
    """
    cursor.execute("""CREATE TABLE if not exists filecontent_table (
            patient_id text,
            file_name text,
            file_type text,
            feature_count integer,
            feature_type text
            )""")
    connection.commit()

def create_missingfiles_table(connection, cursor):
    """
    Creates table to store 'Missing files' information per file per 
    patient if it does not exist already.

    Args:
        connection: sqlite3 connection to database using the connect 
            function. 
            E.g.: connection = sqlite3.connect('database_name.db')
        cursor: sqlite3 cursor created in the connection using the 
            cursor method. 
            E.g.: cursor = connection.cursor()
    
    Returns:
        Commited 'Missing files' table into the database.
    """
    cursor.execute("""CREATE TABLE if not exists missingfiles_table (
            patient_id text,
            date string,
            file_missing text,

            UNIQUE(patient_id, date, file_missing)
            )""")
    connection.commit()

def count_records(cursor: str, table: str, column: str, value: str):
    """
    Counts the amount of records per patient ID stored in a 
    given database table.

    Args:
        cursor: sqlite3 cursor created in the connection using the 
            cursor method. 
            E.g.: cursor = connection.cursor()
        table: table name where to count the records.
        column: column name where to count the records.
        patient_id: unique string used to identify the patient.

    Returns:
        Number of records in a database table per patient ID. 
    """
    cursor.execute(f"""SELECT COUNT({column}) 
                    AS files_per_patient 
                    FROM {table} 
                    WHERE {column}='{value}'""")
    count = cursor.fetchone()[0]
    return count

def count_essential_files(cursor: str, connection: str, column_filename: str, 
        table: str, patient_id: str, column_patient_id: str):
    """
    This function looks for the existance of four essential files
    for the study that should exist within the list of 
    files per patient:
        - SV.germline
        - SNV.germline
        - SV.somatic
        - SNV.somatic

    Args:
        cursor: sqlite3 cursor created in the connection using the 
            cursor method. 
            E.g.: cursor = connection.cursor()
        table: table name where to count the records.
        column_filename: column where file name is stored.
        patient_id: unique string used to identify the patient.
        column_patient_id: column where patient ID is stored.
    
    Returns:
        List of counts where essential files found in the file list given.
    """
    # Instantiate list 
    counts_list = []
    
    # Count records starting with: SV.germline and appends the number to a list
    cursor.execute(f"""SELECT COUNT({column_filename})
                AS essential_files
                FROM {table}
                WHERE {column_filename} LIKE 'SV.germline%' 
                AND {column_patient_id} = '{patient_id}'
                """)
    sv_germline_count = cursor.fetchone()[0]
    counts_list.append(sv_germline_count)

    # If the count == 0, records the missing file into a table in the database
    if sv_germline_count == 0:
        cursor.execute("""INSERT OR IGNORE INTO missingfiles_table VALUES(
                :patient_id,
                :date,
                :file_missing)""",
                    {"patient_id": patient_id,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "file_missing": 'SV.germline'})
        connection.commit()

    # Count records starting with: SNV.germline and appends the number to a list
    cursor.execute(f"""SELECT COUNT({column_filename})
                AS essential_files
                FROM {table}
                WHERE {column_filename} LIKE 'SNV.germline%' 
                AND {column_patient_id} = '{patient_id}'
                """)
    snv_germline_count = cursor.fetchone()[0]
    counts_list.append(snv_germline_count)

    # If the count == 0, records the missing file into a table in the database
    if snv_germline_count == '0':
        cursor.execute("""INSERT OR IGNORE INTO missingfiles_table VALUES(
                :patient_id,
                :date,
                :file_missing)""",
                    {"patient_id": patient_id,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "file_missing": 'SNV.germline'})
        connection.commit()

    # Count records starting with: SV.somatic and appends the number to a list
    cursor.execute(f"""SELECT COUNT({column_filename})
                AS essential_files
                FROM {table}
                WHERE {column_filename} LIKE 'SV.somatic%' 
                AND {column_patient_id} = '{patient_id}'
                """)
    sv_somatic_count = cursor.fetchone()[0]
    counts_list.append(sv_somatic_count)

    # If the count == 0, records the missing file into a table in the database
    if sv_somatic_count == '0':
        cursor.execute("""INSERT OR IGNORE INTO missingfiles_table VALUES(
                :patient_id,
                :date,
                :file_missing)""",
                    {"patient_id": patient_id,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "file_missing": 'SV.somatic'})
        connection.commit()   
    
    # Count records starting with: SNV.somatic and appends the number to a list
    cursor.execute(f"""SELECT COUNT({column_filename})
                AS essential_files
                FROM {table}
                WHERE {column_filename} LIKE 'SNV.somatic%' 
                AND {column_patient_id} = '{patient_id}'
                """)
    snv_somatic_count = cursor.fetchone()[0]
    counts_list.append(snv_somatic_count)   

    # If the count == 0, records the missing file into a table in the database
    if snv_somatic_count == '0':
        cursor.execute("""INSERT OR IGNORE INTO missingfiles_table VALUES(
                :patient_id,
                :date,
                :file_missing)""",
                    {"patient_id": patient_id,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "file_missing": 'SNV.somatic'})
        connection.commit() 
        
    return counts_list


######################################################################
######################################################################
### Quality control & Stats functions
######################################################################

def list_patients_missing_files(cursor: str):
    """
    This function records the missing essential files per patient
    at the date when the program was executed. For the study, 
    four files per patient should exist:
        - SV.germline
        - SNV.germline
        - SV.somatic
        - SNV.somatic

    Args:
        file_list: python list of the files to search per patient
    
    Returns:
        List of essential files found in the file list given.
    """
    cursor.execute(f"""SELECT DISTINCT patient_id
                FROM missingfiles_table
                WHERE date = {datetime.now().date()}
                """)
    for row in cursor:
        print(row[0])