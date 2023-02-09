

#
# Complete the 'reverse' function below.
#
# The function is expected to return an INTEGER_DOUBLY_LINKED_LIST.
# The function accepts INTEGER_DOUBLY_LINKED_LIST llist as parameter.
#

#
# For your reference:
#
# DoublyLinkedListNode:
#     int data
#     DoublyLinkedListNode next
#     DoublyLinkedListNode prev
#
#

def reverse(head):
    while head.next != None:
        #swap the pointers
        head.next, head.prev, head = head.prev, head.next, head.next
        
    #changes to the tail node
    head.next, head.prev = head.prev, None
    
    return head

