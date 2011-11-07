import os

def count(f,word):
	content = open(f).read()
	return content.count(word)

if __name__ == "__main__":
	import sys
	f,word = sys.argv[1:]
	f = os.path.abspath(f)
	count = main(f,word)
	print "'%s' word encountered %s times in '%s' file"%(word,count,f)
