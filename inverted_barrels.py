from collections import defaultdict
import csv
import os

from collections import defaultdict
import csv

def create_inverted_barrel(forward_barrel_file):
    # Initialize an inverted barrel where the key is wordID and the value is three concatenated strings
    inverted_barrel = defaultdict(lambda: ["", "", ""])  # Three strings: docIDs, frequencies, hitlists

    with open(forward_barrel_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Extract values from the forward barrel row
            word_id = int(row['wordID'])
            doc_id = row['docID']  # Keep as string for concatenation
            frequency = row['frequency']  # Keep as string for concatenation
            hitlist = row['hitlist']
            
            # Append the docID, frequency, and hitlist to the corresponding strings for this wordID
            if inverted_barrel[word_id][0]:  # Add a | if not the first value
                inverted_barrel[word_id][0] += f"|{doc_id}"
                inverted_barrel[word_id][1] += f"|{frequency}"
                inverted_barrel[word_id][2] += f"|{hitlist}"
            else:  # First value, no |
                inverted_barrel[word_id][0] += doc_id
                inverted_barrel[word_id][1] += frequency
                inverted_barrel[word_id][2] += hitlist

    return inverted_barrel


    return inverted_barrel
def save_inverted_barrel(inverted_barrel, output_file):
    """
    Saves the inverted barrel to a CSV file. The structure is {wordID -> [docIDs, frequencies, hitlists]}.
    """
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['wordID', 'docID', 'frequency', 'hitlist']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate through the inverted barrel structure
        for word_id, lists in inverted_barrel.items():
            doc_ids = str(lists[0])
            frequencies = lists[1]
            hitlists = lists[2]
            writer.writerow({
                'wordID': word_id,
                'docID': doc_ids,
                'frequency': frequencies,
                'hitlist': hitlists
                })
            inverted_barrel[word_id].clear()

def process_forward_barrels(forward_barrels_dir, inverted_barrels_dir):
    """
    Processes all forward barrel files in the directory, creating and saving inverted barrels.

    Args:
        forward_barrels_dir (str): Directory containing forward barrel files.
        inverted_barrels_dir (str): Directory to save the generated inverted barrel files.
    """
    # Ensure the output directory exists
    os.makedirs(inverted_barrels_dir, exist_ok=True)

    # Iterate over all forward barrel files in the input directory
    for file_name in os.listdir(forward_barrels_dir):
        if file_name.startswith('forward_barrel_') and file_name.endswith('.csv'):
            forward_barrel_file = os.path.join(forward_barrels_dir, file_name)
            inverted_barrel_file = os.path.join(inverted_barrels_dir, file_name.replace('forward_barrel_', 'inverted_barrel_'))

            # Step 1: Load forward barrel into an inverted barrel (dictionary structure)
            inverted_barrel = create_inverted_barrel(forward_barrel_file)

            # Step 2: Save the inverted barrel to the output directory
            save_inverted_barrel(inverted_barrel, inverted_barrel_file)

    print(f"All inverted barrels have been processed and saved in '{inverted_barrels_dir}'.")


# Main program
if __name__ == "__main__":
    # Directory paths
    forward_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'  # Directory containing forward barrels
    inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'  # Directory to save inverted barrels

    # Process all forward barrels
    process_forward_barrels(forward_barrels_dir, inverted_barrels_dir)
