# Ushba
lexicon_file = r'C:\Users\DELL\Desktop\Search-Engine-DSA\lexicon.json'
docMapper_file = r'C:\Users\DELL\Desktop\Search-Engine-DSA\docmapper.json'
forward_barrel_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\forward_barrels'
inverted_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels'
offset_barrels_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\offset_barrels'
dataset_file = r'C:\Users\DELL\Desktop\University\Data Structures and Algorithms\Project\Medium Articles\medium_articles.csv'
new_doc_output_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\new_docs\csv_files'
scraped_articles_file= r'C:\Users\DELL\Desktop\scraped_medium_articles.csv'
json_dir = r'C:\Users\DELL\Desktop\Search-Engine-DSA\new_docs\json_files'

def offset_barrel(barrel_number):
    return r'C:\Users\DELL\Desktop\Search-Engine-DSA\offset_barrels\inverted_barrel_{}.bin'.format(barrel_number)

def inverted_barrel(barrel_number):
    return r'C:\Users\DELL\Desktop\Search-Engine-DSA\inverted_barrels\inverted_barrel_{}.csv'.format(barrel_number)

# Dansh
#lexicon_file = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\lexicon.json'
#docMapper_file = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\Search-Engine-DSA\docmapper.json'
#forward_barrel_dir = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\forward_barrels'
# inverted_barrels_dir = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\inverted_barrels'
# offset_barrels_dir = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\Search-Engine-DSA NEW\offset_barrels'
# dataset_file = r'C:\Users\Sohail\Desktop\THIRD SEMESTER\DSA\FINAL PROJECT DSA\LEXICON\medium_articles.csv'
# new_doc_output_dir = r'Search-Engine-DSA NEW/Search-Engine-DSA/new_docs'
