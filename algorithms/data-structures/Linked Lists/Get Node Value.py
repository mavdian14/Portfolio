

#
# Complete the 'getNode' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_SINGLY_LINKED_LIST llist
#  2. INTEGER positionFromTail
#

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#

def getNode(head, positionFromTail):
    #initialize 2 pointers
    ptr1 = head
    ptr2 = head
    
    #traverse to the position from the head
    for i in range(positionFromTail):
        ptr1 = ptr1.next
    
    #traverse both pointers
    while ptr1.next != None:
        ptr1 = ptr1.next
        ptr2 = ptr2.next
    
    return ptr2.data

