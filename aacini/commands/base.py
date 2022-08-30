from email.policy import default
from genericpath import isdir, isfile
import click
import os
import datetime

from aacini import __version__ as version

# File information extraction functions
from aacini.utils.functions import list_file_path
from aacini.utils.functions import list_files
from aacini.utils.functions import get_file_name
from aacini.utils.functions import get_extension
from aacini.utils.functions import get_absolute_path
from aacini.utils.functions import get_patient_id
from aacini.utils.functions import get_file_size
from aacini.utils.functions import create_sha256
from aacini.utils.functions import get_hts

# Database infrastructure functions
from aacini.utils.functions import create_file_information_table
from aacini.utils.functions import create_essential_files_missing_table
from aacini.utils.functions import create_unmatching_hash_table

# Database interaction functions
from aacini.utils.functions import record_file_info
from aacini.utils.functions import count_records
from aacini.utils.functions import check_essential_files

# Quality control & Stats functions
from aacini.utils.functions import list_patients_missing_files
from aacini.utils.functions import list_unmatching_hashes
from aacini.utils.functions import list_empty_files
from aacini.utils.functions import list_missing_files
from aacini.utils.functions import define_status
from aacini.utils.functions import compare_hash

# Report creation functions
from aacini.utils.functions import create_patient_summary
from aacini.utils.functions import create_report_summary
from aacini.utils.functions import export_to_txt

# Updating functions
from aacini.utils.functions import update_record_status

@click.group()
@click.version_option(version=version, prog_name="aacini")
def cli():
    """
    This script contains Aacini, a program that helps understand
    the structure of files and directories, as well as the data
    they contain.
    """
    pass

@click.command("extract")
@click.option("--input_path", "-i", help="Specify path.")
@click.option("--db", "-db", help="Specify database name.", default="aacini.db")
def extract_file_info(input_path, db):
    """
    Extract information of file and directory structure.

    eg. aacini extract_file_info -i ./files -db database.db
    """

    # Get ticket name
    ticket = os.path.basename(input_path)
    print("\nTicket:", ticket)
    
    # List directories
    directory_list = os.listdir(input_path)
    print("\nPatients to process:", len(directory_list),"\n")
    
    # Establish transaction datetime
    today_readable = datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
    today_string = datetime.datetime.today().strftime("%d%m%Y_%H%M%S") 

    # Return message if directory is empty
    if len(directory_list) == 0:
        click.secho("Found nothing to sort! Bye!", fg="blue")

    # Instantiate missing files list
    missing_files_list = []

    # List paths of directories to process
    for directory in directory_list:
        directory_path = os.path.join(input_path, directory)

        # List files and paths in the directory
        file_list = list_files(directory_path= directory_path)
        file_path_list = list_file_path(directory_path= directory_path)

        # Count files found in the directory
        found_files = len(file_list)

        # Create tables if they do not exist
        create_file_information_table(database=db)
        create_unmatching_hash_table(database=db)

        # Count past records of the patient
        past_records = count_records(
            database=db,
            table="file_information", 
            column="patient_id",
            value=directory)

        # Look if files are missing from previously recorded
        missing_files_list.append(list_missing_files(
            database= db, 
            directory= directory,
            file_list= file_list))

        # Insert a progress bar per patient directory to process
        with click.progressbar(file_path_list, fill_char="|", 
                                empty_char="") as files_to_process:
            
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

                # Compare hashes
                compare_hash(
                    database= db,
                    patient_id= patient_id,
                    file_name= filename,
                    current_date= today_readable,
                    current_hash= hash256,
                    current_size= size,
                    current_location= abs_path)

                # Record information into database
                record_file_info(
                    database= db,
                    ticket= ticket,
                    patient_id= patient_id,
                    file_name= filename,
                    extension= extension,
                    file_size= size,
                    first_hash= hash256,
                    abs_path= abs_path,
                    file_type= hts)        

            # Create table in database to register missing essential files
            create_essential_files_missing_table(database=db)

            # Count and record the missing files per patient
            essential_files_count = check_essential_files(
                            database=db,
                            patient_id=patient_id)
    
            # Count records after commit
            records_after_commit = count_records(
                        database=db,
                        table="file_information",
                        column="patient_id",
                        value=patient_id)
            
            # Count new records recorded in database
            new_records = records_after_commit - past_records
            
            # Print patient_id to show on progress bar
            print("\tPatient:", patient_id)

            # Append patient summary to txt file
            export_to_txt(
                txt_file_name= "content.txt", 
                mode="a", 
                content= create_patient_summary(
                    patient_id= patient_id,
                    found_files= found_files,
                    past_records= past_records,
                    new_records= new_records,
                    SV_germline_count= essential_files_count[0],
                    SNV_germline_count= essential_files_count[1],
                    SV_somatic_count= essential_files_count[2],
                    SNV_somatic_count= essential_files_count[3]))

    # List patients_missing_essential_files, empty_files, files_unmatching_hashes
    # and missing_files

    patients_missing_essential_files_list = list_patients_missing_files(database=db)
    empty_files_list = list_empty_files(database=db)
    unmatching_hash_list = list_unmatching_hashes(database=db)

    define_status(database= db,
        unmatch_hash_list= unmatching_hash_list,
        empty_files_list= empty_files_list,
        missing_files_list= missing_files_list)

    # Write report summary to txt file
    export_to_txt(
        txt_file_name= "summary.txt", 
        mode="w", 
        content= create_report_summary(
            ticket= ticket,
            today_readable= today_readable,
            patients_processed= len(directory_list),
            essential_files_missing_list= patients_missing_essential_files_list,
            empty_files_list= empty_files_list,
            unmatching_hash_list= unmatching_hash_list,
            missing_files_list= missing_files_list))

    # Print and export the report
    report_name = f"aacini_report_{ticket}_{today_string}.txt"

    files = ["summary.txt", "content.txt"]

    with open(report_name, "w") as report:
        # Iterate through list
        for file in files:
  
            # Open each file in read mode
            with open(file) as infile:
  
                # read the data from file1 and
                # file2 and write it in file3
                report.write(infile.read())

            os.remove(file)

@click.command("update_status")
@click.option("--db", "-db", help="Specify database name.", default="aacini.db")
@click.option("--file_name", "-fn", help="Specify file name.")
@click.option("--patient_id", "-pid", help="Specify patient ID.")
@click.option("--status", "-st", 
    type= click.Choice(["pass", "hash_unmatch", "empty_file", "missing_file", "other"]), 
    help="Specify status to change to.")
def update_status(db, file_name, patient_id, status):
    """
    Update record status the file_information table.

    eg. aacini update_status -db database.db -fn tumor.merged-scatter.pdf
        -pid F0054321 -st pass
    """

    update_record_status(
        database=db,
        patient_id=patient_id,
        file_name=file_name,
        status=status)
    
    feedback = f"""\nUpdated record:
    - Patient: {patient_id}
    - File: {file_name}
    - New status: {status}
        """
    
    print(feedback)

cli.add_command(extract_file_info)
cli.add_command(update_status)

if __name__ == "__main__":
    cli()