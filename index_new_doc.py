import json
import csv
import os
import lexicon_plus_barrels
from indexing import index_articles
import file_paths as file
from scraping import scrap_docs


output_directory = file.new_doc_output_dir

def json_to_csv(json_file_path, output_directory):
    # Ensure the input file exists
    if not os.path.exists(json_file_path):
        print(f"File not found: {json_file_path}")
        return None
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Define the output CSV file path
    csv_file_path = os.path.join(output_directory, os.path.splitext(os.path.basename(json_file_path))[0] + '.csv')

    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Check if the JSON data is a dictionary (single record)
    if isinstance(data, dict):
        data_list = [data]
    else:
        print("Unsupported JSON structure.")
        return None

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


def index_new_doc(json_file_path, output_directory):
    doc_mapper_file= file.docMapper_file
    doc_mapper_data = lexicon_plus_barrels.load_read_docs(doc_mapper_file)
    dataset_file = json_to_csv(json_file_path, output_directory)
    for index, row in doc_mapper_data.iterrows():
        url = row['url']
        
        # Skip processing if URL is already in the read_docs
        if url not in doc_mapper_data.values():
            if dataset_file:
                index_articles(dataset_file)
            else:
                print("Failed to create CSV file from JSON.")
            # after indexing, scrap the document
            scrap_docs(dataset_file)
        
        else: 
            print(f"Skipping already processed URL: {url}")




#index_new_doc(r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\new_docs\json_files\test.json', output_directory)
