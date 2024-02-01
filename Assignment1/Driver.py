'''
Driver code to implement Bplus tree
Author: Mantha Sai Gopal
Reg.no: 23358
'''

from BplusTree import *

file_path = "Text.txt"
output_file_path = 'Bplustree.dat'

with open(file_path, 'r') as file:
    words = file.read().split()

bplus_tree = BplusTree(order=3) 

current_offset = 0

for word in words:
    processed_word = word[:25].ljust(25, '\0')
    bplus_tree.insert(processed_word, key=current_offset)
    current_offset += len(word.encode('utf-8')) + 1

# Write to the file
bplus_tree.write_to_file(output_file_path)

search_value = "about"
search_value = search_value[:25].ljust(25, '\0')

# Create a new BplusTree instance for searching
search_bplus_tree = BplusTree(order=3)
    
# Use the search_and_print method
search_bplus_tree.search_and_print(search_value, data_file='Text.txt')

delete_value = "about"
delete_value = delete_value[:25].ljust(25, '\0')

# Call the delete method
bplus_tree.delete(delete_value)

# Write the updated tree to the file
bplus_tree.write_to_file(output_file_path)

# Perform a search again after deletion
search_bplus_tree.search_and_print(search_value, data_file='Text.txt')