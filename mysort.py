from random import randint 

def shuffle_it(l):
	for i in range(1,5):
		r1 = randint(0,len(l)-1)
		r2 = randint(0,len(l)-1)
		l[r1],l[r2] = l[r2],l[r1]

	return l

def run(iteration,l):

	for i in xrange(1,101):
		if sorted(l) == shuffle_it(l):
			print "sorted list ",l
			print "sorted in %s iteration %s time"%(iteration,i)
	  		return True
	else:
	  return False

def main():
	i = 0
	l = []
	while i < 10:
		l.append(input("Enter Number : "))
		i += 1

	#l = [1,4,5,6,2,8,9,7,3,0]
	for i in range(len(l)):
		if not run(i,l):
			l.pop()			
			l.pop()			
		else:
			break

if __name__ == "__main__":
	main()
