

# Complete the findMergeNode function below.

#
# For your reference:
#
# SinglyLinkedListNode:
#     int data
#     SinglyLinkedListNode next
#
#
def findMergeNode(head1, head2):
    #get the count of the linked list
    def getcount(head):
        n = 0
        while head.next != None:
            head = head.next
            n+=1
        return n
    
    # get the common node
    def getnode(d, head1, head2):
        #traverse up to d (difference in length between 2 linked lists) so for the rest of the function, head1 and head2 start at same position in the linked list
        for i in range(d):
            head1 = head1.next
        
        #check the common node
        while head1 and head2:
            if head1 == head2:
                return head1.data
            else:
                head1 = head1.next
                head2 = head2.next
    
    c1 = getcount(head1)
    c2 = getcount(head2)
    
    #check the difference between counts of linked lists
    if c1 > c2:
        return getnode(c1-c2, head1, head2)
    else:
        return getnode(c2-c1, head2, head1)
    

