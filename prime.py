def square(n) : 
	"""
	squares the given number
	>>> square(3)
	4
	>>> square(10)
	100
	"""
	return n * n

def find_divisor(n, test_divisor):
	"""
	finds a divisor for a given number
	>>> find_divisor(16,2)
	2
	>>> find_divisor(27,2)
	3
	>>> find_divisor(49,2)
	7
	"""
	if square(test_divisor) > n: return n
	elif n % test_divisor == 0:return test_divisor
	else:return find_divisor(n, test_divisor+1)


def smallest_divisor(n): 
	"""
	return's smallest divisor of given number
	>>> smallest_divisor(121)
	11
	>>> smallest_divisor(22)
	2
	>>> smallest_divisor(25)
	5
	"""
	return find_divisor(n,2)


def prime(n):
	"""
	test's the given number is prime or not
	>>> prime(3)
	True
	>>> prime(4)
	False
	>>> prime(103)
	True
	"""
	return n == smallest_divisor(n)


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	#print prime(input("ENTER A NUMBER : "))
	
