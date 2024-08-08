class ListNode:
     def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        result = ListNode(0)
        k = 0
        while l1 is not None or l2 is not None:
            digit1 = l1.val
            digit2 = l2.val

            sum = digit1 + digit2 + k
            k = sum // 10
            ost = sum % 10
            newNode = ListNode(ost)
            result = newNode
            result = result.next
            l1 = l1.next
            l2 = l2.next

        return result