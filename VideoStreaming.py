class VideoStreaming:
    '''
        Método que retorna o pipe de vídeo em H264 com mesagem "Câmera Incompativel" do gstreamer.
    '''

    def camera_imcompativel_h264(width=1280, height=720):
        gst_str = ('videotestsrc pattern=black ! video/x-raw,width=%s,height=%s ! '
                   'textoverlay text="Câmera incompátivel" valignment=center '
                   'halignment=center font-desc="Sans, 48" ! '
                   'x264enc  speed-preset=ultrafast bitrate=1000 ! h264parse ! rtph264pay ! '
                   'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   (width, height))
        return gst_str
    '''
        Método que retorna o pipe de vídeo em H264 com mesagem "Sem câmera" do gstreamer.
    '''
    def sem_camera_h264(width=1280, height=720):

        gst_str = ('videotestsrc pattern=black ! video/x-raw,width=%s,height=%s ! '
                   'textoverlay text="Sistema sem câmera" valignment=center '
                   'halignment=center font-desc="Sans, 48" ! '
                   'x264enc  speed-preset=ultrafast bitrate=1000 ! h264parse ! rtph264pay ! '
                   'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   (width, height))
        return gst_str

    def sem_camera_vp8(width=1280, height=720):
        gst_str = ('videotestsrc pattern=black ! video/x-raw,width=%s,height=%s ! '
                   'textoverlay text="Sistema sem câmera" valignment=center '
                   'halignment=center font-desc="Sans, 48" ! '
                   'vp8enc deadline=1 target-bitrate=1000000 ! rtpvp8pay ! '
                   'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   (width, height))
        return gst_str

    def camera_imcompativel_vp8(width=1280, height=720):
        gst_str = ('videotestsrc pattern=black ! video/x-raw,width=%s,height=%s ! '
                   'textoverlay text="Câmera incompátivel" valignment=center '
                   'halignment=center font-desc="Sans, 48" ! '
                   'vp8enc deadline=1 target-bitrate=1000000 ! rtpvp8pay ! '
                   'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   (width, height))
        return gst_str

    def camera_h264(rate=512,dev=0,width=1280, height=720,framerate=30):
        gst_str = ('uvch264src initial-bitrate=%s average-bitrate=%s iframe-period=3000 '
                  'device=/dev/video%s  name=src auto-start=true  src.vidsrc ! '  
                  'video/x-h264,width=%s,height=%s,framerate=%s/1,profile=constrained-baseline ! ' 
                  'h264parse ! rtph264pay ! multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   ((rate*1000), (rate*1000), dev, width, height, framerate)
                  )
        return gst_str

    def camera_sem_h264(rate=512,dev=0,width=1280, height=720,framerate=30):
        gst_str = ( 'v4l2src  device=/dev/video%s ! '
                    'video/x-raw,width=%s,height=%s,framerate=%s/1 ! '
                    'x264enc  speed-preset=ultrafast bitrate=%s ! h264parse ! rtph264pay ! '
                    'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                    (dev, width, height, framerate, rate)
                   )
        return gst_str

    def camera_vp8(rate=512,dev=0,width=1280, height=720,framerate=30):
        gst_str =( 'v4l2src device=/dev/video%s ! '
                   'video/x-raw,width=%s,height=%s,framerate=%s/1  ! '
                   'vp8enc deadline=1 target-bitrate=%s ! rtpvp8pay ! '
                   'multiudpsink clients=127.0.0.1:9000,127.0.0.1:9001' %
                   (dev,  width, height, framerate, (rate * 1000))
                 )
        return gst_str

    def rtsp_server_vp8(port=9000):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtpvp8depay ! rtpvp8pay name=pay0 pt=96 ' %
                   (port)
                   )
        return gst_str

    def rtsp_server_h264(port=9000):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtph264depay ! rtph264pay name=pay0 pt=96 ' %
                   (port)
                  )
        return gst_str

    def rtsp_client_vp8(host='127.0.0.1', port=8554, factory="video", latency=100):

        gst_str= ('rtspsrc location=rtsp://%s:%s/%s latency=%s ! '
                  'rtpvp8depay ! decodebin ! '
                  'tee  name = tee ! queue  name = videoqueue ! '
                  'videobox left=0 right=0 top=-125 bottom=0 ! '
                  'xvimagesink sync=false ' %
                  (host,port,factory, latency)
                 )
        return gst_str

    def rtsp_client_h264(host='127.0.0.1', port=8554, factory="video", latency=100):
        gst_str = ('rtspsrc location=\"rtsp://%s:%s/%s\"  latency=%s ! '
                   'rtph264depay ! h264parse ! avdec_h264 ! '
                   'tee  name = tee ! queue  name = videoqueue ! '
                   'videobox left=0 right=0 top=-125 bottom=0 ! '
                   'xvimagesink sync=false' %
                   (host,port,factory, latency))
        return gst_str

    def rtp_client_vp8(port=9001):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtpvp8depay ! decodebin ! '
                   'xvimagesink sync=false' %
                   (port))
        return gst_str

    def rtp_client_h264(port=9001):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtph264depay ! decodebin ! '
                   'tee  name = tee ! queue  name = videoqueue ! '
                   'xvimagesink sync=false' %
                   (port))
        return gst_str