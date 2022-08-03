

from email.policy import default
from genericpath import isdir
import click
import os
import sqlite3

from aacini import __version__ as version
from aacini.utils.functions import connect_database, create_filetype_table
from aacini.utils.functions import create_cursor
from aacini.utils.functions import commit_input
from aacini.utils.functions import close_connection
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
@click.option('--db', '-db', help='Specify database.', default='aacini.db')
def extract_file_info(input_path, db):
    """
    Extract information of file and directory structure.

    eg. aacini extract_file_info -i .
    """
    directory_list = os.listdir(input_path)

    if len(directory_list) == 0:
        click.secho('Found nothing to sort! Bye!', fg='blue')
    
    with click.progressbar(directory_list) as dir_bar:
        for directory in dir_bar:
            directory_path = os.path.join(input_path, directory)
            file_list = os.listdir(directory_path)
            file_count = len(file_list)

            with click.progressbar(file_list, show_eta='enable', fill_char='|', empty_char='') as bar:
                for file in bar:
                    file_path = os.path.join(directory_path,file)

                    # Connect to database
                    connection = connect_database(db)

                    # Create a cursor
                    cursor = create_cursor(connection)

                    # Create table if it does not exist
                    create_filetype_table(connection,cursor)

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

                    cursor.close()
            
                print()
                print("  Records of patient {} inserted successfully into database: {}".format(patient_id, file_count))
  
                # Close connection
                connection.close()

cli.add_command(extract_file_info)

if __name__ == "__main__":
    cli()