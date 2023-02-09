

#
# Complete the 'deleteNode' function below.
#
# The function is expected to return an INTEGER_SINGLY_LINKED_LIST.
# The function accepts following parameters:
#  1. INTEGER_SINGLY_LINKED_LIST llist
#  2. INTEGER position
#

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#

def deleteNode(head, position):
    if position == 0:
        head = head.next
    else:
        temp = head
        count = 1
        while temp != None and count < position:
            temp = temp.next
            count +=1
        #delete the node when we're at the position
        temp.next = temp.next.next
        #by making the next element the next next value, this will delete the value at position
    
    return head
            
        

