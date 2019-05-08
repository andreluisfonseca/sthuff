import os
from datetime import datetime
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk
from VideoStreaming import VideoStreaming
from AudioStreaming import AudioStreaming
from RTSP import RTSP_Server
from v4l2 import V4l2ctl


class Streaming_Server:

    def __init__(self):

        Gst.init(None)
        self.v_drive = V4l2ctl()

        # Listas as cameras do sistema
        cams= self.v_drive.cams
        cams.sort()

        if len(cams) == 0:
            self.dev=-1
        else:
            self.dev = cams[0]

        self.pipevideo = None
        self.pipeaudio = None
        self.rtsp_video = None
        self.rtsp_audio = None
        # dados para captura do vídeo
        self.width = 1280
        self.height = 720
        self.frame = 30
        self.bitrate = 500

    def set_capture_parameters(self,dev=0, bitrate=500, width=1280, height=720, frame=30):
        self.dev = dev
        self.width = width
        self.height = height
        self.frame = frame
        self.bitrate = bitrate

    def start_capture_video(self,gst_cap=None):

        if gst_cap is None:
            if self.dev == -1:
                gst_cap = VideoStreaming.sem_camera_h264()

            else:
                formats = self.v_drive.get_formats(self.dev).keys()

                if "H264" in formats:
                    gst_cap = VideoStreaming.camera_h264(dev=self.dev,
                                                         rate=self.bitrate,
                                                         width= self.width,
                                                         height=self.height,
                                                         framerate=self.frame)
                elif "MJPG" in formats:
                    gst_cap = VideoStreaming.camera_sem_h264(dev=self.dev,
                                                             rate=self.bitrate,
                                                             width= self.width,
                                                             height=self.height,
                                                             framerate=self.frame)
                else:
                    gst_cap = VideoStreaming.camera_imcompativel_h264()

        self.pipevideo = Gst.parse_launch(gst_cap)
        self.__set_bus_video(self.pipevideo)
        self.pipevideo.set_state(Gst.State.PLAYING)

    def start_capture_audio(self):

        gst_cap = AudioStreaming.opus_audio()
        self.pipeaudio = Gst.parse_launch(gst_cap)
        self.__set_bus_audio(self.pipeaudio)
        self.pipeaudio.set_state(Gst.State.PLAYING)


    def __on_error_capture(self, bus, msg):
        print('on_error():', msg.parse_error())

    def __on_eos_video(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipevideo.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def __on_eos_audio(self, bus, msg):
        print('on_eos(): seeking to start of audio')
        self.pipeaudio.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def __set_bus_video(self,pipe):

        # Create bus to get events from GStreamer pipeline
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_error_capture)
        bus.connect('message::error', self.__on_eos_video)

    def __set_bus_audio(self, pipe):
        # Create bus to get events from GStreamer pipeline
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_error_capture)
        bus.connect('message::error', self.__on_eos_audio)

    def stop_capture_video(self):
        if self.pipevideo is not None:
            self.pipevideo.set_state(Gst.State.NULL)

    def stop_capture_audio(self):
        if self.pipeaudio is not None:
            self.pipeaudio.set_state(Gst.State.NULL)


    def __start_RTSP_Server__(self):
        self.rtsp_video = RTSP_Server(ip="0.0.0.0", port="8554", factory="/video", gst_str=VideoStreaming.rtsp_server_h264())
        self.rtsp_audio = RTSP_Server(ip="0.0.0.0", port="8555", factory="/audio", gst_str=AudioStreaming.rtsp_server_opus())

    '''
    Método que retorna o pipe RSTP server para trasmitir video em VP8 e áudio do gstreamer.
    '''
    def rtsp_video_audio_vp8(self):

        gst_str = ('udpsrc  host=%s port=%s caps=\"application/x-rtp\" ! '
                   'rtpvp8depay  !  rtpvp8pay name=pay0 pt=96 '
                   'pulsesrc ! opusenc ! rtpopuspay name=pay1 pt=97 ' %
                   (9000, '127.0.0.1'))

        return gst_str

    '''
    Método que retorna o pipe RSTP server para trasmitir video em H264 e áudio do gstreamer.
    '''
    def rtsp_video_audio_h264(self):

        gst_str = ('udpsrc  host=%s port=%s caps=\"application/x-rtp\" ! '
                   'rtph264depay !  rtph264pay name=pay0 pt=96 '
                   'pulsesrc ! opusenc ! rtpopuspay name=pay1 pt=97 ' %
                   (9000, '127.0.0.1'))

        return gst_str


    def run(self):
        self.stop()
        self.start_capture_video()
        self.start_capture_audio()
        self.__start_RTSP_Server__()
        print("Server RTSP inicado!!!")


    def stop(self):
        self.stop_capture_video()
        self.stop_capture_audio()
        #self.rtsp_server.stop()


