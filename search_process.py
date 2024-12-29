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
import scraping

lemmatizer = WordNetLemmatizer()
lb.preprocess_word('apple')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Paths for files
docmapper_path = r"C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\Search-Engine-DSA\\docmapper.json"
csv_file_path = r'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\20articles.csv'

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
    threads = []

    for word in query_tokens:
        this_thread = th.Thread(target=retrieve_word_docs, args=(word, words))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    doc_lists = [docs for docs in words.values() if docs]
    intersections = rk.intersect(doc_lists)
    ranked_docs = rk.rank_docs([doc for docs in words.values() for doc in docs], intersections)

    result_docs_set = set()
    unique_result_docs = []
    for score, doc_id in ranked_docs:
        if (doc_id not in result_docs_set):
            unique_result_docs.append((score, doc_id))
            result_docs_set.add(doc_id)

    sorted_docs = sorted(unique_result_docs, key=lambda x: -x[0])

    results = []
    all_tags = set()
    threads = []

    for score, doc_id in sorted_docs:
        this_thread = th.Thread(target=retrieve_doc_info, args=(doc_id, results))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    for result in results:
        tags = result.get("tags", "").split(",")
        all_tags.update(tag.strip() for tag in tags if tag.strip())

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
    try:
        doc_url = doc_mapper.get(str(doc_id))
        if not doc_url:
            return

        if doc_url in documents_df.index:
            doc_details = documents_df.loc[doc_url].to_dict()
            results.append({
                "doc_id": doc_id,
                "title": doc_details.get('title', 'Unknown Title'),
                "text": doc_details.get('text', 'No Content Available'),
                "url": doc_url,
                "authors": doc_details.get('authors', 'Unknown Author'),
                "timestamp": doc_details.get('timestamp', 'Unknown Timestamp'),
                "tags": doc_details.get('tags', 'No Tags')
            })

    except Exception as e:
        print(f"Error while retrieving document info for doc_id {doc_id}: {str(e)}")

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

        scraping.index_new_doc(json_file_path, file_paths.new_doc_output_dir)

        return jsonify({"message": "Document added and saved as JSON file successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)