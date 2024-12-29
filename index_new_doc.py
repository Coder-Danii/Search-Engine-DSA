import json
import csv
import os
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

    # Check if the data is a list or a dictionary containing a list
    if isinstance(data, dict):
        key = next(iter(data.keys()))
        data_list = data[key]
    elif isinstance(data, list):
        data_list = data
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
    dataset_file = json_to_csv(json_file_path, output_directory)

    if dataset_file:
        index_articles(dataset_file)
    else:
        print("Failed to create CSV file from JSON.")
    # after indexing, scrap the document
    scrap_docs(dataset_file)


#json_file_path = r'C:\Users\DELL\Desktop\Search-Engine-DSA\new_docs\json_files\test.json'

#index_new_doc(json_file_path, output_directory)
