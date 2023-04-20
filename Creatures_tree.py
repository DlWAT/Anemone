# class for creating binary tree (that has key(node), left(node), right(node)) 
class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


# instead of linking nodes one by one, we can represent nodes in the form of tuple
# and we can use recursion technique to automate linking process.  
  
def parse_tuple(data):

    # check if the parameter passed is of type tuple and it's length is 3 (left node, key, right node)
    if isinstance(data, tuple) and len(data) == 3:
        node = TreeNode(data[1])
        node.left = parse_tuple(data[0])
        node.right = parse_tuple(data[2])
    
    # if it is the leaf node(last node) and it is also == None, then assign node = None
    elif data is None:
        node = None
    
    # if it is a leaf node(last node) and not != to None, then assign node = current value
    else:
        node = TreeNode(data)
    
    return node


def tree_to_tuple(node):
    if isinstance(node, TreeNode):
        # check if left and right node are equal to None if so, then it means it has no child nodes
        # and simply just return key node
        if node.left is None and node.right is None:
            return node.key
        
        # use recursion to iterate through each sub tree and get the left , key and right nodes
        return (
            tree_to_tuple(node.left),
            node.key,
            tree_to_tuple(node.right)
        )
    # else simply return node
    else:
        return node

    
tree_tuple = ((["x","y","vx","vy","weight","height","K","Strength","Freq"],3,None), 2, ((None, 3, 4), 5, (6, 7, 8)))
tree2 = parse_tuple(tree_tuple)
print(tree_to_tuple(tree2))


#                  2      
#       3                     5
#    1    None           3          7        
#                   None   4     6     8
