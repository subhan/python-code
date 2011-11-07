import sys

def convert(num,number):
	l = {}
	n = 1
	while num > 0:
		if num%10 !=0:
			if n in number:
				l[n] = num%10
			elif n and n not in number:
				l[n/10] = l.get(n/10,0)+10
		n *= 10
		num /= 10
	return l

def concat(d,numbers):
	sum = 0
	for (k,v) in d.items():
		sum += k*v
	
	if sum in numbers:
		return numbers[sum]
	else:
		return False

def main(num):
	numbers = {
			1 : 'one', 2 : 'two', 3: 'three', 4: 'four', 5: 'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
			11 : 'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',
			18 : 'eighteen', 19:'nineteen',20:'twenty', 30 : 'thirty',40:'forty',50:'fifty',60:'sixty',70:'seventy',
			80: 'eighty',90:'ninety',100:'hundred',1000:'thousand',100000:'lac',10000000:'crore'

	}

	print "In Words : ",

	if num in numbers:
		print numbers[num]
		return 

	org = convert(num,numbers)
	keys = sorted(org.keys(),reverse=True)

	for k in keys:
		whole = concat(org,numbers)
		val = org.pop(k)
		if whole:
			print whole,
			return
		elif k*val in numbers:
			print val == 1 and 'one' or '',numbers[k*val],
		elif k not in numbers:
			k /=  10
			val *= 10
			if k in org:
				print numbers[val],
			else:
				print numbers[val],numbers[k],
		else:
			print numbers[val],numbers[k],

if __name__ == "__main__":
	main(int(sys.argv[1]))
