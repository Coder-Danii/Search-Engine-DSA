from sortedcontainers import SortedList
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def rank_docs(docs, intersections):
    added = np.zeros(6, dtype=bool)  # Prevents bonuses from stacking
    top_docs = SortedList()  # Stores documents in sorted order

    def process_doc(doc):
        doc_id = doc[0]
        hit_list = doc[1]
        frequency = doc[2]  # Use frequency instead of hitlist length

        # Base score based on frequency, capped at 20
        this_score = min(frequency, 20)

        # Intersection multiplier
        multiplier = intersection_multiplier(doc, intersections)
        this_score += 10 if multiplier != 1 else 0

        # Iterating over hitlist to check and assign scores
        i = 0
        step = 1  # Initially forward
        while i >= 0 and i < len(hit_list):
            hit = hit_list[i]

            # Match the hit type using modulo operation
            if hit[0] == 3:  # TITLE
                if not added[3]:
                    this_score += 50
                    added[3] = True
            elif hit[0] == 0:  # TEXT (skipped after handling non-TEXT)
                if step == 1:  # Forward iteration
                    i = len(hit_list) - 1
                    step = -1  # Switch to backward iteration
                else:
                    break  # Stop after TEXT hits are encountered
            elif hit[0] == 2:  # TAGS
                if not added[2]:
                    this_score += 30
                    added[2] = True
            elif hit[0] == 1:  # AUTHORS
                if not added[1]:
                    this_score += 20
                    added[1] = True

            # Move to the next hit
            if hit[0] != 1:  # Avoid moving when encountering TEXT (handled above)
                i += step
            else:
                break  # Break after handling TEXT hits

        # Apply the intersection multiplier to the score
        this_score *= multiplier

        # Add score and document ID to the SortedList (negative score for descending order)
        top_docs.add((-this_score, doc_id))

    # Use a thread pool to process documents concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(process_doc, docs)

    return top_docs

# Computes intersections of document lists for multi-word queries
def intersect(doc_lists):
    if len(doc_lists) <= 1:
        return []

    # Convert each doc_list into dictionaries for fast lookup
    doc_lists = [{doc[0]: is_relevant(doc[1]) for doc in doc_list} for doc_list in doc_lists]
    intersections = [doc_lists[0]]

    for i in range(1, len(doc_lists)):
        this_intersection = {}
        for doc_id in doc_lists[i]:
            if doc_id in intersections[i - 1]:
                if doc_lists[i][doc_id] and intersections[i - 1][doc_id]:
                    this_intersection[doc_id] = True
                else:
                    this_intersection[doc_id] = False
        intersections.append(this_intersection)
    return intersections

# Checks if a hit list is relevant (has hits other than TEXT)
def is_relevant(hit_list):
    # Check if any hit type (hit[0]) is not TEXT (which is represented by hit_type 1)
    return any(hit[0] != 1 for hit in hit_list)

# Multiplier based on intersection level
def intersection_multiplier(doc, intersections):
    for i in range(len(intersections) - 1, 0, -1):
        if doc[0] in intersections[i]:
            if intersections[i][doc[0]]:
                return (i + 1) * 10  # Intersection in title/authors/tags
            return (i + 1) * 2
    return 1

# Parses the hitlist from the CSV format
def parse_hitlist(hitlist_str):
    return [(int(hit.split(',')[0]), int(hit.split(',')[1])) for hit in hitlist_str.split('|')]

# Example utility function to process document lists
def process_docs(doc_data):
    doc_list = []
    for doc_id, freq, hitlist_str in zip(doc_data['doc_ids'], doc_data['frequencies'], doc_data['hitlists']):
        hitlist = parse_hitlist(hitlist_str)
        doc_list.append((int(doc_id), hitlist, int(freq)))  # Include frequency in the tuple
    return doc_list
