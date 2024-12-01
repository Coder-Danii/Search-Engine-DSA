import json
from collections import defaultdict

# Function to create the inverted index from the forward index
def create_inverted_index(forward_index):
    inverted_index = defaultdict(lambda: defaultdict(list))  # Structure: {word_id: {doc_id: [hits]}}

    for doc_id, word_dict in forward_index.items():
        for word_id, hits in word_dict.items():
            total_hits = hits[0]  # First element is the total number of hits
            hit_list = hits[1:]  # The rest are the actual hits
            if total_hits > 0:  # Check if the word actually has hits
                inverted_index[word_id][doc_id] = [total_hits] + hit_list  # Add total_hits in front of the hit list

    # Convert defaultdict to regular dict for JSON serialization
    return {word_id: dict(doc_dict) for word_id, doc_dict in inverted_index.items()}

# Save the inverted index to a JSON file
def save_inverted_index_to_json(inverted_index, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, ensure_ascii=False)  # Removed `indent=4`

# Main program
if __name__ == "__main__":
    # Load the forward index from the JSON file
    forward_index_file = 'forward_index.json'  # Matches your forward index JSON file name
    with open(forward_index_file, 'r', encoding='utf-8') as f:
        forward_index = json.load(f)

    # Create the inverted index
    inverted_index = create_inverted_index(forward_index)

    # Save the inverted index to a JSON file
    inverted_index_file = 'invertedIndex.json'  # Matches your desired inverted index JSON file name
    save_inverted_index_to_json(inverted_index, inverted_index_file)

    print(f"Inverted index has been saved to '{inverted_index_file}'.")
