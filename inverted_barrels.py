import csv
import os
import struct

def load_forward_barrel(forward_barrel_file):
    """
    Loads a single forward barrel CSV file and returns the data in a list of dictionaries.
    Each dictionary contains a row from the CSV with keys 'wordID', 'docID', 'frequency', and 'hitlist'.
    """
    forward_barrel = []

    with open(forward_barrel_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            forward_barrel.append({
                'wordID': int(row['wordID']),
                'docID': int(row['docID']),
                'frequency': int(row['frequency']),
                'hitlist': row['hitlist']
            })

    return forward_barrel

def create_inverted_barrel(forward_data):
    """
    Converts the loaded forward barrel data (list of dictionaries) into an inverted barrel structure.
    The result is a list of lists, each containing: [wordID, docID, frequency, hitlist].
    """
    inverted_data = []

    # Iterate over the forward data and create a flat inverted barrel structure
    for row in forward_data:
        word_id = row['wordID']
        doc_id = row['docID']
        hitlist = row['hitlist']
        frequency = row['frequency']

        # Store each entry with the format [wordID, docID, frequency, hitlist]
        inverted_data.append([word_id, doc_id, frequency, hitlist])

    return inverted_data


def save_inverted_barrel(inverted_data, inverted_barrel_file):
    """
    Saves the inverted barrel to a CSV file.
    """
    print(f"Saving inverted barrel to '{inverted_barrel_file}'...")

    with open(inverted_barrel_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['wordID', 'docIDs', 'frequencies', 'hitlists'])  # Header

        # Write each row of inverted barrel data
        for row in inverted_data:
            writer.writerow(row)

def process_forward_barrels(forward_barrels_dir, inverted_barrels_dir):
    """
    Processes all forward barrel files in the directory, creating and saving inverted barrels.
    """
    # Ensure the output directory exists
    os.makedirs(inverted_barrels_dir, exist_ok=True)

    # Iterate over all forward barrel files
    for file_name in os.listdir(forward_barrels_dir):
        if file_name.startswith('forward_barrel_') and file_name.endswith('.csv'):
            forward_barrel_file = os.path.join(forward_barrels_dir, file_name)
            inverted_barrel_file = os.path.join(inverted_barrels_dir, file_name.replace('forward_barrel_', 'inverted_barrel_'))

            # Step 1: Load forward barrel into memory
            forward_data = load_forward_barrel(forward_barrel_file)

            # Step 2: Create inverted barrel from loaded forward barrel data
            inverted_data = create_inverted_barrel(forward_data)

            # Step 3: Save the inverted barrel to a file
            save_inverted_barrel(inverted_data, inverted_barrel_file)

    print(f"All inverted barrels have been processed and saved in '{inverted_barrels_dir}'.")

# Main program
if __name__ == "__main__":
    # Directory paths
    forward_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'  # Directory containing forward barrels
    inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'  # Directory to save inverted barrels

    # Process all forward barrels
    process_forward_barrels(forward_barrels_dir, inverted_barrels_dir)
