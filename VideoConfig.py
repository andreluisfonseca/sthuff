import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from v4l2 import V4l2ctl, Image


class VideoConfig(Gtk.Box):

    def __init__(self,server):
        Gtk.Box.__init__(self)

        self.set_border_width(5)

        self.server = server
        # Obtém informaçoes das cameras no sistema (Drive V4l2)
        self.v_control = V4l2ctl()
        self.cams = self.v_control.cams
        self.image = None

        # dados para as configuração de vídeo
        self.formats = {}
        self.controls = {}
        self.devices = {}

        # lista de câmeras
        self.__cam_list = Gtk.ListStore(int, str)
        # lista de resolução
        self.__res_list = Gtk.ListStore(str)
        # lista de FPS
        self.__fps_list = Gtk.ListStore(int)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(250)

        self.video_config = self.__create_VideoConfig()
        stack.add_titled(self.video_config, "Vídeo", "Vídeo")

        self.image_config = self.__create_ImageConfig()
        stack.add_titled(self.image_config, "Imagem", "Imagem")

        # Cria a lista de informação das configuração
        self.update_list()

        stack_switcher = Gtk.StackSwitcher(halign=Gtk.Align.CENTER)
        stack_switcher.set_stack(stack)
        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, True, True, 0)

    def __create_ImageConfig(self):

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        self.ad_brilho = Gtk.Adjustment(0, 0, 255, 1, 0, 0)
        self.ad_contraste = Gtk.Adjustment(0, 0, 255, 1, 0, 0)
        self.ad_saturacao = Gtk.Adjustment(0, 0, 255, 1, 0, 0)
        self.ad_nitidez = Gtk.Adjustment(0, 0, 255, 1, 0, 0)

        # Ajuste de Brilho
        label_bri = Gtk.Label(label="Brilho:")
        grid.attach(label_bri, 0, 0, 1, 1)
        self.scale_bri = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.ad_brilho)
        self.scale_bri.set_digits(0)
        grid.attach(self.scale_bri, 1, 0, 2, 1)

        self.scale_bri.connect("button-release-event", self.__on_brightness_moved)
        self.scale_bri.connect("key_release_event", self.__on_brightness_moved)

        # Ajuste de Contraste
        label_con = Gtk.Label(label="Contraste:")
        grid.attach(label_con, 0, 1, 1, 1)
        self.scale_con = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.ad_contraste)
        self.scale_con.set_digits(0)
        grid.attach(self.scale_con, 1, 1, 2, 1)

        self.scale_con.connect("button-release-event", self.__on_contrast_moved)
        self.scale_con.connect("key_release_event", self.__on_contrast_moved)

        # Ajuste de Saturação
        label_sat = Gtk.Label(label="Saturação:")
        grid.attach(label_sat, 0, 2, 1, 1)
        self.scale_sat = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.ad_saturacao)
        self.scale_sat.set_digits(0)
        grid.attach(self.scale_sat, 1, 2, 2, 1)

        self.scale_sat.connect("button-release-event", self.__on_saturation_moved)
        self.scale_sat.connect("key_release_event",  self.__on_saturation_moved)

        # Ajuste de Nitidez
        label_nit = Gtk.Label(label="Nitidez:")
        grid.attach(label_nit, 0, 3, 1, 1)
        self.scale_nit = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.ad_nitidez)
        self.scale_nit.set_digits(0)
        grid.attach(self.scale_nit, 1, 3, 2, 1)

        self.scale_nit.connect("button-release-event", self.__on_sharpness_moved)
        self.scale_nit.connect("key_release_event", self.__on_sharpness_moved)


        icon_size = Gtk.IconSize.LARGE_TOOLBAR
        change_icon = Gtk.Image.new_from_icon_name("emblem-default", icon_size)
        reset_btn = Gtk.Button(image=change_icon, label="Restaurar Padrão")
        grid.attach(reset_btn, 0, 4, 3, 1)
        reset_btn.connect("clicked", self.__reset_default)

        frame_image = Gtk.Frame(label="Imagem (Câmera):")
        frame_image.add(grid)
        #frame_image.set_sensitive(False)

        return frame_image

    def __create_VideoConfig(self):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        ad_bitrate = Gtk.Adjustment(500, 500, 3000, 1, 0, 0)

        # Escolha da Interface de Video
        label_int = Gtk.Label(label="Interface:")
        grid.attach(label_int, 0, 0, 1, 1)
        self.interface_combo = Gtk.ComboBox.new_with_model(self.__cam_list)
        renderer_text = Gtk.CellRendererText()
        self.interface_combo.pack_start(renderer_text, True)
        self.interface_combo.add_attribute(renderer_text, "text", 1)
        grid.attach(self.interface_combo, 1, 0, 2, 1)
        self.interface_combo.connect("changed", self.__on_select_device)

        # Ajuste de Resolução
        label_resolucao = Gtk.Label(label="Resolução:")
        grid.attach(label_resolucao, 0, 1, 1, 1)
        self.resolucao_combo = Gtk.ComboBox.new_with_model(self.__res_list)
        renderer_text = Gtk.CellRendererText()
        self.resolucao_combo.pack_start(renderer_text, True)
        self.resolucao_combo.add_attribute(renderer_text, "text", 0)
        grid.attach(self.resolucao_combo, 1, 1, 2, 1)
        self.resolucao_combo.connect("changed", self.__on_select_resolution)
        self.resolucao_combo.connect("move-active", self.__moved__)

        # Ajuste de FPS
        label_FPS = Gtk.Label(label="FPS:")
        grid.attach(label_FPS, 0, 2, 1, 1)
        self.FPS_combo = Gtk.ComboBox.new_with_model(self.__fps_list)
        renderer_text = Gtk.CellRendererText()
        self.FPS_combo.pack_start(renderer_text, True)
        self.FPS_combo.add_attribute(renderer_text, "text", 0)
        grid.attach(self.FPS_combo, 1, 2, 2, 1)
        self.FPS_combo.connect("changed", self.__on_select_fps)

        # Ajuste de Taxa de bits
        label_nit = Gtk.Label(label="Taxa de bits:")
        grid.attach(label_nit, 0, 3, 1, 1)
        self.scale_bitrate = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad_bitrate)
        self.scale_bitrate.set_digits(0)
        self.scale_bitrate.set_value(500)
        grid.attach(self.scale_bitrate, 1, 3, 2, 1)

        self.scale_bitrate.connect("button-release-event", self.__on_bitrate_moved)
        self.scale_bitrate.connect("key_release_event", self.__on_bitrate_moved)

        icon_size = Gtk.IconSize.LARGE_TOOLBAR
        change_icon = Gtk.Image.new_from_icon_name(Gtk.STOCK_OK, icon_size)
        self.alter_btn = Gtk.Button(image=change_icon, label="Alterar")
        grid.attach(self.alter_btn, 0, 4, 3, 1)
        self.alter_btn.connect("clicked",self.__alter_parameters)

        frame_video = Gtk.Frame(label="Vídeo (Streaming):")
        frame_video.add(grid)

        #frame_video.set_sensitive(False)

        return frame_video

    def update_list(self):
        # Se existir alguma câmera
        if len(self.cams) != 0:
            self.formats.clear()
            self.controls.clear()
            for i in self.cams:
                self.formats[i]= self.v_control.get_formats(i)
                formats_name = self.formats[i].keys()
                if "H264" in formats_name or "MJPG" in formats_name:
                    self.controls[i] = self.v_control.get_controls(i)

            self.devices = self.v_control.get_devices()

            # Atualiza a lista de câmera
            self.__update_device_list()

            # Marca primeiro valor na interface
            self.interface_combo.set_active(0)
            # self.resolucao_combo.set_active(0)
            # self.FPS_combo.set_active(0)

        # Se não existir nenhuma câmera
        else:
            self.video_config.set_sensitive(False)
            self.image_config.set_sensitive(False)

    def __set_list_stored(self, lista, data):
        lista.clear()
        for item in data:
            if type(item) == list:
                lista.append(item)
            else:
                lista.append([item])

    def __update_device_list(self):
        # Atualiza a lista de câmera
        cam_list = [[c, self.devices["/dev/video%s" % c]['name']] for c in self.cams]
        self.__set_list_stored(self.__cam_list, cam_list)

    def __update_res_list(self,cam):
        # Atualiza a lista de resolução
        res_list = [k for k in self.formats[cam]['MJPG'].keys()]
        res_list.sort(key=lambda x: int(x.split("x")[0]),reverse = True)
        self.__set_list_stored(self.__res_list, res_list)

    def __update_fps_list(self, size, cam):
        # Atualiza a lista de fps
        if size != '':
            fps_list = self.formats[cam]['MJPG'][size]
            self.__set_list_stored(self.__fps_list, fps_list)

    def __get_selected_value(self, combo, index=0):
        tree_iter = combo.get_active_iter()
        value = ""
        if tree_iter is not None:
            model = combo.get_model()
            value = model[tree_iter][index]
        return value

    def __clear_image_config(self):
        self.scale_bri.set_value(0)
        self.scale_con.set_value(0)
        self.scale_sat.set_value(0)
        self.scale_nit.set_value(0)

    def __set_image_config(self):
        # Altera os valores da imagem
        self.scale_bri.set_value(self.image.brightness)
        self.scale_con.set_value(self.image.contrast)
        self.scale_sat.set_value(self.image.saturation)
        self.scale_nit.set_value(self.image.sharpness)
        # Configura os valores máximos
        self.ad_brilho.set_upper(self.image.brightness_max)
        self.ad_contraste.set_upper(self.image.contrast_max)
        self.ad_saturacao.set_upper(self.image.saturation_max)
        self.ad_nitidez.set_upper(self.image.sharpness_max)

    def __reset_default(self, action):
        self.image.reset_default()
        self.__set_image_config()

    def __alter_parameters(self, action):
        self.set_streaming_parameters()

    def set_streaming_parameters(self):
        dev =  self.__get_selected_value(self.interface_combo)
        res = self.__get_selected_value(self.resolucao_combo)
        fps = self.__get_selected_value(self.FPS_combo)
        width = int(res.split("x")[0])
        height = int(res.split("x")[1])
        frame = int(fps)
        bitrate = int(self.scale_bitrate.get_value())

        # Reinicia o streaming de vídeo
        self.server.stop_capture_video()
        self.server.set_capture_parameters(dev,
                                           bitrate,
                                           width,
                                           height,
                                           frame)
        self.server.start_capture_video()

    def __moved__(self, event, data):
        self.set_streaming_parameters()

    def __on_brightness_moved(self, event, data):
        self.image.brightness = self.scale_bri.get_value()

    def __on_contrast_moved(self,event, data):
        self.image.contrast = self.scale_con.get_value()

    def __on_saturation_moved(self, event, data):
        self.image.saturation = self.scale_sat.get_value()

    def __on_sharpness_moved(self, event, data):
        self.image.sharpness = self.scale_nit.get_value()

    def __on_bitrate_moved(self, event, data):
        print("bitrate=", self.scale_bitrate.get_value())

    def __on_select_device(self, combo):
        cam = self.__get_selected_value(combo)
        if cam != "":
            self.formats[cam] = self.v_control.get_formats(cam)
            formats_name = self.formats[cam].keys()
            if "H264" in formats_name or "MJPG" in formats_name:
                # Habilita interfaces
                self.image_config.set_sensitive(True)
                self.scale_bitrate.set_sensitive(True)
                self.alter_btn.set_sensitive(True)
                # Atualiza Lista
                self.__update_res_list(cam)
                self.resolucao_combo.set_active(0)
                # Configuração para alteração da Imagem
                self.image = Image(cam)
                self.__set_image_config()
            else:
                # Desabilita interfaces
                self.image_config.set_sensitive(False)
                self.scale_bitrate.set_sensitive(False)
                self.alter_btn.set_sensitive(False)
                # Limpa listas
                self.__res_list.clear()
                self.__fps_list.clear()
                # Reseta as configurção da imagem
                self.__clear_image_config()


    def __on_select_resolution(self, combo):
        cam = self.__get_selected_value(self.interface_combo)
        self.__update_fps_list(self.__get_selected_value(combo), cam)
        self.FPS_combo.set_active(0)

    def __on_select_fps(self, combo):
        pass