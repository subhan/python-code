
def remove_all(list):
	"""
	is this function returns empty list?
	"""
	for item in list:
		list.remove(item)
	return list

def remove_all_fix(list):
	"""
	make a copy of the orginial list,run a loop on duplicate
	"""
	dup_list = list[:]

	for item in dup_list:
		list.remove(item)
	return list
	

if __name__ == "__main__":
	Mylist = range(11)
	print remove_all(Mylist)
	Mylist = range(11)
	print remove_all_fix(Mylist)
	
