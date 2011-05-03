import socket 
import sys
import time
import re
import logging, string
import threading
from common_modules import get_info

logging.basicConfig(level=logging.INFO)

import ANSI

ESC = chr(27)
ENTER = chr(13)
F10 = ESC + '0'
F1 = ESC + '1'
F2 = ESC + '2'
DOWN = ESC + '[B'
UP = ESC + '[A'

class KThread(threading.Thread):
	"""A subclass of threading.Thread, with a kill()
	method."""
	def __init__(self, *args, **keywords):
		threading.Thread.__init__(self, *args, **keywords)
		self.killed = False
	
	def start(self):
		"""Start the thread."""
		self.__run_backup = self.run
		self.run = self.__run # Force the Thread toinstall our trace.
		threading.Thread.start(self)
	
	def __run(self):
		"""Hacked run function, which installs the
		trace."""
		sys.settrace(self.globaltrace)
		self.__run_backup()
		self.run = self.__run_backup

	def globaltrace(self, frame, why, arg):
		if why == 'call':
			return self.localtrace
		else:
			return None

	def localtrace(self, frame, why, arg):
		if self.killed:
			if why == 'line':
				raise SystemExit()
		return self.localtrace

	def kill(self):
		self.killed = True




#buffer class
class StringBuffer:
	strBuff = ''
	def write(self,input):
		self.strBuff += input

	def __str__(self):
		temp = self.strBuff
		self.strBuff = ""
		return temp

	def __repr__(self):
		temp = self.strBuff
		self.strBuff = ""
		return temp

def read_args(term,buff):
	while True:
		data = term.recv(1024)
		buff.write(data)


