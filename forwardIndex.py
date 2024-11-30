import json
import csv
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from num2words import num2words
import nltk

# Ensure necessary NLTK resources are downloaded
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Preprocess each word to standardize it for the lexicon
def preprocess_word(word):
    word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Remove non-alphabetic characters except digits
    word = word.lower()  # Convert to lowercase

    # Check if the word is a digit, return it as is if true
    if word.isdigit():
        word = num2words(word)  # Convert number to words
        return word
    
    if len(word) == 1:
        return None  # Ignore single-character words
    
    if word and word not in stop_words:  # Remove stopwords and non-empty words
        # Perform lemmatization by considering word as a verb
        lemmatized_word = lemmatizer.lemmatize(word, pos="v")
        # Only apply general lemmatization if needed
        if lemmatized_word == word:
            lemmatized_word = lemmatizer.lemmatize(word)
        
        if len(lemmatized_word) == 1:  # Check if lemmatized word is a single letter
            return word  # Return the original word if it's a single letter
        
        return lemmatized_word
    return None  # Return None for stopwords and unwanted words

# Function to load the lexicon from a JSON file
def load_lexicon_from_json(filename):
    with open(filename, 'r') as f:
        lexicon = json.load(f)
    return lexicon

# Function to load documents from a CSV file
def load_documents_from_csv(filename):
    documents = {}
    doc_id_counter = 1  # Start document IDs from 1 and increment for each document
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = doc_id_counter  # Assign a numeric document ID
            title = row['title']
            text = row['text']
            authors = row['authors']  # Can be a comma-separated list of authors
            timestamp = row['timestamp']
            tags = row['tags'].split(',')  # Assuming tags are comma-separated
            documents[doc_id] = {
                'title': title,
                'text': text,
                'authors': authors,
                'timestamp': timestamp,
                'tags': tags
            }
            doc_id_counter += 1  # Increment the document ID for the next document
    return documents

# Create the forward index dictionary
forward_index = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))  # [author, title, text, tag]

# Function to process each document and update the forward index
def create_forward_index(documents, lexicon):
    for doc_id, doc in documents.items():
        # Process fields: title, text, authors, tags
        fields = {
            'authors': doc['authors'],
            'title': doc['title'],
            'text': doc['text'],
            'tags': doc['tags']
        }

        # Update hitlist for each word in each field
        for field_index, (field_name, content) in enumerate(fields.items()):
            if field_name == 'tags':
                words = content  # tags is already a list
            else:
                words = content.split()  # Split other fields (title, text, authors) into words

            # Update hitlist for each word in the lexicon
            for word in words:
                processed_word = preprocess_word(word)
                if processed_word:  # If the word is not None (not a stopword)
                    if processed_word in lexicon:
                        word_id = lexicon[processed_word]
                        forward_index[doc_id][word_id][field_index] += 1

# Save the forward index to a JSON file
def save_forward_index_to_json(forward_index, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(forward_index, f, ensure_ascii=False, indent=4)

# Load lexicon and documents from files
lexicon = load_lexicon_from_json('lexicon.json')  # Update path as needed
documents = load_documents_from_csv('20articles.csv')  # Update path as needed

# Populate the forward index with the documents
create_forward_index(documents, lexicon)

# Print the forward index to the console
def print_forward_index(forward_index):
    for doc_id, word_dict in forward_index.items():
        print(f"Document ID: {doc_id}")
        for word_id, hitlist in word_dict.items():
            # Here we will print the word instead of word_id
            word = [w for w, w_id in lexicon.items() if w_id == word_id][0]  # Reverse lookup to get the word from word_id
            print(f"  Word: {word}, Hitlist: {hitlist}")
        print("\n")

print_forward_index(forward_index)  # Print the forward index

# Save the forward index to a JSON file
save_forward_index_to_json(forward_index, 'forward_index.json')

print("Forward index has been saved to 'forward_index.json'.")
