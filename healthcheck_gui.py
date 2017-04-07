#!/usr/bin/env python
# $Id: listdir.py,v 1.8 2000/05/26 10:19:30 wesc Exp $
#
# listdir.py -- traverse directory tree
#
# created by wesc 00/02/20
#

import Tkinter, os, time, string, logging, threading
from Tkinter import *
import tkFileDialog
from ScrolledText import ScrolledText
import tkMessageBox
from workflow.workflow import Workflow
from workflow.workflow import utility
from workflow.workflow import constants

log = logging.getLogger(__name__)
FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(filename=os.path.join(os.getcwd(),'healthcheck_gui.log'),
					filemode='w',
					level=logging.DEBUG,
					format=FORMAT)

class GUI_hcheck:

    # do everything!
	def __init__(self):
		self.top = Tk()
		self.top.title('Health Check Tool')
		self.top.geometry('1400x800')

		#------- Label,Entry defination ----------#
		self.l1 = Label(self.top, text="IP:").grid(row=1, column=1, sticky="w")
		self.e1 = Entry(self.top)
		self.e1.grid(row=1, column=2,sticky="ew")
		self.l2 = Label(self.top, text="User:").grid(row=2, column=1, sticky="w")
		self.e2 = Entry(self.top)
		self.e2.grid(row=2, column=2,sticky="ew")
		self.l3 = Label(self.top, text="Passwd:").grid(row=3, column=1, sticky="w")
		self.e3 = Entry(self.top)
		self.e3['show'] = '*'
		self.e3.grid(row=3, column=2,sticky="ew")
		self.l4 = Label(self.top, text="Command pool:").grid(row=4, column=1, sticky="e")
		self.l5 = Label(self.top, text="To be run command:").grid(row=4, column=5, sticky="e")
		self.e4 = Entry(self.top, width=30)
		self.e4.grid(row=16, column=0, columnspan=3, sticky="ew")

		#------- Checkbutton defination ----------#
		self.cb1State = IntVar()
		self.cb1 = Checkbutton(self.top, variable=self.cb1State, text = "Always Yes", command=self.callCheckbutton)
		self.cb1.grid(row=21, column=16)

		#------- Listbox defination ----------#
		self.cmdfm = Frame(self.top)
		self.cmdsb = Scrollbar(self.cmdfm)
		self.cmdsb_x = Scrollbar(self.cmdfm,orient = HORIZONTAL)
		self.cmdsb.pack(side=RIGHT, fill=Y)
		self.cmdsb_x.pack(side=BOTTOM, fill=X)
		self.cmdls = Listbox(self.cmdfm, selectmode=EXTENDED, height=25, width=40, xscrollcommand=self.cmdsb_x.set, yscrollcommand=self.cmdsb.set)
		self.cmdsb.config(command=self.cmdls.yview)
		self.cmdsb_x.config(command=self.cmdls.xview)
		self.cmdls.pack(side=LEFT, fill=BOTH)
		self.cmdfm.grid(row=5, rowspan=10, column=0,columnspan=4,sticky="ew")
		self.db_file = os.path.join(os.getcwd(),'%s' % constants.DB_NAME)
		flist = utility.load_file(self.db_file)
		if flist != None:
			log.debug ("db file found, start load command")
			for element in flist:
				element = element.strip('\n')
				if element == '' or element.startswith('#'):
					continue
				self.cmdls.insert(END, element)
		else:
			log.debug ("db file doesn't existed, initail cmd")
			for element in constants.CMD_LIST_COMM:
				self.cmdls.insert(END, element)

		self.dirfm = Frame(self.top)
		self.dirsb = Scrollbar(self.dirfm)
		self.dirsb_x = Scrollbar(self.dirfm,orient = HORIZONTAL)
		self.dirsb.pack(side=RIGHT, fill=Y)
		self.dirsb_x.pack(side=BOTTOM, fill=X)
		self.dirs = Listbox(self.dirfm, selectmode=EXTENDED, height=25, width=40, xscrollcommand=self.dirsb_x.set,yscrollcommand=self.dirsb.set)
		self.dirsb.config(command=self.dirs.yview)
		self.dirsb_x.config(command=self.dirs.xview)
		self.dirs.pack(side=LEFT, fill=BOTH)
		self.dirfm.grid(row=5, rowspan=10, column=5,columnspan=4,sticky="ew")

		#------- Buttion defination ----------#
		# add command button
		self.b1 = Button(self.top,text=">>",width=6,borderwidth=3,relief=RAISED, command=self.move_cmd)
		self.b1.grid(row=7, column=4)
		# del command button
		self.b2 = Button(self.top,text="<<",width=6,borderwidth=3,relief=RAISED, command=self.del_cmd)
		self.b2.grid(row=8, column=4)
		# move up command button
		self.b3 = Button(self.top,text="up",width=6,borderwidth=3,relief=RAISED, command=self.up_cmd)
		self.b3.grid(row=7, column=10)
		# move down command button
		self.b4 = Button(self.top,text="down",width=6,borderwidth=3,relief=RAISED, command=self.down_cmd)
		self.b4.grid(row=8, column=10)
		# start command button
		self.b5 = Button(self.top,text="Start",bg='red',width=10,borderwidth=3,relief=RAISED, command=self.start_process)
		self.b5.grid(row=2, column=11)
		# yes button
		self.b6 = Button(self.top,text="Yes",width=6,borderwidth=3,relief=RAISED, command=self.set_confirm_yes)
		self.b6.grid(row=21, column=13)
		# No button
		self.b7 = Button(self.top,text="No",width=6,borderwidth=3,relief=RAISED, command=self.set_confirm_no)
		self.b7.grid(row=21, column=14)
		# Skip button
		self.b8 = Button(self.top,text="Skip",width=6,borderwidth=3,relief=RAISED, command=self.set_confirm_skip)
		self.b8.grid(row=21, column=15)
		# Add button
		self.b9 = Button(self.top,text="add cmd",width=10,borderwidth=3,relief=RAISED, command=self.add_command)
		self.b9.grid(row=15, column=1)
		# Del button
		self.b10 = Button(self.top,text="del cmd",width=10,borderwidth=3,relief=RAISED, command=self.del_command)
		self.b10.grid(row=15, column=2)
		# Manual button
		self.manual = False
		self.b11 = Button(self.top,text="Manual model",width=10,borderwidth=3,relief=RAISED, command=self.manual_mode)
		self.b11.grid(row=2, column=12)

		#------- ScrolledText defination ----------#
		self.sfm = Frame(self.top)
		self.console = ScrolledText(self.sfm,height=45, width=86,bg='black',fg='green',insertbackground='green')
		self.console['font'] = ('lucida console','10')
		self.console.bind("<Return>", self.process_input)
		self.console.pack()
		self.sfm.grid(row=4, rowspan=15, column=11,columnspan=10,sticky="ew")

		self.redir = redirect(self.console)
		sys.stdout = self.redir
		sys.stderr = self.redir
		self.fconsole = logging.StreamHandler(sys.stdout)
		self.fconsole.setLevel(logging.INFO)
		logging.getLogger('').addHandler(self.fconsole)

		#------- Menu defination ----------#
		self.menubar = Menu()
		# file menu
		self.fmenu = Menu()
		#self.fmenu.add_command(label = 'New',command=self.new_win)
		self.fmenu.add_command(label = 'Import cmd',command=self.load_cmd)
		self.fmenu.add_command(label = 'Export cmd',command=self.export_cmd)
		self.menubar.add_cascade(label = 'File', menu = self.fmenu)
		# edit menu
		self.emenu = Menu()
		self.cmenu = Menu()
		self.cvar = StringVar()
		for item in ['white/black', 'black/white', 'green/black']:
			self.cmenu.add_radiobutton(label = item, variable=self.cvar, value=item, command=self.sel_color_style)
		self.emenu.add_cascade(label = 'console style', menu = self.cmenu)
		self.emenu.add_command(label = 'reset cmd pool',command=self.reset_cmd_pool)
		self.menubar.add_cascade(label = 'Edit', menu = self.emenu)

		self.top['menu'] = self.menubar

	def new_win(self):
		#GUI_hcheck()
		pass

	def sel_color_style(self):
		log.debug ("select console color style: %s " % self.cvar.get())
		color = self.cvar.get()
		if color == 'white/black':
			self.console.config(bg='black',fg='white',insertbackground='white')
		elif color == 'black/white':
			self.console.config(bg='white',fg='black',insertbackground='black')
		elif color == 'green/black':
			self.console.config(bg='black',fg='green',insertbackground='green')

	def move_cmd(self):
		if self.cmdls.curselection() != ():
			for i in self.cmdls.curselection():
				if utility.elemet_exists(self.dirs.get(0,END), self.cmdls.get(i)) == None:
					self.dirs.insert(END,self.cmdls.get(i))
					log.debug ("move command %s" % self.cmdls.get(i))
		else:
			tkMessageBox.showwarning('Message', 'Please select at lease one item')

	def load_cmd(self):
		file = tkFileDialog.askopenfilename()
		flist = utility.load_file(file)
		if flist != None:
			self.dirs.delete(0,END)
			for element in flist:
				element = element.strip('\n')
				if element == '' or element.startswith('#'):
					continue
				if utility.elemet_exists(self.dirs.get(0,END), element) == None:
					self.dirs.insert(END, element)
		else:
			tkMessageBox.showerror('Message', 'import failed')

	def export_cmd(self):
		file = tkFileDialog.askopenfilename()
		if utility.export_file(self.dirs.get(0,END), file) == True:
			tkMessageBox.showinfo('Message', 'export finish')
		else:
			tkMessageBox.showerror('Message', 'export failed')

	def del_cmd(self):
		if self.dirs.curselection() != ():
			for i in self.dirs.curselection():
				self.dirs.delete(i)
		else:
			tkMessageBox.showwarning('Message', 'Please select at lease one item')

	def up_cmd(self):
		select = self.dirs.curselection()
		if (len(select)) >= 2:
			tkMessageBox.showwarning('Message', 'Only one select is supported')
			return
		log.debug ("move up select pos: %s" % str(select))
		if select != () and select != (0,):
			element = self.dirs.get(select)
			self.dirs.delete(select)
			self.dirs.insert((select[0] - 1), element)
			self.dirs.select_set(select[0] - 1)

	def down_cmd(self):
		select = self.dirs.curselection()
		if (len(select)) >= 2:
			tkMessageBox.showwarning('Message', 'Only one select is supported')
			return
		log.debug ("move down select pos: %s" % str(select))
		if select != () and select != (END,):
			element = self.dirs.get(select)
			self.dirs.delete(select)
			self.dirs.insert((select[0] + 1), element)
			self.dirs.select_set(select[0] + 1)

	def start_process(self):
		log.debug ("current thread total numbers: %d" % threading.activeCount())
		response = tkMessageBox.askokcancel('Message', 'Will start healthcheck, please click OK to continue, or cancel')
		if response == False:
			return
		th = threading.Thread(target=self.start_cmd)
		th.setDaemon(True)
		th.start()

	def start_cmd(self):
		self.manual = False
		cmd = list(self.dirs.get(0,END))
		if len(cmd) == 0:
			log.info ("To be run cmd numbers none, quit...")
			return
		log.debug ("fetch cmd list from GUI: %s" % cmd)
		(ip, port) = utility.getipinfo(self.e1.get())
		log.debug ("get ip infor-> ip: %s, port:%s" % (ip,port))
		if ip == False:
			log.error ("Given ip infor is wrong! The right ip address: xxx.xxx.xxx.xxx or IP:port ")
			return
		self.b5.config(state=DISABLED)
		self.b11.config(state=DISABLED)
		self.console.delete('1.0',END)
		try:
			self.wf = Workflow(cmd, ip, self.e2.get(), self.e3.get(), port)
			self.wf.start()
		except:
			pass
		self.b5.config(state=NORMAL)
		self.b11.config(state=NORMAL)

	def manual_mode(self):
		cmd = []
		(ip, port) = utility.getipinfo(self.e1.get())
		log.debug ("get ip infor-> ip: %s, port:%s" % (ip,port))
		if ip == False:
			log.error ("Given ip infor is wrong! The right ip address: xxx.xxx.xxx.xxx or IP:port ")
			return
		self.wf_manual = Workflow(cmd, ip, self.e2.get(), self.e3.get(), port)
		if self.wf_manual.setup_ssh(self.wf_manual.hostip) == False:
			log.error ("\nssh setup error! please check ip/user/passwd and network is okay")
			del self.wf_manual
			return
		self.console.delete('1.0',END)
		self.console.insert(END, "Switch to manual mode...\n\
Please input command directly after \">>> \"\n\n")
		self.prompt = ">>> "
		self.insert_prompt()
		self.manual = True
		self.b5.config(state=DISABLED)
		self.b11.config(state=DISABLED)

	def set_confirm_yes(self):
		try:
			self.wf.set_confirm('Yes')
		except AttributeError:
			log.debug("wf doesn't existed")
	def set_confirm_no(self):
		try:
			self.wf.set_confirm('No')
		except AttributeError:
			log.debug("wf doesn't existed")
	def set_confirm_skip(self):
		try:
			self.wf.set_confirm('Skip')
		except AttributeError:
			log.debug("wf doesn't existed")

	def callCheckbutton(self):
		try:
			if self.cb1State.get() == 1:
				self.wf.set_automatic(5)
			else:
				self.wf.set_automatic(None)
		except AttributeError:
			log.debug("wf doesn't existed")
			self.cb1.deselect()
			tkMessageBox.showwarning('Message', 'please press start button first')

	def saveinfo(self):
		pass

	def add_command(self):
		item = self.e4.get()
		if item != '':
			if utility.elemet_exists(self.cmdls.get(0,END), item) == None:
				self.cmdls.insert(END,item)
				self.cmdls.see(END)
				log.debug ("add new command %s" % item)
				self.save_command()
		else:
			tkMessageBox.showwarning('Message', 'entry can not empty')

	def del_command(self):
		if self.cmdls.curselection() != ():
			for i in self.cmdls.curselection():
				self.cmdls.delete(i)
				self.save_command()
		else:
			tkMessageBox.showwarning('Message', 'Please select at lease one item')

	def save_command(self):
		if utility.export_file(self.cmdls.get(0,END), self.db_file) != True:
			log.error ("save command pool failed")

	def reset_cmd_pool(self):
		log.debug ("start to reset command pool list")
		self.cmdls.delete(0,END)
		for element in constants.CMD_LIST_COMM:
			self.cmdls.insert(END, element)
		self.save_command()

	def insert_prompt(self):
		c = self.console.get("end-2c")
		if c != "\n":
			self.console.insert("end", "\n")
		self.console.insert("end", self.prompt, ("prompt",))
		#self.text.insert("end", self.prompt)
		# this mark lets us find the end of the prompt, and thus
		# the beggining of the user input
		self.console.mark_set("end-of-prompt", "end-1c")
		self.console.mark_gravity("end-of-prompt", "left")

	def process_input(self,event):
		index = self.console.index("end-1c linestart")
		line = self.console.get(index,'end-1c')
		log.debug ("last line: %s" % line)
		if self.manual == True:
			self.console.insert("end", "\n")
			command = self.console.get("end-of-prompt", "end-1c")
			command = command.strip()
			if command != '':
				if command == 'bye' or command == 'exit':
					log.info ("quit from manual mode...")
					self.wf_manual.ssh.close()
					self.manual = False
					self.b5.config(state=NORMAL)
					self.b11.config(state=NORMAL)
					return
				elif command == 'help':
					log.info ("This is used for run command on target server by ssh, for example: >>> df -h, >>> svcs -xv")
				elif self.wf_manual.remote_cmd(command) == 1:
					log.error ("command %s execute failed" % command)
			self.insert_prompt()
			self.console.see("end")
			# this prevents the class binding from firing, since we 
			# inserted the newline in this method
			return "break"
		else:
			if line == 'Yes' or line == 'y' or line == 'yes': 
				self.set_confirm_yes()
			elif line == 'No' or line == 'n' or line == 'no':
				self.set_confirm_no()
			elif line == 'Skip' or line == 's' or line == 'skip':
				self.set_confirm_skip()
			else:
				pass

class redirect(object):

	def __init__(self, text):
		self.output = text

	def write(self, string):
		self.output.insert(END, string)
		self.output.see("end")

GUI_hcheck()

Tkinter.mainloop()
