#!/usr/bin/python3
# This program is licensed under BSD 2.

from os import path
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('WebKit', '3.0')
from gi.repository import GObject, Gst, Gtk, Gdk, WebKit
from gi.repository import GdkX11, GstVideo

from Streaming import *
from DeviceConfig import DeviceConfig
from VideoConfig import VideoConfig
from AudioConfig import AudioConfig


class Player(Gtk.Window):

    def __init__(self, ip="127.0.0.1", port="8554"):

        Gtk.Window.__init__(self, title="Video Display")
        self.set_default_size(800, 600)
        self.set_default_geometry(800, 600)
        self.connect('destroy', self.on_close)

        self.set_position(Gtk.WindowPosition.CENTER)

        # Is pointer over the toolbar Event box?
        self.in_toolbar = False
        # Is pointer motion timer running?
        self.timer = False
        # Time in milliseconds after point stops before toolbar is hidden
        self.time_interval = 1500
        # Mostra ou esconde o Preview
        self.is_previewed = False
        # Verifica se esta em tela cheia
        self.is_fullscreen = False

        # Inicia servidor RTSP
        self.server = Streaming_Server()
        self.server.run()
        # Inicia o cliente RTSP
        time.sleep(0.5)
        self.client = Streaming_Client(ip, port)

        # Inicia o preview RTP
        self.preview = Streaming_Preview()


        # An EventBox to capture events inside Frame,
        # i.e., for the Toolbar and its child widgets.
        ebox = Gtk.EventBox()
        ebox.show()
        ebox.set_above_child(True)
        ebox.connect("enter_notify_event", self.eventbox_cb)
        ebox.connect("leave_notify_event", self.eventbox_cb)

        self.__create_MenuToolbar()

        frame = Gtk.Frame()
        self.revealer = Gtk.Revealer()
        frame.add(self.toolbar)
        self.revealer.add(frame)
        ebox.add(self.revealer)
        ebox.set_valign(Gtk.Align.START)
        ebox.set_halign(Gtk.Align.CENTER)

        self.connect("motion_notify_event", self.motion_notify_cb)
        self.connect("key-press-event", self._key_press_event)

        # Create a box for the DrawingArea and buttons
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Create DrawingArea for video widget
        self.drawingarea = Gtk.DrawingArea()
        box.pack_start(self.drawingarea, True, True, 0)

        # Create DrawingArea for video preview
        self.previewarea = Gtk.DrawingArea()
        self.previewarea.set_size_request(300, 200)
        self.previewarea.set_valign(Gtk.Align.END)
        self.previewarea.set_halign(Gtk.Align.END)
        self.previewarea.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                                 Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        # Needed or else the drawing area will be really small (1px)
        self.drawingarea.set_hexpand(True)
        self.drawingarea.set_vexpand(True)
        self.drawingarea.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                                    Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.webview = WebKit.WebView()
        self.scrolled_window.add(self.webview)
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                                    Gdk.EventMask.POINTER_MOTION_HINT_MASK)


        overlay = Gtk.Overlay()
        overlay.add(box)
        overlay.add_overlay(self.previewarea)
        overlay.add_overlay(ebox)
        overlay.set_overlay_pass_through(ebox, True)
        overlay.add_overlay(self.scrolled_window)
        overlay.set_overlay_pass_through(self.scrolled_window,True)

        overlay.show()

        self.add(overlay)

    def __create_MenuToolbar(self):

        self.toolbar = Gtk.Toolbar()
        context = self.toolbar.get_style_context()
        context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        # Botão de gravação
        #self.record = Gtk.ToolButton(Gtk.STOCK_MEDIA_RECORD, label="Gravar")
        #self.toolbar.insert(self.record, 0)
        #self.record.connect("clicked", self.record_button)

        # Botão da Dispositivo
        icon_size = Gtk.IconSize.LARGE_TOOLBAR
        device_icon = Gtk.Image.new_from_icon_name("phone", icon_size)
        self.device_button = Gtk.ToolButton.new(device_icon, label="Dispositivo")
        self.toolbar.insert(self.device_button, 0)
        self.device_config_menu = self.__create_DeviceConfig(self.device_button)
        self.device_button.connect("clicked", self. __open_menu_deviceconfig)

        # Botão do Video
        video_icon = Gtk.Image.new_from_icon_name("camera-web", icon_size)
        self.video_button = Gtk.ToolButton.new(video_icon, label="Vídeo")
        self.toolbar.insert(self.video_button, 1)
        self.video_config_menu = self.__create_VideoConfig(self.video_button)
        self.video_button.connect("clicked", self.__open_menu_videoconfig)

        # Botão do audio
        audio_volume_icon = Gtk.Image.new_from_icon_name("audio-speakers", icon_size)
        self.audio_volume_button = Gtk.ToolButton.new(audio_volume_icon, label="Audio")
        self.toolbar.insert(self.audio_volume_button, 2)
        self.sound_config_menu = self.__create_SoundConfig(self.audio_volume_button)
        self.audio_volume_button.connect("clicked", self.__open_menu_soundconfig)

        # Botão da Configuracao
        # config_icon = Gtk.Image.new_from_icon_name("document-page-setup", icon_size)
        # self.config_button = Gtk.ToolButton.new(config_icon , label="Configuração")
        # self.toolbar.insert(self.config_button, 3)

        # Botão de "Preview"
        config_icon = Gtk.Image.new_from_icon_name("preferences-system-windows", icon_size)
        self.preview_button = Gtk.ToolButton.new(config_icon, label="Preview")
        self.toolbar.insert(self.preview_button, 3)
        self.preview_button.connect("clicked", self.__preview_test)

        # Botão de "fullscreen"
        self.fullscreen_button = Gtk.ToolButton(Gtk.STOCK_FULLSCREEN)
        self.toolbar.insert(self.fullscreen_button, 4)
        self.fullscreen_button.connect("clicked", self.fullscreen_callback)

        # Botão sair
        self.quit = Gtk.ToolButton(Gtk.STOCK_QUIT)
        self.toolbar.insert(self.quit, 5)
        self.quit.connect("clicked", self.on_close)


    def __create_SoundConfig(self,button):

        self.soundconf = AudioConfig()
        popover = Gtk.Popover()
        popover.set_relative_to(button)
        popover.add(self.soundconf)
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.connect("hide", self.__hide_menu)

        return popover

    def __hide_preview(self,action):
        self.previewarea.hide()

    def __open_menu_soundconfig(self, action):

        self.show_toolbar(True)
        self.soundconf.update_list()
        self.sound_config_menu.show_all()
        self.in_toolbar = True

    def __create_VideoConfig(self,button):

        self.vidconf = VideoConfig(self.server)
        popover = Gtk.Popover()
        popover.set_relative_to(button)
        popover.add(self.vidconf)
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.connect("hide", self.__hide_menu)

        return popover

    def __open_menu_videoconfig(self, action):

        self.show_toolbar(True)
        self.vidconf.update_list()
        self.video_config_menu.show_all()
        if not self.is_previewed:
            self.previewarea.show()
        self.in_toolbar = True


    def __preview_test(self, action):

        if self.is_previewed:
            self.previewarea.hide()
            self.is_previewed = False
        else:
            self.previewarea.show()
            self.is_previewed = True


    def __create_DeviceConfig(self,button):

        deviceconf = DeviceConfig(self)
        popover = Gtk.Popover()
        popover.set_relative_to(button)
        popover.add(deviceconf)
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.connect("hide", self.__hide_menu)

        return popover

    def __open_menu_deviceconfig(self, action):

        self.show_toolbar(True)
        self.device_config_menu.show_all()
        self.in_toolbar = True


    def __hide_menu(self, action):

        self.in_toolbar = False
        self.show_toolbar(False)
        if not self.is_previewed:
            self.previewarea.hide()

    def __hide_mouse__(self):

        cursor = Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR)
        self.get_window().set_cursor(cursor)

    def __show_mouse__(self):

        self.get_window().set_cursor(None)

    def show_toolbar(self, show):

        if show:
            self.revealer.set_reveal_child(True)
            self.revealer.set_visible(True)
            self.__show_mouse__()
        else:
            self.revealer.set_reveal_child(False)
            self.revealer.set_visible(False)
            self.__hide_mouse__()


    def timeout_cb(self):

        self.show_toolbar(self.in_toolbar)
        if not self.in_toolbar:
            self.timer = False
        return self.in_toolbar

    def start_timer(self, interval):

        self.timer = True
        #Timer will restart if callback returns True
        GObject.timeout_add(interval, self.timeout_cb)

    def motion_notify_cb(self, widget, event):

        if not self.timer:
            #print (event.x, event.y)
            self.show_toolbar(True)
            self.start_timer(self.time_interval)
        return True

    def eventbox_cb(self, widget, event):

        #in_toolbar = event.type == Gdk.EventMask.POINTER_MOTION_MASK
        # print event, in_toolbar
        #self.in_toolbar = in_toolbar
        self.show_toolbar(True)
        return True

    def _key_press_event(self, widget, event):

        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)

        if  ctrl and keyval_name=="s" or keyval_name=="S" :
            self.__open_menu_soundconfig(event)
        elif ctrl and keyval_name=="v" or keyval_name=="V" :
            self.__open_menu_videoconfig(event)
        elif ctrl and keyval_name == "p" or keyval_name == "P":
            self.__preview_test(event)
        elif  keyval_name == "F11" or (ctrl and keyval_name == "f" or keyval_name == "F"):
            self.__set_fullscreen()
        else:
            return False

    def __set_fullscreen(self):
        #is_fullscreen = self.get_window().get_state(
        #) & Gdk.WindowState.FULLSCREEN != 0
        if not self.is_fullscreen:
            self.fullscreen_button.set_stock_id(Gtk.STOCK_LEAVE_FULLSCREEN)
            self.fullscreen()
            self.is_fullscreen = True
        else:
            self.fullscreen_button.set_stock_id(Gtk.STOCK_FULLSCREEN)
            self.unfullscreen()
            self.is_fullscreen = False

    def fullscreen_callback(self, action):
        self.__set_fullscreen()

    def create_streamer(self):

        try:
            self.client.connect()
            self.preview.connect()
        except Exception as erro:
            self.client.stop()
            self.preview.stop()
            self.server.stop()
            self.__message__(erro, self)

    def getPlayerID(self):

        return self.drawingarea.get_property('window').get_xid()

    def getPreviewPlayerID(self):

        return self.previewarea.get_property('window').get_xid()

    def run(self):

        self.show_all()
        self.previewarea.hide()
        self.scrolled_window.hide()
        self.show_toolbar(False)
        self.client.playerID = self.getPlayerID()
        self.preview.playerID = self.getPreviewPlayerID()
        self.create_streamer()
        self.__set_fullscreen()
        Gtk.main()

    def on_close(self, window):

        self.client.stop()
        self.server.stop()
        self.preview.stop()
        self.hide()
        time.sleep(0.3)
        Gtk.main_quit()

    def __message__(self, data="", obj=None):

        dialog = Gtk.MessageDialog(obj, 0, Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()

    def record_button(self, widget):
        self.scrolled_window.show()

        #if self.record.get_label() == "Gravar":
        #    self.record.set_label("Parar")
        #    self.client.start_record()
        #else:
        #    self.client.stop_record()
         #   self.record.set_label("Gravar")
