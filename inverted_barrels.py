from collections import defaultdict
import csv
import os

from collections import defaultdict
import csv
import struct

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

def create_offsets(input_file, output_file):
    """
    Creates a binary file containing offsets for each line in a given inverted barrel CSV file.
    """
    with open(input_file, mode='r', encoding='utf-8') as file, \
         open(output_file, mode='wb') as offset_file:
        # Skip the header row
        file.readline()
        while True:
            offset = file.tell()  # Get the current byte offset
            line = file.readline()
            if not line:  # End of file
                break
            # Write the offset directly to the binary file
            offset_file.write(struct.pack('Q', offset))
    
    print(f"Offsets saved to {output_file}.")

def load_offsets(offset_file):
    """
    Loads all offsets from the binary offset file into a list.
    """
    offsets = []
    try:
        with open(offset_file, mode='rb') as offset_bin:
            while True:
                offset_bytes = offset_bin.read(8)  # Read 8 bytes (Q = unsigned long long)
                if not offset_bytes:
                    break
                offset = struct.unpack('Q', offset_bytes)[0]
                offsets.append(offset)
    except (FileNotFoundError, struct.error) as e:
        print(f"Error loading offsets: {e}")
    return offsets

def process_forward_barrels(forward_barrels_dir, inverted_barrels_dir, offset_barrel_dir):
    """
    Processes all forward barrel files in the directory, creating and saving inverted barrels.
    """
    # Ensure the output directory exists
    os.makedirs(inverted_barrels_dir, exist_ok=True)
    
    # Create the output directory if it doesn't exist
    os.makedirs(offset_barrel_dir, exist_ok=True)

    # Iterate over all forward barrel files in the input directory
    for file_name in os.listdir(forward_barrels_dir):
        if file_name.startswith('forward_barrel_') and file_name.endswith('.csv'):
            forward_barrel_file = os.path.join(forward_barrels_dir, file_name)
            inverted_barrel_file = os.path.join(inverted_barrels_dir, file_name.replace('forward_barrel_', 'inverted_barrel_'))
            offset_barrel_file = os.path.join(offset_barrel_dir, file_name.replace('forward_barrel_', 'inverted_barrel_').replace('.csv', '.bin'))
            
            # Step 1: Load forward barrel into an inverted barrel (dictionary structure)
            inverted_barrel = create_inverted_barrel(forward_barrel_file)

            # Step 2: Save the inverted barrel to the output directory
            save_inverted_barrel(inverted_barrel, inverted_barrel_file)

            # Step 3: Generate offset file for the inverted barrel
            create_offsets(inverted_barrel_file, offset_barrel_file)

    print(f"All inverted barrels have been processed and saved in '{inverted_barrels_dir}'.")


## Use this method in query processing, this was added here to test the offsets 
def get_row_by_word_id(word_id, inverted_barrel_file, offset_file):
    offsets = load_offsets(offset_file)  # Load all offsets

    if word_id >= len(offsets):
        print(f"Error: word ID {word_id} is out of range.")
        return None

    try:
        # Get the byte offset for the given word_id
        offset = offsets[word_id]
        offsets.clear()
        # Read the row from the CSV file using the offset
        with open(inverted_barrel_file, mode='r', encoding='utf-8') as csv_file:
            csv_file.seek(offset)
            row = csv_file.readline().strip()  # Read the row and remove trailing whitespace
        print(row)
        return row
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None


# Main program
if __name__ == "__main__":
    # Directory paths
    forward_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'  # Directory containing forward barrels
    inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'  # Directory to save inverted barrels
    offset_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\offset_barrels'  # Directory to save inverted barrels

    # Process all forward barrels
    process_forward_barrels(forward_barrels_dir, inverted_barrels_dir,offset_barrels_dir)