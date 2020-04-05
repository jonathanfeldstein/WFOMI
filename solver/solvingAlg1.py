
def solvingAlg1(root):
    root.compute()
    if root.left != None:
        solvingAlg1(root.left)
    if root.right != None:
        solvingAlg1(root.right)
    
