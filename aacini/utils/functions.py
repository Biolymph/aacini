from curses import pair_content
from genericpath import exists
import hashlib
import json
from numpy import equal, var
import pandas as pd
import fnmatch
import pathlib
import os
import sqlite3
import pysam
import datetime
import sys

# Extensions list and categories from constants.py
from aacini.utils.constants import extensions_list
from aacini.utils.constants import extensions_categories

######################################################################
### File information extraction functions
######################################################################

def return_json_as_pydict(file: str) -> str:
    """
    Function that returns a json file containing multiple objects as 
    a python dictionary.

    Use case: files with multi samples.

    Args:
        file (str): file name or absolute path.

    Returns:
        Python dictionary with the names of the samples within the 
        multi-sample file.
    """

    # Open JSON file
    opened_file = open(file)
  
    # Return JSON object as a dictionary
    data = json.load(opened_file)

    # Extract samples names
    for sample in data["samples"]:
        print(sample["name"])

    # Close file
    opened_file.close()

def get_file_name(file: str) -> str:
    """
    This function gets the original file name.

    Args:
        file (str): file name or absolute path.

    Returns:
        Final component of a file path (file name).
    """

    # Get file name as final component of path
    filename = pathlib.PurePath(file).name
    return filename

def get_extension(file: str) -> str:
    """
    This function gets the file extension name. 
    
    The extension pattern of the file is compared to a list 
    instantiated in "constants.py". It is usefull when the 
    extension format has more than 2 suffixes or when '.' is 
    used to separate the file name. Hence, if other file 
    extensions are required, the list needs to be updated.

    Args:
        file (str): file name or absolute path.

    Returns:
        File extension.
    """

    # Extensions list in constants.py
    for extension in extensions_list:
        if fnmatch.fnmatch(file, "*"+extension):
            file_extension = extension  
            return file_extension
        
def get_absolute_path(file: str) -> str:
    """
    This function gets the original absolute path of the file.

    Args:
        file (str): file name or absolute path..
    
    Returns:
        Absolute path where the file is located.
    """

    # Get absoulte path
    absolute_path = os.path.abspath(file)
    return absolute_path

def get_patient_id(directory: str) -> str:
    """
    This function gets the unique string used to identify 
    a patient from the name of the directory were the 
    patient's files are stored.

    Args:
        directory (str): directory name or absolute path.

    Returns:
        Unique string used to identify a patient.
    """

    # Get patient_id from the directory name
    patient_ID = os.path.basename(directory)
    return patient_ID

def get_file_size(file: str) -> str:
    """
    This function gets the size of the file.

    Args:
        file (str): file name or absolute path.

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
        file (str): file name or absolute path.

    Returns:
        Hexadecimal 32-byte hash of the file using the sha256 algorithm.
    """

    # Instantiate sha256 algorithm
    sha256 = hashlib.sha256()
    
    # Open file in read binary mode
    with open(file, "rb") as opened_file:

        # Read file content
        content = opened_file.read()   

        # Create hash for the file
        sha256.update(content)

        # Close file
        opened_file.close()

    # Return hash
    return sha256.hexdigest()

def get_hts(file: str) -> str:
    """
    Detect file format via pysamtools using htsfile functionality.

    Args: 
        file (str): file name or absolute path.

    Returns:
        File format.
    """
    
    # For now it takes the category based on the dictionary in constants.py
    for extension, category in extensions_categories.items():
        if fnmatch.fnmatch(file, "*"+extension):
            file_category = category
            return file_category

    ## Failed attempt to use htsfile from samtools
    ## It seems that the function was deprecated or changed in some 
    ## undocumented way...

    # with open(file, "rt") as opened_file:
    #     # Read file content
    #     content = opened_file.read()

    #     # Extract file format
    #     file_format = pysam.HTSFile(content).format
    #     return file_format

######################################################################
### Database infrastructure functions
######################################################################

def create_file_information_table(database:str):
    """
    Creates table to store general file information of each file in 
    the directory corresponding the patient.

    Args:
        database (str): name of the database to connect to.
    
    Returns:
        Commited 'File information' table into the database.
    """ 
    
    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Create file_information table if it does not exists 
    cursor.execute("""CREATE TABLE if not exists file_information (
            date text,
            patient_id text,
            file_name text,
            extension text,
            file_size real,
            first_hash text,
            file_location text,
            hts text,
            status text,
            
            UNIQUE(patient_id, file_name, first_hash)
            )""")
    
    # Commit cursor to database
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

