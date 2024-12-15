import csv
import json

def create_inverted_index(forward_index_file, inverted_index_file):
    """
    Converts a forward index in CSV format to an inverted index in CSV format without using an intermediate structure.
    """
    # Read forward index and write to the inverted index directly
    with open(forward_index_file, mode='r', encoding='utf-8') as infile, \
        open(inverted_index_file, mode='w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ['wordID', 'docID', 'frequency', 'hitlist']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                # Parse input data
                doc_id = int(row['docID'])
                word_id = int(row['wordID'])
                frequency = int(row['frequency'])
                hitlist = json.loads(row['hitlist'])  # Convert json string to a python list
                
                # Write directly to the inverted index
                writer.writerow({
                    'wordID': word_id,
                    'docID': doc_id,
                    'frequency': frequency,
                    'hitlist': json.dumps(hitlist)  # Convert back to JSON string
                })
            
            except (ValueError, json.JSONDecodeError) as e:
                print(f"Error processing row {row}: {e}")
                continue  # Skip invalid rows

    print(f"Inverted index has been saved to '{inverted_index_file}'.")


# Main program
if __name__ == "__main__":
    forward_index_file = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\forwardindex_test.csv'  # Input forward index CSV file
    inverted_index_file = 'inverted_index.csv'  # Output inverted index CSV file

    create_inverted_index(forward_index_file, inverted_index_file)
