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

## Description
First, the columns "NO_OF_REVIEWS" and "RATING" are dropped from both csv files. Furthermore we separate both ADDRESS and PHONENUMBER columns into separate city, state and phone area code columns. Using the link between these three datapoints and a dictionary which saves the complete links between city, state and phone area code, it is possible to reconstruct missing info if at least two others are present (e.g. city and phone area code can give us info about the state, etc...). The remaining entries which are not able to achieve these three entries are dropped.
By analyzing the data, it was noticed that we need to delete strange symbols, delete records that have only numbers or that contain null as a name. First, we delete records that contain only numbers as the name of the restaurant. We considered such records to be errors, so they do not need to be in the dataset. Furthermore, we deleted all characters from the column name that were not numbers or letters, or ordinary symbols. After applying this technique, some records become null in the restaurant name column, and therefore need to be deleted. After these methods, we applied feature encoding. We replaced the country names using the BaseNEncode method with base=8, while we apply the TargetEncoder method to the city names, where the target was "PHONEAREACODE". After calculating the accuracy at the end of the task, it was noticed that a better result was achieved by using strings instead of the encoding.

To create the blocking scheme, we used the signature as "country + city + the first three numbers from the PHONEAREACODE column". This way we got 2890 blocks in Zomato, 5466 blocks in Yelp. Cosine similarity method was used to find duplicates between blocks within each csv file. Total deleted duplicates in Zomato is 5 and in Yelp is 198. Also, this same method was used to find the same records between the two csv files. A threshold of 0.80 percent was used for both mentioned cases. After duplicates were found, they are saved in a temporary array and duplicate records are marked with "1" and the rest with "0".

Using a temporary field allowed us to compare duplicates with duplicates from the labeled_data.csv file. The analysis determined that true positive is 224, true negative is 193, false positive is 0, and false negative is 16. Also, the number of matched records which are also in the labeled_data csv file is 67, while the number of matches records which are not in file is 157. The matching accuracy of our pipeline is 96.30%. This percentage is primarily high due to the large number of duplicates that we found using a different blocking scheme, compared to the one specified in the task.

## Files
Code for this task is in the files blocking_schema.py, data_cleaning.py, deleteDuplicates.py, scoring.py

## Extra Output:
 - **data folder**:
     - TABLENAME\_loc\_cleaned.csv is the cleaned file of restaurants
     - city_names.csv list of all unique city names with their states and phone area codes
     