def create_file_content_table(database:str):
    """
    Creates table to store 'File content' information per file per 
    patient if it does not exist already.

    Args:
        :param database: name of the database to connect to.
    
    Returns:
        Commited 'File content' table into the database.
    """
    
    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Create file_content table if it does not exist
    cursor.execute("""CREATE TABLE if not exists file_content (
            patient_id text,
            file_name text,
            file_type text,
            feature_count integer,
            feature_type text
            )""")
    
    # Commit cursor to database
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

def create_missing_files_table(database: str):
    """
    Creates table to store 'Missing files' information per file per 
    patient if it does not exist already.

    Args:
        database (str): name of the database to connect to.
    
    Returns:
        Commited 'Missing files' table into the database.
    """
    
    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Create missing_files table if it does not exist
    cursor.execute("""CREATE TABLE if not exists missing_files (
            patient_id text,
            file_missing text,
            first_date_missing text,
            last_date_missing text,
            date_added text,

            UNIQUE(patient_id, file_missing)
            )""")

    # Commit cursor to database
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

def create_unmatching_hash_table(database: str):
    """
    Creates table to store 'Unmatching hash' file information per file 
    per patient if it does not exist already.

    Args:
        database (str): name of the database to connect to.
    
    Returns:
        Commited 'Changed hash' table into the database.
    """
    
    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Create changed_hash table if it does not exist
    cursor.execute("""CREATE TABLE if not exists unmatching_hash (
            patient_id text,
            file_name text,
            first_hash text,
            last_hash text,
            first_date text,
            last_date text,
            first_size text,
            last_size text,
            first_location text,
            last_location text,

            UNIQUE(patient_id, file_name)
            )""")
    
    # Commit cursor to database
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

######################################################################
### Database interaction functions
######################################################################

def record_file_info(database: str, patient_id: str, file_name: str, 
    extension: str, file_size: str, first_hash: str, abs_path: str, 
    file_type: str):
    """
    Extracts file information and records it in a table in the 
    database.

    Args:
        patient_id (str): unique string to identify the patient.
        file_name (str): full file name.
        extension (str): literal file extension.
        file_size (str): file size.
        first_hash (str): file hash.
        abs_path (str): absolute path of the file.
        file_type (str): file type according to the extension. 
            E.g.: If extension is "cram.crai" the file type is "cram".
        status (str): status of the file in relation to the study.
            Options: "pass", "hash_unmatch", "empty_file".

    Returns:
        Information recorded into the "File Content" table in the 
        database.
    """

    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Record information into database table
    cursor.execute("""INSERT OR IGNORE INTO file_information VALUES(
                    :date,
                    :patient_id,
                    :file_name,
                    :extension,
                    :file_size,
                    :first_hash,
                    :file_location,
                    :hts,
                    :status)""",
                        {"date": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
                        "patient_id": patient_id,
                        "file_name": file_name,
                        "extension": extension,
                        "file_size": file_size,
                        "first_hash": first_hash,
                        "file_location": abs_path,
                        "hts": file_type,
                        "status": ""})

    # Commit cursor to database
    connection.commit()
    
    # Close cursor and connection
    cursor.close()
    connection.close()

def count_records(database: str, table: str, column: str, value: str):
    """
    Counts the amount of records per patient ID stored in a 
    given database table.

    Args:
        database (str): name of the database to connect to.
        table (str): table name where to count the records.
        column (str): column name where to count the records.
        value (str): value to count in the records.

    Returns:
        Number of records in a database table per patient ID. 
    """

    # Connect to database and create a cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # Select and count files per patient ID
    cursor.execute(f"""SELECT COUNT({column}) 
                    AS files_per_patient 
                    FROM {table}
                    WHERE {column} ='{value}'""")
    
    # Fetch the first value in the cursor
    count = cursor.fetchone()[0]
    
    # Close cursor and connection
    cursor.close()
    connection.close()

    return count

