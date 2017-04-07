"""
 Utility
"""
import re
import os
import logging

log = logging.getLogger(__name__)

def elemet_exists(list, element):
	position = None
	element = element.strip().split()
	for x in list:
		y = x.strip().split()
		if y == element:
			position = list.index(x)
			break

	return position

def ip_check(ip_str):
	pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
	if re.match(pattern, ip_str):
		return True
	else:
		return False

def is_num_by_except(num):
	try:
		int(num)
		return True
	except ValueError:
		print ("%s ValueError" % num)
		return False

def confirm_yn(message):
	while True:
		yn = raw_input("%s: " % message)
		if yn in ['yes', 'y', 'Y', 'YES']:
			return True
		elif yn in ['no', 'n', 'N', 'NO']:
			return False
		else:
			print ("Must input yes or no")

def getipinfo(ip):

	if len(ip.split(':')) == 2 and ip_check(ip.split(':')[0]) == True:
		return (ip.split(':')[0], int(ip.split(':')[1]))
	elif len(ip.split(' ')) == 1 and ip_check(ip) == True:
		return (ip, 22)

	return (False, False)

def export_file(config, file):
	#file=os.path.join(os.getcwd(),'monitor_tool_config')
	log.debug ("Export configuration into file : %s" % file)
	try:
		fo = open(file,"w")
		fo.truncate()
		for i in config:
			fo.write(i)
			fo.write("\n")
		fo.close
		log.debug ("Export configuration successfully")
		return True
	except Exception, e:
		log.error ("%s" % str(e))

def load_file(file):
	#file=os.path.join(os.getcwd(),'monitor_tool_config')
	log.debug ("Load configuration from file %s" % file)
	try:
		fo = open(file,"r")
		config = fo.readlines()
		fo.close
		log.debug ("Load configuration successfully")
		return config
	except Exception, e:
		log.error ("%s" % str(e))
		return None

def time2sec(sTime):

	if len(sTime.split(':')) == 2:
		sTime = '00:' + sTime
	p = "^(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$"
	cp = re.compile(p)
	try:
		mTime = cp.match(sTime)
	except TypeError:
		return "[InModuleError]:time2itv(sTime) invalid argument type"

	if mTime:
		t = map(int,mTime.group(1,2,3))
		return 3600*t[0]+60*t[1]+t[2]
	else:
		return "[InModuleError]:time2itv(sTime) invalid argument value"

def parseTime(stdout):

	if len(stdout.rsplit()) == 2:
		x = stdout.rsplit()
		pid_start_time = x[0]
		y = x[1]
		if len(y.split('-')) == 2:
			z = y.split('-')
			pid_run_time_str = "%s days %s " % (z[0], z[1])
			sec = time2sec(z[1])
			pid_run_time_sec = 3600 * 24 * int(z[0]) + int(sec)
		elif len(y.split('-')) == 1:
			z = y.split('-')
			pid_run_time_str = "%s" % (z[0])
			pid_run_time_sec = time2sec(z[0])
		else:
			return None
		return (pid_start_time, pid_run_time_str, pid_run_time_sec)
	else:
		return None
