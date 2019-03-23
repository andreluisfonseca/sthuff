#!/usr/bin/python3
# This program is licensed under GPLv3.

import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk, Gdk, GdkPixbuf
from JanelaChamada import JanelaChamada

Gst.init(None)


class AgendaDialog(Gtk.Dialog):

    def __init__(self, parent,title="Perfil do Usuário"):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))


        hbox1 =  Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Calendário
        self.frame_cal= Gtk.Frame(label="Calendário:")
        self.calendario = Gtk.Calendar()
        self.frame_cal.add(self.calendario)
        hbox1.pack_start(self.frame_cal, False, False , 10)


        sep = Gtk.VSeparator()
        hbox1.pack_start(sep, False, True , 0)

        # Reunião
        self.frame_reuniao= Gtk.Frame(label="Reunião (Horários):")
        self.textview_reuniao = Gtk.TextView()
        self.textview_reuniao.set_wrap_mode(True)
        self.textview_reuniao.set_editable(False)

        scroller = Gtk.ScrolledWindow()
        scroller.set_border_width(5)
        scroller.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.textview_reuniao)
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        self.frame_reuniao.add(scroller)
        hbox1.pack_start(self.frame_reuniao, False, True , 10)

        # Descrição do Paciente
        self.frame_paciente = Gtk.Frame(label="Descrição (Paciente):")
        self.textview_paciente = Gtk.TextView()
        self.textview_paciente.set_wrap_mode(True)


        scroller = Gtk.ScrolledWindow()
        scroller.set_border_width(5)
        scroller.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.textview_paciente)
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        self.frame_paciente.add(scroller)
        hbox2.pack_start(self.frame_paciente, True , True, 10)

        self.set_default_size(500, 400)
        # self.set_resizable(False)

        self.get_content_area().add(hbox1)
        self.get_content_area().add(hbox2)

        self.show_all()

class PerfilUserDialog(Gtk.Dialog):

    def __init__(self, parent,title="Perfil do Usuário"):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        #self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()

        # Usuario
        self.label_nome = Gtk.Label(label="Usuário:")
        self.grid.attach(self.label_nome, 0, 0, 1, 1)
        self.entry_nome = Gtk.Entry()
        #self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(20)
        self.grid.attach(self.entry_nome, 1, 0, 1, 1)

        # Nome
        self.label_nome = Gtk.Label(label="Senha:")
        self.grid.attach(self.label_nome, 0, 1, 1, 1)
        self.entry_nome = Gtk.Entry()
        # self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(20)
        self.grid.attach(self.entry_nome, 1, 1, 1, 1)


        # Nome
        self.label_nome = Gtk.Label(label="Nome:")
        self.grid.attach(self.label_nome, 0, 2, 1, 1)
        self.entry_nome = Gtk.Entry()
        #self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(20)
        self.grid.attach(self.entry_nome, 1, 2, 1, 1)

        # CPF
        self.label_sigla = Gtk.Label(label="CPF:")
        self.grid.attach(self.label_sigla, 0, 3, 1, 1)
        self.entry_sigla = Gtk.Entry()
        #self.entry_sigla.set_max_length(150)
        self.entry_sigla.set_width_chars(20)
        self.grid.attach(self.entry_sigla, 1, 3, 1, 1)

        # Email
        self.label_rede = Gtk.Label(label="Email:")
        self.grid.attach(self.label_rede, 0, 4, 1, 1)
        self.entry_rede = Gtk.Entry()
        self.grid.attach(self.entry_rede, 1, 4, 1, 1)
        #self.entry_rede.set_max_length(150)
        self.entry_rede.set_width_chars(20)

        # Endereço
        self.label_rede = Gtk.Label(label="Endereço:")
        self.grid.attach(self.label_rede, 0, 5, 1, 1)
        self.entry_rede = Gtk.Entry()
        self.grid.attach(self.entry_rede, 1, 5, 1, 1)
        # self.entry_rede.set_max_length(150)
        self.entry_rede.set_width_chars(20)

        # Descricao
        self.frame_descricao = Gtk.Frame(label="Descrição")
        self.textview_descricao = Gtk.TextView()
        self.textview_descricao.set_wrap_mode(True)

        scroller = Gtk.ScrolledWindow()
        scroller.set_border_width(5)
        scroller.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.textview_descricao)
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        self.frame_descricao.add(scroller)
        self.grid.attach(self.frame_descricao, 0, 6, 2, 1)


        self.set_default_size(200, 300)
        #self.set_resizable(False)

        self.get_content_area().add(self.grid)

        self.show_all()

