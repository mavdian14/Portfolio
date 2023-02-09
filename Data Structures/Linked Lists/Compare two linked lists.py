

# Complete the compare_lists function below.

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#
def compare_lists(llist1, llist2):
    head1 = llist1
    head2 = llist2
    
    #check both head nodes aren't Null or empty
    while head1 != None and head2 != None:
        # checking data in each node is the same
        if head1.data == head2.data:
            head1 = head1.next
            head2 = head2.next
        else:
            return 0
    
    #Once we get to the final node at one of the linkedlists
    if head1 == None and head2 == None:
        return 1
    else:
        return 0
             
        

