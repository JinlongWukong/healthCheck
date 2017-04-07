"""
	workflow
"""
import argparse
import logging
import os
import constants
import utility
import commands
import time
import paramiko
import sys

log = logging.getLogger(__name__)

class Workflow:

	def __init__(self, cmd, ip, user, passwd, port=22, auto=None):
		self.hostip = ip
		self.port = port
		self.username = user
		self.password = passwd
		self.host = commands.getoutput('uname -n')
		self.cmd_list = cmd
		self.automatic = auto
		self.confirm = None

	def set_confirm(self, value):
		self.confirm = value

	def set_automatic(self, value):
		self.automatic = value

	def list_cmd(self):
		log.info("List total health check command list\n")
		log.info("-----------------------------------------------------")
		for element in self.cmd_list:
			log.info("%s" % element.strip())
		log.info("-----------------------------------------------------\n")
		log.info('Total commands number: %s ' % len(self.cmd_list))

	def setup_ssh(self, ip):
		log.debug("Try ping %s" % ip)
		res = os.system('ping %s' % ip)
		if res == 0:
			try:
				log.debug("Ready to setup ssh connect to %s" % ip)
				#paramiko.util.log_to_file('paramiko.log')  
				self.ssh = paramiko.SSHClient()
				self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				self.ssh.connect(ip, self.port, self.username, self.password, timeout=5)
				log.debug("Setup ssh connect successfully")
				self.host = ip
				return True
			except:
				return False
				log.error ('Error: setup ssh to %s failed\n' % ip)
		else:
			return False
			log.error ("Error : %s is not pingnable\n" % ip)

	def remote_cmd(self, cmd):
		try:
			stdin, stdout, stderr = self.ssh.exec_command(cmd)
			stdin.write("Y")
			for out in stdout.readlines():
				print out,
			for err in stderr.readlines():
				print err,
			return 0
		except:
			log.error ('Error: remote execute %s failed\n' % cmd)
			return 1

	def start(self):
		print ("        Welcome to health check tools..\n")
		if self.setup_ssh(self.hostip) == False:
			log.error ("ssh error, health check quit..")
			return
		self.run()
		self.ssh.close()
		time.sleep(2)

	def run(self):

		self.list_cmd()
		print ("Are you sure to run above cmd list on target server? Yes or No: ")
		self.confirm = None
		while True:
			if self.confirm == 'Yes':
				yn = 'yes'
				self.confirm = None
				break
			elif self.confirm == 'No':
				yn = 'no'
				self.confirm = None
				log.info ("program quit..")
				return
			time.sleep(1)

		# Exective cmd list, interacive ask continue or not, or skip this command
		last = len(self.cmd_list) - 1
		index = 0
		while index < len(self.cmd_list):
			#val = os.system(constants.CLEAR)
			log.debug ("The clear command is: %s, it depends on server platform" % constants.CLEAR)
			log.info ("Below health check cmd will execute:")
			log.info ("-------------------------------------------------------------------")
			log.info ("%s" % self.cmd_list[index])
			time.sleep(2)
			val = self.remote_cmd(self.cmd_list[index])
			log.info ("-------------------------------------------------------------------")
			if val == 0:
				log.info ("%s health check finished\n" % self.cmd_list[index].strip('\n'))
			else:
				log.error ("%s health check failed\n" % self.cmd_list[index].strip('\n'))

			# if already last cmd, no need interacive confirm
			if index >= last:
				log.info ("Health check commands execute finished\n")
				break

			if self.automatic != None:
				log.info ("Wait %ss to continue..." % self.automatic)
				time.sleep(int(self.automatic))

			#interacive confirm to continue..
			while True:
				next = index + 1;
				if self.automatic != None:
					yn = 'yes'
				else:
					print ("The next cmd is %s, Do you want to continue? Yes or No or Skip: " % self.cmd_list[next].strip('\n'))
					self.confirm = None
					while True:
						if self.confirm == 'Yes' or self.automatic != None:
							yn = 'yes'
							self.confirm = None
							break
						elif self.confirm == 'No':
							yn = 'no'
							self.confirm = None
							break
						elif self.confirm == 'Skip':
							yn = 'skip'
							self.confirm = None
							break
						time.sleep(1)

				if yn in ['yes', 'y', 'Y', 'YES','']:
					break
				elif yn in ['no', 'n', 'N', 'NO']:
					log.info ("Exiting..")
					return False
				elif yn in ['skip', 's', 'S', 'SKIP']:
					log.info ("Skip this cmd: %s\n" % self.cmd_list[next].strip('\n'))
					index = index + 1
					if next >= last:
						log.info ("Health check commands execute finished\n")
						break
				else:
					log.info ("Must input yes or no or skip")
			index = index + 1
