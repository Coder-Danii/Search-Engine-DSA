import json
import nltk
import os
import csv
import re
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

import pandas as pd

# Set the standard output encoding to UTF-8 (Windows compatibility)
sys.stdout.reconfigure(encoding='utf-8')

# Download NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize NLTK tools
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Global variables
word_id_counter = 0
doc_id_counter = 0  # Global variable for docs read


# Define weights for each field
weights = {
    'text': 0,
    'authors': 1,
    'tags': 2,
    'title': 3
}

### Helper Functions ###
# Function to split a token by special characters (hyphen, underscore, slash)
def split_token(token):
    return re.split(r'[-_/]', token)

def lemmatize_with_pos(word):
    # Try lemmatizing as verb
    lemmatized_word = lemmatizer.lemmatize(word, pos="v")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as noun
    lemmatized_word = lemmatizer.lemmatize(word, pos="n")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as adjective
    lemmatized_word = lemmatizer.lemmatize(word, pos="a")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as adverb
    lemmatized_word = lemmatizer.lemmatize(word, pos="r")
    return lemmatized_word if lemmatized_word != word else word

# Function to clean and preprocess words (lemmatization)
def preprocess_word(word):

    if word.isdigit():
        return word  # Keep the word as it is if it's all digits

    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphanumeric characters
    word = word.lower()  # Convert to lowercase
    
    # Remove words having only 1 character
    if len(word) == 1 or len(word)>50:
        return None
    if word and word not in stop_words:  # Remove stopwords and empty words
        lemmatized_word=lemmatize_with_pos(word)
        
        if len(lemmatized_word) == 1:  # Check if lemmatized word is a single letter
            return word  # Return the original word if it's a single letter
        
        return lemmatized_word
    return None


def create_hit(field_index, position):
    """Create a hit (word location and reference info)."""
    return [field_index, position]

def load_lexicon(lexicon_json_file):
    """Load the lexicon from a JSON file and return the last wordID."""
    global word_id_counter
    if os.path.exists(lexicon_json_file):
        try:
            with open(lexicon_json_file, 'r', encoding='utf-8') as file:
                lexicon = json.load(file)
                if lexicon:  # Ensure lexicon is not empty
                    word_id_counter = list(lexicon.values())[-1]  # Get the last wordID
                    print(f"The last wordID in the lexicon is: {word_id_counter}")
                    word_id_counter+=1
                return lexicon
        except json.JSONDecodeError:
            print(f"Error reading {lexicon_json_file}. Starting with an empty lexicon.")
    return {}

def load_read_docs(doc_mapper_json):
    """Load the doc mapper from a JSON file and return the last docID."""
    global doc_id_counter
    read_docs = {}
    
    if os.path.exists(doc_mapper_json):
        try:
            with open(doc_mapper_json, 'r', encoding='utf-8') as file:
                read_docs = json.load(file)
                if read_docs:  # Ensure the dictionary is not empty
                    # Get the highest docID from the keys of the dictionary
                    doc_id_counter = list(read_docs.keys())[-1] # get the last docID assigned
                    doc_id_counter = int(doc_id_counter)
                    print(f"The last docID read is: {doc_id_counter}")
                    doc_id_counter+=1
        except json.JSONDecodeError:
            print(f"Error reading {doc_mapper_json}. Starting with no read docs.")
            # If no documents have been read yet, start from 1
    
    return read_docs

def save_lexicon(lexicon, lexicon_file):
    """Save the lexicon to a JSON file."""
    try:
        with open(lexicon_file, 'w', encoding='utf-8') as file:
            json.dump(lexicon, file, ensure_ascii=False)
            print(f"Lexicon saved to {lexicon_file}.")
    except IOError:
        print(f"Error writing to {lexicon_file}.")

def save_doc_mapper(read_docs, docMapper_file):
    """Save the docID to URL mapping to a JSON file."""
    try:
        with open(docMapper_file, 'w', encoding='utf-8') as file:
            json.dump(read_docs, file, ensure_ascii=False, indent=4)
            print(f"Document mapper saved to {docMapper_file}.")
    except IOError:
        print(f"Error writing to {docMapper_file}.")

