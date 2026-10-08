

#
# Complete the 'sortedInsert' function below.
#
# The function is expected to return an INTEGER_DOUBLY_LINKED_LIST.
# The function accepts following parameters:
#  1. INTEGER_DOUBLY_LINKED_LIST llist
#  2. INTEGER data
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

def sortedInsert(head, data):
    # create a new node
    node = DoublyLinkedListNode(data)
    
    # case 1: if list is empty
    if head == None:
        head = node
    
    #case 2: insert before head
    elif data < head.data:
        node.next = head
        #.prev refers to node before the head
        head.prev = node
        head = node
    
    #case 3: insert at specific position or at the end
    else:
        cur = head
        # traverse to the specific position
        while cur.next != None and cur.data < data:
            cur = cur.next
        
        #insert at the end
        if cur.next == None and cur.data < data:
            cur.next = node
            node.prev = cur
        
        #insert at specific position
        else:
            previous = cur.prev
            #make changes for previous node
            previous.next = node
            node.prev = previous
            #make changes for current node
            node.next = cur
            cur.prev = node
    
    return head
        
    

