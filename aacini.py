# Libraries
from genericpath import isdir
import click
import os
import functions
import sqlite3

@click.group()
@click.version_option(version="1.0.0", prog_name="aacini")
def cli():
    """
    This script contains Aacini, a program that helps understand
    the structure of files and directories, as well as the data
    they contain.
    """
    pass

# Organize by extension
@click.command()
@click.option('--input_path', '-i', help='Specify path.')
def extract_file_info(input_path):
    """
    Extract information of file and directory structure.

    eg. aacini extract_file_info -i .
    """
    directory_list = os.listdir(input_path)

    if len(directory_list) == 0:
        click.secho('Found nothing to sort! Bye!', fg='blue')
    
    for directory in directory_list:
        directory_path = input_path+"/"+directory
        file_list = os.listdir(directory_path)

        for file in file_list:
            file_path = directory_path+"/"+file

            # Connect to database
            connect_db = sqlite3.connect('aacini.db')

            # Create a cursor
            cursor = connect_db.cursor()

            if os.path.isfile(file_path) == True:
                patient_id = functions.get_patient_id(directory_path)
                filename = functions.get_file_name(file_path)
                extension = functions.get_extension(file_path)
                size = functions.get_file_size(file_path)
                hash256 = functions.create_sha256(file_path)
                abs_path = functions.get_absolute_path(file_path)
                hts = functions.get_hts(file_path)

                cursor.execute("""INSERT INTO filetype_table VALUES(
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

                connect_db.commit()

            cursor.close()

        print("Records of patient {} inserted successfully into database.".format(patient_id))
  
        # Close connection
        connect_db.close()

cli.add_command(extract_file_info)

if __name__ == "__main__":
    cli()