class Sth_uff(Gtk.Window):

    def show_toolbar(self, show):
        if show:
            self.revealer.set_reveal_child(True)
            self.revealer.set_visible(True)

        else:
            self.revealer.set_reveal_child(False)
            self.revealer.set_visible(False)

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

    def __init__(self):

        self.chamada = None

        # Is pointer over the toolbar Event box?
        self.in_toolbar = False

        # Is pointer motion timer running?
        self.timer = False

        # Time in milliseconds after point stops before toolbar is hidden
        self.time_interval = 1500

        Gtk.Window.__init__(self,title="STH-UFF")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.connect('destroy', self.on_close)

        overlay = Gtk.Overlay()
        self.add(overlay)

        # An EventBox to capture events inside Frame,
        # i.e., for the Toolbar and its child widgets.
        ebox = Gtk.EventBox()
        ebox.show()
        ebox.set_above_child(True)
        ebox.connect("enter_notify_event", self.eventbox_cb)
        ebox.connect("leave_notify_event", self.eventbox_cb)

        #box.pack_start(ebox, False, False, 0)

        self.toolbar = Gtk.Toolbar()
        context = self.toolbar.get_style_context()
        context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        # Botão de Chamadas
        icon_size = Gtk.IconSize.LARGE_TOOLBAR
        chamada_icon = Gtk.Image.new_from_icon_name("modem", icon_size)
        self.chamada_button = Gtk.ToolButton.new(chamada_icon, label="Chamadas")
        self.toolbar.insert(self.chamada_button, 0)
        self.chamada_button.connect("clicked", self.iniciar_chamada)


        # Botão de Agendamento
        agendar_icon = Gtk.Image.new_from_icon_name("appointment-new", icon_size)
        self.agendar_button = Gtk.ToolButton.new(agendar_icon, label="Agendar")
        self.toolbar.insert(self.agendar_button, 1)
        self.agendar_button.connect("clicked", self.agendar)

        # Botão do Perfil
        perfil_icon = Gtk.Image.new_from_icon_name("avatar-default", icon_size)
        self.perfil_button = Gtk.ToolButton.new(perfil_icon, label="Perfil")
        self.toolbar.insert(self.perfil_button, 2)
        self.perfil_button.connect("clicked", self.perfil)


        # Botão de Preferencia
        config_icon = Gtk.Image.new_from_icon_name("preferences-desktop", icon_size)
        self.config_button = Gtk.ToolButton.new(config_icon , label="Preferências")
        self.toolbar.insert(self.config_button, 3)

        # Botão do Sobre
        about_icon = Gtk.Image.new_from_icon_name("help-about", icon_size)
        self.about_button = Gtk.ToolButton.new(about_icon, label="Sobre")
        self.toolbar.insert(self.about_button, 4)
        self.about_button.connect("clicked", self.about)

        # Botão sair
        self.quit = Gtk.ToolButton(Gtk.STOCK_QUIT)
        self.toolbar.insert(self.quit, 5)
        self.quit.connect("clicked", self.on_close)

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


        logo_file = GdkPixbuf.Pixbuf.new_from_file("logo.png")
        self.logo  = Gtk.Image()
        self.logo.set_from_pixbuf(logo_file)

        black = Gdk.color_parse("black")
        rgba = Gdk.RGBA.from_color(black)
        box.override_background_color(0, rgba)

        box.pack_start(self.logo, True, True, 0)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.POINTER_MOTION_HINT_MASK)


        overlay.add(box)
        overlay.add_overlay(ebox)
        overlay.show()

    def _key_press_event(self, widget, event):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)

        if  ctrl and keyval_name=="s" or keyval_name=="S" :
            self.close()
        else:
            return False


    def run(self):
        self.show_all()
        self.show_toolbar(False)
        Gtk.main()

    def on_close(self, window):
        self.hide()
        time.sleep(0.1)
        Gtk.main_quit()

    def __message__(self, data="", obj=None):
        dialog = Gtk.MessageDialog(obj, 0, Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()


    def iniciar_chamada(self,  widget):
        self.hide()
        if self.chamada is None:
            self.chamada = JanelaChamada()
            self.chamada.run()
            self.chamada = None
        self.show()

    def perfil(self, widget):
        dialog = PerfilUserDialog(self)
        response = dialog.run()
        msg=None

        if response == Gtk.ResponseType.OK:
            print("OK perfil")

        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()


    def agendar(self, widget):
        dialog = AgendaDialog(self)
        response = dialog.run()
        msg=None

        if response == Gtk.ResponseType.OK:
            print("OK Agenda")

        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
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