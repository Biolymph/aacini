# Change log

## [0.0.1] (2022-07-29)

### Added:
* Basic functions needed to record "Filetype table".
* Click script to fill "Filetype table" by giving an input_path.


## [0.0.2] (2022-07-29)

### Added:
* Added "Missing Files table".
* Added "count_essential_files" function to record one row per missing 
file to "Missing Files table".
* Added "list_patients_missing_files" function to list the patients and the
filetype that is missing.


## [0.0.3] (2022-08-18)

### Changed:
* Changed name of function count_essential_files to check_essential_files.

### Fixed:
* Function to fill "Mising Files table": check_essential_files now records
one row per missing filetype including the first_date_missing, 
last_date_missing and date_added. The purpose is to easily track when the
file was missing and when it was added.

## [0.1.0] (2022-08-29)

### Changed: 
* Report prints directly to txt. Only summary is shown in the terminal. 
* Modularity of print/list functions.

### Added:
* Function to compare hashes from the same file and record it in a new
table in the database. 

## [0.2.0] (2022-08-30)

### Changed:
* Function to list missing files exports a tuple, not a list. The list 
is creating by iterating the directories in the "extract" Click command.
* Separated list for "missing essential files" and for files that were
previously in the database and were lately removed, hence "missing files".

### Added:
* New Click command to update status of record in file_information table.
* Added ticket name to report and terminal feedback.

## [1.0.0] (2022-08-30)

### Fixed:
* Updated Readme.md.

### Changed:
* Hash creation function calculates hash in chunks of 128MB, which increases
speed and decreases memory usage.