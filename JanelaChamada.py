import subprocess, time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from AmbienteBD import Ambiente
from VideoDisplay import Player

class CadastroDialog(Gtk.Dialog):

    def __init__(self, parent,title="Chamada(s)"):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        #self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()

        # Texto e Campo de entrada nome do local
        self.label_nome = Gtk.Label(label="Local:")
        self.grid.attach(self.label_nome, 0, 0, 1, 1)
        self.entry_nome = Gtk.Entry()
        #self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(20)
        self.grid.attach(self.entry_nome, 1, 0, 1, 1)

        # Texto e Campo de entrada da sigla
        self.label_sigla = Gtk.Label(label="Sigla:")
        self.grid.attach(self.label_sigla, 0, 1, 1, 1)
        self.entry_sigla = Gtk.Entry()
        #self.entry_sigla.set_max_length(150)
        self.entry_sigla.set_width_chars(20)
        self.grid.attach(self.entry_sigla, 1, 1, 1, 1)

        # Texto e campo de entrada para o rede
        self.label_rede = Gtk.Label(label="Rede IP:")
        self.grid.attach(self.label_rede, 0, 2, 1, 1)
        self.entry_rede = Gtk.Entry()
        self.grid.attach(self.entry_rede, 1, 2, 1, 1)
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
        self.grid.attach(self.frame_descricao, 0, 3, 2, 1)


        self.set_default_size(200, 250)
        #self.set_resizable(False)

        self.get_content_area().add(self.grid)

        self.show_all()


