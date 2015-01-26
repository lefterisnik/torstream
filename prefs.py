#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import Gtk
import vlc
import datetime


class Prefs:
    def __init__(self, parent, media_player, media):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('prefs.ui')
        self.builder.connect_signals(self)

        self.prefs_dialog = self.builder.get_object('prefs_dialog')
        self.prefs_label_title = self.builder.get_object('prefs_label_title')
        self.prefs_label_fn = self.builder.get_object('prefs_label_fn')
        self.prefs_label_time = self.builder.get_object('prefs_label_time')
        self.prefs_label_channel = self.builder.get_object('prefs_label_channel')
        self.prefs_label_resolution = self.builder.get_object('prefs_label_resolution')
        self.prefs_dialog.set_transient_for(parent)
        self.prefs_dialog.set_modal(True)
        
        
        self.prefs_label_title.set_label(media.get_mrl().split('/')[-1])
        self.prefs_label_fn.set_label(media.get_mrl().replace('file://',''))
        hours, milliseconds = divmod(media.get_duration(), 3600000)
        minutes, milliseconds = divmod(milliseconds, 60000)
        seconds = float(milliseconds) / 1000
        s = "%i:%02i:%02i" % (hours, minutes, seconds)
        self.prefs_label_time.set_label(str(s))
        self.prefs_label_resolution.set_label("%sx%s" %media_player.video_get_size())
        self.prefs_label_channel.set_label(str(media_player.audio_get_channel()))
        

        self.prefs_dialog.show_all()


    def on_prefs_dialog_delete_event(self, widget, event):
        self.prefs_dialog.destroy()

    def on_prefs_button_close_clicked(self, widget):
        self.prefs_dialog.destroy()
        
