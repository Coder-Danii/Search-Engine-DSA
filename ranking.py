from sortedcontainers import SortedList

# Rank documents based on weighted hits
def rank_documents(docs, intersections):
    max_text_hits = 20  # Limit text hits to avoid overemphasis
    top_docs = SortedList()  # Stores documents ranked by relevance (-score for descending order)

    for doc in docs:
        doc_id = doc[0]
        hit_list = doc[1]
        score = 0

        # Track fields to avoid stacking bonuses
        processed_fields = set()

        # Process each hit
        for hit in hit_list:
            weight, position = hit  # Extract weight and position
            if weight not in processed_fields:
                score += weight  # Add the field's weight to the score
                processed_fields.add(weight)

        # Apply text hit bonus (capped at the threshold)
        text_hits = sum(1 for hit in hit_list if hit[0] == 0)  # Weight 0 is for text hits
        score += min(text_hits, max_text_hits)

        # Adjust score based on intersections
        multiplier = calculate_intersection_multiplier(doc_id, intersections)
        score *= multiplier

        # Add to sorted list (negative score for descending order)
        top_docs.add((-score, doc_id))

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
        for doc_id, hitlist in doc_list:
            if isinstance(doc_id, list):
                doc_id = tuple(doc_id)  # Convert list to tuple to make it hashable
            doc_dict[doc_id] = is_hit_list_relevant(hitlist)  # Store relevance of the hitlist
    return doc_dict

    intersections = [doc_dicts[0]]  # Initialize intersections with the first doc_dict

    # Perform intersection across all doc_dicts
    for i in range(1, len(doc_dicts)):
        this_intersection = {}
        for doc_id in doc_dicts[i]:
            if doc_id in intersections[i - 1]:  # Check if doc_id exists in previous intersection
                # Logical AND for relevance (both need to be relevant)
                this_intersection[doc_id] = intersections[i - 1][doc_id] and doc_dicts[i][doc_id]
        intersections.append(this_intersection)

    return intersections



# Determine if a hit list is relevant (contains non-text hits)
def is_hit_list_relevant(hit_list):
    return any(hit[0] != 0 for hit in hit_list)  # Non-text hits have weight != 0
