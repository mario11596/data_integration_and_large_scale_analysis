import configparser
import pandas as pd
import nltk

# at first run, you have to download this three packages
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('stopwords')

from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']


def jaccard_similarity(string_a, string_b):
    string_a = set(string_a)
    string_b = set(string_b)

    # calucate jaccard similarity
    result = float(len(string_a.intersection(string_b))) / len(string_a.union(string_b))
    return result


def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Remove stop words and punctuation
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]

    return set(tokens)


# create blocking schema with condition state-city-name(only first two letters)
def blocking_schema():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)
    blocking = {}
    Number_of_record = 0

    for index, row in data_file.iterrows():
        blocking_signature = row['STATE'] + row['CITY'] + row['NAME'][:2]
        blocking_signature = blocking_signature.replace(" ", "")

        if blocking.get(blocking_signature) is not None:
            blocking[blocking_signature].extend([row])
            Number_of_record = Number_of_record + 1

        else:
            blocking[blocking_signature] = []
            blocking[blocking_signature].extend([row])
            Number_of_record = Number_of_record + 1

    print('Number of blocks: ' + str(len(blocking.keys())))
    print('Length of dataset: ' + str(len(data_file['ID'])))
    print('Number of done record: ' + str(Number_of_record))

    return blocking


def find_duplicate_in_cluster(blocking):
    records_to_delete = []
    for key, values in blocking.items():
        #print('Print cluster for key: ' + key)

        if len(values) > 1:
            print('Size of cluster is: ' + str(len(values)))
            similarity_array = []

            # Calculate similarity
            threshold = 0.5
            for i in range(len(values)):
                for j in range(i + 1, len(values)):
                    restaurant_one = values[i]['NAME'] + ' ' + values[i]['ADDRESS'] + ' ' + values[i]['CITY'] + ' ' + values[i]['STATE'] + ' ' + str(values[i]['PHONEAREACODE'])
                    restaurant_two = values[j]['NAME'] + ' ' + values[j]['ADDRESS'] + ' ' + values[j]['CITY'] + ' ' + values[j]['STATE'] + ' ' + str(values[j]['PHONEAREACODE'])

                    tokens1 = preprocess_text(restaurant_one)
                    tokens2 = preprocess_text(restaurant_two)

                    similarity_score = jaccard_similarity(tokens1, tokens2)

                    similarity_array.append(similarity_score)
                    #print(similarity_array)

                if similarity_array and max(similarity_array) > threshold:
                    records_to_delete.append(values[i]['ID'])
                    print("Records are similar.")
                else:
                    print("Records are not similar.")
                similarity_array = []
    return records_to_delete


if __name__ == '__main__':
    blocks = blocking_schema()
    ids_records = find_duplicate_in_cluster(blocks)
