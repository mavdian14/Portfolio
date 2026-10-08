

#
# Complete the 'insertNodeAtPosition' function below.
#
# The function is expected to return an INTEGER_SINGLY_LINKED_LIST.
# The function accepts following parameters:
#  1. INTEGER_SINGLY_LINKED_LIST llist
#  2. INTEGER data
#  3. INTEGER position
#

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#

def insertNodeAtPosition(head, data, position):
    #create a new node
    node = SinglyLinkedListNode(data)
    # case where head pointer is null
    if head == None:
        head = node
    else:
        temp = head
        #skip the nodes to reach position
        count = 1
        while temp != None and count < position:
            temp = temp.next
            count +=1
            #insert the node when we reach the position
        node.next = temp.next
        temp.next = node
        
    return head
