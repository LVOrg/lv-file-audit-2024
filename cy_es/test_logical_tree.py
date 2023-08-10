# Class to define a node
# structure of the tree
class Node:
    def __init__(self, key):
        self.data = key
        self.left = None
        self.right = None


# Function to convert ternary
# expression to a Binary tree
# It returns the root node
# of the tree
__AND_OP__ = "and"
__OR_OP__ = "or"
def convert_expression(expression, i):
    if i >= len(expression):
        return None

    # Create a new node object
    # for the expression at
    # ith index
    root = Node(expression[i])

    i += 1

    # if current character of
    # ternary expression is '?'
    # then we add next character
    # as a left child of
    # current node
    if (i < len(expression) and
            expression[i] is __AND_OP__):
        root.left = convert_expression(expression, i + 1)

    # else we have to add it
    # as a right child of
    # current node expression[0] == ':'
    elif i < len(expression):
        root.right = convert_expression(expression, i + 1)
    return root


# Function to print the tree
# in a pre-order traversal pattern
def print_tree(root):
    if not root:
        return
    print(root.data, end=' ')
    print_tree(root.left)
    print_tree(root.right)


# Driver Code

string_expression = "a?b?c:d:e"
expr= "fx search 'aaa' and fy=1".split(' ')
root_node = convert_expression(expr, 0)
print_tree(root_node)

# This code is contributed
# by Kanav Malhotra
