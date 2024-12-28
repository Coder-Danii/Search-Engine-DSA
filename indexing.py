import os
import pandas as pd
from lexicon_plus_barrels import load_lexicon, load_read_docs, process_article_data, save_doc_mapper, save_lexicon
from inverted_barrels import process_forward_barrels

def index_articles(dataset_file):
    lexicon_file = r'lexicon.json'
    docMapper_file = r'docmapper.json'
    forward_barrel_directory = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'
    inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'
    offset_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\offset_barrels'
    
    article_data = pd.read_csv(dataset_file, encoding='utf-8')  # Ensure UTF-8 encoding
    
    # Load the lexicon, forward index, and docMapper
    lexicon = load_lexicon(lexicon_file)
    read_docs = load_read_docs(docMapper_file)
    
    updated_forward_barrels = []

    # Process the articles and update lexicon, forward index, and barrels
    lexicon, read_docs, updated_forward_barrels = process_article_data(article_data, lexicon, read_docs, forward_barrel_directory)
    
    # Save the updated lexicon, forward index, and barrels
    save_lexicon(lexicon, lexicon_file)
    save_doc_mapper(read_docs, docMapper_file)

    # Process only updated forward barrels
    forward_barrel_files = [os.path.join(forward_barrel_directory, f'forward_barrel_{barrel}.csv') for barrel in updated_forward_barrels]
    process_forward_barrels(forward_barrel_files, inverted_barrels_dir, offset_barrels_dir)

    print("Processing complete! Lexicon, forward barrels, and inverted barrels updated.")

# Example usage
dataset_file = r'C:\Users\DELL\Desktop\University\Data Structures and Algorithms\Project\Medium Articles\medium_articles.csv'
index_articles(dataset_file)
