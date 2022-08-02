import hashlib
import json
import os
import pandas as pd

def return_json_as_pydict():
    '''
    Function that returns a json file containing multiple objects as a python dictionary.

    Use case: files with multi samples.
    '''
    # Opening JSON file
    file = open('Lymfoid_220301_AK.json')
  
    # returns JSON object as a dictionary
    data = json.load(file)

    for sample in data['samples']:
        print(sample['name'])


def get_file_name(file: str) -> str:
    '''
    This function gets the original file name.

    Args:
        Absolute path of a file.
    Returns:
        Final component of a file path (file name).
    '''
    filename = os.path.basename(file)
    return filename

def get_extension():
    '''
    This function gets the extension type of a file and 
    '''
    pass

def get_absolute_path():
    '''
    This function gets the original absolute path of the file.
    '''
    pass

def get_patient_id():
    '''
    This function gets the unique string used to identify a patient.
    '''
    pass

def get_file_size():
    '''
    This function gets the size of the file in KB.
    '''
    pass

def create_sha256(path: str) -> str:
    '''
    This function creates a 32-byte hash or message digest using the sha256 algorithm.

    Args:
        Absolute path of a file.

    Returns:
        Hexadecimal 32-byte hash of the file using the sha256 algorithm.
    '''
    with open(path, "rb") as opened_file:
        content = opened_file.read()
        sha256 = hashlib.sha256()
        sha256.update(content)
        return sha256.hexdigest()

# patient_id text,
# sample_id text,
#         file_name text,
#         file_type text,
#         size real,
#         hash256 text,
#         file_location text,
#         index_file text,
#         index_file_size,
#         index_file_hash256 text,
#         hts_file text