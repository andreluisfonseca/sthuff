'''
Classe para realizar a caputura de informação sobre as web câmeras do sistema
compatível com o drive v4l2,  mesma usava um subprocesso para recuperar
a saída do comando 'v4l2-ctl', porém o mesmo muda o retorno de acordo com a versão
ficando oneroso sua alteração de acordo com a plataforma do linux que usar.
portanto ainda ainda será deixa nessa ambiente só como referência para futuros usos.
'''

import subprocess
import re
import os

class V4l2ctl:

    def __init__(self):
        # lista das cameras
        self.cams = self.get_cams()

    def get_cams(self):
        cams = [x.replace("video","") for x in os.listdir("/dev") if x.startswith("video")]
        cams.sort()
        self.__parse_to_int__(cams)
        return cams

    def get_devices(self,video=0):
        dev = self.__get_v4l2_data__('--list-devices', video)
        return self.__parse_devices__(dev)

    def get_formats(self,video=0):
        formats = self.__get_v4l2_data__('--list-formats-ext', video)
        return self.__parse_format__(formats)

    def get_controls(self,video=0):
        controls = self.__get_v4l2_data__('--list-ctrls', video)
        return  self.__parse_controls__(controls)

    def __get_v4l2_data__(self, options, video=0):
        """Run v4l2"""
        cams = self.cams

        if len(cams) == 0:
            raise Exception("No has camera in system")

        output = subprocess.check_output(['v4l2-ctl', str(options), '-d', str('/dev/video'+str(video))]).decode()

        return output

    def __parse_devices__(self, data):

        # Pré-processanto do texto
        lines = data.split("\n\n")
        items = [[kv.strip() for kv in line.split('\n\t')] for line in lines]

        # dados de retorno
        devices = {}

        for item in items:
            if item[0] != "":
                data = item[0].split(' (')
                devices[item[1]] = dict(name=data[0].strip().replace(":",""),
                                        bus=data[1].strip().replace("):", ""))

        return devices

    def __parse_to_int__(self,list):
        """Parse items in list to int"""
        for i in range(len(list)):
            try:
                list[i] = int(list[i])
            except:
                continue

    def __parse_controls__(self, data):
        """Parse v4l2 control"""

        # Pré-processanto do texto
        lines = data.split('\n')
        items = [[kv.strip() for kv in line.split(':')] for line in lines]

        # dados de retorno
        controls = {}

        for item in items:
            if len(item) > 1:
                values = item[1].replace("=", " ").split(" ")
                self.__parse_to_int__(values)
            i = iter(values)
            dic_values = dict(dict(zip(i, i)))

            index = item[0].split(" ")[0]
            if index != "":
                controls[index] = dic_values

        # print(controls)
        return controls

    def __parse_format__(self, data):
        """Parse v4l2 format"""

        # Pré-processanto do texto
        lines = data.split('\n')
        items = [[kv.strip() for kv in line.split(':')] for line in lines]

        # dados de retorno
        formatos = {}
        parens = re.compile(r"\(.+?\)")
        resolucao = []
        FPS = []
        fps_set = []
        for item in items:
            # print(item)
            if item[0] == 'Pixel Format':
                formato = item[1].split(" ")[0].replace("'","")

                resolucao = []
                FPS = []
                formatos[formato] = (resolucao,FPS)
                #print('\n{}\n'.format(formato))

            elif item[0] == 'Size':

                size = item[1].strip('Discrete').strip(' ')
                resolucao.append(size)
                fps_set = []
                if len(formatos.keys()) > 0:
                    FPS.append(fps_set)
                #print('Size:{}'.format(size))

            elif item[0] == 'Interval':

                res = parens.search(item[1]).group(0)
                fps = res.strip('(').strip(')').split(' ')[0]
                fps_set.append(fps)
                #print('FPS:{}'.format(fps))

        # Transforma todas as listas de resolução de cada formato
        # em dicionário com sua respectiva lista de FPS
        for f in formatos:
           resolucao = {}
           res = formatos[f][0]
           for r in range(len(res)):
               resolucao[res[r]] = formatos[f][1][r]
           formatos[f] = resolucao

        #print(formatos)
        return formatos

    def main_test(self):
        """Main function test"""

        print('### devices')
        devices = self.get_devices(self.cams[0])
        print(devices)

        print('\n\n### Controls')
        controls = self.get_controls(self.cams[0])
        for control in controls:
            print(control, controls[control])

        print('\n\n### Formats')
        formats = self.get_formats(self.cams[0])
        print(formats)
        # ordena a lista de resolução de H264
        teste = [k for k in formats['MJPG'].keys()]
        teste.sort(key=lambda x: int(x.split("x")[0]))
        print(teste)

V4l2ctl().main_test()