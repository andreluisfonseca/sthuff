import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

class JanelaRequisicao(Gtk.Window):

    def __init__(self,user=""):
        self.aceita = True

        Gtk.Window.__init__(self)
        self.set_default_size(300, 180)
        self.set_position(Gtk.WindowPosition.CENTER)

        hb = Gtk.HeaderBar(title="Requisição de Chamada!")
        hb.set_show_close_button(True)
        self.set_titlebar(hb)

        hbox = Gtk.VBox(orientation=Gtk.Orientation.HORIZONTAL)

        Message_Icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic", Gtk.IconSize.DIALOG)
        hbox.pack_start(Message_Icon, True, False, 0)

        self.msg = Gtk.Label()
        self.set_user(user)
        self.msg.set_justify(Gtk.Justification.CENTER)
        self.msg.set_line_wrap(True)
        hbox.pack_start(self.msg, True, True, 0)

        toolbarAceitar = self.__create_Toolbar_Desligar__()
        #self.progressbar = Gtk.ProgressBar()

        vbox = Gtk.VBox(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(hbox, True, True, 0)
        #vbox.pack_start(self.progressbar, True, True, 0)
        vbox.pack_start(toolbarAceitar, False, False, 0)

        self.add(vbox)

        self.connect("delete-event", self.__close__)

    def on_timeout(self, userdata):
        """
        atualiza o progress bar
        """
        new_value = self.progressbar.get_fraction() + 0.01
        if new_value > 1:
            self.on_close()
            return False
        self.progressbar.set_fraction(new_value)
        return True

    def set_data(self, data):
        self.__data = data

    def set_user(self,user):
        self.msg.set_markup("Ligando para: <b>%s</b>" % str(user))

    def set_message(self, msg):
        self.msg.set_markup(msg)

    def __create_Toolbar_Desligar__(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        iconSize = Gtk.IconSize.LARGE_TOOLBAR
        Desligar_Icon = Gtk.Image.new_from_icon_name("call-stop", iconSize)

        Desligartb = Gtk.ToolButton.new(Desligar_Icon, label="Desligar")
        Desligartb.connect("clicked", self.__desligar__)

        toolbar.insert(Desligartb, 0)
        toolbar.child_set_property(Desligartb, "expand", True)

        return toolbar

    def __desligar__(self, widget):
        self.on_close()
        self.aceita = False

    def run(self):
        #self.timeout_id = GObject.timeout_add(100, self.on_timeout, None)
        self.show_all()
        Gtk.main()
        self.hide()
        return self.aceita

    def on_close(self):
        self.hide()
        #GObject.source_remove(self.timeout_id)
        Gtk.main_quit()
        return False

    def __close__(self, widget, data=None):
        self.on_close()
        self.aceita = False
        return True
