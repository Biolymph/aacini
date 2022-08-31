<img width="713" alt="aacini_logo3" src="https://user-images.githubusercontent.com/78170591/182372880-17ffe77a-a390-4c6f-9bcc-5ba2c333926f.png">

# aacini
Data summarization tools and scripts for Biolymph deliveries from SciLifeLab. 

The program is named after the Nahualt word "aacini", which refers to one who comes to know something completely [1](https://nahuatl.uoregon.edu/content/aacini). Aacini is represented as an axolotl named Maria. Axolotls symbolize health and regeneration in Mexican culture [2](https://www.nationalgeographic.com/animals/article/mexico-is-finally-embracing-its-quirky-salamander-the-axolotl).

Here, have a meme by Nathan W. Pyle:

<img width="350" alt="axolotl_meme" src="https://user-images.githubusercontent.com/78170591/187660047-448d6a61-81fe-44fc-8b72-f386756517b5.png">

## Getting the code
You can download a copy of all the files in this repository by cloning the git repository:

`git clone https://github.com/biolymph/minerva`

## Setting up a Python virtual environment
It is recommended to create a virtual environment in conda and manage project dependencies in isolation, but other similar tools can be used. To set up the conda environment run the following commands in the repository folder.

**Create a conda environment with Python 3.7 and pip:**

`conda create -n aacini python=3.10.5 pip`

**Activate the conda environment:**

`conda activate aacini`

**Install the setup:**

`python3 setup.py install`

## Commands available

The program runs two commands (extract_file_info and update_status) that help understand the structure of files and directories, as well as the data they contain. To access the information for the commands run:

`aacini --help`

**extract_file_info**

This commands extracts all the file and directory information for a given location.

```
Command:
  extract        Extract information of file and directory structure.

Usage: aacini extract [OPTIONS]

  Extract information of file and directory structure.

  eg. aacini extract_file_info -i ./files -db database.db

Options:
  -i, --input_path TEXT  Specify path.
  -db, --db TEXT         Specify database name.
  ```

**update_status**

This commands updates the record status in the file_information table in the database.

```
Command:
  update_status  Update record status the file_information table.
 
Usage: aacini update_status [OPTIONS]

  Update record status the file_information table.

  eg. aacini update_status -db database.db -fn tumor.merged-scatter.pdf -pid F0054321 -st pass

Options:
  -db, --db TEXT                  Specify database name.
  -fn, --file_name TEXT           Specify file name.
  -pid, --patient_id TEXT         Specify patient ID.
  -st, --status [pass|hash_unmatch|empty_file|missing_file|other]
                                  Specify status to change to.
```

### References:
1. Wood, S. (n.d.). AACINI. aacini. | Nahuatl Dictionary. Retrieved August 31, 2022, from https://nahuatl.uoregon.edu/content/aacini 
2. Deines, T., &amp; Rojas, L. A. (2022, January 15). Mexico City's endangered axolotl has found fame-is that enough to save it? Animals. Retrieved August 31, 2022, from https://www.nationalgeographic.com/animals/article/mexico-is-finally-embracing-its-quirky-salamander-the-axolotl 
