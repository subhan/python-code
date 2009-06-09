
def power(a,b):
	if b == 1:
		return a
	elif b % 2 != 0:
		return a * power(a, b/2)
	else:
		return power(a,b/2)* power(a, b/2)



if __name__ == "__main__":
	
	a = input("enter base : ")
	b = input("enter exponent : ")
	print power(a,b)