def check_essential_files(database: str, patient_id: str):
    """
    This function counts the amount of four essential file 
    types for the study, then registers the information in a 
    table if they are missing. 
    
    The four file types are: 
        - SV.germline
        - SNV.germline
        - SV.somatic
        - SNV.somatic

    Args:
        database (str): name of the database to connect to.
        patient_id (str): unique string used to identify the patient.
    
    Returns:
        List of counts per essential file type in the following 
        positional order: 
            [0]: 'SV.germline', 
            [1]: 'SNV.germline', 
            [2]: 'SV.somatic', 
            [3]: 'SNV.somatic'.
    """
    
    try:
        # Connect to database and create a cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Instantiate empty counts list 
        counts_list = []

        # File patterns to search for and count
        file_patterns = ['SV.germline', 'SNV.germline', 'SV.somatic', 'SNV.somatic']
    
        for file_pattern in file_patterns:
            
            # Select and count records starting with file_pattern
            cursor.execute(f"""SELECT COUNT(patient_id)
                AS essential_files
                FROM file_information
                WHERE file_name LIKE '{file_pattern}%' 
                    AND patient_id = '{patient_id}'
                """)
            
            # Fetch the first value in the cursor
            essential_files_count = cursor.fetchone()[0]

            # Append number to a list
            counts_list.append(essential_files_count)

            # Select and count records in missing_files that match the 
            # file_pattern and patient_id.
            cursor.execute(f"""SELECT COUNT(file_missing)
                FROM missing_files
                WHERE patient_id = "{patient_id}" 
                    AND file_missing = "{file_pattern}"
                """)
            
            # Fetch the first value in the cursor
            files_registered_missing_count = cursor.fetchone()[0]

            # If there are no essential files for the pattern (fetched count == 0), 
            # then record the missing file into a table in the database
            if essential_files_count == 0 and files_registered_missing_count == 0:
                
                # Insert or ignore the registry of the missing file
                cursor.execute("""INSERT OR IGNORE INTO missing_files VALUES(
                    :patient_id,
                    :file_missing,
                    :first_date_missing,
                    :last_date_missing,
                    :date_added)""",
                        {"patient_id": patient_id,
                        "file_missing": file_pattern,
                        "first_date_missing": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
                        "last_date_missing": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
                        "date_added": ""})
                
                # Commit cursor to database
                connection.commit()

            # If there are no essential files for the pattern (fetched count == 0)
            # but it that has been previously registered (registered missing > 0), 
            # then update the last_date_missing column to today
            elif essential_files_count == 0 and files_registered_missing_count > 0:
                
                # Update last_date_missing if the file is still missing today
                cursor.execute(f"""UPDATE missing_files 
                    SET last_date_missing = "{datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")}"
                    WHERE patient_id = "{patient_id}" AND file_missing = "{file_pattern}"
                    """)
                
                # Commit cursor to database
                connection.commit()

            # If there are essential files for the pattern (fetched count > 0)
            # but it was previously registered as missing (registered missing > 0), 
            # then update the date_added column to today
            elif essential_files_count > 0 and files_registered_missing_count > 0:
                
                # Select date_added from file_pattern and patient_id
                cursor.execute(f"""SELECT date_added
                    FROM missing_files
                    WHERE patient_id = "{patient_id}" AND file_missing = "{file_pattern}"
                    """)

                # Fetch the first value in the cursor
                file_added = cursor.fetchone()[0]    

                # If the date_added info is missing, update it to today
                if file_added == "":
                    
                    # Update date_added to today
                    cursor.execute(f"""UPDATE missing_files 
                        SET date_added = "{datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")}"
                        WHERE patient_id = "{patient_id}" AND file_missing = "{file_pattern}"
                        """)

                    # Commit cursor to database
                    connection.commit()
    
    # Print error if encountered
    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    # Finalize function
    finally:

        # Close cursor and connection
        cursor.close()
        connection.close()

        return counts_list

######################################################################
### Quality control & Stats functions
######################################################################

def list_patients_missing_files(database: str) -> list:
    """
    This function records the missing essential files per patient
    at the date when the program was executed. For the study, 
    four files per patient should exist:
        - SV.germline
        - SNV.germline
        - SV.somatic
        - SNV.somatic

    Args:
        database (str): name of the database to connect to.
    
    Returns:
        List of tuples of essential files missing.
    """
    
    try:
        # Connect to database and create cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Select patient_ids and fetch all distinct records
        cursor.execute(f"""SELECT DISTINCT patient_id,file_missing
                FROM missing_files
                WHERE first_date_missing > 0 
                    AND last_date_missing > 0 
                    AND date_added = "" 
                """)

        # Fetch full list of records in the cursor
        patients_missing_files_list = cursor.fetchall()     

    # Print error if encountered      
    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    # Finalize function
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

        # Return list of patients missing files
        return patients_missing_files_list

