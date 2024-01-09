## Task 2:

## How to Run:
**Windows**
 - run_install_requirements.bat - will run pip install for all required libraries
 - run_task2.bat will run the task.
- In terminal it can be seen results of hyper-parametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.bat - will run pip uninstall for all previously installed libraries

**Linux**
 - you might need to run "chmod u+x SCRIPTNAME" before calling "./SCRIPTNAME" for the following scripts 
 - run_install_requirements.sh - will run pip install for all required libraries
 - run_task2.sh will run the task.
 - In terminal it can be seen results of hyper-parametric search, accuracy for the 3-fold cross validation with best parameters, and the final accuracy with test dataset
 - OPTIONAL: run_uninstall_requirements.sh - will run pip uninstall for all previously installed libraries


## Description
First, we started by separating and manipulating the dataset to have a proper shape. It was noticed that the "address" (ltable.ADDRESS, rtable.ADDRESS) columns contain the following information: country (state), city, address name, address number. We separated all this data into separate columns, after we took the name of the restaurant, the name of the address and the number of the address for the purposes of training the model. We decided for this data since this features are also available in the test dataset and it is not possbile to train the model on more features than the test csv has. The next step was to transformed all strings into numbers. The method which we use for is called TfidfVectorizer which transformed dataset into TF-IDF features. Since this method gives vectors of different lengths for each record, we transformed the vectors by using the mean for the each vector. In this way, a number was obtained which replaces the string.

The machine learning model which has been applied is Support Vector Machine. We decided on it because of the type of dataset, i.e. binary classification and the possibility of overfitting because of the imbalance between positive and negative classifications.

Hyper-parametric search was done using the "GridSearchCV" method. A set of possible parameters was defined and tested, namely: C, gamma and kernel. Also, during the search for the best parameters, 3-fold cross-validation was used. After the search was done, the parameters with which the model achieved the best average accuracy were automatically taken. The best parameters are: 'C'=100, 'gamma' = 0.001, 'kernel' ='rbf'. Furthermore, the training of the model in 3-fold cross-validation was again carried out with these parameters. Accuracies for this cross-validation are: Fold 1: 0.8733, Fold 2: 0.8591, Fold 3: 0.8322. The model was tested with predictX.csv dataset and achieved an accuracy of 0.8425 (84.25%).

## Files
Code for this task is in the file machine_learning.py