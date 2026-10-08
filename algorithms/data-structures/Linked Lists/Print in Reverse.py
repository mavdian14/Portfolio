

#
# Complete the 'reversePrint' function below.
#
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

def reversePrint(head):
    #solve with recursion
    #base case
    if head == None:
        return
    reversePrint(head.next)
    print(head.data)
