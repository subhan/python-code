def permutate(word):
	if not word:
		return [word]
	else:
		temp = []
		for i in range(len(word)):
			part = word[:i] + word[i+1:]
			for m in permutate(part):
				st = word[i:i+1] + m
				if st not in temp:
					temp.append(st)
		return temp


def mutate(word,search=None):
	chars = 'abcdefghijklmnopqrstuvwxyz'
	l = [i for i in word]

	#adding one extra char to the word
	comb1 = []
	for c in chars:
		comb1 += permutate(word+c)

	if search and search in comb1:
		return True

	#replaceing any one char in word with other
	comb2 = []
	for i in range(len(word)):
		temp = l[:]
		temp.remove(temp[i])
		for c in chars:
			comb2 += permutate("".join(temp)+c)

	if search and search in comb2:
		return True

	comb3 = []
	#remove one single element from the word
	for i in range(len(word)):
		temp = l[:]
		temp.remove(temp[i])
		comb3 += permutate("".join(temp))

	if search and search in comb3:
		return True
	elif search:
		return False

	return comb1+comb2+comb3

def nearly_equal(word,word1):

	if word == word1:
		print "both are equal"
		return 
	elif len(word) > len(word1):
		word,word1 = word1,word

	#words_list = mutate(new)
	if mutate(word,word1):
		print "Both are nearly equal"
	else:
		print "Both are not equal"

if __name__ == "__main__":
	import sys
	#mutate(sys.argv[1])
	nearly_equal(sys.argv[1],sys.argv[2])
