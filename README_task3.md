## Task 3:

## How to Run:
**Windows**
 - run_install_requirements.bat - will run pip install for all required libraries
 - run_task3.bat will run the task.
- In terminal it can be seen results of hyper-parametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.bat - will run pip uninstall for all previously installed libraries

**Linux**
 - you might need to run "chmod u+x SCRIPTNAME" before calling "./SCRIPTNAME" for the following scripts 
 - run_install_requirements.sh - will run pip install for all required libraries
 - run_task3.sh will run the task.
 - In terminal it can be seen results of hyper-parametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.sh - will run pip uninstall for all previously installed libraries


## Description
To clean the Yelp_error file we apply two main methods. 
Firstly we look for missing Values in PHONENUMBER and replace them with a more sensable String. 
Secondly we look at both NAME and ADDRESS and try and fix the existing Typos with the help of regex. 
After applying these the resulting table is compared to the original Yelp.csv file and its accuracy of 93.57% is reported.
In addition we also report the amount of corrupted and fixed instances: 6044 as well as the specific types of errors per entry, namely the amount of typos: 11737 and missing values: 162. 

## Files
Code for this task is in the file error_cleaning.py

## Extra Output:
 - **data folder**:
     - Csv output is in the file yelp_error_cleaned.csv