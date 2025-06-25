# 色々（本来ここにはセンサの名前が入る）


# ここから説明文を追加する
# factorial(n)
# 階乗を計算する関数。

# fibonacci(n)
# フィボナッチ数列のn番目の項を計算する関数。

# conbinations(n, r)
# nCr (n個の中からr個を選ぶ組み合わせの数)を計算する関数。
# 使い方: combinations(5, 2) -> 10

####################################################################

def factorial(n):
  if n == 0:
    return 1
  else:
    return n * factorial(n-1)

def fibonacci(n):
  if n <= 1:
    return n
  else:
    return fibonacci(n-1) + fibonacci(n-2)

def combinations(n, r):
  if r < 0 or r > n:
    return 0
  if r == 0 or r == n:
    return 1
  if r > n // 2:
    r = n - r
  # 階乗を使用
  # numerator = factorial(n)
  # denominator = factorial(r) * factorial(n - r)
  # return numerator // denominator

  # 組み合わせの定義に基づき計算 (効率が良い)
  result = 1
  for i in range(r):
      result = result * (n - i) // (i + 1)
  return result


# ここからはdefinition内には書かない
# 書いてもいいけどちゃんとコメントアウトすること
# print(factorial(5))
# print(fibonacci(6))
# print(combinations(5, 2))
