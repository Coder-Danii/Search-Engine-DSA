from sortedcontainers import SortedList

# Rank documents based on weighted hits and frequency
def rank_documents(docs, intersections):
    max_text_hits = 20  # Limit text hits to avoid overemphasis
    top_docs = SortedList()  # Stores documents ranked by relevance (-score for descending order)

    for doc in docs:
        doc_ids, frequencies, hit_lists = doc  # Unpack the doc data
        score = 0

        # Track fields to avoid stacking bonuses
        processed_fields = set()

        # Process each hit list
        for hit_str in hit_lists:
            # Parse the hit string (assuming the format is: weight, position)
            hits = parse_hit_format(hit_str)

            # Iterate over the parsed hits
            for weight, position in hits:
                if weight not in processed_fields:
                    score += weight  # Add the field's weight to the score
                    processed_fields.add(weight)

        # Apply frequency bonus
        for frequency in frequencies:
            score += int(frequency)  # Add frequency to score

        # Apply text hit bonus (capped at the threshold)
        text_hits = sum(1 for hit in hit_lists if hit[0] == 0)  # Weight 0 is for text hits
        score += min(text_hits, max_text_hits)

        # Adjust score based on intersections
        multiplier = calculate_intersection_multiplier(doc_ids[0], intersections)
        score *= multiplier

        # Add to sorted list (negative score for descending order)
        top_docs.add((-score, doc_ids))

    return top_docs


# Calculate multiplier for documents based on intersections
def calculate_intersection_multiplier(doc_id, intersections):
    for i in range(len(intersections) - 1, -1, -1):  # Start from deepest intersection
        if doc_id in intersections[i]:
            if intersections[i][doc_id]:  # Relevant intersection
                return (i + 1) * 100
            return (i + 1) * 2
    return 1


# Compute intersections for multi-word queries
def compute_intersections(doc_lists):
    doc_dict = {}

    for doc_list in doc_lists:
        print("Processing doc_list:", doc_list)  # Debug print to see the data structure
        # Iterate over the elements in doc_list
        for i in range(len(doc_list[0])):  # Assuming each list in doc_list has the same length
            # Extract doc_id, frequency, and hitlist based on index
            doc_id = doc_list[0][i]  # doc_ids list
            hitlist = doc_list[2][i]  # hitlist list

            # Now we need to process the hitlist, assuming the hitlist is a string of comma-separated values
            hits = parse_hit_format(hitlist)

            # Add the processed doc_id and hits to doc_dict
            doc_dict[doc_id] = is_hit_list_relevant(hits)  # You can process hits as needed

    return doc_dict



# Determine if a hit list is relevant (contains non-text hits)
def is_hit_list_relevant(hit_list):
    return any(hit[0] != 0 for hit in hit_list)  # Non-text hits have weight != 0


# Parse hit string into weight, position pairs
def parse_hit_format(hit_str):
    # Format: "weight, position"
    hits = []
    for hit in hit_str.split(";"):
        weight, position = hit.split(",")
        hits.append((int(weight), int(position)))  # Return as a tuple (weight, position)
    return hits
