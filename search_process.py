import csv
#from sortedcontainers import SortedList
import lexicon_plus_barrels as lb
import threading as th
import ranking as rk
import json
import inverted_barrels as ib
import sys

# Increase the CSV field size limit
csv.field_size_limit(10**7)

def get_results(query, lexicon):
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
        this_thread = th.Thread(target=retrieve_word_docs, args=(word, lexicon, words))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    # Compute intersections for all retrieved document lists
    doc_lists = [docs for docs in words.values() if docs]  # Only include non-empty doc lists
    intersections = rk.intersect(doc_lists)

    # Rank documents for each word based on intersections
    ranked_docs = []
    for docs in words.values():
        if docs:
            ranked_docs.extend(rk.rank_docs(docs, intersections))

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
def retrieve_word_docs(word, lexicon, words):
    try:
        
        # Retrieve the word ID from the lexicon
        word_id = lexicon.get(word)
        if word_id is None:
            print(f"Error: Word '{word}' not found in lexicon.")
            return

        # Load offsets from the binary offset file
        barrel_number = word_id // 1000
        offset_file = r'C:\\Users\\DELL\\Desktop\\Search-Engine-DSA\\offset_barrels\\inverted_barrel_{}.bin'.format(barrel_number)
        
        offsets = ib.load_offsets(offset_file)  # Load all offsets from the binary file

        # Determine the barrel number from the word ID and locate the corresponding CSV file
        file_name = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels\inverted_barrel_{}.csv'.format(barrel_number)
        # Find the offset for the word ID
        offset = offsets[word_id % 1000]  # Get the offset for the specific word

        # Open the barrel file and seek to the offset
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            file.seek(offset)  # Seek to the position in the file where the data for this word starts

            # Read the corresponding line for the word
            reader = csv.reader(file)
            row = next(reader)  # This should be the line for the word

            # Extract document IDs and hitlist strings
            doc_ids = row[1].split('|')  # Split doc IDs by '|'
            hitlists = row[3].split('|')  # Split hitlists by '|'

            # Each doc_id corresponds to a hitlist, parse them as needed
            parsed_results = []
            for doc_id, hitlist in zip(doc_ids, hitlists):
                hits = hitlist.split(';')  # Split each hitlist by ';'
                parsed_hits = [tuple(map(int, hit.split(','))) for hit in hits]  # Convert each hit to a tuple of (hit_type, position)
                parsed_results.append((doc_id, parsed_hits))  # Append the document ID and its corresponding hit list

            # Store results in the words dictionary, keyed by the word
            words[word] = parsed_results

    except FileNotFoundError:
        print(f"Error: Inverted barrel file '{file_name}' or offset file '{offset_file}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")



# Function to retrieve detailed document info (for example, metadata, content)
def retrieve_doc_info(doc_id, results):
    # Implement the logic for retrieving document information (e.g., title, content)
    # For this example, it's just a placeholder
    results.append(f"Document {doc_id} info retrieved.")


if __name__ == "__main__":
    lexicon_path = "lexicon.json"  # Update this path to the actual lexicon JSON file
    lexicon= lb.load_lexicon(lexicon_path)
    query_word = "mental"
    
    results, total_docs = get_results(query_word, lexicon)
    if results:
        print(f"\nTotal results for '{query_word}': {total_docs}")
    else:
        print("No results found.")
