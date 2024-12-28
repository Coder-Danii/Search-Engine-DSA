from collections import defaultdict
import csv
import os

from concurrent.futures import ThreadPoolExecutor

from collections import defaultdict
import csv
import struct

def process_chunk(chunk):
    local_inverted_barrel = defaultdict(lambda: ["", "", ""])
    for row in chunk:
        word_id = int(row['wordID'])
        doc_id = row['docID']
        frequency = row['frequency']
        hitlist = row['hitlist']
        
        if local_inverted_barrel[word_id][0]:
            local_inverted_barrel[word_id][0] += f"|{doc_id}"
            local_inverted_barrel[word_id][1] += f"|{frequency}"
            local_inverted_barrel[word_id][2] += f"|{hitlist}"
        else:
            local_inverted_barrel[word_id][0] += doc_id
            local_inverted_barrel[word_id][1] += frequency
            local_inverted_barrel[word_id][2] += hitlist
    return local_inverted_barrel

def merge_inverted_barrels(main_barrel, local_barrel):
    for word_id, values in local_barrel.items():
        if main_barrel[word_id][0]:
            main_barrel[word_id][0] += f"|{values[0]}"
            main_barrel[word_id][1] += f"|{values[1]}"
            main_barrel[word_id][2] += f"|{values[2]}"
        else:
            main_barrel[word_id][0] += values[0]
            main_barrel[word_id][1] += values[1]
            main_barrel[word_id][2] += values[2]


def create_inverted_barrel(forward_barrel_file):
    inverted_barrel = defaultdict(lambda: ["", "", ""])

    with open(forward_barrel_file, mode='r', encoding='utf-8') as file:
        print("Processing " + forward_barrel_file)
        reader = csv.DictReader(file)
        
        chunk_size = 10000
        chunk = []
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for row in reader:
                chunk.append(row)
                if len(chunk) >= chunk_size:
                    futures.append(executor.submit(process_chunk, chunk))
                    chunk = []
            
            if chunk:
                futures.append(executor.submit(process_chunk, chunk))
            
            for future in futures:
                local_inverted_barrel = future.result()
                merge_inverted_barrels(inverted_barrel, local_inverted_barrel)
    
    return inverted_barrel

def save_inverted_barrel(inverted_barrel, output_file):
    """
    Saves the inverted barrel to a CSV file. The structure is {wordID -> [docIDs, frequencies, hitlists]}.
    """
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['wordID', 'docID', 'frequency', 'hitlist']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for word_id, values in inverted_barrel.items():
            writer.writerow({
                'wordID': word_id,
                'docID': values[0],
                'frequency': values[1],
                'hitlist': values[2]
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

def process_forward_barrels(forward_barrel_files, inverted_barrels_dir, offset_barrels_dir):
    """
    Process forward barrels to create inverted barrels.
    """
    os.makedirs(inverted_barrels_dir, exist_ok=True)
    os.makedirs(offset_barrels_dir, exist_ok=True)

    for forward_barrel_file in forward_barrel_files:
        # Process each forward barrel file
        inverted_barrel = create_inverted_barrel(forward_barrel_file)
        barrel_number = os.path.basename(forward_barrel_file).split('_')[-1].split('.')[0]
        inverted_barrel_file = os.path.join(inverted_barrels_dir, f'inverted_barrel_{barrel_number}.csv')
        offset_file = os.path.join(offset_barrels_dir, f'inverted_barrel_{barrel_number}.bin')
        
        save_inverted_barrel(inverted_barrel, inverted_barrel_file)
        create_offsets(inverted_barrel_file, offset_file)

        print(f"Processed forward barrel: {forward_barrel_file}")

    print("Inverted barrels created successfully.")


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
