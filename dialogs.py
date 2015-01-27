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
            
        self.add_filters(self)
        self.set_default_response(Gtk.ResponseType.CANCEL)

    def add_filters(self, dialog):
        '''
        Add filter for torrent files to choose dialog
        :param dialog:
        :return: None
        '''
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Torrent files")
        #filter_text.add_mime_type("application/x-bittorrent")
        filter_text.add_pattern("*.torrent")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
    
    def showup(self):
        '''
        main function to run choose dialog and return filename
        :return: choosen filename
        '''
        filename = None
        response = self.run()
        if response == Gtk.ResponseType.OK:
            filename = self.get_filename()
        self.destroy()
        return filename
        
