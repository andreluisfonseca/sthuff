import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import pulsectl

class AudioConfig(Gtk.Box):

    def __init__(self):

        Gtk.Box.__init__(self)
        self.set_border_width(5)

        self.__pulse = pulsectl.Pulse(self.__class__.__name__)

        # Lista de Saídas
        self.__sink_list = []

        # Lista de Entradas
        self.__source_list = []

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.input_list = Gtk.ListStore(int, str, str, float,int)
        self.output_list = Gtk.ListStore(int, str, str, float,int)
        self.__set_InputList(self.input_list)
        self.__set_OutputList(self.output_list)

        self.input_config = self.__create_InputConfig()
        self.output_config = self.__create_OutputConfig()

        vbox.pack_start(self.input_config, True, True, 0)
        vbox.pack_start(self.output_config, True, True, 0)

    def __create_InputConfig(self):

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        ad1 = Gtk.Adjustment(0, 0, 100, 1, 0, 0)

        frame_in = Gtk.Frame(label="Entrada:")

        # Ajuste de Interface de entrada
        label_input = Gtk.Label(label="Interface:")
        grid.attach(label_input, 0, 0, 1, 1)

        self.input_combo = Gtk.ComboBox.new_with_model(self.input_list)
        renderer_text = Gtk.CellRendererText()
        self.input_combo.pack_start(renderer_text, True)
        self.input_combo.add_attribute(renderer_text, "text", 2)
        self.input_combo.connect("changed", self.__on_select_input)
        grid.attach(self.input_combo, 1, 0, 2, 1)

        # Ajuste do volume da entrada
        label_input_vol = Gtk.Label(label="Volume:")
        grid.attach(label_input_vol, 0, 1, 1, 1)
        self.scale_in = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.scale_in.set_digits(0)
        grid.attach(self.scale_in, 1, 1, 2, 1)

        self.scale_in.connect("button-release-event", self.__volume_input_moved)
        self.scale_in.connect("key_release_event", self.__volume_input_moved)

        frame_in.add(grid)

        return frame_in

    def __create_OutputConfig(self):

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        ad1 = Gtk.Adjustment(0, 0, 100, 1, 0, 0)

        frame_out = Gtk.Frame(label="Saída:")

        # Ajuste de Interface de saída
        label_output = Gtk.Label(label="Interface:")
        grid.attach(label_output, 0, 0, 1, 1)

        self.output_combo = Gtk.ComboBox.new_with_model(self.output_list)
        renderer_text = Gtk.CellRendererText()
        self.output_combo.pack_start(renderer_text, True)
        self.output_combo.add_attribute(renderer_text, "text", 2)
        self.output_combo.connect("changed", self.__on_select_output)
        grid.attach(self.output_combo, 1, 0, 2, 1)

        # Ajuste do volume da saída
        label_output_vol = Gtk.Label(label="Volume:")
        grid.attach(label_output_vol, 0, 1, 1, 1)
        self.scale_out = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.scale_out.set_digits(0)
        grid.attach(self.scale_out, 1, 1, 2, 1)

        self.scale_out.connect("button-release-event", self.__volume_output_moved)
        self.scale_out.connect("key_release_event", self.__volume_output_moved)

        frame_out.add(grid)

        return frame_out

    def set_muted_input(self, index, muted):

        pulse = self.__pulse
        pulse.source_mute(index, muted)

    def set_muted_output(self, index, muted):

        pulse = self.__pulse
        pulse.sink_mute(index, muted)

    def set_volume_input(self, index, value, channels=1):

        if channels == 1:
            volume = pulsectl.PulseVolumeInfo([value])
        else:
            volume = pulsectl.PulseVolumeInfo([value, value])

        self.__pulse.source_volume_set(index, volume)

    def set_volume_output(self, index, value, channels=1):

        if channels == 1:
            volume = pulsectl.PulseVolumeInfo([value])
        else:
            volume = pulsectl.PulseVolumeInfo([value,value])

        self.__pulse.sink_volume_set(index, volume)

    def __set_InputList(self, list):

        list.clear()
        self.__source_list.clear()
        sources = self.__pulse.source_list()
        for input in sources:
            if not "Monitor" in input.description:
                source_data = [input.index,
                               input.name,
                               input.description,
                               input.volume.values[0],
                               input.channel_count
                              ]
                list.append(source_data)
                self.__source_list.append(source_data)

    def __set_OutputList(self, list):

        list.clear()
        self.__sink_list.clear()
        sinks = self.__pulse.sink_list()
        for output in sinks:
            if not "Monitor" in output.description:
                sink_data = [output.index,
                               output.name,
                               output.description,
                               output.volume.values[0],
                               output.channel_count
                              ]
                list.append(sink_data)
                self.__sink_list.append(sink_data)

    def update_list(self):

        self.__set_InputList(self.input_list)
        self.__set_OutputList(self.output_list)

        # Desabilita a configuração de entrada
        # se a lista de entrada esta vazia
        in_empty = len(self.__source_list) == 0
        self.input_config.set_sensitive(not in_empty)
        if in_empty:
            self.scale_in.set_value(0)
        else:
            # Seleciona a saída padrão na interface gráfica
            row = 0
            for output in self.__sink_list:
                default_sink = self.__pulse.server_info().default_sink_name
                if output[1] == default_sink:
                    self.output_combo.set_active(row)
                else:
                    row += 1

        # Desabilita a configuração de saída
        # se a lista de saída esta vazia
        out_empty = len(self.__sink_list) == 0
        self.output_config.set_sensitive(not out_empty)
        if out_empty:
            self.scale_out.set_value(0)
        else:
            # Seleciona a entrada padrão na interface gráfica
            row = 0
            for input in self.__source_list:
                default_source = self.__pulse.server_info().default_source_name
                if input[1] == default_source:
                    self.input_combo.set_active(row)
                else:
                    row += 1

    def __get_index_selected(self,combo):

        tree_iter = combo.get_active_iter()
        index = -1
        if tree_iter is not None:
            model = combo.get_model()
            index = model[tree_iter][0]
        return index

    def __get_name_selected(self,combo):

        tree_iter = combo.get_active_iter()
        name = ""
        if tree_iter is not None:
            model = combo.get_model()
            name = model[tree_iter][1]
        return name

    def __source_output_move_all(self, index):
        streams = self.__pulse.source_output_list()
        for stream in streams:
            self.__pulse.source_output_move(stream.index, index)

    def __sink_input_move_all(self, index):
        streams = self.__pulse.sink_input_list()
        for stream in streams:
            self.__pulse.sink_input_move(stream.index, index)

    def __on_select_input(self, combo):

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            # Define o valor do volume na interface
            volume = model[tree_iter][3]
            self.scale_in.set_value(int(volume*100))
            # Move todos streams para a entrada seleciona
            index = model[tree_iter][0]
            self.__source_output_move_all(index)
            # Seleciona a entrada como padrão
            name = model[tree_iter][1]
            self.__pulse.source_default_set(name)

    def __on_select_output(self, combo):

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            # Define o valor do volume na interface
            volume = model[tree_iter][3]
            self.scale_out.set_value(int(volume * 100))
            # Move todos streams para a saída selecionada
            index = model[tree_iter][0]
            self.__sink_input_move_all(index)
            # Seleciona saída como padrão
            name = model[tree_iter][1]
            self.__pulse.sink_default_set(name)

    def __volume_input_moved(self, event, data):

        value = self.scale_in.get_value() / 100
        channels = 1
        # Atualiza o valor na lista do combobox
        tree_iter = self.input_combo.get_active_iter()
        if tree_iter is not None:
            model = self.input_combo.get_model()
            model[tree_iter][3] = value
            channels = model[tree_iter][4]
        # Altera o volume da entrada no pulse
        self.set_volume_input(self.__get_index_selected(self.input_combo),
                              value, channels)

    def __volume_output_moved(self, event, data):

        value = self.scale_out.get_value() / 100
        channels = 1
        # Atualiza o valor na lista do combobox
        tree_iter = self.output_combo.get_active_iter()
        if tree_iter is not None:
            model = self.output_combo.get_model()
            model[tree_iter][3] = value
            channels = model[tree_iter][4]

        # Altera o volume da saída no pulse
        self.set_volume_output(self.__get_index_selected(self.output_combo),
                               value, channels)
