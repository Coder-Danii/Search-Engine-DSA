from collections import defaultdict
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import csv
import struct

# Function to process a chunk of rows from the forward barrel
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

# Function that merges chunk after they have been processed
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

# Function takes one forward barrel file and converted it in inverted barrel
def create_inverted_barrel(forward_barrel_file):
    inverted_barrel = defaultdict(lambda: ["", "", ""])

    with open(forward_barrel_file, mode='r', encoding='utf-8') as file:
        print("Processing " + forward_barrel_file)
        reader = csv.DictReader(file)
        
        chunk_size = 10000
        chunk = []
        
        # Process chunks in threads
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
    """Saves the inverted barrel to a CSV file. The structure is {wordID -> [docIDs, frequencies, hitlists]}."""
    print(f"Saving inverted barrel to {output_file}")
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
    """Creates a binary file containing offsets for each line in a given inverted barrel CSV file."""
    print(f"Creating offsets for {input_file} and saving to {output_file}")
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
    
    print(f"Offsets saved to {output_file}")

def load_offsets(offset_file):
    """Loads all offsets from the binary offset file into a list."""
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

def process_forward_barrel(forward_barrel_file, inverted_barrels_dir, offset_barrels_dir):
    """Process a single forward barrel file to create an inverted barrel and its offsets."""
    inverted_barrel = create_inverted_barrel(forward_barrel_file)
    barrel_number = os.path.basename(forward_barrel_file).split('_')[-1].split('.')[0]
    inverted_barrel_file = os.path.join(inverted_barrels_dir, f'inverted_barrel_{barrel_number}.csv')
    offset_file = os.path.join(offset_barrels_dir, f'inverted_barrel_{barrel_number}.bin')
    
    print(f"Processing forward barrel: {forward_barrel_file}")
    print(f"Inverted barrel file: {inverted_barrel_file}")
    print(f"Offset file: {offset_file}")

    save_inverted_barrel(inverted_barrel, inverted_barrel_file)
    create_offsets(inverted_barrel_file, offset_file)

    print(f"Processed forward barrel: {forward_barrel_file}")

def process_forward_barrels(forward_barrel_files, inverted_barrels_dir, offset_barrels_dir):
    """Process forward barrels to create inverted barrels."""
    os.makedirs(inverted_barrels_dir, exist_ok=True)
    os.makedirs(offset_barrels_dir, exist_ok=True)

    # Use a thread pool to process multiple forward barrels concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for forward_barrel_file in forward_barrel_files:
            futures.append(executor.submit(process_forward_barrel, forward_barrel_file, inverted_barrels_dir, offset_barrels_dir))
        
        # Wait for all threads to complete
        for future in futures:
            future.result()

    print("Inverted barrels created successfully.")
