def word_pattern (p, s): 
    words = s.split()  # s を空白で区切る
    pattern_words = p.split()  # パターン p を空白で区切る
    if len(words) != len(pattern_words):  # 単語数が異なる場合は False を返す
        return False
    word_to_pattern = {}  # 単語とパターンの対応を格納する辞書
    for word, pattern in zip(words, pattern_words):
        if pattern not in word_to_pattern:  # パターンがまだ登録されていない場合
                word_to_pattern[pattern] = word
        elif word_to_pattern[pattern] != word:  # パターンに対応する単語が異なる場合は False を返す
            return False
    return True
    
# テストケース
p1 = "abba"
s1 = "dog cat cat dog"
print(word_pattern(p1, s1))  # True

p2 = "abba"
s2 = "dog cat cat fish"
print(word_pattern(p2, s2))  # False
