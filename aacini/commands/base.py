

from email.policy import default
from genericpath import isdir, isfile
import click
import os
import sqlite3

from aacini import __version__ as version
from aacini.utils.functions import create_filetype_table
from aacini.utils.functions import count_records
from aacini.utils.functions import get_patient_id
from aacini.utils.functions import get_file_name
from aacini.utils.functions import get_extension
from aacini.utils.functions import get_file_size
from aacini.utils.functions import create_sha256
from aacini.utils.functions import get_absolute_path
from aacini.utils.functions import get_hts

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
    directory_list = os.listdir(input_path)
    print('----------------------------------------------------------------------')
    print()
    print('Total patients to process: ', len(directory_list))
    print()
    print('----------------------------------------------------------------------')
    print()

    if len(directory_list) == 0:
        click.secho('Found nothing to sort! Bye!', fg='blue')
    
    for directory in directory_list:
        directory_path = os.path.join(input_path, directory)
        
        # Iterate directory to include only files
        file_list = []

        for directory_path, subdir_path, file_names in os.walk(directory_path):
            file_list.append(file_names)
        
        found_files = len(file_list)

        with click.progressbar(file_list, show_eta='enable', fill_char='|', empty_char='') as files_to_process:
            for file in files_to_process:
                file_path = os.path.join(directory_path,file)

                # Connect to database
                connection = sqlite3.connect(db)

                # Create a cursor
                cursor = connection.cursor()

                # Create table if it does not exist
                create_filetype_table(connection, cursor)

                past_records = count_records(
                                        cursor= cursor,
                                        table='filetype_table', 
                                        column='patient_id',
                                        value=directory)

                if os.path.isfile(file_path) == True:
                    patient_id = get_patient_id(directory_path)
                    filename = get_file_name(file_path)
                    extension = get_extension(file_path)
                    size = get_file_size(file_path)
                    hash256 = create_sha256(file_path)
                    abs_path = get_absolute_path(file_path)
                    hts = get_hts(file_path)                    

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
                            "hts": hts
                            })

                    connection.commit()
                    
                    # Count records after commit
                    records_after_commit = count_records(
                                        cursor= cursor,
                                        table='filetype_table', 
                                        column='patient_id', 
                                        value=patient_id)

                    new_records = records_after_commit - past_records

                cursor.close()
    
            print()
            print("Records of patient {}".format(patient_id))
            print('Found in directory: {}'.format(found_files) )
            print('Previous records in database: {}'.format(past_records))
            print('New records in database: {}'.format(new_records))
            print()
            print('----------------------------------------------------------------------')
  
            # Close connection
            connection.close()

cli.add_command(extract_file_info)

if __name__ == "__main__":
    cli()