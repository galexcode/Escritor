#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2011 - Thomas Chace <ithomashc@gmail.com>
# Copyright (C) 2004 - Iñigo Serna <inigoserna@telefonica.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os
import sys
import gtk
import gtksourceview2
import pango


######################################################################
##### global vars
MARK_CATEGORY_1 = 'one'
MARK_CATEGORY_2 = 'two'
DATADIR = '/usr/share'


######################################################################
##### error dialog
def error_dialog(parent, msg):
    dialog = gtk.MessageDialog(parent,
                               gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_OK,
                               msg)
    dialog.run()
    dialog.destroy()

######################################################################
##### load file
def load_file(buffer, path):
    buffer.begin_not_undoable_action()
    try:
        txt = open(path).read()
    except:
        return False
    buffer.set_text(txt)
    buffer.set_data('filename', path)
    buffer.end_not_undoable_action()

    buffer.set_modified(False)
    buffer.place_cursor(buffer.get_start_iter())
    return True


######################################################################
##### buffer creation
def open_file(buffer, filename):
    # get the new language for the file mimetype
    manager = buffer.get_data('languages-manager')

    if os.path.isabs(filename):
        path = filename
    else:
        path = os.path.abspath(filename)

    language = manager.guess_language(filename)
    if language:
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)
    else:
        print 'No language found for file "%s"' % filename
        buffer.set_highlight_syntax(False)

    load_file(buffer, path) # TODO: check return
    return True


######################################################################
##### Printing callbacks
def begin_print_cb(operation, context, compositor):
    while not compositor.paginate(context):
        pass
    n_pages = compositor.get_n_pages()
    operation.set_n_pages(n_pages)


def draw_page_cb(operation, context, page_nr, compositor):
    compositor.draw_page(context, page_nr)


######################################################################
##### Action callbacks
def numbers_toggled_cb(action, sourceview):
    sourceview.set_show_line_numbers(action.get_active())

def auto_indent_toggled_cb(action, sourceview):
    sourceview.set_auto_indent(action.get_active())
    
def insert_spaces_toggled_cb(action, sourceview):
    sourceview.set_insert_spaces_instead_of_tabs(action.get_active())
    sourceview.set_tab_width(4)
       

def new_view_cb(action, sourceview):
    window = create_view_window(sourceview.get_buffer(), sourceview)
    window.set_default_size(600, 480)
    window.show()
    

def print_cb(action, sourceview):
    window = sourceview.get_toplevel()
    buffer = sourceview.get_buffer()
    
    compositor = gtksourceview2.print_compositor_new_from_view(sourceview)
    compositor.set_wrap_mode(gtk.WRAP_CHAR)
    compositor.set_highlight_syntax(True)
    compositor.set_print_line_numbers(5)
    compositor.set_header_format(False, 'Printed on %A', None, '%F')
    filename = buffer.get_data('filename')
    compositor.set_footer_format(True, '%T', filename, 'Page %N/%Q')
    compositor.set_print_header(True)
    compositor.set_print_footer(True)
    
    print_op = gtk.PrintOperation()
    print_op.connect("begin-print", begin_print_cb, compositor)
    print_op.connect("draw-page", draw_page_cb, compositor)
    res = print_op.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, window)
     
    if res == gtk.PRINT_OPERATION_RESULT_ERROR:
        error_dialog(window, "Error printing file:\n\n" + filename)
    elif res == gtk.PRINT_OPERATION_RESULT_APPLY:
        print 'file printed: "%s"' % filename


######################################################################
##### Buffer action callbacks
def save_file_cb(action, buffer):
    chooser = gtk.FileChooserDialog('Save file...', None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        filename = chooser.get_filename()
        if filename:
			
            fil = open(filename, "w")
            fil.writelines(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), include_hidden_chars=True))
    chooser.destroy()
    
