def find_all_numbers(nums):
    num_set = set(nums)  # 配列 nums をセットに変換
    n = len(nums)
    missing_numbers = []
    # [1, n] の範囲の整数を反復処理
    for i in range(1, n + 1):
        if i not in num_set:  # セットに含まれていない整数を結果のリストに追加
            missing_numbers.append(i)
    return missing_numbers

# テストケース
nums1 = [4, 3, 2, 7, 8, 2, 3, 1]
print(find_all_numbers(nums1))  # [5, 6]

nums2 = [1, 2, 3, 4, 5]
print(find_all_numbers(nums2))  # []

nums3 = [1]
print(find_all_numbers(nums3))  # [2]