class dell_rc(object):
	Rows = 26
	Cols = 80
	def get_bios_version(self):
		self.update()
		pattern = re.compile('BIOS Version(:?)+\s?((?:\w*\S?)+)')
		results = re.search(pattern, self.buffer.dump())
		if results:
			return results.groups()[1]    
	def __init__(self,port=0):
		self.buffer = ANSI.ANSI(self.Rows, self.Cols)
		self.record = file('record.txt', 'wb')

		serial = get_info('serial_info')

		self.conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.conn.connect((serial['host'],623))

		self.buff = StringBuffer() 
		self.thread = KThread(target=read_args,args=(self.conn,self.buff)) 
		self.thread.start()

		if serial['type'].find('remote') >= 0:
			self.conn.send("%s\r\n"%serial['user'])
			time.sleep(1)
			self.conn.send("%s\r\n"%serial['password'])
			time.sleep(1)

		self.conn.send("3\r\n")
		time.sleep(1)
		self.conn.send("%s\r\n"%get_info('sys_info','drac_ip'))
		time.sleep(1)
		self.conn.send("root\r\n")
		time.sleep(1)
		self.conn.send("calvin\r\n")
		time.sleep(1)
		self.conn.send("\r\n")
		time.sleep(1)

		logging.debug('Connected to serial port 0')

	def _write(self, input):
		if input[0] == chr(27):
			logging.debug('Sending data <ESC>%s' % input[1:])
		else:
			logging.debug('Sending data %s' % input)
		self.conn.send(input+ '\r\n')

	def _read(self):
		#if len(output) > 0:
		#    logging.debug('Recieved %i bytes' % len(output))
		return str(self.buff)

	def update(self, input=None, reads=2):
		if input:
			self._write(input)
		while reads > 0:
			reads = reads - 1
			output = self._read()
			self.record.write(output)
			self.record.flush()
			self.buffer.write(output)
			time.sleep(0.1)

	def process_help(self, diffedScreen):
		#UGH...removes the box and blank lines
		lines = diffedScreen.split('\n')
		lines = [l[1:-1] for l in lines]
		lines = [l.strip() for l in lines]
		lines = [l for l in lines if l != '']
		lines = lines[1:-1]
		return " ".join(lines)

	def Boot_To_USC(self, device_num = 1):
		self.reboot()
		self.boot_usc(device_num)
		print "searching for launcher shell....."
		while True:
			self.update()
			#area = "\n".join(self.buffer.get_region(60, 50, 25, 15))
			#if re.search("ystem_services.*startup.nsh.*endif.*", area):
			area = self.buffer.dump()
			if re.search(r"idrac1:\\Tools>\s", area):
				print "#"*30,area,"#"*30
				logging.info('Launching USC GUI')
				time.sleep(5)
				self.update(ENTER)
				self.update("Launcher.efi /n")
				logging.info('Setup screen is fully drawn')
				return True

		return False

	def PercH200Controller(self,controller,raid,raid_info):
		ctrl_c = chr(3)
		pattern = re.compile('Press Ctrl-C to start Dell.*H200.*Configuration Utility')
		key_sent = False
		kPress = 0
		while True:
			self.update()
			area = self.buffer.dump()
			if pattern.search(area,re.I):
				if kPress < 2:
					print "Pressed <CTRL><C>"
					self.update(ctrl_c)
				key_sent = True
				kPress += 1	
			elif key_sent and re.search(r'Adapter\s.*PERC H200I', area):
				print "Controller available %s"%controller
				self.update(DOWN)
				break
	
		for i in xrange(60):	
			self.update()
			area = self.buffer.dump()
			raid_level = re.findall('TypeRAID(\d+)xx',area)
			if raid_level:
				break
	
		print "serial info : \n%s"%area
		area = area.replace(' ','')
		raid_level = re.findall('TypeRAID(\d+)xx',area)
		if raid_level:
			raid_level = raid_level[0].strip()
			if raid_level == raid[1:]:
				print "Raid Level : %s in Controller Properites --> PASS"%raid
			else:
				return """Unable to find expected Raid Level : %s in Controller Properites\n\t
				Got different Raid Level :%s --> FAIL"""%(raid,raid_level),True
		else:
			return "Unable to find Raid Level '%s' in Controller Properties --> FAIL "%raid,True

		config_size = raid_info.get('raid size')
		size = re.findall('Size.GB.(\d+)xx',area)
		if size and config_size.strip().find(size[0].strip()) >= 0:
			print "Virtual Disk Size : %s in Controller"%size
		else:
			return "Unable to find the virtual disk size '%s', '%s' in Controller properties"%(size[0].strip(), config_size.strip()),True 
		
		return "Virtual disk details verified successfully in controller properties",False 

	def Perc6_i_Controller(self,controller,raid,raid_info):
		ctrl_r = chr(18)
		pattern = re.compile('Press <Ctrl><R> to Run Configuration Utility')
		key_sent = False
		kPress = 0
		while True:
			self.update()
			area = self.buffer.dump()
			if pattern.search(area,re.I):
				if kPress < 2:
					print "Pressed <CTRL><R>"
					self.update(ctrl_r)
				key_sent = True
				kPress += 1	
			elif key_sent and re.search(r'F1-Help', area):
				break

		print "serial info : \n%s"%area
		raid_level = re.findall('RAID Level\s\s:(\s\d+)\s+xx\s',area)
		if raid_level:
			raid_level = raid_level[0].strip()
			if raid_level == raid:
				print "Raid Level : %s in Controller Properites --> PASS"%raid
			else:
				print """Unable to find expected Raid Level : %s in Controller Properites\n\t
				Got different Raid Level :%s --> FAIL"""%(raid,raid_level)
		else:
			print "Unable to find Raid Level '%s' in Controller Properties"%r1

		if re.search(controller,area):
			print "Controller available %s"%controller
		else:
			print "Unable to find the Controller Name : %s"%controller
		
		size = raid_info.get('raid size')
		if re.search('Size.*:.*%s.*GB'%size,area):
			print "Virtual Disk Size : %s in Controller"%size

		return area

	def RaidControllerSetUp(self,controller_type='PERC H200',raid='r1',raid_info={}):
		print "Searching for Controller Properites option ..."
		
		keys = {
			'PERC.*H200':('C',3,self.PercH200Controller),
			'PERC.*6/i':('R',18,self.Perc6_i_Controller)
		}
	
		for k in keys:
			if re.search(k,controller_type):
				ctrl_key,key_char,func = keys[k]

		return func(controller_type,raid,raid_info)

	def boot_usc(self,device_num = 1):
		logging.info('Looking for USC Setup prompt...')
		kPress = 0
		while True:
			self.update()
			area = "\n".join(self.buffer.get_region(2, 60, 2, 100))

			if re.search('F10.*=.*System Services', area):
				logging.info('Found prompt, sending F10')
				if kPress < 2:
					self.update(F10)
				kPress += 1	
				

			if re.search('ering System Services',area):
				return

	def do_setup(self):
		logging.info('Looking for BIOS Setup prompt...')
		while True:
			self.update()
			area = "\n".join(self.buffer.get_region(0, 60, 1, 80))
			if re.search('F2.*=.*Setup', area):
				logging.info('Found prompt, sending F2')
				self.update(F2)
			elif re.search('Entering System Setup', area):
				logging.info('Entering System Setup')
				while True:
					self.update()
					area = "\n".join(self.buffer.get_region(23, 60, self.Cols, 77))
					if re.search('F1.{0,4}Help', area):
						logging.info('Setup screen is fully drawn')
						return 0

	def do_bmc_setup(self):
		logging.info('Looking for BMC Setup prompt...')
		key_sent = False
		pattern = re.compile('Press <Ctrl-E> for Remote Access Setup')
		while True:
			self.update()
			area = self.buffer.dump()
			if pattern.search(area):
				logging.info('Found prompt, sending Ctrl+E')
				self.update(chr(5))
				key_sent = True
			elif key_sent and re.search('F1=Help', area):
				logging.info('Setup screen is fully drawn')
				return 0

	def get_screenshot(self):
		return self.buffer.pretty()

	def reboot(self):
		logging.info('Sending Ctrl+Alt+Del')
		rebootCmd = ESC + 'R'+ ESC + 'r' + ESC + 'R'
		self._write(rebootCmd)
		#time.sleep(2)
		#self._write(rebootCmd)

	def get_asset_tag(self):
		self.update()
		pattern = re.compile('Asset Tag: (\w*)')
		results = re.search(pattern, self.buffer.dump())
		if results:
			return results.groups()[0]

	def get_service_tag(self):
		self.update()
		pattern = re.compile('Service Tag: (\w*)')
		results = re.search(pattern, self.buffer.dump())
		if results:
			return results.groups()[0]
		
	def get_system_id(self):
		self.update()
		pattern = re.compile('PowerEdge (\w*)')
		results = re.search(pattern, self.buffer.dump())
		if results:
			return ('PowerEdge %s' %results.groups()[0])

	def get_help_text(self):
		before = self.buffer.pretty()
		b.update(F1, 5)
		after = self.buffer.pretty()
		b.update(F1, 5)

		diffedScreen = self.diff_screens(before, after)
		help = self.process_help(diffedScreen)
		return help

	def get_popup_menu(self):
		before = self.buffer.pretty()
		b.update(' ', 5)
		after = self.buffer.pretty()
		self.update(ESC, 5)
		diff = self.diff_screens(before, after)
		pattern = re.compile('((?:[A-Z]\w*\s?)+)\.+\s?((?:\S+\s?)+)')
		results = pattern.findall(diff)

		return results

	def find_box(self, screen0, screen1):
		rows0 = [row for row in screen0.split('\n') if row != '']
		rows1 = [row for row in screen1.split('\n') if row != '']
		
		# Grab the columns
		cols0 = ["".join(column) for column in map(None, *rows0)]
		cols1 = ["".join(column) for column in map(None, *rows1)]
		
		# Isolate the row numbers that changed
		diff_rows = [row[0] for row in enumerate(zip(rows0, rows1)) if row[1][0] != row[1][1]]

		# Isolate the columns that changed
		diff_cols = [col[0] for col in enumerate(zip(cols0, cols1)) if col[1][0] != col[1][1]]

		return (diff_cols[0], diff_rows[0], diff_cols[-1], diff_rows[-1])


	def diff_screens(self, screen0, screen1):
		"""
		Take two screens and isolate the areas that changed
		"""
		# Split the rows into lists for processing
		rows0 = [row for row in screen0.split('\n') if row != '']
		rows1 = [row for row in screen1.split('\n') if row != '']
		
		# Grab the columns
		cols0 = ["".join(column) for column in map(None, *rows0)]
		cols1 = ["".join(column) for column in map(None, *rows1)]
		
		# Isolate the row numbers that changed
		diff_rows = [row[0] for row in enumerate(zip(rows0, rows1)) if row[1][0] != row[1][1]]

		# Isolate the columns that changed
		diff_cols = [col[1] for col in zip(cols0, cols1) if col[0] != col[1]]

		# Transpose the columns
		diff_cols = ["".join(column) for column in map(None, *diff_cols)]

		# Put it back into a string and return
		return '\n'.join(diff_cols[diff_rows[0]:diff_rows[-1]+1])

	def get_option(self, start, end):
		pattern = re.compile('((?:[A-Z]\w*\s?)+)\.+\s?((?:\S+\s?)+)')
		text = self.buffer.get_region(start[0], start[1], end[0], end[1])
		text = "\n".join(text)
		print text
		results = pattern.findall(text)
		if results:
			results = [(x.strip(),y.strip()) for x,y in  results]
		try:
			return (results[0][0], results[0][1])
		except IndexError:
			return text.strip()
		except:
			print "Unexpected error:", sys.exc_info()[0]
			raise
			 
	def find_boot_order(self, x0=2, y0=None, x1=78, y1=None, boot_seq=0):
		old_result = -1
		self.update(DOWN, 2)
		line = self.buffer.get_cursor_pos()[0]        
		self.update(UP, 2)
		line=line-1
		set=0
		while True:
			text = self.buffer.get_region(line, x0, line, x1)
			text = "\n".join(text)
			tem_str1 = text.strip('x')
			tem_str= tem_str1.rstrip('a ')
			if old_result == line:
				raise StopIteration
			elif tem_str.find('<ENTER>') != -1:
				if tem_str.find('Boot Sequence') != -1:
					boot_seq=1              
				before = self.buffer.pretty()
				self.update(' ', 5)
				after = self.buffer.pretty()
				coords = self.find_box(before, after)
				for option in self.find_boot_order(coords[0],coords[1],coords[2],coords[3], boot_seq):
					yield option             
				if boot_seq==1:
					yield 2
				self.update(ESC, 5)
			else:
				if set == 1:
					self.update(' ', 5)
					yield 1
				if boot_seq == 1 and tem_str.find('*') != -1:
					self.update(' ', 5)
					set=1
				old_result = line
				yield 0              
			self.update(DOWN, 2)
			line = self.buffer.get_cursor_pos()[0]


	def boot_diag(self,device_num = 1):
		logging.info('Looking for BIOS Setup prompt...')
		while True:
			self.update()
			area = "\n".join(self.buffer.get_region(0, 60, 1, 80))
			if re.search('F2.*=.*Setup', area):
				logging.info('Found F2 prompt')
				break
		while True:
			self.update()
			area = self.buffer.dump()
			if re.search('No boot device', area):
				logging.warning('No boot device available')
				log_name=('logs\Log_Device_%d.txt' % device_num)
				f=file(log_name,'w')
				area = 'No boot device available'
				f.write(area)
				f.close()              
				print 
				break
			if re.search('PXE Environment', area):
				logging.info('Boot into PXE')
				self.update('4', 2)
				self.update(ENTER, 2)
			if re.search('Enter option', area):
				logging.info('Customer Diagnostics loaded')
				self.update(DOWN, 2)
				self.update('4', 2)
				logging.info('Extended Dell diags Running')
				self.run_cmd('ddgui /b /olog.txt /clk /np')
				self.get_logs(device_num)
				print 
				break

	def run_cmd(self, cmd=''):
		pattern = re.compile('(\S*\s*)')
		res = pattern.findall(cmd)
		for s in res:
			self.update(s)
		self.update(ENTER)

	def save_bios(self):
		while True:
			before = self.buffer.pretty()
			self.update(ESC, 5)
			after = self.buffer.pretty()
			diffedScreen = self.diff_screens(before, after)
			help = self.process_help(diffedScreen)
			if help.find('Save Changes and Exit') != -1:
				self.update(' ', 5)
				logging.info('BIOS Settings got Saved')
				return    

	def change_boot_order(self, device_num = 1):
		self.boot_diag(device_num)
		self.reboot()
		self.do_setup()
		for opt in self.find_boot_order():
			if opt == 1:
				self.save_bios()              
				return '0'
			if opt == 2:
				return '1'


	def get_logs(self, device_num = 1):
		while True:
			self.update(ENTER)
			area = self.buffer.dump()
			if re.search('Diag ',area):
				logging.info('Capturing the Dell diagnostics logs')      
				self.run_cmd('type log.txt /p')
				area=self.buffer.dump()
				log_name=('logs\Log_Device_%d.txt' % device_num)
				f=file(log_name,'w')               
				while True:
					area = "\n".join(self.buffer.get_region(24,0,25,80))                                      
					if re.search('Strike a key',area):
						area= "\n".join(self.buffer.get_region(0,0,23,80))
						f.write(area)
						f.write("\n")
						f.write("\n")                       
						self.update()                       
						self.update(ENTER)
					else:
						area = "\n".join(self.buffer.get_region(0,0,24,80))                   
						f.write(area)
						f.close()
						self.update()
						logging.info('Finished capturing logs')
						return 0
