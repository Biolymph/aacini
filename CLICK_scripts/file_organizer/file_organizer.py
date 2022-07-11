#Libraries
import click
import os, shutil
import fnmatch
import glob

#Read file_extensions dictionary
# exec(open('file_organizer.py').read())
extensions = {
    'vcf.gz': 'vcf',
    'vcf.gz.tbi': 'vcf',
    'vcf': 'vcf',
    'cram': 'cram',
    'cram.cai': 'cram',
    'bam': 'bam',
    'bam.bai': 'bam',
    'fastq': 'fastq',
    'fastq.gz': 'fastq',
    'cgh': 'cgh',
    'html':'html',
    'pdf': 'pdf',
    'json': 'json'
}

#Main entry point
@click.command()
@click.version_option(version='0.01', prog_name='file_organizer')
@click.option('--what-to-do', prompt='Hello! Welcome to File Organizer. What do you want to do today? (1: organize a particular extension, 2: organize all files, q: quit)', type=click.Choice(['1','2','q']))
def main(what_to_do):
    '''
    This script contains a File organizer which organizes and sorts files into folders based on their extensions.
    '''
    if what_to_do == '1':
        organize_by_extension()
    if what_to_do == '2':
        organize_all_files()
    if what_to_do == 'q':
        click.secho('Ok, bye!', fg='blue')
        quit
    else:
        click.secho('Sorry, I cannot helo you with that :/', fg='red')

@click.command()
@click.option('--input_path', prompt='Specify the path of the folder with the files to sort', help='Specify input path.')
@click.option('--extension', '-e', prompt='Specify the Extension to sort by', help='Specify the Extension to sort by.')
@click.option('--output_path', prompt='Specify the path to output the sorted directories and files', help='Specify output path.')
def organize_by_extension(input_path, extension, output_path):
    '''
    Organize and sort files by extension.
    eg. file_organizer organize_by_extension . --extension (or -e) fastq
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
    
@click.command()
@click.option('--input_path', prompt='Specify the path of the folder with the files to sort', help='Specify path.')
@click.option('--output_path', prompt='Specify the path to output the sorted directories and files', help='Specify output path.')
@click.option('--all_files', prompt='Do you want to organize all files in the current path?', type=click.Choice(['Yes', 'No']), help='Provide confirmation.')
def organize_all_files(input_path, all_files, output_path):
    '''
    Organize and sort all files in the current path.
    eg. file_organizer organize_all_files . --all_files Yes
    '''
    if all_files == 'Yes':
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
    if all_files == 'No':
        click.secho('Ok, bye!', fg='blue')
        quit

if __name__ == "__main__":
    main()