class Streaming_Client:

    def __init__(self,ip="127.0.0.1",parent=None,xid=None):

        Gst.init(None)

        self.__reconection = 0

        self.parent = parent
        self.ip=ip
        self.playerID=xid

        self.pipevideo = None
        self.pipeaudio = None

    def connect(self):

        self.pipevideo = Gst.parse_launch(VideoStreaming.rtsp_client_h264())
        self.pipeaudio = Gst.parse_launch(AudioStreaming.rtsp_client())

        self.__set_bus_video(self.pipevideo)
        self.__set_bus_audio(self.pipeaudio)

        self.start()

    def __set_bus_video(self,pipe):

        # Create bus to get events from GStreamer pipeline
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_eos_video)
        bus.connect('message::error', self.__on_error_client)

        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.__on_sync_message)

    def __set_bus_audio(self,pipe):

        # Create bus to get events from GStreamer pipeline
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_eos_audio)
        bus.connect('message::error', self.__on_error_client)

    def __on_error_client(self,pipe, bus, msg):
        print('on_error():', msg.parse_error())

        print("tentando se reconectar")
        self.stop()

        if self.__reconection < 3:
            self.connect()
            self.start()
            self.__reconection += 1
        else:
            self.__reconection = 0

            self.__message__("Houve uma falha na Rede!\n"
                             "Não conseguiu se conectar ao serviço!")

    def __message__(self, data=""):
        dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()

    def __on_eos_video(self, bus, msg):
        print('on_eos(): seeking to start video')
        self.pipevideo.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0)

    def __on_eos_audio(self, bus, msg):
        print('on_eos(): seeking to start of audio')
        self.pipeaudio.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0)

    def __on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle' and self.playerID is not None:
            print('prepare-window-handle')
            msg.src.set_window_handle(self.playerID)

    def start(self):
        if self.pipevideo is not None:
            self.pipevideo.set_state(Gst.State.PLAYING)

        if self.pipeaudio is not None:
            self.pipeaudio.set_state(Gst.State.PLAYING)

    def stop(self):
        if self.pipevideo is not None:
            self.pipevideo.set_state(Gst.State.NULL)

        if self.pipeaudio is not None:
            self.pipeaudio.set_state(Gst.State.NULL)

    def start_record(self):
        # Filename (current time)

        # record avi
        #filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".avi"
        #gst_str = ("queue name=filequeue ! x264enc  speed-preset=ultrafast bitrate=1500 ! avimux !"
        #           "filesink location=" + filename, True)
        #self.recordpipe = Gst.parse_bin_from_description(gst_str, True)

        # record mkv
        filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".mkv"
        gst_str = ("queue name=filequeue  ! x264enc  speed-preset=ultrafast bitrate=1500 ! "
                   "matroskamux ! filesink location=" + filename)
        self.recordpipe = Gst.parse_bin_from_description(gst_str, True)

        print(filename)
        self.pipevideo.add(self.recordpipe)
        self.pipevideo.get_by_name("tee").link(self.recordpipe)
        self.pipevideo.set_state(Gst.State.PLAYING)
        print("Start recording")

    def stop_record(self):
        filequeue = self.recordpipe.get_by_name("filequeue")
        filequeue.get_static_pad("src").add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        self.pipevideo.get_by_name("tee").unlink(self.recordpipe)
        filequeue.get_static_pad("sink").send_event(Gst.Event.new_eos())
        print("Stopped recording")

    def probe_block(self, pad, buf):
        print("blocked")
        return True


    '''
    Método que retorna o pipe RSTP cliente para reproduzir video H264 e áudio do gstreamer.
    '''
    def rtsp_client_h264(self, ip, port=8554):

        gst_srt = (' rtspsrc location=rtsp://%s:%s/stream latency=100 '
                   ' name=src src. ! rtph264depay ! avdec_h264 ! '
                   ' tee  name = tee ! queue  name = videoqueue ! '
                   ' videobox left=0 right=0 top=-125 bottom=0 ! autovideosink sync=false'
                   ' src. ! rtpopusdepay ! decodebin ! pulsesink sync=false ' %
                   (ip, port))
        return gst_srt


    '''
    Método que retorna o pipe RSTP cliente para reproduzir automaticamente a 
    codificação de áudio e video do gstreamer.
    '''
    def rtsp_client_all(self, ip, port=8554):
        # Em testes essa função ficou dessincronizado o video em relação áudio após a
        # segunda tentativa de execução para o serviço RTSP server.
        gst_srt = ('playbin uri=rtsp://%s:%s/stream uridecodebin0::source::latency=10 ' %
                   (ip, port))

        return gst_srt

    '''
    Método que retorna o pipe RSTP cliente para reproduzir video vp8 e áudio do gstreamer.
    '''
    def rtsp_client_vp8(self, ip, port=8554):

        gst_srt = (' rtspsrc location=rtsp://%s:%s/stream latency=100 '
                   ' name=src src. ! rtpvp8depay ! decodebin ! '
                   ' tee  name = tee ! queue  name = videoqueue ! '
                   ' videobox left=0 right=0 top=-125 bottom=0 ! autovideosink sync=false '
                   ' src. ! rtpopusdepay ! decodebin ! pulsesink sync=false ' %
                   (ip, port))
        return gst_srt