def compare_hash(database: str, patient_id: str, file_name: str,
    current_date: str, current_hash: str, current_size: str,
    current_location: str):
    """
    This function compares the current hash with the hash previously
    recorded in the database. 

    Args:


    Returns:

    """
    
    try:
        # Connect to database and create cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Select hash for a patient_id and file_name
        cursor.execute(f"""SELECT first_hash
            FROM file_information
            WHERE patient_id = "{patient_id}"
                AND file_name = "{file_name}"
            """)

        # Fetch the hash recorded in database
        record = cursor.fetchall()

        if record == []:
            return
        else:
            for tuple in record:
                recorded_hash = tuple[0]

        # If the there is no hash recorded or the recorded hash  
        # matches the file hash given, then pass.
        if current_hash == recorded_hash:
            return
        
        # If the file hash given and the recorded hash in the database 
        # does not match, then record the file information in the 
        # correponding table
        elif current_hash != recorded_hash:

            # Select first data recorded in database
            cursor.execute(f"""SELECT date,first_hash,file_size,file_location
                FROM file_information
                WHERE patient_id = "{patient_id}"
                    AND file_name = "{file_name}"
                """)
            
            records = cursor.fetchall()

            if records == []:
                pass

            elif records != []:
                for tuple in records:
                    # Retrieve first recording data
                    first_date = tuple[0]
                    first_hash = tuple[1]
                    first_size = tuple[2]
                    first_location = tuple[3]
            
                # Define current data
                last_date = current_date
                last_hash = current_hash
                last_size = current_size
                last_location = current_location

                # Record file info into unmatching_hash table
                cursor.execute("""INSERT OR IGNORE INTO unmatching_hash VALUES(
                    :patient_id,
                    :file_name,
                    :first_hash,
                    :last_hash,
                    :first_date,
                    :last_date,
                    :first_size,
                    :last_size,
                    :first_location,
                    :last_location)""",{
                        "patient_id": patient_id,
                        "file_name": file_name,
                        "first_hash": first_hash,
                        "last_hash": last_hash,
                        "first_date": first_date,
                        "last_date": last_date,
                        "first_size": first_size,
                        "last_size": last_size,
                        "first_location": first_location,
                        "last_location": last_location})
        
            # Commit cursor to database
            connection.commit()
    
    # Print error if encountered  
    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    # Finalize function
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

def list_unmatching_hashes(database: str):
    """
    Compares the hash or message direct of the files in the 
    directory to the one recorded in the database and returns 
    the names of the files changed.

    Args:
        database (str): name of the database to connect to.
        file_name (str): full file name.
        patient_id (str): unique string identifying the patient.
        file_hash (str): hash value of the file in the directory.

    Returns:
        List of tuples of files with different hash than recorded 
        before.
    """

    try:
        # Connect to database and create cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Select hash for a patient_id and file_name
        cursor.execute(f"""SELECT patient_id,file_name
            FROM unmatching_hash
            """)

        # Fetch the hash recorded in database
        unmatching_hashes_list = cursor.fetchall()
        
        if unmatching_hashes_list == []:
            return None
        else:
            return unmatching_hashes_list

    # Print error if encountered  
    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    # Finalize function
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()     

def list_empty_files(database: str) -> list:
    """
    Identify if there are empty files in the directory being
    processed. 

    Args:
        database (str): name of the database to connect to.

    Returns:
        Names of files that are empty files.
    """
    
    empty_sha256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    empty_size = '0 bytes'

    try:
        # Connect to database and create cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Select hash, size, patient_id and file_name
        cursor.execute(f"""SELECT patient_id,file_name
            FROM file_information
            WHERE first_hash = "{empty_sha256}"
                AND file_size = "{empty_size}"
            """)

        # Fetch complete list of records in the cursor
        empty_files_list = cursor.fetchall()

    # Print error if encountered  
    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    # Finalize function
    finally:

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Return empty files list
        return empty_files_list

