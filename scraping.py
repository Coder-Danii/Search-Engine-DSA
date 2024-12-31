import os
import pandas as pd
import json
import csv
import file_paths

def scrap_docs(dataset_file):
    data_iter=pd.read_csv(dataset_file, encoding='utf-8',iterator=True, chunksize=1)
    # Load the docMapper JSON
    with open(file_paths.docMapper_file, 'r', encoding='utf-8') as json_file:
        doc_mapper = json.load(json_file)

    # Load the medium_articles.csv iterator

    # Check if the file already exists
    if not os.path.exists(file_paths.scraped_articles_file):
        # Create the output CSV file with headers
        with open(file_paths.scraped_articles_file, 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=['docID', 'url', 'title', 'first_two_lines', 'author', 'tags', 'timestamp']
            , quoting=csv.QUOTE_ALL)
            writer.writeheader()
    else:
        print("File already exists.")

    # Initialize a counter for processed documents
    processed_count = 0

    # Process one row at a time
    for chunk in data_iter:
        row = chunk.iloc[0]
        url = row['url']
        
        # Find docID corresponding to the URL
        doc_id = next((k for k, v in doc_mapper.items() if v == url), None)
        if doc_id is None:
            continue

        title = row['title']
        text = row['text']
        text_lines = text.splitlines()  # Split text into lines
        first_two_lines = '\n'.join(text_lines[:3]) if len(text_lines) >= 3 else text
        author = row['authors'].strip("[]").replace("'", "")  # Remove brackets and single quotes from author field
        tags = row['tags']
        timestamp = str(row['timestamp']).split(' ')[0]  # Convert to string and extract only the date part (YYYY-MM-DD)

        # Write the processed row to the output CSV
        with open(file_paths.scraped_articles_file, 'a', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=['docID', 'url', 'title', 'first_two_lines', 'author', 'tags', 'timestamp'], quoting=csv.QUOTE_ALL)
            writer.writerow({
                'docID': doc_id,
                'url': url,
                'title': title,
                'first_two_lines': first_two_lines,
                'author': author,
                'tags': tags,
                'timestamp': timestamp
            })

        # Increment the processed count
        processed_count += 1
        print(f"Processed {processed_count} documents.")

    print("Filtered CSV file created: scraped_medium_articles.csv")



#scrap_docs(file_paths.dataset_file)
