

#
# Complete the 'reverse' function below.
#
# The function is expected to return an INTEGER_SINGLY_LINKED_LIST.
# The function accepts INTEGER_SINGLY_LINKED_LIST llist as parameter.
#

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#

def reverse(head):
    # initialize 3 pointers
    prev = None
    cur = head
    nxt = head.next
    
    while cur != None:
        #change the direction of the nodes
        nxt = cur.next
        cur.next = prev
        #shifting the nodes, essentially a left rotation between these 3 nodes
        prev = cur
        cur = nxt
    head = prev
    return head

