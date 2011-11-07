import re
import math

def myrange(start=0,n=0):
	i = start
	while i < n:
		yield i
		i += 1

def main():
	str_num = raw_input("Enter a num : ")
	if re.search(".+[024685]$",str_num):
	#if re.search("(.+[024685]$)|(^1.*[02486]1$)",str_num):
		print "not prime : ",str_num
		return 

	num = long(str_num)
	for i in myrange(2,long(num**0.5)+1L):
		if num % i == 0:
			print "not prime : ",num
			print "divider : ",i
			break
	else:
		print "prime num : ",num

def isprime(num):
	
	if num == 2 or num == 1:
		return True

	if num % 2 == 0:
		return False

	for i in myrange(3,math.sqrt(num)+1L):
		rem = num % i
		if rem != 1 and isprime(rem):
			return True
		elif rem == 0:
			return False
	else:
		return False


if __name__ == "__main__":
	#main()
	import sys
	print isprime(long(sys.argv[1]))
