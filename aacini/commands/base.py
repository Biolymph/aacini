

from email.policy import default
from genericpath import isdir, isfile
import click
import os
import sqlite3
import pathlib

from aacini import __version__ as version
from aacini.utils.functions import create_filetype_table, list_patients_missing_files
from aacini.utils.functions import count_records
from aacini.utils.functions import get_patient_id
from aacini.utils.functions import get_file_name
from aacini.utils.functions import get_extension
from aacini.utils.functions import get_file_size
from aacini.utils.functions import create_sha256
from aacini.utils.functions import get_absolute_path
from aacini.utils.functions import get_hts
from aacini.utils.functions import count_essential_files
from aacini.utils.functions import create_missingfiles_table

@click.group()
@click.version_option(version=version, prog_name="aacini")
def cli():
    """
    This script contains Aacini, a program that helps understand
    the structure of files and directories, as well as the data
    they contain.
    """
    pass

# Organize by extension
@click.command('extract')
@click.option('--input_path', '-i', help='Specify path.')
@click.option('--db', '-db', help='Specify database name.', default='aacini.db')
def extract_file_info(input_path, db):
    """
    Extract information of file and directory structure.

    eg. aacini extract_file_info -i ./files -db database.db
    """
    # List directories 
    directory_list = os.listdir(input_path)

    # Return message if directory is empty
    if len(directory_list) == 0:
        click.secho("Found nothing to sort! Bye!", fg="blue")
    
    # List paths of directories to process
    for directory in directory_list:
        directory_path = os.path.join(input_path, directory)

        # List files in the directory
        file_list = []
        file_path_list = []
        
        # Recursively iterate through the directory
        for file_path in pathlib.Path(directory_path).rglob("*"):
            
            # Keep only files
            if os.path.isfile(file_path) == True:
                name = pathlib.Path(file_path).name
                file_path = file_path
                
                # Avoid files that start with . (e.g. ".DS_Store")
                if not name.startswith("."):
                    file_list.append(name)
                    file_path_list.append(file_path)
        
        # Count files found in the directory
        found_files = len(file_list)

        # Connect to database
        connection = sqlite3.connect(db)

        # Create a cursor
        cursor = connection.cursor()

        # Create table if it does not exist
        create_filetype_table(connection, cursor)

        # Count past records of the patient
        past_records = count_records(
                    cursor= cursor,
                    table='filetype_table', 
                    column='patient_id',
                    value=directory)

        # Insert a progress bar per patient directory to process
        with click.progressbar(file_path_list, show_eta='enable', fill_char='|', 
                                empty_char='') as files_to_process:
            
            # Iterate through the files in the file list
            for file in files_to_process:
                
                # Extract information from the file list
                patient_id = get_patient_id(directory_path)
                filename = get_file_name(file)
                extension = get_extension(file)
                size = get_file_size(file)
                hash256 = create_sha256(file)
                abs_path = get_absolute_path(file)
                hts = get_hts(file)                                    

                # Insert information into database table
                cursor.execute("""INSERT OR IGNORE INTO filetype_table VALUES(
                            :patient_id,
                            :filename,
                            :extension,
                            :size,
                            :hash_sha256,
                            :file_location,
                            :hts)""",
                                {"patient_id": patient_id,
                                "filename": filename,
                                "extension": extension,
                                "size": size,
                                "hash_sha256": hash256,
                                "file_location": abs_path,
                                "hts": hts})   

                connection.commit()

                # Create table in database to register missing files
                create_missingfiles_table(connection, cursor)

                # Count and record the missing files per patient
                essential_files_count = count_essential_files(
                            cursor=cursor,
                            connection=connection,
                            column_filename='filename',
                            table='filetype_table',
                            column_patient_id='patient_id',
                            patient_id=patient_id)
    
            # Count records after commit
            records_after_commit = count_records(
                                        cursor= cursor,
                                        table='filetype_table', 
                                        column='patient_id', 
                                        value=patient_id)
            
            # Count new records recorded in database
            new_records = records_after_commit - past_records
            
            print("\n")
            print("Patient: {}".format(patient_id),"\n")
            print("Found in directory: {}".format(found_files))
            print("Previous records in database: {}".format(past_records))
            print("New records in database: {}".format(new_records),"\n")
            print("Essential files:")
            print("     SV.germline: {}".format(essential_files_count[0]))
            print("     SNV.germline: {}".format(essential_files_count[1]))
            print("     SV.somatic: {}".format(essential_files_count[2]))
            print("     SNV.somatic: {}".format(essential_files_count[3]),"\n")

            
        print("----------------------------------------------------------------------")
    print("----------------------------------------------------------------------")
    print()
    print("Total patients processed: ", len(directory_list))
    print("Patients missing essential files: \n")
    print(list_patients_missing_files(cursor))

    # Close cursor
    cursor.close()

    # Close connection
    connection.close()

cli.add_command(extract_file_info)

if __name__ == "__main__":
    cli()