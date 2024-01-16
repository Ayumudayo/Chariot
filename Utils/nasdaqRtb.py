import csv
import json

class Node:
    def __init__(self, key, value=None, color="RED"):
        self.key = key
        self.value = value
        self.left = self.right = self.parent = None
        self.color = color

class RedBlackTree:
    def __init__(self):
        self.NIL_LEAF = Node(None)
        self.NIL_LEAF.color = "BLACK"
        self.root = self.NIL_LEAF

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL_LEAF:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL_LEAF:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x

    def insert(self, key, value=None):
        new_node = Node(key, value)
        new_node.parent = None
        new_node.left = self.NIL_LEAF
        new_node.right = self.NIL_LEAF
        new_node.color = "RED"

        y = None
        x = self.root

        while x != self.NIL_LEAF:
            y = x
            if new_node.key < x.key:
                x = x.left
            else:
                x = x.right

        new_node.parent = y
        if y is None:
            self.root = new_node
        elif new_node.key < y.key:
            y.left = new_node
        else:
            y.right = new_node

        if new_node.parent is None:
            new_node.color = "BLACK"
            return

        if new_node.parent.parent is None:
            return

        self.fix_insert(new_node)

    def fix_insert(self, k):
        while k.parent.color == "RED":
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if u.color == "RED":
                    u.color = "BLACK"
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    self.left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right
                if u.color == "RED":
                    u.color = "BLACK"
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    self.right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = "BLACK"

    def search_by_key(self, key):
        return self._search_by_key_recursive(self.root, key)

    def _search_by_key_recursive(self, node, key):
        if node == self.NIL_LEAF or key == node.key:
            return node.value
        if key < node.key:
            return self._search_by_key_recursive(node.left, key)
        return self._search_by_key_recursive(node.right, key)

    def search_by_value(self, value):
        return self._search_by_value_recursive(self.root, value.lower())

    def _search_by_value_recursive(self, node, value):
        if node == self.NIL_LEAF:
            return []
        result = []
        if value in node.value.lower():
            result.append(node.key)
        result += self._search_by_value_recursive(node.left, value)
        result += self._search_by_value_recursive(node.right, value)
        return result
    
    def to_dict(self, node):
        if node == self.NIL_LEAF:
            return None
        return {
            "key": node.key,
            "value": node.value,
            "color": node.color,
            "left": self.to_dict(node.left),
            "right": self.to_dict(node.right)
        }

    def save_to_json(self, filename):
        serialized_tree = self.to_dict(self.root)
        with open(filename, "w") as json_file:
            json.dump(serialized_tree, json_file)

    def load_from_json(self, filename):
        with open(filename, "r") as json_file:
            tree_dict = json.load(json_file)
        self.root = self._deserialize(tree_dict)

    def _deserialize(self, tree_dict):
        if tree_dict is None:
            return self.NIL_LEAF

        node = Node(tree_dict["key"], tree_dict["value"], tree_dict["color"])
        node.left = self._deserialize(tree_dict["left"])
        node.right = self._deserialize(tree_dict["right"])
        if node.left != self.NIL_LEAF:
            node.left.parent = node
        if node.right != self.NIL_LEAF:
            node.right.parent = node

        return node
    
    def insert_from_csv(self, csv_filename):
        with open(csv_filename, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                symbol = row['Symbol']
                name = row['Name']
                self.insert(symbol, name)