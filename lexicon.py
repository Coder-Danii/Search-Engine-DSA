import json
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string
import re
import csv
from num2words import num2words

# Download NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize NLTK tools
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Function to split a token by special characters (hyphen, underscore, slash)
def split_token(token):
    return re.split(r'[-_/]', token)

# Function to clean and preprocess words (lemmatization)
def preprocess_word(word):
    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphabetic characters except digits
    word = word.lower()  # Convert to lowercase

    # Check if the word is a digit, return it as a word
    if word.isdigit():
        word=num2words(word)
        return word
    
    # Remove words having only 1 character
    if len(word)==1:
        return None
    if word and word not in stop_words:  # Remove stopwords and empty words
        # Perform lemmatization by considering word as a verb
        lemmatized_word = lemmatizer.lemmatize(word, pos="v")
        # Only apply lemmatization as noun if needed
        if (lemmatized_word == word):
            lemmatized_word = lemmatizer.lemmatize(word)
        
        if len(lemmatized_word)==1:  # Check if lemmatized word is a single letter
            return word  # Return the original word if it's a single letter
        
        return lemmatized_word
    return None

# Function to create lexicon
def create_lexicon(article_data):
    lexicon = {}
    word_id_counter = 0
    
    for row in article_data:
        # Combine fields
        article_text = f"{row['title']} {row['tags']} {row['authors']} {row['text']}"
        
        # Tokenize the text
        words = word_tokenize(article_text)
        
        for word in words:
            split_tokens = split_token(word)  # Split token by hyphens, underscores, and slashes
            for sub_token in split_tokens:
                clean_word = preprocess_word(sub_token)
                if clean_word and clean_word not in lexicon:
                    lexicon[clean_word] = word_id_counter
                    word_id_counter += 1
    
    return lexicon


### Main Program
# File path for the CSV (Add path of your 20articles.csv file)
csv_file = r'C:\Users\DELL\Desktop\University\Data Structures and Algorithms\Project\Implementation\Lexicon\20articles.csv'

# Read the CSV file
with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    article_data = csv.DictReader(file)
    # create lexicon
    lexicon = create_lexicon(article_data)

# Save the lexicon to a JSON file (Add path of your lexicon.json file)
lexicon_json_file = r'C:\Users\DELL\Desktop\Search-Engine-DSA\lexicon.json'
with open(lexicon_json_file, 'w', encoding='utf-8') as file:
    json.dump(lexicon, file, ensure_ascii=False, indent=4)

# Confirmatory Message
print("Lexicon creation complete!")
