import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class JanelaLogin:

    def __init__(self):
        builder = Gtk.Builder.new()
        builder.add_from_file('login.glade')

        self.main_window = builder.get_object('login')
        self.main_window.connect('destroy', Gtk.main_quit)
        self.main_window.set_position(Gtk.WindowPosition.CENTER)

        hb = Gtk.HeaderBar(title="Login STH-UFF")
        hb.set_show_close_button(True)
        self.main_window.set_titlebar(hb)
        self.main_window.set_default_size(300, 300)
        self.main_window.show_all()

        btn_OK = builder.get_object('btn_OK')
        btn_OK.connect("clicked", self._on_ok_clicked)

        btn_CANCEL = builder.get_object('btn_CANCEL')
        btn_CANCEL.connect("clicked", self._on_cancel_clicked)

        # Loop da interface.
        Gtk.main()

    def _on_ok_clicked(self,button):
        self.main_window.hide()
        self.main_window.destroy()
        Gtk.main_quit()


    def _on_cancel_clicked(self,button):
        exit(0)