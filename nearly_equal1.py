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
	new_words = []

	#removing one char
	for i in range(len(word))
		nw = word[:i]+word[i+1])
		new_words.append(nw)

	print new_words

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
