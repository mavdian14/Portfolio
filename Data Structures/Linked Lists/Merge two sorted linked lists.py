

# Complete the mergeLists function below.

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#
import sys
sys.setrecursionlimit(100000)

def mergeLists(head1, head2):
    #solution uses recursion
    
    # base case: both lists are NULL
    if head1 == None and head2 == None:
        return None
    
    #2nd case: 1 list is null
    if head1 == None:
        return head2
    elif head2 == None:
        return head1
    
    #general case
    if head1.data < head2.data:
        temp = head1
        temp.next = mergeLists(head1.next, head2)
    else:
        temp = head2
        temp.next = mergeLists(head1, head2.next)
    
    return temp

