#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import Gtk, Gdk, GdkX11, GObject
from common import dialogs
from core import session
from media import stream
import about
import os
import datetime
import logging
import subprocess

logging.getLogger().setLevel(logging.INFO)

class Torrent:
    def __init__(self, torrent_handle = None):
        self.torrent_handle = torrent_handle
        self.name = self.torrent_handle.name()
        self.save = self.torrent_handle.save_path()
        self.torrent_info = torrent_handle.get_torrent_info()
        self.total_size = str((self.torrent_info.total_size()/1024)/1024)
        self.num_pieces = str(self.torrent_info.num_pieces())
        self.piece_length = str(self.torrent_info.piece_length())


class TorrentGui:
    def __init__(self):
        logging.info('Initialize TorrentSession instance')
        self.session = session.TorrentSession()

        logging.info('Connect GUI to event of TorrentSession')
        self.session.connect("stats_alert", self.on_session_stats_alert)

        GObject.timeout_add(1, self.session.run)
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui/main.ui')
        self.builder.connect_signals(self)

        self.window = self.builder.get_object('window') 
        self.liststore_torrent = self.builder.get_object('liststore_torrent')
        self.liststore_summary = self.builder.get_object('liststore_summary')
        self.treeview_torrent = self.builder.get_object('treeview_torrent')
        self.notebook_torrent = self.builder.get_object('notebook_notebook')
        self.general_title = self.builder.get_object('general_title')
        self.general_added = self.builder.get_object('general_added')
        self.general_size = self.builder.get_object('general_size')
        self.general_save = self.builder.get_object('general_save')
        self.pieces_num_pieces = self.builder.get_object('pieces_num_pieces')
        self.pieces_piece_length = self.builder.get_object('pieces_piece_length')
        
        ## Popup menu
        self.popup = Gtk.Menu()
        self.play = Gtk.MenuItem("Αναπαραγωγή")
        self.open_folder = Gtk.MenuItem("Ανοίγμα φακέλου")
        self.popup.append(self.play)
        self.popup.append(self.open_folder)

        ## Popup menu callback
        self.play.connect('activate', self.on_play_activate)
        self.open_folder.connect('activate', self.on_open_folder_activate)

        self.window.show_all()
   
    def populate_treeview(self, torrent_handle):
        torrent = Torrent(torrent_handle)
        self.liststore_torrent.append([torrent, torrent.name, "", "", "", "",
                                      "", "", torrent.save])
    def populate_notebook(self, torrent):
        self.general_title.set_label(torrent.name)
        self.general_size.set_label(torrent.total_size)
        self.general_save.set_label(torrent.save)
        self.pieces_num_pieces.set_label(torrent.num_pieces)
        self.pieces_piece_length.set_label(torrent.piece_length)
    
## Libtorrent Callbacks

    ## Stat alert for update gui
    def on_session_stats_alert(self, widget, torrent_handle):
        for row in self.liststore_torrent:
            if row[0].name == torrent_handle.name():
                status = torrent_handle.status()
                row[2] = str(status.download_rate/1024) + " KB/s" 
                row[3] = str(status.upload_rate/1024) + " KB/s"
                row[4] = "%s (%s)" %(status.num_peers, status.list_peers)
                row[5] = "%s (%s)" %(status.num_seeds, status.list_seeds)
                row[6] = str(status.finished_time)
                row[7] = str(status.progress * 100)
     

## Torrent Gui Callbacks

    ## Main Window Callbacks
    def on_window_delete_event(self, widget, event):
        self.window.destroy()
        exit()

    ## Main Menu Callbacks
    def on_menuitem_open_activate(self, widget):
        torrent = dialogs.Chooser("Επιλογή αρχείου...", self.window).showup()
        if torrent is None:
            return
        save = dialogs.Chooser("Επιλογή φακέλου αποθήκευσης...",
                                self.window,
                                Gtk.FileChooserAction.SELECT_FOLDER).showup()
        if save is not None:
            # dont forget logging
            self.populate_treeview(self.session.add_torrent(torrent, save))
        return
    
    def on_menuitem_exit_activate(self, widget):
        self.window.destroy()
        exit()

    def on_menuitem_about_activate(self, widget):
        about.About()

    ## Main Treeview Callbacks
    def on_treeview_torrent_button_press_event(self, widget, event):
        if event.button == 1:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.treeview_torrent.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                self.treeview_torrent.grab_focus()
                self.treeview_torrent.set_cursor( path, col, 0)
                self.populate_notebook(self.liststore_torrent[path][0])
            return True
        elif event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.treeview_torrent.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                self.treeview_torrent.grab_focus()
                self.popup.popup( None, None, None, None, event.button, time)
                self.popup.show_all()
            return True

    ## Main Menu Callbacks
    def on_play_activate(self, widget):
        treeselection = self.treeview_torrent.get_selection()
        treemodel, iter = treeselection.get_selected()
        if iter:
            path = treemodel.get_path(iter)
            stream.Stream().load_media(self.liststore_torrent[path][8])

    def on_open_folder_activate(self, widget):
        treeselection = self.treeview_torrent.get_selection()
        treemodel, iter = treeselection.get_selected()
        if iter:
            path = treemodel.get_path(iter)
            subprocess.Popen(['nautilus', self.liststore_torrent[path][8]])

    ## Main Toolbar Callbacks
    def on_toolbar_torrent_properties_clicked(self, widget):
        pass

    def on_toolbar_start_torrent_clicked(self, widget):
        treeselection = self.treeview_torrent.get_selection()
        treemodel, iter = treeselection.get_selected()
        if iter:
            path = treemodel.get_path(iter)
            print path, self.liststore_torrent[path][0].torrent_handle
            self.liststore_torrent[path][0].torrent_handle.resume()

    def on_toolbar_pause_torrent_clicked(self, widget):
        treeselection = self.treeview_torrent.get_selection()
        treemodel, iter = treeselection.get_selected()
        if iter:
            path = treemodel.get_path(iter)
            self.liststore_torrent[path][0].torrent_handle.pause()

    def on_toolbar_remove_torrent_clicked(self, widget):
        treeselection = self.treeview_torrent.get_selection()
        treemodel, iter = treeselection.get_selected()
        if iter:
            path = treemodel.get_path(iter)
            remove = dialogs.RemoveTorrent(message_format='Είστε σίγουροι ότι θέλετε να προχωρήσετε στην αφαίρεση του torrent;').showup()
            if remove:
                torrent_handle = self.liststore_torrent[path][0].torrent_handle
                self.liststore_torrent.remove(iter)
            else:
                return

            remove = dialogs.RemoveTorrent(message_format='Είστε σίγουροι ότι θέλετε να προχωρήσετε στην αφαίρεση των μεταφορτομένων αρχείων;').showup()
            if remove:
                self.session.remove_torrent(torrent_handle, True)
            else:
                self.session.remove_torrent(torrent_handle)

    def on_toolbar_add_torrent_clicked(self, widget):
        torrent = dialogs.Chooser("Επιλογή αρχείου...", self.window).showup()
        if torrent is None:
            return
        save = dialogs.Chooser("Επιλογή φακέλου αποθήκευσης...",
                                self.window, 
                                Gtk.FileChooserAction.SELECT_FOLDER).showup()
        if save is not None:
            logging.info("Save folder: %s" %(save))
            self.populate_treeview(self.session.add_torrent(torrent, save))
        return


if __name__ == '__main__':
    logging.info('Program starts. Initialize GUI instance.')
    TorrentGui()
    Gtk.main()
