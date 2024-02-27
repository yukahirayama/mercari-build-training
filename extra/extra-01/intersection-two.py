class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def getIntersectionNode(headA, headB):
    # リストの長さを取得
    def get_length(head):
        length = 0
        while head:
            length += 1
            head = head.next
        return length
    
    lenA = get_length(headA)
    lenB = get_length(headB)
    
    # 長いリストを短いリストと同じ長さまで進める
    while lenA > lenB:
        headA = headA.next
        lenA -= 1
    while lenB > lenA:
        headB = headB.next
        lenB -= 1
    
    # 2つのリストを同時に進め、交差するノードを見つける
    while headA != headB:
        headA = headA.next
        headB = headB.next
    
    return headA  # 交差するノードまたは None を返す

# テストケース
# 交差するノード: 8
#    4 → 1 → 8 → 4 → 5
#                  ↑
#          5 → 6 → 1
headA = ListNode(4)
headA.next = ListNode(1)
headA.next.next = ListNode(8)
headA.next.next.next = ListNode(4)
headA.next.next.next.next = ListNode(5)

headB = ListNode(5)
headB.next = ListNode(6)
headB.next.next = ListNode(1)
headB.next.next.next = headA.next.next

print(getIntersectionNode(headA, headB).val)

# 交差しない場合: None
# 1 → 9 → 1 → 2 → 4
#                ↑
#          3 → 2
headC = ListNode(1)
headC.next = ListNode(9)
headC.next.next = ListNode(1)
headC.next.next.next = ListNode(2)
headC.next.next.next.next = ListNode(4)

headD = ListNode(3)
headD.next = ListNode(2)

print(getIntersectionNode(headC, headD))
