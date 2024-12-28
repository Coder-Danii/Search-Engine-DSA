from flask import Flask, request, jsonify
import csv
import pandas as pd
import threading as th
import lexicon_plus_barrels as lb
import ranking as rk
import json
import inverted_barrels as ib
from flask_cors import CORS
# # Initialize Flask app
app = Flask(__name__)
CORS(app)
# Load docmapper.json once during initialization for O(1) lookups
with open(r"C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\Search-Engine-DSA\\docmapper.json", 'r', encoding='utf-8') as docmapper_file:
    doc_mapper = json.load(docmapper_file)

# Load the CSV file containing document details
csv_file_path = r'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\50000articles.csv'
documents_df = pd.read_csv(csv_file_path)

# Ensure 'url' column is used as the index for quick access
documents_df.set_index('url', inplace=True)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    lexicon_path =r"C:\\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\lexicon.json"

    if not query:
        return jsonify({"error": "Both 'query' are required."}), 400

    try:
        results, total_docs = get_results(query, lexicon_path)
        return jsonify({"total_results": total_docs, "results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_results(query, lexicon_path):
    query_tokens = []
    for word in query.split():
        tokenized_words = lb.split_token(word)
        for token in tokenized_words:
            processed_word = lb.preprocess_word(token)
            if processed_word is not None:
                query_tokens.append(processed_word)
            else:
                raise ValueError(f"Query word '{token}' could not be processed.")

    words = {}
    threads = []

    for word in query_tokens:
        this_thread = th.Thread(target=retrieve_word_docs, args=(word, lexicon_path, words))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    doc_lists = [docs for docs in words.values() if docs]
    intersections = rk.intersect(doc_lists)

    ranked_docs = []
    for docs in words.values():
        if docs:
            ranked_docs.extend(rk.rank_docs(docs, intersections))

    result_docs_set = set()
    unique_result_docs = []
    for score, doc_id in ranked_docs:
        if doc_id not in result_docs_set:
            unique_result_docs.append((score, doc_id))
            result_docs_set.add(doc_id)

    sorted_docs = sorted(unique_result_docs, key=lambda x: -x[0])

    results = []
    threads = []

    for score, doc_id in sorted_docs:
        this_thread = th.Thread(target=retrieve_doc_info, args=(doc_id, results))
        threads.append(this_thread)
        this_thread.start()

    for thread in threads:
        thread.join()

    return results, len(sorted_docs)

def retrieve_word_docs(word, lexicon_path, words):
    try:
        with open(lexicon_path, 'r', encoding='utf-8') as file:
            lexicon = json.load(file)

        word_id = lexicon.get(word)
        if word_id is None:
            return

        barrel_number = word_id // 1000
        offset_file = r'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\Search-Engine-DSA\\offset_barrels\\inverted_barrel_{}.bin'.format(barrel_number)
        offsets = ib.load_offsets(offset_file)

        file_name = r'C:\\Users\\Sohail\\Desktop\\THIRD SEMESTER\\DSA\\FINAL PROJECT DSA\\LEXICON\\Search-Engine-DSA NEW\\Search-Engine-DSA\\inverted_barrels\\inverted_barrel_{}.csv'.format(barrel_number)
        offset = offsets[word_id % 1000]

        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            file.seek(offset)
            reader = csv.reader(file)
            row = next(reader)

            doc_ids = row[1].split('|')
            hitlists = row[3].split('|')

            parsed_results = []
            for doc_id, hitlist in zip(doc_ids, hitlists):
                hits = hitlist.split(';')
                parsed_hits = [tuple(map(int, hit.split(','))) for hit in hits]
                parsed_results.append((doc_id, parsed_hits))

            words[word] = parsed_results

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error: {str(e)}")

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

if __name__ == "__main__":
    app.run(debug=True)
