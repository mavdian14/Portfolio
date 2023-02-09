

# Complete the insertNodeAtTail function below.

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#
def insertNodeAtTail(head, data):
    # create a new node
    # SinglyLinkedListNode is the class of the pointer defined below
    node = SinglyLinkedListNode(data)
    
    #case 1: head pointer is NULL
    if head == None:
        head = node
    else:
        # case 2: insert node at tail
        temp = head
        while temp.next != None:
            #iterate thru linked list to get to the tail
            temp = temp.next
        # at the tail insert node
        temp.next = node
    
    return head

