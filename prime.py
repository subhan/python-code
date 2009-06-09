def square(n) : return n * n

def find_divisor(n, test_divisor):
	if square(test_divisor) > n: return n
	elif n % test_divisor == 0:return test_divisor
	else:return find_divisor(n, test_divisor+1)


def smallest_divisor(n): return find_divisor(n,2)

def prime(n): return n == smallest_divisor(n)


if __name__ == "__main__":
	#import doctest
	print prime(input("ENTER A NUMBER : "))
	