class JanelaChamada(Gtk.Window):

    def __init__(self,parent=None):

        Gtk.Window.__init__(self)

        self.ambientes = Ambiente()
        self.lista = []

        self.parent = parent
        self.set_transient_for(parent)
        self.set_modal(True)


        self.set_default_size(300, 300)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        hb = Gtk.HeaderBar(title="Lista de Chamada(s)")
        hb.set_show_close_button(True)
        self.set_titlebar(hb)

        self.liststore = self.__criaListStore__()


        self.treeview = Gtk.TreeView(model=self.liststore)

        renderer_local = Gtk.CellRendererText()
        column_local = Gtk.TreeViewColumn("LOCAL", renderer_local, text=0)
        self.treeview.append_column(column_local)

        renderer_rede = Gtk.CellRendererText()
        column_rede = Gtk.TreeViewColumn("REDE:IP/NOME",
            renderer_rede, text=1)
        self.treeview.append_column(column_rede)
        self.treeview.set_cursor(0)

        toolbaredit = self.__create_Toolbar_Edit__()
        toolbarOK = self.__create_Toolbar_Ok_Cancel__()

        box = Gtk.VBox(orientation=Gtk.Orientation.VERTICAL)

        box.pack_start(toolbaredit, False, False, 0)
        box.pack_start(self.treeview,True, True, 0)
        box.pack_start(toolbarOK,False, False, 0)
        self.add(box)

    def __cadastro_local__(self):
        if len(self.lista) == 0 :
            self.__message__("Não exite o cadastro do ambiente Local"
                             "\n Por favor, realize o cadastro agora!!!",self)
            self.on_add_clicked(None)

    def __criaListStore__(self):
        liststore = Gtk.ListStore(str, str)
        self.lista = self.ambientes.listar_ambientes()
        for item in self.lista:
            liststore.append([item[2], item[3]])
        return liststore

    def __update_lista__(self):
        liststore = self.liststore
        liststore.clear()
        self.lista = self.ambientes.listar_ambientes()
        for item in self.lista:
            liststore.append([item[2], item[3]])
        self.treeview.set_cursor(0)

    def __create_Toolbar_Edit__(self):
        toolbar = Gtk.Toolbar(halign = Gtk.Align.CENTER)
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        newtb = Gtk.ToolButton(Gtk.STOCK_ADD)
        newtb.connect("clicked", self.on_add_clicked)

        edittb = Gtk.ToolButton(Gtk.STOCK_EDIT)
        edittb.connect("clicked", self.on_update_clicked)

        delltb = Gtk.ToolButton(Gtk.STOCK_REMOVE)
        delltb.connect("clicked", self.on_delete_clicked)

        toolbar.insert(newtb, 0)
        toolbar.insert(edittb, 1)
        toolbar.insert(delltb, 2)

        return toolbar

    def __create_Toolbar_Ok_Cancel__(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)

        oktb = Gtk.ToolButton(Gtk.STOCK_OK,label="Iniciar")
        oktb.connect("clicked", self.__OK__)
        canceltb = Gtk.ToolButton(Gtk.STOCK_CANCEL,label="Cancelar")
        canceltb.connect("clicked", self.__Cancel__)

        toolbar.insert(oktb, 0)
        toolbar.child_set_property(oktb, "expand", True)
        toolbar.insert(canceltb, 1)
        toolbar.child_set_property(canceltb, "expand", True)

        return toolbar

    def __call_request(self):
        request = subprocess.check_output(["python3", "RequisicaoChamada.py",self.__select_item__(1)])
        request = request.decode().rstrip("\n\r")

        if request == "OK":
            self.aceita = True
            p = Player(ip=self.__select_item__(1))
            p.run()
        elif request == "BLOCKED":
            self.__message__("O ambiente já se encontra em uma chamada!", self)
        elif request == "NO":
            self.__message__("A chamada não foi aceita!", self)
        elif request == "Timeout":
            self.__message__("Parece que o ambiente está fora de alcance!", self)

        self.on_close()

        GObject.source_remove(self.id_request)

    def __OK__(self, widget):

        self.hide()
        if self.parent is not None:
            self.parent.hide()

        self.id_request = GObject.idle_add(self.__call_request)

    def __Cancel__(self, widget):
        self.on_close()
        self.aceita = False

    def __select_item__(self,i):

        select = self.treeview.get_selection()

        model, treeiter = select.get_selected()
        return str(model[treeiter][i])

    def __message__(self,data="",obj=None):
        dialog = Gtk.MessageDialog(obj, 0, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()

    def on_close(self):
        Gtk.main_quit()
        self.destroy()

    def on_add_clicked(self, widget):
        dialog = CadastroDialog(self)
        response = dialog.run()
        msg=None

        if response == Gtk.ResponseType.OK:
            nome = dialog.entry_nome.get_text()
            sigla = dialog.entry_sigla.get_text()
            ip = dialog.entry_rede.get_text()

            buf = dialog.textview_descricao.get_buffer()
            start = buf.get_start_iter()
            end = buf.get_end_iter()
            desc = buf.get_text(start,end,True)

            msg=self.ambientes.cadastrar(nome,sigla,ip,desc)
            self.__update_lista__()

        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
        if msg is not None:
            self.__message__(msg, dialog)

    def on_update_clicked(self, widget):

        if len(self.lista) == 0:
            return

        ip = self.__select_item__(1)

        dados = self.ambientes.listar_ambiente_por_IP(ip)

        dialog = CadastroDialog(self)

        dialog.entry_nome.set_text(dados[1])
        dialog.entry_sigla.set_text(dados[2])
        dialog.entry_rede.set_text(dados[3])
        dialog.textview_descricao.get_buffer().set_text(dados[4])

        response = dialog.run()
        msg = None

        if response == Gtk.ResponseType.OK:
            nome = dialog.entry_nome.get_text()
            sigla = dialog.entry_sigla.get_text()
            ip = dialog.entry_rede.get_text()

            buf = dialog.textview_descricao.get_buffer()
            start = buf.get_start_iter()
            end = buf.get_end_iter()

            desc = buf.get_text(start,end,True)

            msg = self.ambientes.atualizar(dados[0],nome,sigla,ip,desc)
            self.__update_lista__()

        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

        if msg is not None:
            self.__message__(msg, dialog)

    def on_delete_clicked(self, widget):

        if len(self.lista) == 0:
            return

        ip = self.__select_item__(1)

        dados = self.ambientes.listar_ambiente_por_IP(ip)
        id = dados[0]

        if id < 2:
            self.__message__("O ambiente %s só pode ser alterado!" % (dados[2]), self)
            return

        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, "Atenção!!!")
        dialog.format_secondary_text("O Ambiente '%s' vai ser removido!" % (dados[2]))

        response = dialog.run()
        msg=None

        if response == Gtk.ResponseType.YES:
            msg =  self.ambientes.deletar(id)
            self.__update_lista__()

        elif response == Gtk.ResponseType.NO:
            pass

        dialog.destroy()

        if msg is not None:
            self.__message__(msg, dialog)


    def run(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.__cadastro_local__()
        Gtk.main()

