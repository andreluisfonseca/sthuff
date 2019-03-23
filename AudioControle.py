from RTSP import RTSP_Server, RTSP_Server_Password

class AudioControl:

    def gst_rtsp_server(volume=0.5,rate = 44100,interface=""):
        gst_str = (' pulsesrc ! volume volume = %s !'
                   'audio / x - raw, format = S16LE, rate = %s , channels = 1 ! '
                   'speexenc ! rtpspeexpay name=pay0 pt=96 ' %
                   (volume,rate))
        return gst_str

    def gst_rtsp_client(host='127.0.0.1', port=8553, factory="audio", latency=100, tee=""):
        gst_str = ( 'rtspsrc location=\"rtsp://%s:%s/%s\"  latency=%s ! '
                   'rtpspeexdepay ! speexdec ! audioconvert %s ! pulsesink sync=false'                   (host,port,factory, latency, tee))


class AudioRTSP:


    def __init__(self,ip="127.0.0.1",port=8553,gst_str=AudioControl.gst_rtsp_server()):
        self.rtsp_server = RTSP_Server(ip=ip,port=port, factory="/audio", gst_str=gst_str)


    def __init__(self, ip="127.0.0.1", port=8553, user="audio", password="123456",
                 gst_str=AudioControl.gst_rtsp_server()):
        self.rtsp_server = RTSP_Server_Password(ip=ip, port=port, user = user,password = password,
                                       factory="/audio", gst_str=gst_str)