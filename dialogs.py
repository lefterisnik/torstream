#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import Gtk


class Chooser(Gtk.FileChooserDialog):
    def __init__(self, title, parent, action = None, buttons = None):
        super(Chooser, self).__init__(title = title,
                                      parent = parent)
        if action:
            self.set_action(action)
        else:
            self.set_action(Gtk.FileChooserAction.OPEN)
    
        if buttons:
            self.add_buttons(buttons)
        else:
            self.add_buttons(Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OPEN,
                             Gtk.ResponseType.OK)
            
            
        self.set_default_response(Gtk.ResponseType.CANCEL)
    
    def showup(self):
        response = self.run()
        if response == Gtk.ResponseType.OK:
            filename = self.get_filename()
        self.destroy()
        return filename
        
