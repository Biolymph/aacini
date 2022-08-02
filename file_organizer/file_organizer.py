# Libraries
import click
import os, shutil
import fnmatch
import glob
from constants import extensions

@click.group()
@click.version_option(version='0.02', prog_name='file_organizer')
def cli():
    '''
    This script contains a File organizer which organizes and sorts files into folders based on their extensions.
    '''
    pass

# Organize by extension
@click.command()
@click.option('--input_path', '-i', help='Specify input path.')
@click.option('--extension', '-e', help='Specify the Extension to sort by.')
@click.option('--output_path', '-o', help='Specify output path.')
def organize_by_extension(input_path, extension, output_path):
    '''
    Organize and sort based on a given extension.
    eg. file_organizer organize_by_extension -i . -e fastq -o ./output
    '''
    # Get matching files to the extensions dictionary
    file_list = glob.glob(os.path.join(input_path, '*.{}'.format(extension)))

    if len(file_list) == 0:
        click.secho('Found nothing to sort! Bye!', fg='blue')

    for file in file_list:
        if fnmatch.fnmatch(file, '*'+extension):
            click.secho('[*] Found {}'.format(len(file_list)) + ' files with {}'.format(extension) + ' extension', fg='blue')
            folder_name = dict.get(extensions, extension)

        # Make new directory if it does not exist for the extension
        if not os.path.isdir(os.path.join(output_path, folder_name)) and file_list:            
            click.secho('[+] Making {}'.format(folder_name) + ' folder')
            os.mkdir(os.path.join(output_path, folder_name))
            
        # Move file to corresponding folder
        for file in file_list:                                                          
            basename = os.path.basename(file)
            destination = os.path.join(output_path, folder_name, basename)
            click.secho('Moving {}'.format(file) + ' to {}'.format(destination))
            shutil.move(file, destination)
        click.secho('Done!', fg='green')

# Organize all files in a folder    
@click.command()
@click.option('--input_path', '-i', help='Specify path.')
@click.option('--output_path', '-o', help='Specify output path.')
def organize_all_files(input_path, output_path):
    '''
    Organize and sort all files in a given path.
    eg. file_organizer organize_all_files -i . -o ./output
    '''
        # Get matching files to the extensions dictionary
    for extension, folder_name in extensions.items():                               
        file_list = glob.glob(os.path.join(input_path, '*.{}'.format(extension)))
        click.secho('[*] Found {}'.format(len(file_list)) + ' files with {}'.format(extension) + ' extension', fg='blue')
            
            # Make new directory if it does not exist for the extension
        if not os.path.isdir(os.path.join(output_path, folder_name)) and file_list:            
            click.secho('[+] Making {}'.format(folder_name) + ' folder')
            os.mkdir(os.path.join(output_path, folder_name))
            
            # Move file to corresponding folder
        for file in file_list:                                                          
            basename = os.path.basename(file)
            destination = os.path.join(output_path, folder_name, basename)
            click.secho('Moving {}'.format(file) + ' to {}'.format(destination))
            shutil.move(file, destination)
    click.secho('Done!', fg='green')

cli.add_command(organize_all_files)
cli.add_command(organize_by_extension)

if __name__ == "__main__":
    cli()