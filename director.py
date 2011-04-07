#!/usr/bin/env python

import pygtk
import gtk
import vte

class Terminal:
	def __init__(self):
		self.window = gtk.Window()
		self.box = gtk.VBox()
		self.terminal = vte.Terminal()
		self.terminal.fork_command()
		#self.terminal.connect("window-title-changed")
		
		self.box.pack_start(self.terminal)
		self.window.add(self.box)
		
		self.window.show_all()

Terminal()
gtk.main()
