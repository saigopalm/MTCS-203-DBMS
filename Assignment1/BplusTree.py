'''
This file contains the classes for Node and Bplus tree. 
Includes methods for inserting, deleting and updating Bplus tree.
Author: Mantha Sai Gopal
Reg.no: 23358
'''

import pickle
import math

class Node:
    def __init__(self, n): # n determines the number of.keys at a node
        self.order = n
        self.keys = []
        self.pointers = []
        self.isLeaf = False
        self.parent = None
        self.next = None

    # Insert at the leaf
    def insert_at_leaf(self, value, key):
        if (self.keys):
            temp1 = self.keys
            for i in range(len(temp1)):
                if (value == temp1[i]):
                    self.pointers[i].append(key)
                    break
                elif (value < temp1[i]):
                    self.keys = self.keys[:i] + [value] + self.keys[i:]
                    self.pointers = self.pointers[:i] + [[key]] + self.pointers[i:]
                    break
                elif (i + 1 == len(temp1)):
                    self.keys.append(value)
                    self.pointers.append([key])
                    break
        else:
            self.keys = [value]
            self.pointers = [[key]]
        
# key - pointer
# value - key
            
class BplusTree:
    def __init__(self, order):
        self.root = Node(order)
        self.root.isLeaf = True
 
    # Insert operation
    def insert(self, value, key):
        value = str(value)
        old_node = self.search(value)
        old_node.insert_at_leaf(value, key)
 
        if (len(old_node.keys) == old_node.order):
            node1 = Node(old_node.order)
            node1.isLeaf = True
            node1.parent = old_node.parent
            mid = int(math.ceil(old_node.order / 2)) - 1
            node1.keys = old_node.keys[mid + 1:]
            node1.pointers = old_node.pointers[mid + 1:]
            node1.next = old_node.next
            old_node.keys = old_node.keys[:mid + 1]
            old_node.pointers = old_node.pointers[:mid + 1]
            old_node.next = node1
            self.insert_in_parent(old_node, node1.keys[0], node1)
            
    def search(self, value):
        current_node = self.root
        while(current_node.isLeaf == False):
            temp2 = current_node.keys
            for i in range(len(temp2)):
                if (value == temp2[i]):
                    current_node = current_node.pointers[i + 1]
                    break
                elif (value < temp2[i]):
                    current_node = current_node.pointers[i]
                    break
                elif (i + 1 == len(current_node.keys)):
                    current_node = current_node.pointers[i + 1]
                    break
        return current_node
    
    # Inserting at the parent
    def insert_in_parent(self, n, value, ndash):
        if (self.root == n):
            rootNode = Node(n.order)
            rootNode.keys = [value]
            rootNode.pointers = [n, ndash]
            self.root = rootNode
            n.parent = rootNode
            ndash.parent = rootNode
            return
 
        parentNode = n.parent
        temp3 = parentNode.pointers
        for i in range(len(temp3)):
            if (temp3[i] == n):
                parentNode.keys = parentNode.keys[:i] + \
                    [value] + parentNode.keys[i:]
                parentNode.pointers = parentNode.pointers[:i +
                                                  1] + [ndash] + parentNode.pointers[i + 1:]
                if (len(parentNode.pointers) > parentNode.order):
                    parentdash = Node(parentNode.order)
                    parentdash.parent = parentNode.parent
                    mid = int(math.ceil(parentNode.order / 2)) - 1
                    parentdash.keys = parentNode.keys[mid + 1:]
                    parentdash.pointers = parentNode.pointers[mid + 1:]
                    value_ = parentNode.keys[mid]
                    if (mid == 0):
                        parentNode.keys = parentNode.keys[:mid + 1]
                    else:
                        parentNode.keys = parentNode.keys[:mid]
                    parentNode.pointers = parentNode.pointers[:mid + 1]
                    for j in parentNode.pointers:
                        j.parent = parentNode
                    for j in parentdash.pointers:
                        j.parent = parentdash
                    self.insert_in_parent(parentNode, value_, parentdash)


    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            self._write_node_to_file(file, self.root)

    def _write_node_to_file(self, file, node):
        pickle.dump(node, file)  # Serialize the node and write to file

        if not node.isLeaf:
            for child in node.pointers:
                self._write_node_to_file(file, child)


    def search_and_print(self, search_value, data_file):
        # Deserialize the tree from the data file
        with open("Bplustree.dat", 'rb') as file:
            self.root = pickle.load(file)

        # Search for the value in the tree
        node = self.search(str(search_value))

        # Find the index of the value in the keys list
        index = None
        for i, key in enumerate(node.keys):
            if str(search_value) == key:
                index = i
                break

        if index is not None:
            # Go to the same index in the pointers list
            offset = node.pointers[index][0]  # Assuming the offset is the first element in the list

            # Open the data file and go to the appropriate offset
            """with open(data_file, 'r') as data_file:
                data_file.seek(offset)
                line = data_file.readline().strip()

            # Print the entire line
            print(line)"""

            with open(data_file, 'r') as file:
                file.seek(offset)
                current_offset = file.tell()

                # Move the file pointer to the beginning of the current line
                while current_offset > 0 and file.read(1) != '\n':
                    file.seek(current_offset - 1)
                    current_offset -= 1

                # Now you reead the entire line
                line = file.readline().strip()
                print(line)

        else:
            print("Value does not exist in the tree.")

    def delete(self, value):
        value = str(value)
        leaf_node = self.search(value)

        if value not in leaf_node.keys:
            print(f"Key {value} does not exist in the tree.")
            return

        # Delete the key from the leaf node
        index = leaf_node.keys.index(value)
        leaf_node.keys.pop(index)
        leaf_node.pointers.pop(index)

        # If the root is a leaf and becomes empty after deletion, set it to None
        if leaf_node == self.root and not leaf_node.keys:
            self.root = None
            return

        # If the leaf node is underfilled, borrow or merge with neighbors
        if len(leaf_node.keys) < (leaf_node.order + 1) // 2:
            self.handle_underflow(leaf_node)

    def handle_underflow(self, node):
        # Borrow from left sibling if possible
        left_sibling = self.get_left_sibling(node)
        if left_sibling and len(left_sibling.keys) > (left_sibling.order + 1) // 2:
            self.borrow_from_left_sibling(node, left_sibling)
            return

        # Borrow from right sibling if possible
        right_sibling = self.get_right_sibling(node)
        if right_sibling and len(right_sibling.keys) > (right_sibling.order + 1) // 2:
            self.borrow_from_right_sibling(node, right_sibling)
            return

        # Merge with left sibling if possible
        if left_sibling:
            self.merge_with_left_sibling(node, left_sibling)
        # Merge with right sibling if possible
        elif right_sibling:
            self.merge_with_right_sibling(node, right_sibling)

    def get_left_sibling(self, node):
        if not node.parent:
            return None
        index = node.parent.pointers.index(node)
        if index > 0:
            return node.parent.pointers[index - 1]
        return None

    def get_right_sibling(self, node):
        if not node.parent:
            return None
        index = node.parent.pointers.index(node)
        if index < len(node.parent.pointers) - 1:
            return node.parent.pointers[index + 1]
        return None

    def borrow_from_left_sibling(self, node, left_sibling):
        # Borrow the last key-value pair from the left sibling
        borrowed_key = left_sibling.keys.pop()
        borrowed_pointer = left_sibling.pointers.pop()
        # Insert the borrowed key-value pair to the beginning of the node
        node.keys.insert(0, borrowed_key)
        node.pointers.insert(0, borrowed_pointer)
        # Update the parent's key for the node
        parent_index = node.parent.pointers.index(node)
        node.parent.keys[parent_index - 1] = borrowed_key

    def borrow_from_right_sibling(self, node, right_sibling):
        # Borrow the first key-value pair from the right sibling
        borrowed_key = right_sibling.keys.pop(0)
        borrowed_pointer = right_sibling.pointers.pop(0)
        # Insert the borrowed key-value pair to the end of the node
        node.keys.append(borrowed_key)
        node.pointers.append(borrowed_pointer)
        # Update the parent's key for the right sibling
        parent_index = node.parent.pointers.index(node)
        node.parent.keys[parent_index] = right_sibling.keys[0]

    def merge_with_left_sibling(self, node, left_sibling):
        # Merge node and left sibling
        parent_index = node.parent.pointers.index(node)
        del node.parent.pointers[parent_index]
        del node.parent.keys[parent_index - 1]
        left_sibling.keys.extend(node.keys)
        left_sibling.pointers.extend(node.pointers)
        # Update parent's next pointer
        left_sibling.next = node.next

        # Update parent's keys for the merged node
        if not node.parent.keys:
            # The merged node is the root, update the new root
            self.root = left_sibling
            left_sibling.parent = None
        else:
            # Update parent's key for the merged node
            node.parent.keys[parent_index - 1] = left_sibling.keys[-1]

    def merge_with_right_sibling(self, node, right_sibling):
        # Merge node and right sibling
        parent_index = node.parent.pointers.index(node)
        del node.parent.pointers[parent_index + 1]
        del node.parent.keys[parent_index]
        node.keys.extend(right_sibling.keys)
        node.pointers.extend(right_sibling.pointers)
        # Update node's next pointer
        node.next = right_sibling.next

        # Update parent's key for the merged node
        if not node.parent.keys:
            # The merged node is the root, update the new root
            self.root = node
            node.parent = None
        else:
            # Update parent's key for the merged node
            node.parent.keys[parent_index] = node.keys[-1]
