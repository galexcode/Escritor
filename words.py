#!/usr/bin/python
# Copyright 2011 Thomas Chace

import gtk
import abiword

class Editor(gtk.Window):
    
    def setup(self):
        self.abi.view_print_layout()
        self.abi.set_show_margin(True)
        self.abi.set_font_name("Liberation Sans")
        self.abi.set_font_size("10")
        
    def on_quit(self, c, d):
        self.abi.file_save()
        gtk.main_quit()
        
    def on_open(self, c):
        self.abi.file_open()
        self.setup()
        
    def on_save(self, c):
        self.abi.file_save()
        
    def on_undo(self, c):
        self.abi.undo()
        
    def on_redo(self, c):
        self.abi.redo()
        
    def on_bold(self, c):
        self.abi.toggle_bold()
    
    def on_italic(self, c):
        self.abi.toggle_italic()
        
    def on_underline(self, c):
        self.abi.toggle_underline()

    def on_alignc(self, c):
        self.abi.align_center()
        
    def on_alignj(self, c):
        self.abi.align_justify()
        
    def on_alignl(self, c):
        self.abi.align_left()
        
    def on_alignr(self, c):
        self.abi.align_right()
        
    def toolbar(self):
        self.actions = gtk.ActionGroup("Actions")
        self.actions.add_actions([
            ("new", gtk.STOCK_NEW, "_New", "<ctrl>N", None, self.on_open),
            ("open", gtk.STOCK_OPEN, "_Open", "<ctrl>I", None, self.on_open),
            ("save", gtk.STOCK_SAVE, "_Save", "<ctrl>S", None, self.on_save),
            ("undo", gtk.STOCK_UNDO, "_Undo", "<ctrl>Z", None, self.on_undo),
            ("redo", gtk.STOCK_REDO, "_Redo", "<ctrl>Y", None, self.on_redo),
            ("bold", gtk.STOCK_BOLD, "_Bold", "<ctrl>B", None, self.on_bold),
            ("italic", gtk.STOCK_ITALIC, "_Italic", "<ctrl>I", None, self.on_italic),
            ("underline", gtk.STOCK_UNDERLINE, "_Underline", "<ctrl>U", None, self.on_underline),
            ("alignl", gtk.STOCK_JUSTIFY_LEFT, "_Left", None, None, self.on_alignl),
            ("alignc", gtk.STOCK_JUSTIFY_CENTER, "_Center", None, None, self.on_alignc),
            ("alignj", gtk.STOCK_JUSTIFY_FILL, "_Justify", None, None, self.on_alignj),
            ("alignr", gtk.STOCK_JUSTIFY_RIGHT, "_Right", None, None, self.on_alignr),
        ])

        self.ui_def = """
            <toolbar name="toolbar_format">
            <toolitem action="new" />
            <toolitem action="open" />
            <toolitem action="save" />
            <separator/>
            <toolitem action="undo" />
            <toolitem action="redo" />
            <separator/>
            <toolitem action="bold" />
            <toolitem action="italic" />
            <toolitem action="underline" />
            <separator/>
            <toolitem action="alignl" />
            <toolitem action="alignc" />
            <toolitem action="alignr" />
            <toolitem action="alignj" />
        </toolbar>"""

    def __init__(self):
        gtk.Window.__init__(self)
        self.abi = abiword.Canvas()
        
        self.set_title("Words")
        self.set_default_size(800, 600)
        self.connect('delete-event', self.on_quit)

        ui = gtk.UIManager()
        self.toolbar()
        ui.insert_action_group(self.actions)
        ui.add_ui_from_string(self.ui_def)

        box = gtk.VBox()

        box.pack_start(ui.get_widget("/toolbar_format"), False)
        box.pack_start(self.abi, True)
        
        self.add(box)
        self.show_all()
        self.setup()

if __name__ == '__main__':
    Editor()
    gtk.main()
