from lexicon_plus_barrels import preprocess_word
import csv
import json

query_word = "red"
lexicon_path = "lexicon.json"  # Update this path to the actual lexicon JSON file

def get_word_id(query_word, lexicon_path):
    """ Processes a query word, lemmatizes it, and retrieves its word ID from the lexicon. Returns wordID"""
    # Load the lexicon from the JSON file
    with open(lexicon_path, 'r') as file:
        lexicon = json.load(file)

    # Preprocess the query word
    processed_word = preprocess_word(query_word)
    
    if processed_word is not None:
        # Search for the processed word in the lexicon
        word_id = lexicon.get(processed_word)
        return word_id
    
    return None


def find_related_inverted_barrel(wordID):
    # Determine the file name based on the wordID range
    barrel_number = (wordID // 1000)  # This gives us the 2nd digit of the wordID, which corresponds to the barrel number
    file_name = f'inverted_barrel_{barrel_number}.csv'

    # List to hold the results
    results = []

    try:
        # Open the corresponding barrel CSV file
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header
            
            # Search for the wordID and collect documents and hitlists
            for row in reader:
                if int(row[0]) == (wordID % 1000):
                    docIDs = row[1].split(';')
                    hitlists = row[3].split(';')
                    results.append((docIDs, hitlists))

    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

    return results

    
# Example usage
if __name__ == "__main__":
    word_id = get_word_id(query_word, lexicon_path)
    if word_id is not None:
        print(f"Word ID for '{query_word}': {word_id}")
        
        # Now find the related documents and hitlists from the barrel file
        related_results = find_related_inverted_barrel(word_id)
        if related_results:
            print(f"Related documents and hitlists for word ID {word_id}:")
            for doc_ids, hitlists in related_results:
                print(f"Doc IDs: {doc_ids}")
                print(f"Hitlists: {hitlists}")
        else:
            print(f"No related results found for word ID {word_id}.")
    else:
        print(f"Word '{query_word}' not found in the lexicon.")
