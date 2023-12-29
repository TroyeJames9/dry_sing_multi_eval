def find_substring_index(A, B, threshold=0.6):
    len_B = len(B)
    for i in range(len(A) - len_B + 1):
        substring = A[i:i + len_B]
        match_percentage = sum(1 for x, y in zip(substring, B) if x == y) / len_B
        if match_percentage >= threshold:
            return i
    raise ValueError(f"匹配字符串'{B}' 的头部索引 失败，请重试...")


A = 'qlbyznldrmbwmdxrzcwmxdcczhmzdlzwsdshmgrbpzfczhdhsqlqlqlwmwzyxmzdrdphqjmzdrdphqjqjqjj'
B = 'hmzdlzwxds'

result_index = find_substring_index(A, B, threshold=0.9)
print(result_index)

