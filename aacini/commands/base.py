

from genericpath import isdir
import click
import os
import sqlite3

from aacini import __version__ as version
from aacini.utils.functions import get_patient_id
from aacini.utils.functions import get_file_name
from aacini.utils.functions import get_extension
from aacini.utils.functions import get_file_size
from aacini.utils.functions import create_sha256
from aacini.utils.functions import get_absolute_path
from aacini.utils.functions import get_hts

# @click.group()
@click.version_option(version=version, prog_name="aacini")
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
            connect_db = sqlite3.connect('./database/aacini.db')

            # Create a cursor
            cursor = connect_db.cursor()

            if os.path.isfile(file_path) == True:
                patient_id = get_patient_id(directory_path)
                filename = get_file_name(file_path)
                extension = get_extension(file_path)
                size = get_file_size(file_path)
                hash256 = create_sha256(file_path)
                abs_path = get_absolute_path(file_path)
                hts = get_hts(file_path)

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

# cli.add_command(extract_file_info)

if __name__ == "__main__":
    cli()