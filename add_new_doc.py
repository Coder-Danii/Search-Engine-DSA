import json
import csv
import os

import pandas as pd

from inverted_barrels import process_forward_barrels
from lexicon_plus_barrels import load_lexicon,load_read_docs,process_article_data, save_doc_mapper, save_lexicon

def json_to_csv(json_file_path, output_directory):
    # Ensure the input file exists
    if not os.path.exists(json_file_path):
        print(f"File not found: {json_file_path}")
        return
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Define the output CSV file path
    csv_file_path = os.path.join(output_directory, os.path.splitext(os.path.basename(json_file_path))[0] + '.csv')

    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Check if the data is a list or a dictionary containing a list
    if isinstance(data, dict):
        key = next(iter(data.keys()))
        data_list = data[key]
    elif isinstance(data, list):
        data_list = data
    else:
        print("Unsupported JSON structure.")
        return

    # Determine if the file already exists
    file_exists = os.path.exists(csv_file_path)

    # Write to CSV
    with open(csv_file_path, 'a' if file_exists else 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        if not file_exists:
            # Write headers if the file is being created for the first time
            csv_writer.writerow(data_list[0].keys())

        # Write row data
        for record in data_list:
            csv_writer.writerow(record.values())

    print(f"CSV file '{csv_file_path}' {'updated' if file_exists else 'created'} successfully.")
    return csv_file_path

# Example usage
output_directory = r'C:\Users\DELL\Desktop\Search-Engine-DSA\new_docs\csv_files'
json_file_path = r'C:\Users\DELL\Desktop\Search-Engine-DSA\new_docs\json_files\test.json'

csv_file_path = json_to_csv(json_file_path, output_directory)


lexicon_file = r'lexicon.json'
docMapper_file = r'docmapper.json'
barrel_directory=r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'
article_data = pd.read_csv(csv_file_path, encoding='utf-8')  # Ensure UTF-8 encoding
    
# Load the lexicon, forward index, and docMapper
lexicon = load_lexicon(lexicon_file)
read_docs = load_read_docs(docMapper_file)

for index, row in article_data.iterrows():
    url = row['url']  # Extract URL of the article

    # Skip processing if URL is already in the read_docs
    if url in read_docs.values():
        print(f"Skipping already processed URL: {url}")
        
    else:
        # Process the articles and update lexicon, forward index, and barrels
        lexicon, read_docs = process_article_data(article_data, lexicon, read_docs, barrel_directory)
            
        # Save the updated lexicon, forward index, and barrels
        save_lexicon(lexicon, lexicon_file)
        save_doc_mapper(read_docs, docMapper_file)

        # Directory paths
        forward_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'  # Directory containing forward barrels
        inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'  # Directory to save inverted barrels
        offset_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\offset_barrels'  # Directory to save inverted barrels
        # Process all forward barrels
        process_forward_barrels(forward_barrels_dir, inverted_barrels_dir,offset_barrels_dir)