class Streaming_Preview:

    def __init__(self,xid=None):

        Gst.init(None)
        self.playerID=xid
        self.pipevideo = None

    def connect(self):

        self.pipevideo = Gst.parse_launch(VideoStreaming.rtp_client_h264())

        self.__set_bus_video(self.pipevideo)
        self.start()

    def __set_bus_video(self,pipe):

        # Create bus to get events from GStreamer pipeline
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_eos_video)
        bus.connect('message::error', self.__on_error_client)

        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.__on_sync_message)


    def __on_error_client(self,pipe, bus, msg):
        print('on_error():', msg.parse_error())

    def __on_eos_video(self, bus, msg):
        print('on_eos(): seeking to start video')
        self.pipevideo.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0)

    def __on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle' and self.playerID is not None:
            print('prepare-window-handle')
            msg.src.set_window_handle(self.playerID)

    def start(self):
        if self.pipevideo is not None:
            self.pipevideo.set_state(Gst.State.PLAYING)

    def stop(self):
        if self.pipevideo is not None:
            self.pipevideo.set_state(Gst.State.NULL)


    def start_record(self):
        # Filename (current time)

        # record avi
        #filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".avi"
        #gst_str = ("queue name=filequeue ! x264enc  speed-preset=ultrafast bitrate=1500 ! avimux !"
        #           "filesink location=" + filename, True)
        #self.recordpipe = Gst.parse_bin_from_description(gst_str, True)

        # record mkv
        filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".mkv"
        gst_str = ("queue name=filequeue  ! x264enc  speed-preset=ultrafast bitrate=1500 ! "
                   "matroskamux ! filesink location=" + filename)
        self.recordpipe = Gst.parse_bin_from_description(gst_str, True)

        print(filename)
        self.pipevideo.add(self.recordpipe)
        self.pipevideo.get_by_name("tee").link(self.recordpipe)
        self.pipevideo.set_state(Gst.State.PLAYING)
        print("Start recording")

    def stop_record(self):
        filequeue = self.recordpipe.get_by_name("filequeue")
        filequeue.get_static_pad("src").add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        self.pipevideo.get_by_name("tee").unlink(self.recordpipe)
        filequeue.get_static_pad("sink").send_event(Gst.Event.new_eos())
        print("Stopped recording")

    def probe_block(self, pad, buf):
        print("blocked")
        return True


