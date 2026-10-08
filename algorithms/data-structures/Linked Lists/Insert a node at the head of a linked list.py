

# Complete the insertNodeAtHead function below.

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#
def insertNodeAtHead(head, data):
    # create the new node
    node = SinglyLinkedListNode(data)
    
    #case 1 if head pointer isnt NULL, make the new node the head pointer
    if head != None:
        node.next = head
    
    return node

