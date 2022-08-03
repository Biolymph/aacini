import pysam 

file = '/Users/ki/Documents/GitHub/minerva/test_files/F0046570/2021-28499-03/tumor.merged.cram'

with open(file, "r") as opened_file:

    # Read file content
    # opened_file.read()

    # Extract file format
    #file_format = pysam.HTSFile(opened_file)
    with pysam.HTSFile(opened_file, mode='r') as htsobj:
        #print(opened_file)
        print(dir(htsobj))
        print(htsobj.is_closed)


    #print(file_format)