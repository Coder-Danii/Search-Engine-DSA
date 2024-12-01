import json
import nltk
import os
import csv
import re
from num2words import num2words
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import sys

# Set the standard output encoding to UTF-8 (Windows compatibility)
sys.stdout.reconfigure(encoding='utf-8')

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
    # Check if the word ends with a domain suffix (e.g., .com, .org, .net)
    if re.search(r'\.com$|\.org$|\.net$', word):  
        return word

    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphabetic characters except digits
    word = word.lower()  # Convert to lowercase

    # Check if the word is a digit, return it as a word
    if word.isdigit():
        word = num2words(word)
        return word
    
    # Remove words having only 1 character
    if len(word) == 1:
        return None
    if word and word not in stop_words:  # Remove stopwords and empty words
        # Perform lemmatization by considering word as a verb
        lemmatized_word = lemmatizer.lemmatize(word, pos="v")
        # Only apply lemmatization as noun if needed
        if lemmatized_word == word:
            lemmatized_word = lemmatizer.lemmatize(word)
        
        if len(lemmatized_word) == 1:  # Check if lemmatized word is a single letter
            return word  # Return the original word if it's a single letter
        
        return lemmatized_word
    return None

# Method to get docs_read_lexicon and last_wordID from tracker.json
def get_docs_read_and_last_wordID(track_file):
    docs_read_lexicon, last_wordID = 0, 0  # Default values if the file does not exist or is empty

    if os.path.exists(track_file) and os.stat(track_file).st_size > 0:
        try:
            with open(track_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                docs_read_lexicon = data.get('docs_read_lexicon', 0)
                last_wordID = data.get('last_wordID', 0)
        except json.JSONDecodeError:
            print(f"Error reading or parsing {track_file}. Returning defaults.")
    return docs_read_lexicon, last_wordID

# Method to update the file that keeps track of the last doc read and last wordID
def update_track_file(track_file, docs_read_lexicon, last_wordID):
    data = {'docs_read_lexicon': docs_read_lexicon, 'last_wordID': last_wordID}
    try:
        with open(track_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError:
        print(f"Error writing to {track_file}.")

# Function to load existing lexicon from file
def load_lexicon(lexicon_json_file):
    lexicon = {}
    if os.path.exists(lexicon_json_file):
        try:
            with open(lexicon_json_file, 'r', encoding='utf-8') as file:
                lexicon = json.load(file)
        except json.JSONDecodeError:
            print(f"Error reading or parsing {lexicon_json_file}. Starting with an empty lexicon.")
    return lexicon

# Function to create lexicon and append to existing lexicon
def create_lexicon(article_data, last_wordID, docs_read_lexicon, lexicon_file):
    lexicon = load_lexicon(lexicon_file)
    word_id_counter = last_wordID

    for row in article_data:
        # Combine fields into a single text block
        article_text = f"{row['title']} {row['tags']} {row['authors']} {row['text']}"

        # Tokenize the text
        words = word_tokenize(article_text)

        for word in words:
            split_tokens = split_token(word)  # Split token by hyphens, underscores, and slashes
            for sub_token in split_tokens:
                clean_word = preprocess_word(sub_token)
                if clean_word and clean_word not in lexicon:
                    lexicon[clean_word] = word_id_counter
                    word_id_counter += 1  # Increment word ID only when a new word is added

        # Increment docs_read counter after processing each article
        docs_read_lexicon += 1

    return docs_read_lexicon, word_id_counter, lexicon


### Main Program ###

# File paths (update these as per your directory structure)
csv_file = r'20articles_test.csv'
lexicon_json_file = r'Search-Engine-DSA\lexicon.json'
track_file = r'Search-Engine-DSA\tracker.json'

# Get current docs_read and last_wordID from tracker.json
docs_read_lexicon, last_wordID = get_docs_read_and_last_wordID(track_file)

# Open the CSV file and read it
with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    # Skip already processed rows based on docs_read_lexicon
    for _ in range(docs_read_lexicon):
        next(reader)

    article_data = list(reader)  # Read the remaining rows into article_data

    # Create lexicon and append new words to it
    docs_read_lexicon, word_id_counter, lexicon = create_lexicon(article_data, last_wordID, docs_read_lexicon, lexicon_json_file)

# Write the updated lexicon to the file
try:
    with open(lexicon_json_file, 'w', encoding='utf-8') as file:
        json.dump(lexicon, file, ensure_ascii=False, indent=4)
except IOError:
    print(f"Error writing to {lexicon_json_file}.")

# Update tracker.json with the latest docs_read_lexicon and last_wordID
update_track_file(track_file, docs_read_lexicon, word_id_counter)

# Confirmatory message
print("Lexicon creation and appending complete!")
