import hashlib
import json
from numpy import var
import pandas as pd
import fnmatch
import pathlib
import os
import sqlite3
import pysam

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
    cursor.execute(f"SELECT COUNT({column})AS files_per_patient FROM {table} WHERE {column}='{value}'")
    count = cursor.fetchone()[0]
    return count

######################################################################
######################################################################
### Quality control functions
######################################################################
