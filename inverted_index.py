import csv
from collections import defaultdict

def create_inverted_index_from_csv(forward_index_file, inverted_index_file):
    """
    Converts a forward index in CSV format to an inverted index in CSV format.
    """
    # Initialize inverted index: {wordID -> {docID -> [frequency, hitlist]}}
    inverted_index = defaultdict(lambda: defaultdict(list))
    
    # Read forward index CSV
    with open(forward_index_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract values from the forward index row
            doc_id = int(row['docID'])
            word_id = int(row['wordID'])
            frequency = int(row['frequency'])
            hitlist = eval(row['hitlist'])  # Convert the hitlist string back to a Python list
            
            # Add entry to the inverted index
            inverted_index[word_id][doc_id] = [frequency] + hitlist

    # Write inverted index to CSV
    with open(inverted_index_file, mode='w', encoding='utf-8', newline='') as file:
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

    print(f"Inverted index has been saved to '{inverted_index_file}'.")


# Main program
if __name__ == "__main__":
    forward_index_file = 'forwardindex_test.csv'  # Input forward index CSV file
    inverted_index_file = 'invertedindex_test.csv'  # Output inverted index CSV file

    create_inverted_index_from_csv(forward_index_file, inverted_index_file)
