from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
import csv
import pandas as pd
import threading as th
import lexicon_plus_barrels as lb
import ranking as rk
import json
import inverted_barrels as ib
from flask_cors import CORS
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import file_paths as file
import os
import file_paths
import index_new_doc as scraping

lemmatizer = WordNetLemmatizer()
lb.preprocess_word('apple')

global scraped_articles_df  # Declare as global at the beginning

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Paths for files
docmapper_path = r"C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\docmapper.json"
csv_file_path = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\medium_articles.csv' 
scraped_articles_path = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\scraped_medium_articles.csv'
# Load docmapper.json once during initialization
with open(docmapper_path, 'r', encoding='utf-8') as docmapper_file:
    doc_mapper = json.load(docmapper_file)

# Load the CSV file containing document details
try:
    documents_df = pd.read_csv(csv_file_path, delimiter=',', quotechar='"')
    documents_df.set_index('url', inplace=True)
except pd.errors.ParserError as e:
    print(f"Error reading CSV file: {e}")
    # Handle the error appropriately, e.g., log it, raise an exception, etc.

# Increase the CSV field size limit
csv.field_size_limit(10**7)
lexicon = lb.load_lexicon(file.lexicon_file)

# Load the scraped articles CSV file
try:
    scraped_articles_df = pd.read_csv(scraped_articles_path, delimiter=',', quotechar='"')
    scraped_articles_df.set_index('docID', inplace=True)
    scraped_articles_df.index = scraped_articles_df.index.astype(int)  # Ensure docID is integer
except FileNotFoundError:
    print(f"File not found: {scraped_articles_path}")
    scraped_articles_df = pd.DataFrame()  # Create an empty DataFrame to avoid further errors
except pd.errors.ParserError as e:
    print(f"Error reading scraped articles CSV file: {e}")
    # Handle the error appropriately, e.g., log it, raise an exception, etc.

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "Query is required."}), 400

    try:
        results, total_docs, tags = get_results(query)
        return jsonify({
            "total_results": total_docs,
            "results": results,
            "tags": tags
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Process query tokens
def process_query(query):
    query_tokens = word_tokenize(query)
    processed_tokens = []

    for word in query_tokens:
        tokenized_words = lb.split_token(word)
        for token in tokenized_words:
            processed_word = lb.preprocess_word(token)
            if processed_word:
                processed_tokens.append(processed_word)

    return processed_tokens


# Get search results
def get_results(query):
    global lexicon
    
    query_tokens = process_query(query)

    if not query_tokens:
        raise ValueError("Query is empty")

    words = {}
    
    # Use a thread pool to retrieve documents for each word in parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(retrieve_word_docs, word, words) for word in query_tokens]
        for future in futures:
            future.result()

    # Compute intersections for all retrieved document lists
    doc_lists = [docs for docs in words.values() if docs]
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

    sorted_docs = sorted(unique_result_docs, key=lambda x: -x[0])

    # Get detailed document info for each sorted document
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(retrieve_doc_info, doc_id) for score, doc_id in sorted_docs]
        for future in futures:
            results.append(future.result())

    all_tags = set()
    for result in results:
        tags = result.get("tags", "")
        if isinstance(tags, str):
            tags = tags.split(",")
        all_tags.update(str(tag).strip() for tag in tags if str(tag).strip())

    return results, len(sorted_docs), list(all_tags)

# Retrieve word document details
def retrieve_word_docs(word, words):
    global lexicon
    try:
        word_id = lexicon.get(word)
        if word_id is None:
            return

        barrel_number = word_id // 1000
        offset_file = f'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\offset_barrels\\inverted_barrel_{barrel_number}.bin'
        offsets = ib.load_offsets(offset_file)

        file_name = f'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\inverted_barrels\\inverted_barrel_{barrel_number}.csv'
        offset = offsets[word_id % 1000]

        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            file.seek(offset)
            reader = csv.reader(file)
            row = next(reader)
            doc_ids = row[1].split('|')
            frequencies = row[2].split('|')
            hitlists = row[3].split('|')

            parsed_results = []
            for doc_id, frequency, hitlist in zip(doc_ids, frequencies, hitlists):
                hits = hitlist.split(';')
                parsed_hits = [tuple(map(int, hit.split(','))) for hit in hits]
                parsed_results.append((doc_id, parsed_hits, int(frequency)))

            words[word] = parsed_results

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error: {str(e)}")

# Retrieve document info
def retrieve_doc_info(doc_id, results):
    global scraped_articles_df  # Declare as global
    try:
        # Convert doc_id to integer
        doc_id = int(doc_id)
        
        if doc_id in scraped_articles_df.index:
            doc_details = scraped_articles_df.loc[doc_id].to_dict()
            results.append({
            "doc_id": doc_id,
            "title": sanitize_value(doc_details.get('title', 'Unknown Title')),
            "text": sanitize_value(doc_details.get('first_two_lines', 'No Content Available')),
            "url": sanitize_value(doc_details.get('url', 'Unknown URL')),
            "authors": "Disney",
            "timestamp": sanitize_value(doc_details.get('timestamp', 'Unknown Timestamp')),
            "tags": sanitize_value(doc_details.get('tags', 'No Tags'))
        })
    except Exception as e:
        pass
def sanitize_value(value, default_value='Unknown'):
    # Check if the value is NaN or null (as strings) and return the default_value
    if isinstance(value, str) and (value.lower() == "nan" or value.lower() == "null"):
        return default_value
    # Return the original value if it's not NaN or null
    return value or default_value
@app.route('/addDocument', methods=['POST'])
def add_document():
    try:
        data = request.json
        required_fields = ['title', 'text', 'url', 'authors', 'timestamp', 'tags']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        if data['url'] in doc_mapper:
            return jsonify({"error": "Document with this URL already exists."}), 400

        # Define the path for saving the JSON files
        json_directory = r"C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\new_docs\json_files"

        # Ensure the directory exists
        os.makedirs(json_directory, exist_ok=True)

        # Generate a filename based on the URL (or another unique identifier)
        json_filename = f"{data['url'].replace('https://', '').replace('http://', '').replace('/', '_')}.json"
        json_file_path = os.path.join(json_directory, json_filename)

        # Save the document content as a JSON file
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)

        return jsonify({"message": "Document added and saved as JSON file successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)