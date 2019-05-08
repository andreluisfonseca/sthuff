#!/usr/bin/env python3

import os , subprocess
import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf

from Sth_uff import Sth_uff
from JanelaLogin import JanelaLogin

CURRDIR = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(CURRDIR, 'hologram.png')

class SysTray(Gtk.StatusIcon):

    def __init__(self,Icon):

        self.call = None
        #self.service = CallServer('0.0.0.0',9999)
        #self.service.start()

        self.service = subprocess.Popen(["python3", "ServicoChamada.py"])

        Gtk.StatusIcon.__init__(self)
        self.set_from_file(Icon)
        self.menu = Gtk.Menu()
        call_item = Gtk.MenuItem("Iniciar")
        close_item = Gtk.MenuItem("Fechar")
        about_item = Gtk.MenuItem("Sobre")

        # Append the menu items
        self.menu.append(call_item)
        self.menu.append(about_item)
        self.menu.append(close_item)
        # add callbacks
        call_item.connect_object("activate", self.iniciar, "Iniciar")
        about_item.connect_object("activate", self.about, "Sobre")
        close_item.connect_object("activate", self.close_app, "Close App")
        # Show the menu items
        call_item.show()
        about_item.show()
        close_item.show()

        self.connect('popup-menu', self.on_PopupMenu)
        self.connect('activate', self.iniciar)

        self.iniciar()


    def iniciar(self,data=None):

        if self.call is None:
            self.call = Sth_uff()
            self.call.run()
            self.call = None

    def open_app(self,data=None):
        self.message(data)

    def close_app(self,data=None):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, "Atenção!!!")
        dialog.format_secondary_text(
            "O Serviço de Atendimento vai parar de funcionar!\n"
            "Mesmo assim, Você gostaria de sair?")
        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            self.service.kill()
            if self.call is not None:
                self.call.close()
            exit(0)
        dialog.destroy()


    def on_PopupMenu(self,icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon,
                        button, time)

    def on_left_click(self,event):
        self.message("Status Icon Left Clicked")

    def about(self, widget, data=None):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_position(Gtk.WindowPosition.CENTER)
        about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file("logo.png"))
        about_dialog.set_program_name("Sistema de Teleatendimento Holográfico da UFF (STH-UFF)")
        about_dialog.set_version('01/03/2019 (Alfa)')
        about_dialog.set_comments('Criando por André Luis de Oliveria Fonseca\n Email: andreluisfonseca@if.uff.br')
        about_dialog.set_website('http://www.midiacom.uff.br/sthuff')
        about_dialog.set_website_label('www.midiacom.uff.br/sthuff')
        about_dialog.set_copyright("2016-2019, UFF - Universidade Federal Fluminense")
        about_dialog.set_license_type(Gtk.License.BSD)
        response_about = about_dialog.run()
        if response_about == -6 or response_about == -4:
            about_dialog.hide()
            about_dialog.destroy()

def message(data=None):
        "Function to display messages to the user."
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()

def __checkPidRunning__(pid):
    '''Check For the existence of a unix pid.
    '''
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True



if __name__ == '__main__':

    pid = str(os.getpid())
    pidfile = os.path.join("/", "tmp", "ssh-uff.pid")

    try:

        if os.path.isfile(pidfile) and __checkPidRunning__(int(open(pidfile,'r').readlines()[0])):
            message("Processo já está em execução!")
            sys.exit(-1)
        else:
            f = open(pidfile, 'w').write(pid)
            ssh_uff = SysTray(ICON)
            Gtk.main()

        os.unlink(pidfile)

    except Exception as erro:
        os.unlink(pidfile)
        message(erro)


