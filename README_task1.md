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
( describe the part about first three points). 
By analyzing the data, it was noticed that we need to delete strange symbols, delete records that have only numbers or that contain null as a name. First, we delete records that contain only numbers as the name of the restaurant. We considered such records to be errors, so they do not need to be in the dataset. Furthermore, we deleted all characters from the column name that were not numbers or letters, or ordinary symbols. After applied this technique, some records got null in the name of the restaurant, and we also deleted such records. After these methods, it was applied feature encoding. We replaced the country names using the BaseNEncode method with base=8, while it was applied the TargetEncoder method to the city names, where the target was "PHONEAREACODE". After calculated the accuracy at the end of the tasks, it was noticed that a better result was achieved by using strings instead of encoding.

To create the blocking scheme, it was used the signature as "country + city + the first three numbers from the PHONEAREACODE column". This way we got 2890 blocks in Zomato, 5466 blocks in Yelp. Cosine similarity method was used to find duplicates between blocks within each csv file. Total deleted duplicates in Zomato is 5 and in Yelp is 198. Also, this same method was used to find the same records between two csv files. A threshold of 0.80 percent was used for both mentioned cases. After duplicates are found, they are saved in a temporary array and duplicate records are marked with "1" and the rest with "0".

Using a temporary field allowed us to compare duplicates with duplicates from the labeled_data.csv file. The analysis determined that true positive is 224, true negative is 193, false positive is 0, and false negative is 16. Also, the number of matches records which are also in the labeled_data csv file is 67, while the number of matches records which are not in file is 157. The matching accuracy of our pipeline is 96.30%. This percentage is primarily high due to the large number of duplicates that we found using a different blocking scheme, compared to the one specified in the task.
## Files
Code for this task is in the files blocking_schema.py, data_cleaning.py, deleteDuplicates.py, scoring.py

## Extra Output:
 - **data folder**:
     - TABLENAME\_loc\_cleaned.csv is the cleaned file of restaurants
     - city_names.csv list of all unique city names with their states and phone area codes
     