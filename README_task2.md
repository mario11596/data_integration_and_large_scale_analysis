## Task 2:

## How to Run:
**Windows**
 - run_install_requirements.bat - will run pip install for all required libraries
 - run_task_2.bat will run the task.
- In terminal it can be seen results of hyperparametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.bat - will run pip uninstall for all previously installed libraries

**Linux**
 - you might need to run "chmod u+x SCRIPTNAME" before calling "./SCRIPTNAME" for the following scripts 
 - run_install_requirements.sh - will run pip install for all required libraries
 - run_task_2.sh will run the task.
 - In terminal it can be seen results of hyperparametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.sh - will run pip uninstall for all previously installed libraries


### Description
At the beginning of the task, we noticed that the "address" column contains the following information: country, city, address name, address number. We separated all this data into separate columns, after we took the name of the restaurant, the name of the address and the number of the address for the purposes of training the model. We decided for this data since this data is only available in the test dataset and it is not possbile to train the model on more features than the test csv has.

The machine learning model we applied is Support Vector Machine. We decided on it because of the type of dataset, i.e. binary classification and the possibility of overfitting due to the imbalance between positive and negative classification.

Hyperparametric search was done using the "GridSearchCV" method. A set of possible parameters was defined and tested, namely: C, gamma and kernel. Also, during the search for the best parameters, 3-fold cross-validation was used. After the search was done, the parameters with which the model achieved the best average accuracy were automatically taken. Furthermore, the training of the model in 3-fold cross-validation was again carried out with these parameters. The model was tested with predictX.csv dataset and achieved an accuracy of 74.25%.

### Files
Code for this task is in the file machine_learning.py