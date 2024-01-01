## Task 1:

## How to Run:
**Windows**
 - run_install_requirements.bat - will run pip install for all required libraries
 - run_task_1.bat will run the respective task.
 - OPTIONAL: run_uninstall_requirements.bat - will run pip uninstall for all previously installed libraries

**Linux**
 - you might need to run "chmod u+x SCRIPTNAME" before calling "./SCRIPTNAME" for the following scripts 
 - run_install_requirements.sh - will run pip install for all required libraries
 - run_task_1.sh will run the respective task.
 - OPTIONAL: run_uninstall_requirements.sh - will run pip uninstall for all previously installed libraries

## Task 1:
 - Cleaning and Encoding
     - The ADDRESS and PHONENUMBER Columns are separated into city, state and phone area code
     - Missing values of city, state or phone area code are created using the other two if possible  
         (e.g. missing state recontstructed from phone area code, etc.)
     - Entries with still missing city, state or phone are code are dropped
     - Delete records with only numbers in the name
     - Remove all symbols from the name column
     - Delete all records with an empty name
     - Encode State and City strings
 - Blocking and Deduplication
     - Create Blocks using State strings, City strings, First word of the Name and phone area code numbers
     - Find duplicates of each block using cosine similarity to compare names over a certain threshold
     - Delete these duplicates
     - Find duplicates between the same blocks of each respective csv file using same method as mentioned above
 - Scoring
     - Use list of duplicates from previous point and compare them to the labeled_data.csv
     - Return Accuracy and additional information (e.g. true positive(tp), true negative(tn), etc.)
     - Using strings rather than encoding gives better accuracy and is therefore preferred

## Description

## Files
Code for this task is in the files blocking_schema.py, data_cleaning.py, deleteDuplicates.py, scoring.py

## Extra Output:
 - **data folder**:
     - TABLENAME\_loc\_cleaned.csv is the cleaned file of restaurants
     - city_names.csv list of all unique city names with their states and phone area codes
     