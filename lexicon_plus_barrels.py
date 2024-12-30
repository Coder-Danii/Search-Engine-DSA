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

sys.stdout.reconfigure(encoding='utf-8')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Global variables
word_id_counter = 0
doc_id_counter = 0

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

# Function to lemmatize a word based on its part of speech (POS)
def lemmatize_with_pos(word):
    lemmatized_word = lemmatizer.lemmatize(word, pos="v")
    if lemmatized_word != word:
        return lemmatized_word

    lemmatized_word = lemmatizer.lemmatize(word, pos="n")
    if lemmatized_word != word:
        return lemmatized_word
    
    lemmatized_word = lemmatizer.lemmatize(word, pos="a")
    if lemmatized_word != word:
        return lemmatized_word

    lemmatized_word = lemmatizer.lemmatize(word, pos="r")
    return lemmatized_word if lemmatized_word != word else word

# Function to clean and preprocess words
def preprocess_word(word):
    if word.isdigit():
        return word  # Keep the word as it is if it's all digits

    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphanumeric characters
    word = word.lower()  # Convert to lowercase
    
    # Remove words having only 1 character or > 50 characters
    if len(word) == 1 or len(word) > 50:
        return None
    if word and word not in stop_words:  # Remove stopwords and empty words
        lemmatized_word = lemmatize_with_pos(word)
        
        if len(lemmatized_word) == 1:
            return word  # Return the original word if after lematization it is a single word
        
        return lemmatized_word
    return None


### Loading Files Methods ###
# Function to load lexicon in memory
def load_lexicon(lexicon_json_file):
    global word_id_counter
    if os.path.exists(lexicon_json_file):
        try:
            with open(lexicon_json_file, 'r', encoding='utf-8') as file:
                lexicon = json.load(file)
                if lexicon:  # Ensure lexicon is not empty
                    word_id_counter = list(lexicon.values())[-1]  # Get the last wordID
                    print(f"The last wordID in the lexicon is: {word_id_counter}")
                    word_id_counter += 1
                return lexicon
        except json.JSONDecodeError:
            print(f"{lexicon_json_file}. Starting with an empty lexicon.")
    return {}

# Function to load the docID to URL mapping in memory
def load_read_docs(doc_mapper_json):
    global doc_id_counter
    read_docs = {}
    
    if os.path.exists(doc_mapper_json):
        try:
            with open(doc_mapper_json, 'r', encoding='utf-8') as file:
                read_docs = json.load(file)
                if read_docs:
                    doc_id_counter = list(read_docs.keys())[-1]  # get the last docID assigned
                    print("cn dhokaa")
                    doc_id_counter = int(doc_id_counter)
                    print(f"The last docID read is: {doc_id_counter}")
                    doc_id_counter += 1
        except json.JSONDecodeError:
            print(f"{doc_mapper_json}. Starting with no read docs.")
    
    return read_docs


### Saving Files Methods ###

# Save lexicon in the json file
def save_lexicon(lexicon, lexicon_file):
    try:
        with open(lexicon_file, 'w', encoding='utf-8') as file:
            json.dump(lexicon, file, ensure_ascii=False)
            print(f"Lexicon saved to {lexicon_file}.")
    except IOError:
        print(f"Error writing to {lexicon_file}.")


# Save docMapper in the json file
def save_doc_mapper(read_docs, docMapper_file):
    try:
        with open(docMapper_file, 'w', encoding='utf-8') as file:
            json.dump(read_docs, file, ensure_ascii=False)
            print(f"Document mapper saved to {docMapper_file}.")
    except IOError:
        print(f"Error writing to {docMapper_file}.")

# Save barrels to CSV
def save_forward_barrels(forward_barrels, barrel_directory):
    
    os.makedirs(barrel_directory, exist_ok=True)

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

# Function to create a hit (field_index, position) for a word
def create_hit(field_index, position):
    return [field_index, position]

def add_word_to_forwardBarrels(docID, wordID, word_hit, forward_barrels):
    # Determine which barrel the word belongs to based on wordID
    barrel_number = wordID // 1000  # Barrel range based on wordID
    wordID = wordID % 1000 
    forward_barrels[barrel_number][docID].setdefault(wordID, []).append(word_hit)  # Add the hit to the barrel

    return forward_barrels

# Add docIID : url mapping
def add_doc_to_docMapper(url, read_docs):
    global doc_id_counter
    print("cn dhoka anoosheh ")
    doc_id_counter = int(doc_id_counter)
    read_docs[doc_id_counter] = url
    doc_id_counter += 1  # Increment doc_id_counter to generate a new docID
    
    return read_docs



### Actual Indexer method that creates lexicon and forward barrels
def process_article_data(data, lexicon, read_docs, barrel_directory):
    
    global doc_id_counter
    counter = 0  # Initialize the counter for no. of docs processed
    
    forward_barrels = defaultdict(lambda: defaultdict(lambda: defaultdict(list))) 
    updated_forward_barrels = set()  # set to track updated forward barrels
    
    os.makedirs(barrel_directory, exist_ok=True)

    for index, row in data.iterrows():
        
        url = row['url']
        
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
            updated_forward_barrels.update(forward_barrels.keys())  # Track updated barrels
            forward_barrels.clear()

    # Save remaining barrels after processing all articles
    if forward_barrels:
        save_forward_barrels(forward_barrels, barrel_directory)
        updated_forward_barrels.update(forward_barrels.keys())  # Track updated barrels
        forward_barrels.clear()

    print(f"Processed {len(data)} articles.")
    return lexicon, read_docs, updated_forward_barrels
