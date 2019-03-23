from RTSP import RTSP_Server, RTSP_Server_Password

class VideoControl:

    def gst_sem_camera(rate = 500, width=1280, height=720,port=6000):
        gst_str = ('videotestsrc pattern=snow ! video/x-raw,width=%s,height=%s ! '
                   'textoverlay text="Sistema sem camera" valignment=center '
                   'halignment=center font-desc="Sans, 48" ! '
                   'x264enc  speed-preset=ultrafast bitrate=%s ! '
                   'mpegtsmux ! tcpserversink host=0.0.0.0 port=%s' %
                   (width, height, rate , port))
        return gst_str

    def gst_camera_com_h264(rate=500,dev=0,width=1280, height=720,framerate=30,port=6000):
        gst_str = ('uvch264src initial-bitrate=%s average-bitrate=%s iframe-period=3000 '
                  'device=/dev/video%s  name=src auto-start=true  src.vidsrc ! '  
                  'video/x-h264,width=%s,height=%s,framerate=%s/1,profile=constrained-baseline !' 
                  ' mpegtsmux ! tcpserversink host=0.0.0.0 port=%s' %
                   ((rate*1000),(rate*1000),dev,width,height,framerate,port)
                  )
        return gst_str

    def gst_camera_sem_h264(rate=500,dev=0,width=1280, height=720,framerate=30,port=6000):
        gst_str = ( 'v4l2src  device=/dev/video%s ! video/x-raw,width=%s,height=%s,framerate=%s/1 ! '
                    'x264enc  speed-preset=ultrafast bitrate=%s !  mpegtsmux ! '
                    'tcpserversink host=localhost port=%s' %
                    (dev, width, height, framerate, rate, port)
                   )
        return gst_str

    def gst_vp8_cam(rate=500,dev=0,width=1280, height=720,framerate=30,port=6000):
        gst_str =( 'v4l2src device=/dev/video%s ! video/x-raw,width=%s,height=%s,framerate=%s/1  ! '
                   'vp8enc deadline=1 target-bitrate=%s ! webmmux !  '
                   'tcpserversink host=localhost port=%s' %
                   (dev,  width, height, framerate,(rate * 1000), port)
                 )
        return gst_str

    def gst_rtsp_server(port=6000,host="127.0.0.1"):
        gst_str = ('tcpclientsrc port=%s host=%s ! '
                   'tsdemux !  rtph264pay name=pay0 pt=96 ' %
                   (port,host))
        return gst_str


    def gst_rtsp_client(host='127.0.0.1', port=8554, factory="video", latency=100, tee=""):
        gst_str = ( 'rtspsrc location=\"rtsp://%s:%s/%s\"  latency=%s ! '
                   'rtph264depay ! avdec_h264 %s ! autovideosink sync=false' %
                   (host,port,factory, latency, tee))
        return gst_str

    def gst_tcp_client(host="127.0.0.1",port=6000):
        gst_str = ('tcpclientsrc port=%s host=%s ! '
                   'tsdemux ! h264parse ! avdec_h264 ! '
                   'autovideosink sync=false' %
                   (port, host))
        return gst_str


class VideoRTSP:

    def __init__(self,ip="127.0.0.1",port=8554,gst_str="( videotestsrc ! x264enc ! rtph264pay name=pay0 pt=96 )"):

        self.rtsp_server = RTSP_Server(ip=ip,port=port, factory="/video", gst_str=gst_str)


    def __init__(self,ip="127.0.0.1",port=8554, user="video", password="123456",
                 gst_str="( videotestsrc ! x264enc ! rtph264pay name=pay0 pt=96 )"):

        self.rtsp_server = RTSP_Server_Password(ip=ip, port=port, user = user,password = password,
                                       factory="/video", gst_str=gst_str)