def define_status(database: str, unmatch_hash_list: list, 
    empty_files_list: list):
    """
    This function returns the status of the file to identify if there
    are issues to be fixed.
    
    Options include: 
        - pass: no issues where detected with the file, hence no 
            action needs to be taken,
        - hash_unmatch: the current hash does not match the previously 
            recorded hash. It could mean that the contents of the file 
            where changed since the file was recorded in the database, 
        - empty_file: the file is empty.

    Args:
        database (str):
        unmatch_hash_list (list):
        empty_files_list (list):

    Return:
        File status.
    """
    try:
        # Connect to database and create cursor
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # Select file name
        cursor.execute(f"""SELECT file_name, patient_id
            FROM file_information
            """) 

        records = cursor.fetchall()

        for record in records:
            if record[0] in unmatch_hash_list:
                status = "hash_unmatch"
                cursor.execute(f"""UPDATE file_information
                    SET status = {status}
                    WHERE patient_id = {record[1]} 
                        AND file_name = {record[0]}""")

            elif record[0] in empty_files_list:
                status = "empty_file"
                cursor.execute(f"""UPDATE file_information
                    SET status = {status}
                    WHERE patient_id = {record[1]} 
                        AND file_name = {record[0]}""")

            elif record[0] not in unmatch_hash_list or empty_files_list:
                status = "pass"
                cursor.execute(f"""UPDATE file_information
                    SET status = {status}
                    WHERE patient_id = {record[1]} 
                        AND file_name = {record[0]}""")

    except sqlite3.Error as error:
        print("Failed to read data from table,", error)
    
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

######################################################################
### Report creation functions
######################################################################

def create_patient_summary(patient_id: str, found_files: int, 
    past_records: int, new_records: int, SV_germline_count: int, 
    SNV_germline_count: int, SV_somatic_count: int, 
    SNV_somatic_count: int)-> str:
    """
    This function creates the summary of per patient of the files found
    in the directory. 

    Args:
        patient_id (str): unique string to identify the patient.
        found_files (int): number of files found in the directory that 
            correspond to the patient.
        past_records (int): number of files previously recorded in the
            database that correspond to the patient.
        new_records (int): number of new files recorded in the database
            that correspond to the patient.
        SV_germline_count (int): number of files with SV.germline% pattern
            recorded in the database.
        SNV_germline_count (int): number of files with SV.germline% pattern
            recorded in the database.
        SV_somatic_count (int): number of files with SV.germline% pattern
            recorded in the database.
        SNV_somatic_count (int): number of files with SV.germline% pattern
            recorded in the database.

    Returns:
        Formatted string with the summarized information per patient that 
        resulted from runnning the program. 
    """
    
    patient_summary = f"""
Patient: {patient_id}\n
Files in directory:
    - Files found: {found_files}
    - Previous records in database: {past_records}
    - New records in database: {new_records}\n
Essential files:
    - SV.germline: {SV_germline_count}
    - SNV.germline: {SNV_germline_count}
    - SV.somatic: {SV_somatic_count}
    - SNV.somatic: {SNV_somatic_count}\n
----------------------------------------------------------------------"""
    
    return patient_summary

def create_report_summary(today_readable: str, patients_processed: int, 
    missing_files_list: str, empty_files_list: str,
    unmatching_hash_list: str) -> str: 
    """
    
    """
 
    string_1 = f"""
----------------------------------------------------------------------
-------------------------- AACINI REPORT -----------------------------
----------------------------------------------------------------------
Date: {today_readable}\n
Total patients processed: {patients_processed}\n
Patients missing essential files:"""

    # If list is empty, print "None"
    if missing_files_list == []:
        missing_files = "\n   - None"
    else:
        missing_files = ""
        # Print records fetched in list as "patient_id: file_name"
        for tuple in missing_files_list:
            missing_files += "\n" +f"   - {tuple[0]}: {tuple[1]}"

    string_2 = "\nEmpty files (patient ID : file name):"

    if empty_files_list == []:
        empty_files = "\n   - None"
    # For each tuple in the list, print "patient_id: file_name"
    else:
        empty_files = ""
        for tuple in empty_files_list:
            empty_files += "\n" + f"   - {tuple[0]}: {tuple[1]}"
    
    string_3 = "\nFiles with unmatching hashes:"

    if unmatching_hash_list == None:
        unmatching_hash = "\n   - None"

    # For each tuple in the list, print "patient_id: file_name"
    else:
        unmatching_hash = ""
        for tuple in unmatching_hash_list:
            unmatching_hash += "\n" + f"   - {tuple[0]}: {tuple[1]}"

    string_4 = "\n----------------------------------------------------------------------"

    report_summary = "{} {}\n {} {}\n {} {}\n {}".format(
        string_1,
        missing_files,
        string_2, 
        empty_files,
        string_3,
        unmatching_hash,
        string_4)

    return report_summary

def export_to_txt(txt_file_name: str, mode: str, content: str):
    """

    Args:

    Returns:

    """

    # Save a reference to the original standard output
    original_stdout = sys.stdout 

    with open(txt_file_name, mode) as file:
        # Change the standard output to the file we created.
        sys.stdout = file
        # Print content
        print(content)

    # Reset the standard output to its original value           
    sys.stdout = original_stdout 