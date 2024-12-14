import json
import nltk
import os
import csv
import re
from collections import defaultdict
from num2words import num2words
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from decimal import Decimal
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

# Global variables
word_id_counter = 0
doc_id_counter = 0  # Global variable for docs read


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
    # Check if the word ends with a domain suffix (e.g., .com, .org, .net)
    match= re.search(r'^(.+\..+\.(com|net|org)).*', word)
    if match:
        return match.group(1)

    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphabetic characters except digits
    word = word.lower()  # Convert to lowercase

    # Check if the word is a digit, return it as a word
    if word.isdigit():
        num = Decimal(word)  # Convert to a Decimal object for comparison
        MAX_VALUE = Decimal("1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        # Skip the number if it exceeds the maximum value
        if num > MAX_VALUE:
            return None
        
        # Convert number to words if it's within the limit
        word = num2words(word)
        return word
    
    # Remove words having only 1 character
    if len(word) == 1 or len(word)>50:
        return None
    if word and word not in stop_words:  # Remove stopwords and empty words
        lemmatized_word=lemmatize_with_pos(word)
        
        if len(lemmatized_word) == 1:  # Check if lemmatized word is a single letter
            return word  # Return the original word if it's a single letter
        
        return lemmatized_word
    return None


def create_hit(word_id, field_index, is_reference, position):
    """Create a hit (word location and reference info)."""
    return [field_index, is_reference, position]

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
                    doc_id_counter = list(read_docs.keys())[-1]  # get the last docID assigned
                    print(f"The last docID read is: {doc_id_counter}")
        except json.JSONDecodeError:
            print(f"Error reading {doc_mapper_json}. Starting with no read docs.")
    
    return read_docs

def load_forward_index(forward_index_json_file):
    """Load the forward index from a JSON file."""
    forward_index = defaultdict(lambda: defaultdict(list))  # Nested defaultdict to store word hits
    if os.path.exists(forward_index_json_file):
        try:
            with open(forward_index_json_file, 'r', encoding='utf-8') as file:
                forward_index_data = json.load(file)
                # Populate forward_index with the loaded data
                for docID, word_data in forward_index_data.items():
                    for wordID, hits in word_data.items():
                        forward_index[docID][wordID] = hits
        except json.JSONDecodeError:
            print(f"Error reading {forward_index_json_file}. Starting with an empty forward index.")
    return forward_index


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


def save_forward_index(forward_index, filename):
    """Save the forward index to a JSON file with hit count."""
    simplified_forward_index = defaultdict(dict)
    for doc_id, word_dict in forward_index.items():
        simplified_forward_index[doc_id] = {}
        for word_id, hits in word_dict.items():
            simplified_forward_index[doc_id][word_id] = [len(hits)] + hits  # First item is the count of hits

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(simplified_forward_index, f, ensure_ascii=False, indent=4)
            print(f"Forward index saved to {filename}.")
    except IOError:
        print(f"Error writing to {filename}.")


### Lexicon and Indexing Logic ###
def add_word_to_lexicon(word, lexicon):
    """Add a word to the lexicon if it's new."""
    global word_id_counter
    if word and word not in lexicon:
        word_id_counter += 1
        lexicon[word] = word_id_counter
    return lexicon

def add_doc_to_docMapper(url, read_docs):
    """Add a new docID and its associated URL to the docMapper if it's new."""
    global doc_id_counter
    
    # Ensure doc_id_counter is an integer
    doc_id_counter = int(doc_id_counter)
    
    doc_id_counter += 1  # Increment doc_id_counter to generate a new docID
    read_docs[doc_id_counter] = url  # Map the new docID to the URL (no need to convert to str)
    return read_docs


def add_word_to_forwardIndex(docID, wordID, word_hit, forward_index):
    """Add a word hit to the forward index."""
    forward_index[docID].setdefault(wordID, []).append(word_hit)
    return forward_index

def process_article_data(article_data, lexicon, forward_index, read_docs):
    """Process articles and update lexicon and forward index."""
    
    for docID, row in enumerate(article_data, start=int(doc_id_counter)):
        
        # Convert url to string without wrapping it in a list
        url = (row['url'])
        
        # Skip processing if URL is already in the read_docs
        if url in read_docs.values():
            print("Skipping already processed URL:", url)
            continue
        
        # Add the document to the docMapper
        read_docs = add_doc_to_docMapper(url, read_docs)
        
        fields = [('authors', row['authors']), ('title', row['title']), ('text', row['text']), ('tags', row['tags'])]
        
        for field_index, (field_name, content) in enumerate(fields):
            if field_name == 'tags':
                # Split tags by commas or other delimiters
                tags = content.split(',')  # Split tags by commas
                tags = [tag.strip() for tag in tags]  # Remove extra spaces
                words = []
                for tag in tags:
                # Split individual tags into words
                    words.extend(tag.split())  # Split by spaces within each tag
            else:
                words = content.split()  # Split non-tag fields by spaces
            for position, word in enumerate(words):
                split_tokens = split_token(word)
                for sub_token in split_tokens:
                    clean_word = preprocess_word(sub_token)  # Ensure consistent preprocessing
                    if clean_word:
                        lexicon = add_word_to_lexicon(clean_word, lexicon)
                        wordID = lexicon.get(clean_word)
                        
                        # Check if the word is a reference (URL)
                        is_reference = 0
                        match = re.search(r'^(.+\..+\.(com|net|org))$', clean_word)
                        if match:
                            is_reference = 1
                        
                        # Create the hit and add to forward index
                        hit = create_hit(wordID, field_index, is_reference, position)
                        forward_index = add_word_to_forwardIndex(docID, wordID, hit, forward_index)

    print(f"Processed {len(article_data)} articles.")
    return lexicon, forward_index, read_docs


### Main Program ###
def main():
    dataset_file = r'C:\Users\DELL\Desktop\20articles.csv'
    lexicon_file = r'C:\Users\DELL\Desktop\Search-Engine-DSA\lexicon.json'
    forwardIndex_file = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_index.json'
    docMapper_file= r'C:\Users\DELL\Desktop\Search-Engine-DSA\doc_mapper.json'

    # Read CSV file and process the remaining articles
    with open(dataset_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for _ in range(doc_id_counter):
            next(reader)  # Skip processed rows
        article_data = list(reader)  # Read remaining rows into article_data

    # Process the articles and update lexicon and forward index
    lexicon = load_lexicon(lexicon_file)
    forward_index = defaultdict(lambda: defaultdict(list))  # Nested dictionary to store word hits
    forward_index = load_forward_index(forwardIndex_file)
    read_docs = load_read_docs(docMapper_file)
    lexicon, forward_index, read_docs = process_article_data(article_data, lexicon, forward_index, read_docs)
    
    # Save the updated lexicon and forward index
    save_lexicon(lexicon, lexicon_file)
    save_forward_index(forward_index, forwardIndex_file)
    save_doc_mapper(read_docs, docMapper_file)

    print("Processing complete! Lexicon and forward index updated.")

if __name__ == '__main__':
    main()
