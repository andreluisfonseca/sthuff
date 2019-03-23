import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class CadastroDialog(Gtk.Dialog):

    def __init__(self, parent,title="Dispositivo(s)"):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        self.grid = Gtk.Grid()

        # Texto e Campo de entrada nome do local
        self.label_nome = Gtk.Label(label="Nome:")
        self.grid.attach(self.label_nome, 0, 0, 1, 1)
        self.entry_nome = Gtk.Entry()
        #self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(20)
        self.grid.attach(self.entry_nome, 1, 0, 1, 1)

        # Texto e campo de entrada para o rede
        self.label_rede = Gtk.Label(label="Rede IP:")
        self.grid.attach(self.label_rede, 0, 1, 1, 1)
        self.entry_rede = Gtk.Entry()
        self.grid.attach(self.entry_rede, 1, 1, 1, 1)
        #self.entry_rede.set_max_length(150)
        self.entry_rede.set_width_chars(20)


        # Texto e campo de entrada para descricao
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
        self.grid.attach(self.frame_descricao, 0, 2, 2, 1)


        self.set_default_size(200, 250)
        #self.set_resizable(False)

        self.get_content_area().add(self.grid)

        self.show_all()


class JanelaDispositivo(Gtk.Window):


    Lista = [["Camera", "localhost"],
            ["Celular", "localhost"]]

    def __criaListStore__(self, lista, liststore):
        for item in lista:
            liststore.append(item)
        return liststore

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_default_size(300, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        hb = Gtk.HeaderBar(title="Lista de Dispositivo(s)")
        hb.set_show_close_button(True)
        self.set_titlebar(hb)

        self.liststore = self.__criaListStore__(self.Lista, Gtk.ListStore(str, str))

        treeview = Gtk.TreeView(model=self.liststore)

        renderer_local = Gtk.CellRendererText()
        column_local = Gtk.TreeViewColumn("DISPOSITIVO", renderer_local, text=0)
        treeview.append_column(column_local)

        renderer_rede = Gtk.CellRendererText()
        column_rede = Gtk.TreeViewColumn("REDE:IP/NOME",
            renderer_rede, text=1)
        treeview.append_column(column_rede)

        toolbaredit = self.__create_Toolbar_Edit__()
        toolbarOK = self.__create_Toolbar_Ok_Cancel__()

        box = Gtk.VBox(orientation=Gtk.Orientation.VERTICAL)

        box.pack_start(toolbaredit, False, False, 0)
        box.pack_start(treeview,True, True, 0)
        box.pack_start(toolbarOK,False, False, 0)
        self.add(box)

    def __create_Toolbar_Edit__(self):
        toolbar = Gtk.Toolbar(halign = Gtk.Align.CENTER)
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        newtb = Gtk.ToolButton(Gtk.STOCK_ADD)
        newtb.connect("clicked", self.on_add_clicked)

        edittb = Gtk.ToolButton(Gtk.STOCK_EDIT)
        delltb = Gtk.ToolButton(Gtk.STOCK_REMOVE)

        toolbar.insert(newtb, 0)
        toolbar.insert(edittb, 1)
        toolbar.insert(delltb, 2)

        return toolbar

    def __create_Toolbar_Ok_Cancel__(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        oktb = Gtk.ToolButton(Gtk.STOCK_OK,label="Iniciar")
        canceltb = Gtk.ToolButton(Gtk.STOCK_CANCEL,label="Cancelar")


        toolbar.insert(oktb, 0)
        toolbar.child_set_property(oktb, "expand", True)
        toolbar.insert(canceltb, 1)
        toolbar.child_set_property(canceltb, "expand", True)

        return toolbar

    def on_add_clicked(self, widget):
        dialog = CadastroDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def run(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()
