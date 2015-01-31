#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import GObject
import libtorrent as lt
import time

class TorrentSession(GObject.GObject):
    __gsignals__ = {"stats_alert": (GObject.SIGNAL_RUN_FIRST, None,
                                   (GObject.TYPE_PYOBJECT,))
                   }

    def __init__(self):
        super(TorrentSession, self).__init__()
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.session.set_alert_mask(0xfffffff)
        
    def add_torrent(self, torrent, save):
        torrent = lt.bdecode(open(torrent, 'rb').read())
        torrent_info = lt.torrent_info(torrent)
        torrent_handle = self.session.add_torrent(torrent_info,
                         save,
                         storage_mode=lt.storage_mode_t.storage_mode_sparse)
        torrent_handle.set_sequential_download(True)
        #torrent_handle.auto_managed(False)
        return torrent_handle

    def remove_torrent(self, torrent_handle, delete=False):
        if delete:
            self.session.remove_torrent(torrent_handle, 1)
        else:
            self.session.remove_torrent(torrent_handle)

    def run(self):
        alert = self.session.pop_alert()
        if alert:
            if alert.category() == 2048:
                self.emit("stats_alert", alert.handle )
            
        return True
    



#print "cATEGORY: " + str(a.category()) + " wHAT: " + str(a.what()) + " mESSAGE: " + str(a.message()) + " sEEVERITY: " + str(a.severity_levels())
