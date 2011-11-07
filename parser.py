from xml.dom import minidom

xl = minidom.parse("Storage_Controllers.xml")

kl = xl.getElementsByTagName("RAID_LEVELS")
tag = kl[0]


print tag.nodeName
childs = tag.childNodes

for ch in childs:
	if ch.nodeType != 3:
		print ch.getAttribute("CLI")
