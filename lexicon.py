import csv
import nltk
import string
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data if not already available
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Define the lexicon creation function with lemmatization and punctuation removal
def create_unique_lexicon_with_lemmatization(filename):
    unique_words = set()
    lexicon = {}
    index = 1  # Start index at 1
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    punctuation_table = str.maketrans('', '', string.punctuation)

    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Combine fields and lower-case the text
            combined_text = f"{row['title']} {row['tags']} {row['authors']} {row['text']}".lower()
            
            # Tokenize the text
            words = word_tokenize(combined_text)
            
            for word in words:
                # Remove punctuation, lemmatize, and apply filtering
                clean_word = lemmatizer.lemmatize(word.translate(punctuation_table))
                if clean_word.isalpha() and clean_word not in stop_words:
                    if clean_word not in unique_words:
                        unique_words.add(clean_word)
                        lexicon[clean_word] = index
                        index += 1

    return lexicon

# Function to save lexicon to a JSON file
def save_lexicon_to_json(lexicon, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(lexicon, file, ensure_ascii=False, indent=4)

# Example usage
filename = "20articles.csv"
lexicon = create_unique_lexicon_with_lemmatization(filename)
save_lexicon_to_json(lexicon, "lexicon.json")

# Print lexicon for verification
print("Lexicon saved to lexicon.json:")
for word, idx in lexicon.items():
    print(f"{word}: {idx}")
