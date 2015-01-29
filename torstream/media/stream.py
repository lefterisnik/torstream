#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import Gtk, Gdk, GdkX11, GObject
from core import vlc
import os
import prefs
import datetime


class Stream:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('media/ui/stream.ui')
        self.builder.connect_signals(self)

        self.stream_main_window = self.builder.get_object('stream_main_window') 
        self.stream_main_window_fullscreen = False
        self.stream_main_menu_bar = self.builder.get_object('stream_main_menu_bar')
        self.stream_main_box = self.builder.get_object('stream_main_box')        
        self.stream_main_toolbar = self.builder.get_object('stream_main_toolbar')
        self.stream_main_drawing_area = self.builder.get_object('stream_main_drawing_area')
        self.stream_main_drawing_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.stream_main_toolbar_play = self.builder.get_object('stream_main_toolbar_play')
        self.stream_main_toolbar_scale = self.builder.get_object('stream_main_toolbar_scale')
        self.stream_main_toolbar_adjust = self.builder.get_object('stream_main_toolbar_adjust')
        
        self.media_player = vlc.MediaPlayer()
        
        self.cssProvider = Gtk.CssProvider()
        self.cssProvider.load_from_path('media/ui/gtkStyledButtonTest.css')
        self.screen = Gdk.Screen.get_default()
        self.styleContext = Gtk.StyleContext()
        self.styleContext.add_provider_for_screen(self.screen, self.cssProvider,Gtk.STYLE_PROVIDER_PRIORITY_USER)
        
        self.stream_main_window.show_all()
             

    #################################################################################################
    #                                                                                               #
    #                                   Main functions                                              #
    #                                                                                               #
    #################################################################################################  
    def load_media(self, media):
        self.media = vlc.Media(media)
        self.media.parse()
        self.stream_main_toolbar_scale.set_range(0, self.media.get_duration()*0.001)
        self.stream_main_toolbar_scale.set_increments(10,10)
        self.media_player.video_set_mouse_input(False)
        self.media_player.set_xwindow(self.stream_main_drawing_area.get_property('window').get_xid())
        self.play_media()
    
    def play_media(self):
        if self.media_player.get_media() is None:
            self.media_player.set_media(self.media) 
        self.media_player.play()
        GObject.timeout_add(1000, self.update_seek)
        self.media_player.audio_set_volume(int(self.stream_main_toolbar_adjust.get_value()*100))
        self.stream_main_toolbar_play.set_stock_id(Gtk.STOCK_MEDIA_PAUSE)

    def stop_media(self):
        self.media_player.stop()
        self.stream_main_toolbar_play.set_stock_id(Gtk.STOCK_MEDIA_PLAY)   

    def pause_media(self):
        self.media_player.pause()
        self.stream_main_toolbar_play.set_stock_id(Gtk.STOCK_MEDIA_PLAY) 

    def fullscreen_media(self):
        self.stream_main_window_fullscreen = True
        self.stream_main_menu_bar.hide()
        self.stream_main_toolbar.hide()
        self.stream_main_window.fullscreen()

    def unfullscreen_media(self):
        self.stream_main_window_fullscreen = False
        self.stream_main_menu_bar.show()
        self.stream_main_toolbar.show()
        self.stream_main_window.unfullscreen()

    def subtitle_media(self, subtitle):
        self.media_player.video_set_subtitle_file(subtitle)

    def update_seek(self):
        if self.media_player.get_state() == vlc.State.Playing:
            self.stream_main_toolbar_scale.set_value(self.media_player.get_time()*0.001)            
            return True
        elif self.media_player.get_state() == vlc.State.NothingSpecial:
            return False
            
    #################################################################################################
    #                                                                                               #
    #                                   Main callbacks                                              #
    #                                                                                               #
    #################################################################################################  
    def on_stream_main_menu_open_activate(self, widget):
        dialog = Gtk.FileChooserDialog("Επιλογή αρχείου...", self.stream_main_window, 
                                        Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.load_media(dialog.get_filename())
        dialog.destroy()

    def on_stream_main_toolbar_play_clicked(self, widget):
        if self.media_player.get_state() == vlc.State.NothingSpecial or self.media_player.get_state() == vlc.State.Stopped:
            dialog = Gtk.FileChooserDialog("Επιλογή αρχείου...", self.stream_main_window, 
                                            Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.load_media(dialog.get_filename())
            dialog.destroy()
        elif self.media_player.get_state() == vlc.State.Playing:
            self.pause_media()
        elif self.media_player.get_state() == vlc.State.Paused:
            self.play_media()
      
    def on_stream_main_toolbar_stop_clicked(self, widget):
        self.stop_media()
        
    def on_stream_main_toolbar_fullscreen_clicked(self, widget):
        self.fullscreen_media()
        
    def on_stream_main_drawing_area_button_press_event(self, widget, event):
        if event.button == 1 and event.type == 5 and not self.stream_main_window_fullscreen:
            self.fullscreen_media() 
        elif event.button == 1 and event.type == 5 and self.stream_main_window_fullscreen:
            self.unfullscreen_media()
            

    def on_stream_main_toolbar_subs_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Επιλογή αρχείου υποτιτλών...", self.stream_main_window, 
                                        Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.subtitle_media(dialog.get_filename())
        dialog.destroy()

    def on_stream_main_toolbar_preferences_clicked(self, widget):
        prefs.Prefs(self.stream_main_window, self.media_player, self.media )
    
    def on_stream_main_toolbar_scale_format_value(self, scale, value):
        formatted_value = datetime.timedelta(seconds=value)
        return str(formatted_value).split('.')[0]  

    def on_stream_main_toolbar_scale_change_value(self, range, scroll, value):
        seek_time = value/0.001
        self.media_player.set_time(int(seek_time))     

    def on_stream_main_toolbar_adjust_value_changed(self, widget, value):
        self.media_player.audio_set_volume(int(value*100))

    def on_stream_main_menu_close_activate(self, widget):
        self.stream_main_window.destroy()

    def on_stream_main_window_delete_event(self, widget, event):
        self.stream_main_window.destroy()

