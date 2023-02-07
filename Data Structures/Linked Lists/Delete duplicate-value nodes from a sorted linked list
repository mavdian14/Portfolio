

#
# Complete the 'removeDuplicates' function below.
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

def removeDuplicates(head):
    # create a temp pointer
    temp = head
    
    while temp.next != None:
        if temp.data == temp.next.data:
            #delete the next node
            temp.next = temp.next.next
        else:
            temp = temp.next
    return head

