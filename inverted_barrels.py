import csv
from collections import defaultdict
import os

def create_inverted_barrel(forward_barrel_file, inverted_barrel_file):
    """
    Converts a single forward barrel (CSV file) to an inverted barrel (CSV file).
    """
    # Initialize inverted index: {wordID -> {docID -> [frequency, hitlist]}}
    inverted_index = defaultdict(lambda: defaultdict(list))
    
    # Read forward barrel (CSV)
    with open(forward_barrel_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract values from the forward barrel row
            doc_id = int(row['docID'])
            word_id = int(row['wordID'])
            hitlist = eval(row['hitlist'])  # Convert the hitlist string back to a Python list
            frequency = len(hitlist)  # Calculate frequency from hits
            
            # Add entry to the inverted index
            inverted_index[word_id][doc_id] = [frequency] + hitlist

    # Write inverted barrel (CSV)
    with open(inverted_barrel_file, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['wordID', 'docID', 'frequency', 'hitlist']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for word_id, doc_dict in inverted_index.items():
            for doc_id, data in doc_dict.items():
                frequency = data[0]
                hitlist = data[1:]  # The rest are actual hits
                writer.writerow({
                    'wordID': word_id,
                    'docID': doc_id,
                    'frequency': frequency,
                    'hitlist': str(hitlist)
                })

    print(f"Inverted barrel has been saved to '{inverted_barrel_file}'.")

def create_inverted_barrels(forward_barrels_dir, inverted_barrels_dir):
    """
    Converts all forward barrels in a directory to inverted barrels and saves them in another directory.
    """
    # Ensure the output directory exists
    os.makedirs(inverted_barrels_dir, exist_ok=True)
    
    # Iterate over all forward barrel files
    for file_name in os.listdir(forward_barrels_dir):
        if file_name.startswith('forward_barrel_') and file_name.endswith('.csv'):
            forward_barrel_file = os.path.join(forward_barrels_dir, file_name)
            inverted_barrel_file = os.path.join(inverted_barrels_dir, file_name.replace('forward_barrel_', 'inverted_barrel_'))
            
            # Create the inverted barrel for each forward barrel
            create_inverted_barrel(forward_barrel_file, inverted_barrel_file)

    print(f"All inverted barrels have been saved in '{inverted_barrels_dir}'.")

# Main program
if __name__ == "__main__":
    forward_barrels_dir = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA'  # Directory containing forward barrels
    inverted_barrels_dir = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA'  # Directory to save inverted barrels

    create_inverted_barrels(forward_barrels_dir, inverted_barrels_dir)
