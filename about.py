#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class About:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("about.ui")
        self.dialog = self.builder.get_object("aboutdialog")
        self.dialog.run()
        self.dialog.destroy()