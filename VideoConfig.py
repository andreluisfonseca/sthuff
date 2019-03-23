import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class VideoConfig(Gtk.Box):

    def __create_ImageConfig(self):

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        ad_brilho = Gtk.Adjustment(0, 0, 100, 1, 0, 0)
        ad_contraste = Gtk.Adjustment(0, 0, 100, 1, 0, 0)
        ad_saturacao = Gtk.Adjustment(0, 0, 100, 1, 0, 0)
        ad_nitidez = Gtk.Adjustment(0, 0, 100, 1, 0, 0)

        # Ajuste de Brilho
        label_bri = Gtk.Label(label="Brilho:")
        grid.attach(label_bri, 0, 0, 1, 1)
        scale_bri = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_brilho)
        scale_bri.set_digits(0)
        grid.attach(scale_bri, 1, 0, 2, 1)

        # Ajuste de Contraste
        label_con = Gtk.Label(label="Contraste:")
        grid.attach(label_con, 0, 1, 1, 1)
        scale_con = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_contraste)
        scale_con.set_digits(0)
        grid.attach(scale_con, 1, 1, 2, 1)

        # Ajuste de Saturação
        label_sat = Gtk.Label(label="Saturação:")
        grid.attach(label_sat, 0, 2, 1, 1)
        scale_sat = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_saturacao)
        scale_sat.set_digits(0)
        grid.attach(scale_sat, 1, 2, 2, 1)

        # Ajuste de Nitidez
        label_nit = Gtk.Label(label="Nitidez:")
        grid.attach(label_nit, 0, 3, 1, 1)
        scale_nit = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_nitidez)
        scale_nit.set_digits(0)
        grid.attach(scale_nit, 1, 3, 2, 1)

        return grid

    def __create_VideoConfig(self):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        ad_bitrate = Gtk.Adjustment(0, 0, 100, 1, 0, 0)

        # Escolha da Interface de Video
        label_int = Gtk.Label(label="Interface:")
        grid.attach(label_int, 0, 0, 1, 1)
        interface_combo = Gtk.ComboBoxText()
        interface_combo.set_entry_text_column(0)
        grid.attach(interface_combo, 1, 0, 2, 1)

        # Ajuste de Resolução
        label_resolucao = Gtk.Label(label="Resolução:")
        grid.attach(label_resolucao, 0, 1, 1, 1)
        resolucao_combo = Gtk.ComboBoxText()
        resolucao_combo.set_entry_text_column(0)
        grid.attach(resolucao_combo, 1, 1, 2, 1)

        # Ajuste de FPS
        label_FPS = Gtk.Label(label="FPS:")
        grid.attach(label_FPS, 0, 2, 1, 1)
        FPS_combo = Gtk.ComboBoxText()
        FPS_combo.set_entry_text_column(0)
        grid.attach(FPS_combo, 1, 2, 2, 1)

        # Ajuste de BitRate
        label_nit = Gtk.Label(label="BitRate:")
        grid.attach(label_nit, 0, 3, 1, 1)
        scale_bitrate = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_bitrate)
        scale_bitrate.set_digits(0)
        grid.attach(scale_bitrate, 1, 3, 2, 1)

        return grid

    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_border_width(10)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(250)

        grid_video = self.__create_VideoConfig()
        stack.add_titled(grid_video, "Vídeo", "Vídeo")

        grid_image = self.__create_ImageConfig()
        stack.add_titled(grid_image, "Imagem", "Imagem")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, True, True, 0)




