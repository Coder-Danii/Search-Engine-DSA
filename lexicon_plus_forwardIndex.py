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
docs_read_lexicon = 0  # Global variable for docs read


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
    print(word)
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
    if len(word) == 1:
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


### File Operations ###
def get_docs_read_and_last_wordID(track_file):
    """Retrieve docs_read_lexicon and last_wordID from the tracker file."""
    global docs_read_lexicon, word_id_counter
    if os.path.exists(track_file) and os.stat(track_file).st_size > 0:
        try:
            with open(track_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                docs_read_lexicon = data.get('docs_read_lexicon', 0)
                word_id_counter = data.get('last_wordID', 0)
        except json.JSONDecodeError:
            print(f"Error reading {track_file}. Using defaults.")


def update_track_file(track_file):
    """Update the tracker file with current doc and word ID states."""
    global docs_read_lexicon
    data = {'docs_read_lexicon': docs_read_lexicon, 'last_wordID': word_id_counter}
    try:
        with open(track_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
    except IOError:
        print(f"Error writing to {track_file}.")


def load_lexicon(lexicon_json_file):
    """Load the lexicon from a JSON file."""
    if os.path.exists(lexicon_json_file):
        try:
            with open(lexicon_json_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error reading {lexicon_json_file}. Starting with an empty lexicon.")
    return {}

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


def save_lexicon(lexicon, lexicon_json_file):
    """Save the lexicon to a JSON file."""
    try:
        with open(lexicon_json_file, 'w', encoding='utf-8') as file:
            json.dump(lexicon, file, ensure_ascii=False)
            print(f"Lexicon saved to {lexicon_json_file}.")
    except IOError:
        print(f"Error writing to {lexicon_json_file}.")


def save_forward_index_to_json(forward_index, filename):
    """Save the forward index to a JSON file with hit count."""
    simplified_forward_index = defaultdict(dict)
    for doc_id, word_dict in forward_index.items():
        simplified_forward_index[doc_id] = {}
        for word_id, hits in word_dict.items():
            simplified_forward_index[doc_id][word_id] = [len(hits)] + hits  # First item is the count of hits

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(simplified_forward_index, f, ensure_ascii=False)
            print(f"Forward index saved to {filename}.")
    except IOError:
        print(f"Error writing to {filename}.")


### Lexicon and Indexing Logic ###
def add_word_to_lexicon(word, lexicon):
    """Add a word to the lexicon if it's new."""
    global word_id_counter
    if word and word not in lexicon:
        lexicon[word] = word_id_counter
        word_id_counter += 1
    return lexicon



def add_word_to_forward_index(docID, wordID, word_hit, forward_index):
    """Add a word hit to the forward index."""
    forward_index[docID].setdefault(wordID, []).append(word_hit)
    return forward_index

def process_article_data(article_data, lexicon_file, forward_file):
    """Process articles and update lexicon and forward index."""
    global docs_read_lexicon
    lexicon = load_lexicon(lexicon_file)
    forward_index = defaultdict(lambda: defaultdict(list))  # Nested dictionary to store word hits
    forward_index=load_forward_index(forward_file)

    for docID, row in enumerate(article_data, start=docs_read_lexicon):
        fields = [('authors', row['authors']), ('title', row['title']), ('text', row['text']), ('tags', row['tags'])]

        for field_index, (field_name, content) in enumerate(fields):
            words = content.split() if field_name != 'tags' else content  # Split content for non-tag fields

            for position, word in enumerate(words):
                split_tokens = split_token(word)
                for sub_token in split_tokens:
                    clean_word = preprocess_word(sub_token) # Ensure consistent preprocessing
                    if clean_word:

                        lexicon = add_word_to_lexicon(clean_word, lexicon)
                        wordID = lexicon.get(clean_word)
                        # Check if the word is a reference (URL)
                        is_reference = 0
                        match = re.search(r'^(.+\..+\.(com|net|org))$', clean_word)
                        if match:
                            is_reference = 1
                        hit = create_hit(wordID, field_index, is_reference, position)
                        forward_index = add_word_to_forward_index(docID, wordID, hit, forward_index)

        docs_read_lexicon += 1

    print(f"Processed {len(article_data)} articles.")
    return lexicon, forward_index

### Main Program ###
def main():
    csv_file = r'C:\Users\DELL\Desktop\University\Data Structures and Algorithms\Project\Medium Articles\medium_articles.csv'
    lexicon_json_file = r'Search-Engine-DSA\lexicon.json'
    forward_json_file = r'Search-Engine-DSA\forward_index.json'
    track_file = r'Search-Engine-DSA\tracker.json'

    get_docs_read_and_last_wordID(track_file)

    # Read CSV file and process the remaining articles
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for _ in range(docs_read_lexicon):
            next(reader)  # Skip processed rows
        article_data = list(reader)  # Read remaining rows into article_data

    # Process the articles and update lexicon and forward index
    lexicon, forward_index = process_article_data(article_data, lexicon_json_file, forward_json_file)

    # Save the updated lexicon and forward index
    save_lexicon(lexicon, lexicon_json_file)
    save_forward_index_to_json(forward_index, forward_json_file)

    # Update the tracker file
    update_track_file(track_file)

    print("Processing complete! Lexicon and forward index updated.")

if __name__ == '__main__':
    main()