# Save barrels to CSV
def save_forward_barrels(forward_barrels, barrel_directory):
    """
    Saves the barrel data into separate CSV files for each barrel.
    Each row in the CSV includes: docID, wordID, frequency, hitlist.
    Writes the header only if the file is empty.
    """
    os.makedirs(barrel_directory, exist_ok=True)  # Ensure the directory exists

    for barrel_number, doc_map in forward_barrels.items():
        barrel_file = os.path.join(barrel_directory, f'forward_barrel_{barrel_number}.csv')
        
        # Check if the file is empty or does not exist
        is_new_file = not os.path.exists(barrel_file) or os.path.getsize(barrel_file) == 0

        try:
            with open(barrel_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['docID', 'wordID', 'frequency', 'hitlist'])
                
                if is_new_file:
                    writer.writeheader()  # Write the header only for a new or empty file
                
                for docID, word_hits in doc_map.items():
                    for wordID, hits in word_hits.items():
                        frequency = len(hits)  # Frequency is the number of hits in the list
                        hitlist_str = ";".join([f"{hit[0]}, {hit[1]}" for hit in hits])  # Convert hits to a string
                        writer.writerow({
                            'docID': docID,
                            'wordID': wordID,
                            'frequency': frequency,
                            'hitlist': hitlist_str
                        })

            print(f"Barrel {barrel_number} saved to {barrel_file}.")
        except IOError as e:
            print(f"Error writing to {barrel_file}: {e}")


### Lexicon and Indexing Logic ###
def add_word_to_lexicon(word, lexicon):
    """Add a word to the lexicon if it's new."""
    global word_id_counter
    if word and word not in lexicon:
        lexicon[word] = word_id_counter
        word_id_counter += 1
    return lexicon

def add_word_to_forwardBarrels(docID, wordID, word_hit, forward_barrels):
    # Determine which barrel the word belongs to based on wordID
    barrel_number = wordID // 1000  # Barrel range based on wordID
    wordID = wordID % 1000 
    forward_barrels[barrel_number][docID].setdefault(wordID, []).append(word_hit)  # Add the hit to the barrel

    return forward_barrels

def add_doc_to_docMapper(url, read_docs):
    """Add a new docID and its associated URL to the docMapper if it's new."""
    global doc_id_counter
    
    # Ensure doc_id_counter is an integer
    doc_id_counter = int(doc_id_counter)
    read_docs[doc_id_counter] = url  # Map the new docID to the URL (no need to convert to str)
    doc_id_counter += 1  # Increment doc_id_counter to generate a new docID
    
    return read_docs

def process_article_data(data, lexicon, read_docs, forward_barrels, barrel_directory):
    """
    Process articles and update lexicon, forward index, and barrels.
    Skip articles with URLs already present in read_docs.
    """
    global doc_id_counter  # Ensure doc_id_counter updates only for new documents
    counter = 0  # Initialize the counter outside the loop
    
    
    os.makedirs(barrel_directory, exist_ok=True)  # Ensure the directory exists

    for index, row in data.iterrows():
        url = row['url']  # Extract URL of the article

        # Skip processing if URL is already in the read_docs
        if url in read_docs.values():
            print(f"Skipping already processed URL: {url}")
            continue

        docID = doc_id_counter  # Use the most recently assigned docID

        # Process the title, text, tags, and authors fields
        for field in ['title', 'text', 'tags', 'authors']:
            field_data = str(row[field])
            weight = weights[field]  # Lookup weight here
            tokens = word_tokenize(field_data)
            for position, token in enumerate(tokens):
                split_tokens = split_token(token)
                for split_word in split_tokens:
                    word = preprocess_word(split_word)
                    if word:
                        if word not in lexicon:
                            lexicon = add_word_to_lexicon(word, lexicon)
                        wordID = lexicon[word]
                        hit = create_hit(weight, position)
                        forward_barrels = add_word_to_forwardBarrels(docID, wordID, hit, forward_barrels)


        # Add the document to the docMapper
        read_docs = add_doc_to_docMapper(url, read_docs)

        # Increment the counter
        counter += 1

        # Save and clear forward barrels every 1000 articles
        if counter % 1000 == 0:
            save_forward_barrels(forward_barrels, barrel_directory)
            forward_barrels.clear()

    # Save remaining barrels after processing all articles
    if forward_barrels:
        save_forward_barrels(forward_barrels, barrel_directory)
        forward_barrels.clear()

    print(f"Processed {len(data)} articles.")
    return lexicon, forward_barrels, read_docs




def main():
    dataset_file = r'C:\Users\DELL\Desktop\articles\20articles.csv'
    lexicon_file = r'lexicon.json'
    docMapper_file = r'docmapper.json'
    barrel_directory = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'
    
    article_data = pd.read_csv(dataset_file, encoding='utf-8')  # Ensure UTF-8 encoding
    
    # Load the lexicon, forward index, and docMapper
    lexicon = load_lexicon(lexicon_file)
    read_docs = load_read_docs(docMapper_file)
    forward_barrels = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # Barrels dictionary to store wordID and hits by docID
    

    # Process the articles and update lexicon, forward index, and barrels
    lexicon, barrels, read_docs = process_article_data(article_data, lexicon, read_docs, forward_barrels, barrel_directory)
    
    # Save the updated lexicon, forward index, and barrels
    save_lexicon(lexicon, lexicon_file)
    save_doc_mapper(read_docs, docMapper_file)

    print("Processing complete! Lexicon, forward barrels updated.")

if __name__ == "__main__":
    main()

