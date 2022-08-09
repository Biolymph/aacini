# import pysam 

# file = '/Users/ki/Documents/GitHub/minerva/test_files/F0046570/2021-28499-03/tumor.merged.cram'

# with open(file, "r") as opened_file:

#     # Read file content
#     # opened_file.read()

#     # Extract file format
#     #file_format = pysam.HTSFile(opened_file)
#     with pysam.HTSFile(opened_file, mode='r') as htsobj:
#         #print(opened_file)
#         print(dir(htsobj))
# #         print(htsobj.is_closed)


# #     #print(file_format)

# import os
# import pathlib

# input_path = './test_files'

# directory_list = os.listdir(input_path)

# print('----------------------------------------------------------------------')
# print()
# print('Total patients to process: ', len(directory_list))
# print()
# print('----------------------------------------------------------------------')
# print()

# for directory in directory_list:
#     directory_path = os.path.join(input_path, directory)
#     print(directory_path)

#     file_list = []
#     for path in pathlib.Path(directory_path).rglob("*"):
#         if os.path.isfile(path) == True:
#             name = pathlib.Path(path).name
#             if not name.startswith("."):
#                 file_list.append(name)
#     print(file_list)
#     print(len(file_list))

    

    # # Iterate directory to include only files
    # for dirpath, dirname, filename in os.walk(directory_path, topdown=True):
    #     file_list.append(filename)

    # # print(file_list)
    #     flat_file_list = []  
    #     for names in file_list:
    #         for name in names:
    #             flat_file_list.append(name)
    #             print(flat_file_list)

import sqlite3
from aacini.utils.functions import count_records
from aacini.utils.functions import list_essential_files
from aacini.utils.functions import count_essential_files

connection = sqlite3.connect("test.db")
cursor = connection.cursor()

cursor.execute("""CREATE TABLE if not exists test_table (
            patient_id text,
            feature_type text
            )""")

connection.commit()

past_records = count_records(cursor= cursor,
                            table='test_table', 
                            column='patient_id',
                            value='A1')
cursor.execute("INSERT INTO test_table VALUES('A1', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A1', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A1', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A1', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A2', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A2', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A2', 'vcf')")
cursor.execute("INSERT INTO test_table VALUES('A3', 'vcf')")


new_records = count_records(cursor= cursor,
                            table='test_table', 
                            column='patient_id',
                            value='A1')

# cursor.execute("DELETE FROM test_table")

connection.commit()

print('Past records: ',past_records)
print('New records: ',new_records)

