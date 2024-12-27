import csv
from sortedcontainers import SortedList
import lexicon_plus_barrels as lb
import threading as th
import ranking as rk
import json

def get_results(query, lexicon_path):
    query_tokens = []
    for word in query.split():
        tokenized_words = lb.split_token(word)  # Tokenize each word
        for token in tokenized_words:
            processed_word = lb.preprocess_word(token)  # Preprocess each token
            if processed_word is not None:
                query_tokens.append(processed_word)
            else:
                print(f"Error: Query word '{token}' could not be processed.")
                return None

    print("Processed tokens:", query_tokens)
    
    words = {}
    threads = []
    
    # Retrieve documents for each word in parallel
    for word in query_tokens:
        this_thread = th.Thread(target=retrieve_word_docs, args=(word, lexicon_path, words))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    # Compute intersections for all retrieved document lists
    doc_lists = [docs for docs in words.values() if docs]  # Only include non-empty doc lists
    intersections = rk.compute_intersections(doc_lists)

    # Rank documents for each word based on intersections
    ranked_docs = []
    for docs in words.values():
        if docs:
            ranked_docs.extend(rk.rank_documents(docs, intersections))

    # Remove duplicates from ranked documents (based on doc_id)
    result_docs_set = set()
    unique_result_docs = []
    for score, doc_id in ranked_docs:
        if doc_id not in result_docs_set:
            unique_result_docs.append((score, doc_id))
            result_docs_set.add(doc_id)

    # Sort documents by their score in descending order (highest score first)
    sorted_docs = sorted(unique_result_docs, key=lambda x: -x[0])  # Sort by score in descending order

    # Get detailed document info for each sorted document
    results = []
    threads = []

    for score, doc_id in sorted_docs:
        this_thread = th.Thread(target=retrieve_doc_info, args=(doc_id, results))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    # Display the sorted documents
    print("Sorted results (by relevance):")
    for idx, result in enumerate(results):
        print(f"Rank {idx + 1}: {result}")

    return results, len(sorted_docs)


# Function to retrieve word documents from lexicon and inverted barrel files
def retrieve_word_docs(word, lexicon_path, words):
    try:
        # Load the lexicon from the JSON file
        with open(lexicon_path, 'r') as file:
            lexicon = json.load(file)

        # Retrieve the word ID from the lexicon
        word_id = lexicon.get(word)
        if word_id is None:
            print(f"Error: Word '{word}' not found in lexicon.")
            return

        # Determine the inverted barrel file name
        barrel_number = (word_id // 1000)  # Determine the barrel number
        file_name = f"inverted_barrels/inverted_barrel_{barrel_number}.csv"

        # List to store results
        results = []

        # Open and search the corresponding inverted barrel file
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header

            for row in reader:
                if int(row[0]) == (word_id % 1000):
                    doc_ids = row[1].split(';')
                    hitlists = row[3].split(';')
                    results.append((doc_ids, hitlists))

        # Store results in the words dictionary
        words[word] = results

    except FileNotFoundError:
        print(f"Error: Inverted barrel file not found.")
    except Exception as e:
        print(f"Error: {str(e)}")


# Function to retrieve detailed document info (for example, metadata, content)
def retrieve_doc_info(doc_id, results):
    # Implement the logic for retrieving document information (e.g., title, content)
    # For this example, it's just a placeholder
    results.append(f"Document {doc_id} info retrieved.")


if __name__ == "__main__":
    query_word = "health mental"
    lexicon_path = "lexicon.json"  # Update this path to the actual lexicon JSON file

    results, total_docs = get_results(query_word, lexicon_path)
    if results:
        print(f"\nTotal results for '{query_word}': {total_docs}")
    else:
        print("No results found.")