def open_file_cb(action, buffer):
    chooser = gtk.FileChooserDialog('Open file...', None,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        filename = chooser.get_filename()
        if filename:
            open_file(buffer, filename)
    chooser.destroy()

######################################################################
##### Actions & UI definition
buffer_actions = [
    ('Open', gtk.STOCK_OPEN, '_Open', '<control>O', 'Open a file', open_file_cb),
    ('Save', gtk.STOCK_OPEN, '_Save', '<control>S', 'Save a file', save_file_cb),
]

view_actions = [
    ('FileMenu', None, '_File'),
    ('ViewMenu', None, '_View'),
    ('Print', gtk.STOCK_PRINT, '_Print', '<control>P', 'Print the file', print_cb),
    ('NewWindow', gtk.STOCK_NEW, '_New Window', None, 'Create a new view of the file', new_view_cb),
]

toggle_actions = [
    ('ShowNumbers', None, 'Show _Line Numbers', None, 'Toggle visibility of line numbers in the left margin', numbers_toggled_cb, False),
    ('AutoIndent', None, 'Enable _Auto Indent', None, 'Toggle automatic auto indentation of text', auto_indent_toggled_cb, False),
    ('InsertSpaces', None, 'Insert _Spaces Instead of Tabs', None, 'Whether to insert space characters when inserting tabulations', insert_spaces_toggled_cb, False)
]

view_ui_description = """
<ui>
  <menubar name='MainMenu'>
    <menu action='FileMenu'>
      <menuitem action='NewWindow'/>
      <placeholder name="FileMenuAdditions"/>
      <separator/>
      <menuitem action='Print'/>
    </menu>
    <menu action='ViewMenu'>
      <separator/>
      <menuitem action='ShowNumbers'/>
      <menuitem action='AutoIndent'/>
      <menuitem action='InsertSpaces'/>
      <separator/>
    </menu>
  </menubar>
</ui>
"""

buffer_ui_description = """
<ui>
  <menubar name='MainMenu'>
    <menu action='FileMenu'>
      <placeholder name="FileMenuAdditions">
        <menuitem action='Open'/>
        <menuitem action='Save'/>
      </placeholder>
    </menu>
    <menu action='ViewMenu'>
    </menu>
  </menubar>
</ui>
"""

    
######################################################################
##### create view window
def create_view_window(buffer, sourceview=None):
    # window
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_border_width(1)
    window.set_title('Text')

    # view
    view = gtksourceview2.View(buffer)

    # action group and UI manager
    action_group = gtk.ActionGroup('ViewActions')
    action_group.add_actions(view_actions, view)
    action_group.add_toggle_actions(toggle_actions, view)

    ui_manager = gtk.UIManager()
    ui_manager.insert_action_group(action_group, 0)
    # save a reference to the ui manager in the window for later use
    window.set_data('ui_manager', ui_manager)
    accel_group = ui_manager.get_accel_group()
    window.add_accel_group(accel_group)
    ui_manager.add_ui_from_string(view_ui_description)

    # misc widgets
    vbox = gtk.VBox(0, False)
    sw = gtk.ScrolledWindow()
    sw.set_shadow_type(gtk.SHADOW_IN)
    menu = ui_manager.get_widget('/MainMenu')

    # layout widgets
    window.add(vbox)
    vbox.pack_start(menu, False, False, 0)
    vbox.pack_start(sw, True, True, 0)
    sw.add(view)

    # setup view
    view.modify_font(pango.FontDescription('Monospace 10'))

    # change view attributes to match those of sourceview
    if sourceview:
        action = action_group.get_action('ShowNumbers')
        action.set_active(sourceview.get_show_line_numbers())
        action = action_group.get_action('AutoIndent')
        action.set_active(sourceview.get_auto_indent())
        action = action_group.get_action('InsertSpaces')
        action.set_active(sourceview.get_insert_spaces_instead_of_tabs())
        if action:
            action.set_active(True)

    vbox.show_all()

    return window
    
    
######################################################################
##### create main window
def create_main_window(buffer):
    window = create_view_window(buffer)
    ui_manager = window.get_data('ui_manager')
    
    # buffer action group
    action_group = gtk.ActionGroup('BufferActions')
    action_group.add_actions(buffer_actions, buffer)
    ui_manager.insert_action_group(action_group, 1)
    # merge buffer ui
    ui_manager.add_ui_from_string(buffer_ui_description)

    # preselect menu checkitems
    groups = ui_manager.get_action_groups()
    # retrieve the view action group at position 0 in the list
    action_group = groups[0]
    action = action_group.get_action('ShowNumbers')
    action.set_active(True)
    action = action_group.get_action('AutoIndent')
    action.set_active(True)
    action = action_group.get_action('InsertSpaces')
    action.set_active(True)

    return window


######################################################################
if __name__ == '__main__':
    # create buffer
    lm = gtksourceview2.LanguageManager()
    buffer = gtksourceview2.Buffer()
    buffer.set_data('languages-manager', lm)

    # parse arguments
    if len(sys.argv) >= 2:
        open_file(buffer, sys.argv[1])
        
    # create first window
    window = create_main_window(buffer)
    window.set_default_size(600, 480)
    window.connect('delete-event', gtk.main_quit)
    window.show()
    
    gtk.main()
