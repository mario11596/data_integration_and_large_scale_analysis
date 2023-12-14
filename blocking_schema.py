from collections import Counter
#from sklearn.metrics.pairwise import cosine_similarity
import math
import os
import configparser
import pandas as pd
import nltk
import re

# at first run, you have to download this three packages
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']
second_file = config['filename_out1']

def common_entries(*dcts) -> tuple[3]:
    if not dcts:
        return
    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)

def stringlist_to_vector(list):
    #cnt = Counter()
    sentence = ""
    for string in list:
        sentence += string
    pattern = re.compile(r"\w+")
    words = pattern.findall(sentence)
    #cnt.update(words)
    return Counter(words)

def custom_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

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
def blocking_schema(csv_file: os.PathLike):
    data_file = pd.read_csv(filepath_or_buffer=csv_file, delimiter=',', low_memory=False)
    blocking = {}
    Number_of_record = 0

    for _, row in data_file.iterrows():
        cleaned_name = row['NAME']
        split = cleaned_name.split('The ', maxsplit=1)
        if len(split) > 1:
            cleaned_name = split[1]
        split = cleaned_name.split('review of ', maxsplit=1)
        if len(split) > 1:
            cleaned_name = split[1]
        cleaned_name = cleaned_name.split(' ')[0]
        blocking_signature = row['STATE'] + row['CITY'] + cleaned_name + str(row['PHONEAREACODE'])[:3]
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


def find_duplicate_in_cluster(blocking: dict, threshold: float) -> list:
    records_to_delete = []
    for key, values in blocking.items():
        #print('Print cluster for key: ' + key)

        if len(values) > 1:
            #print('Size of cluster is: ' + str(len(values)))
            similarity_array = []

            # Calculate similarity
            #threshold = 0.5
            for i in range(len(values)):
                for j in range(i + 1, len(values)):
                    restaurant_one = values[i]['NAME'] + ' ' + values[i]['ADDRESS'] + ' ' + values[i]['CITY'] + ' ' + values[i]['STATE'] + ' ' + str(values[i]['PHONEAREACODE'])
                    restaurant_two = values[j]['NAME'] + ' ' + values[j]['ADDRESS'] + ' ' + values[j]['CITY'] + ' ' + values[j]['STATE'] + ' ' + str(values[j]['PHONEAREACODE'])

                    tokens1 = preprocess_text(restaurant_one)
                    tokens2 = preprocess_text(restaurant_two)

                    #similarity_score = jaccard_similarity(tokens1, tokens2)
                    similarity_score = custom_cosine(Counter(tokens1), 
                                                     Counter(tokens2))
                    #print(similarity_score)

                    similarity_array.append(similarity_score)
                    #print(similarity_array)

                if similarity_array and max(similarity_array) > threshold:
                    records_to_delete.append(values[i]['ID'])
                    #print("Records are similar.")
                #else:
                    #print("Records are not similar.")
                similarity_array = []
    return records_to_delete

def find_duplicate_between_clusters(block_list1: dict, block_list2: dict, threshold: float, idadjust1 = 0, idadjust2 = 0) -> dict:
    matching_entries = {}
    id1 = []
    id2 = []
    score = []
    #threshold = 0.5
    for _, block1, block2 in common_entries(block_list1, block_list2):
        #print(_)
        for entry1 in block1:
            restaurant_one = entry1['NAME'] + ' ' + entry1['ADDRESS'] + ' ' + entry1['CITY'] + ' ' + entry1['STATE'] + ' ' + str(entry1['PHONEAREACODE'])
            tokens1 = preprocess_text(restaurant_one)
            for entry2 in block2:
                restaurant_two = entry2['NAME'] + ' ' + entry2['ADDRESS'] + ' ' + entry2['CITY'] + ' ' + entry2['STATE'] + ' ' + str(entry2['PHONEAREACODE'])
                tokens2 = preprocess_text(restaurant_two)
                
                #similarity_score = jaccard_similarity(tokens1, tokens2)
                similarity_score = custom_cosine(Counter(tokens1), 
                                                 Counter(tokens2))
                
                #1445980000005
                id1.append(int(entry1['ID'] % 1000000)+idadjust1)
                #1450000000002
                id2.append(int(entry2['ID'] % 1000000)+idadjust2)
                if similarity_score > threshold:
                    score.append(1)
                else:
                    score.append(0)
                
    matching_entries['ltable'] = (id1)
    matching_entries['rtable'] = (id2)
    matching_entries['gold'] = (score)
    return matching_entries


if __name__ == '__main__':
    threshold = 0.5
    blocks = blocking_schema(second_file)
    ids_records = find_duplicate_in_cluster(blocks, threshold)
    mult_comp_list = find_duplicate_between_clusters(blocks, blocks, threshold)
    #print(len(mult_comp_list[0]), len(mult_comp_list[1]), len(mult_comp_list[2]))
