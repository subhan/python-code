def fibonacci(n,cache={}):
	if n == 1 or n == 2:
		return n
	elif n in cache:
		return cache[n]
	else:
		cache[n] = fibonacci(n-1,cache)+fibonacci(n-2,cache)
		return cache[n]

if __name__ == "__main__":
	sum,n = 0,1

	while True:
		N = fibonacci(n)
		if sum + N > 4000000:
			break
		elif N % 2 == 0:
			sum += N
		n += 1

	print sum
