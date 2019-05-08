import subprocess
import os
import v4l2ctl

class Image:
    '''
    Classe para realizar a alteração de imagem das web câmeras do sistema
    compatível com o drive v4l2,  mesma usava o modulo 'v4l2ctl'
    '''

    def __init__(self,cam=0):
        self.cam = cam
        self.controls = V4l2ctl(self.cam).get_controls()
        self.start()

        self.bri_id = int(self.controls["Brightness"]["id"])
        self.con_id = int(self.controls["Contrast"]["id"])
        self.sat_id = int(self.controls["Saturation"]["id"])
        self.sha_id = int(self.controls["Sharpness"]["id"])

    def reset_default_factory(self):
        for c in self.controls.values():
            id = c["id"]
            default = c["default"]
            self.control.set_control(id, default)

    def reset_default(self):
        self.control.set_control(self.bri_id, self.controls["Brightness"]["default"])
        self.control.set_control(self.con_id, self.controls["Contrast"]["default"])
        self.control.set_control(self.sat_id, self.controls["Saturation"]["default"])
        self.control.set_control(self.sha_id, self.controls["Sharpness"]["default"])

    def start(self):
        self.control = V4l2ctl(self.cam).drive

        self.bri_id = int(self.controls["Brightness"]["id"])
        self.con_id = int(self.controls["Contrast"]["id"])
        self.sat_id = int(self.controls["Saturation"]["id"])
        self.sha_id = int(self.controls["Sharpness"]["id"])

    def set_brightness(self, value):
        cod = self.bri_id
        self.control.set_control(cod, value)

    def get_brightness(self):
        cod = self.bri_id
        return self.control.get_control(cod)

    def get_brightness_max(self):
        return int(self.controls["Brightness"]["max"])

    def get_brightness_min(self):
        return int(self.controls["Brightness"]["min"])

    def set_contrast(self, value):
        cod = self.con_id
        self.control.set_control(cod, value)

    def get_contrast(self):
        cod = self.con_id
        return self.control.get_control(cod)

    def get_contrast_max(self):
        return int(self.controls["Contrast"]["max"])

    def get_contrast_min(self):
        return int(self.controls["Contrast"]["min"])

    def set_saturation(self, value):
        cod = self.sat_id
        self.control.set_control(cod, value)

    def get_saturation(self):
        cod = self.sat_id
        return self.control.get_control(cod)

    def get_saturation_max(self):
        return int(self.controls["Saturation"]["max"])

    def get_saturation_min(self):
        return int(self.controls["Saturation"]["min"])

    def set_sharpness(self, value):
        cod = self.sha_id
        self.control.set_control(cod, value)

    def get_sharpness(self):
        cod = self.sha_id
        return self.control.get_control(cod)

    def get_sharpness_max(self):
        return int(self.controls["Sharpness"]["max"])

    def get_sharpness_min(self):
        return int(self.controls["Sharpness"]["min"])

    brightness = property(get_brightness, set_brightness)
    contrast = property( get_contrast, set_contrast)
    saturation = property(get_saturation, set_saturation)
    sharpness = property(get_sharpness, set_sharpness)

    brightness_max = property(get_brightness_max)
    contrast_max = property(get_contrast_max)
    saturation_max = property(get_saturation_max)
    sharpness_max = property(get_sharpness_max)

    brightness_min = property(get_brightness_min)
    contrast_min = property(get_contrast_min)
    saturation_min = property(get_saturation_min)
    sharpness_min = property(get_sharpness_min)


class V4l2ctl:
    '''
    Classe para realizar a caputura de informação sobre as web câmeras do sistema
    compatível com o drive v4l2,  mesma usava o modulo 'v4l2ctl'
    '''

    def __init__(self, device=None):
        # lista das cameras
        self.cams = self.get_cams()
        self.drive = None

        if device is not None:
            self.device = device
            self.drive = v4l2ctl.V4l2("/dev/video%s" % str(self.device))


    def get_cams(self):
        cams = [x.replace("video", "") for x in os.listdir("/dev") if x.startswith("video")]
        cams.sort()
        self.__parse_to_int__(cams)
        return cams

    def __start__(self):
        self.drive = v4l2ctl.V4l2("/dev/video%s" % str(self.device))

    def get_devices(self):
        dev_list = v4l2ctl.list_devices()
        devices = {}

        for d in dev_list:
           devices[d['dev_path']] = dict(name=d['dev_name'],
                                         bus=d['bus_info'])
        return devices

    def get_device_info(self,device=None):

        if device is not None:
            self.device = device
            self.__start__()

        return self.dive.get_info()

    def get_formats(self, device=None):

        if device is not None:
            self.device = device
            self.__start__()


        v = self.drive

        # Pega a lista de formatos
        f_list = v.transport_formats
        formats ={}
        for f in f_list:
            v.transport_format = f
            formats[f] = {}
            res_list = v.frame_sizes
            for r in res_list:
                v.frame_size = r
                r = str('%sx%s' % (r[0],r[1]))

                # Cria conjunto para nao repedir valores
                frame_rates = {x[1] for x in v.frame_rates}

                # Transforma conjunto em lista
                frame_rates = [x for x in frame_rates]
                frame_rates.sort(reverse=True)

                formats[f][r] = frame_rates

        return formats

    def __get_uvcl_data__(self, options, video=0):
        """Run uvcdynctrl"""
        cams = self.cams

        if len(cams) == 0:
            raise Exception("No has camera in system")

        output = subprocess.check_output(['uvcdynctrl', str(options), '-d', str('/dev/video' + str(video))]).decode()

        return output

    def get_controls(self, device=None):

        if device is not None:
            self.device = device
            self.__start__()

        # Pega a lista de  controles
        c_list =  self.drive.get_controls()
        controls = {}
        for c in c_list:
            controls[c['name']] = c

        return controls

    def __parse_to_int__(self,list):
        """Parse items in list to int"""
        for i in range(len(list)):
            try:
                list[i] = int(list[i])
            except:
                continue


    def main_test(self):
        """Main function test"""


        self.device = self.cams[0]
        print (self.cams[0])
        print('### devices')
        devices = self.get_devices()
        print(devices)

        self.__start__()

        print('\n\n### Controls')
        controls = self.get_controls()
        for control in controls:
            print(control,controls[control])

        print('\n\n### Formats')
        formats = self.get_formats()
        print(formats)
        # ordena a lista de resolução de H264
        teste = [ k for k in formats['MJPG'].keys()]
        teste.sort(key=lambda x: int(x.split("x")[0]))
        print(teste)

        c = Image(self.device)


       # print(c.brightness)
        #c.brightness = 100
        #print(c.contrast)
        #c.contrast = 9

        #print(c.saturation)
        #print(c.sharpness)
        #c.sharpness = 100

        print(c.contrast_max)
        print(c.saturation_max)

#V4l2ctl().main_test()
