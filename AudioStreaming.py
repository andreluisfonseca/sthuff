class AudioStreaming:

    def opus_audio(volume=0.5, interface=""):
        gst_str = ('pulsesrc  %s ! volume volume = %s ! '
                   'opusenc ! rtpopuspay ! '
                   'multiudpsink clients=127.0.0.1:9002,127.0.0.1:9003' %
                   (interface, volume))
        return gst_str


    def rtsp_server_opus(port=9002):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtpopusdepay ! decodebin ! '
                   'opusenc  ! rtpopuspay name = pay0 pt = 96  ' %
                   (port)
                   )
        return gst_str

    def rtsp_client(host='127.0.0.1', port=8555, factory="audio", latency=50):
        gst_str = ('rtspsrc location=\"rtsp://%s:%s/%s\"  latency=%s ! '
                   'rtpopusdepay ! decodebin  ! '
                   'tee  name = tee ! queue  name = audioqueue ! '
                   'pulsesink sync=false' %
                   (host, port, factory, latency)
                  )
        return gst_str

    def rtp_client_opus(port=9002):
        gst_str = ('udpsrc port=%s caps=\"application/x-rtp\" ! '
                   'rtpopusdepay ! decodebin  ! '
                   'pulsesink sync=false' %
                   (port))
        return gst_str