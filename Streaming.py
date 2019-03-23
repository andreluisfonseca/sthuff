import os
from datetime import datetime
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk
from VideoControle import VideoControl
from RTSP import RTSP_Server


class Streaming_Server:

    def __init__(self):

        Gst.init(None)

        # Listas as cameras do sistem
        cams= [x for x in os.listdir("/dev") if x.startswith("video")]
        cams.sort()
        if len(cams) == 0:
            self.dev=-1
        else:
            print(cams[0])
            self.dev = int(cams[0].replace("video",""))

        self.pipeline = None
        self.rtsp_server = None


    def start_video_capture(self):

        gst_cap = ""

        if self.dev == -1:
            gst_cap = VideoControl.gst_sem_camera()
            print(gst_cap)

        else:
            gst_cap = VideoControl.gst_camera_com_h264(dev=self.dev,width=1280, height=720)

        self.pipeline = Gst.parse_launch( gst_cap )
        # Create bus to get events from GStreamer pipeline
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_eos_capture__)
        bus.connect('message::error', self.__on_error_capture__)
        self.pipeline.set_state(Gst.State.PLAYING)

    def __on_error_capture__(self, bus, msg):
        print('on_error():', msg.parse_error())

    def __on_eos_capture__(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def __message__(self,data=""):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()

    def stop_capture(self):
        self.pipeline.set_state(Gst.State.NULL)


    def __start_RTSP_Server__(self):

        gst_video_audio_vp8 = ('tcpclientsrc port=%s host=%s ! '
                               'matroskademux  !  rtpvp8pay name=pay0 pt=96 ' 
                               'pulsesrc ! opusenc ! rtpopuspay name=pay1 pt=97 ' %
                               (6000, '127.0.0.1'))

        gst_video_audio_h264 = ('tcpclientsrc port=%s host=%s ! '
                                'tsdemux !  rtph264pay name=pay0 pt=96 '
                                'pulsesrc ! opusenc ! rtpopuspay name=pay1 pt=97 ' %
                                (6000, '127.0.0.1'))
        #print(gst_video_audio)

        self.rtsp_server = RTSP_Server(ip="0.0.0.0", port="8554", factory="/stream", gst_str=gst_video_audio_h264)

    def run(self):
        if self.pipeline is not None:
            self.stop_capture()
        self.start_video_capture()
        self.__start_RTSP_Server__()
        print("Server RTSP inicado!!!")


    def stop(self):
        self.stop_capture()
        #self.rtsp_server.stop()


class Streaming_Client:

    def __init__(self,ip="127.0.0.1",port=8554,xid=None):

        self.__reconection = 0

        self.ip=ip
        self.port=port
        self.playerID=xid

        Gst.init(None)
        self.pipeline = None

    def connect(self):
        # pipeline CSH
        gst_rtsp_client_h264 = (' rtspsrc location=rtsp://%s:%s/stream latency=100 '
                           ' name=src src. ! rtph264depay ! avdec_h264 ! '
                           ' tee  name = tee ! queue  name = videoqueue ! '
                           ' videobox left=0 right=0 top=-125 bottom=0 ! autovideosink sync=false'
                           ' src. ! rtpopusdepay ! decodebin ! pulsesink ' %
                           (self.ip, self.port))

        gst_rtsp_client_all = ('playbin uri=rtsp://%s:%s/stream uridecodebin0::source::latency=10 ' %
                              (self.ip, self.port))

        gst_rtsp_client_vp8 =  (' rtspsrc location=rtsp://%s:%s/stream latency=100 '
                           ' name=src src. ! rtpvp8depay ! decodebin ! '
                           ' tee  name = tee ! queue  name = videoqueue ! '
                           ' videobox left=0 right=0 top=-125 bottom=0 ! autovideosink '
                           ' src. ! rtpopusdepay ! decodebin ! pulsesink ' %
                           (self.ip, self.port))

        #pipeline CSV
        #gst_rtsp_client = (' rtspsrc location=rtsp://%s:%s/stream latency=100 '
        #                   ' name=src src. ! rtpvp8depay ! decodebin ! '
        #                   ' tee  name = tee ! queue  name = videoqueue ! autovideosink '
        #                   ' src. ! rtpopusdepay ! decodebin ! pulsesink' %
        #                       (self.ip,self.port))


        self.pipeline = Gst.parse_launch( gst_rtsp_client_h264)

        # Create bus to get events from GStreamer pipeline
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.__on_eos_client)
        bus.connect('message::error', self.__on_error_client)

        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message)

        self.pipeline.set_state(Gst.State.PLAYING)

    def __on_error_client(self, bus, msg):
        print('on_error():', msg.parse_error())

        print("tentando se reconectar")
        self.stop()

        if self.__reconection < 3:
            self.connect()
            self.pipeline.set_state(Gst.State.PLAYING)
            self.__reconection += 1
        else:
            self.__reconection = 0

            self.__message__("Houve uma falha na Rede!\n"
                             "Não conseguiu se conectar ao serviço!")


    def __message__(self,data=""):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK, data)
        dialog.run()
        dialog.destroy()


    def __on_eos_client(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle' and self.playerID is not None:
            print('prepare-window-handle')
            msg.src.set_window_handle(self.playerID)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)

    def start_record(self):
        # Filename (current time)

        # record avi
        #filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".avi"
        #self.recordpipe = Gst.parse_bin_from_description("queue name=filequeue ! x264enc  speed-preset=ultrafast bitrate=1500 ! avimux !"
        #                                                " filesink location=" + filename, True)

        # record mkv
        filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".mkv"
        self.recordpipe = Gst.parse_bin_from_description("queue name=filequeue  ! x264enc  speed-preset=ultrafast bitrate=1500 ! "
                                                        "matroskamux ! filesink location=" + filename, True)

        print(filename)
        self.pipeline.add(self.recordpipe)
        self.pipeline.get_by_name("tee").link(self.recordpipe)
        self.recordpipe.set_state(Gst.State.PLAYING)

    def stop_record(self):
        filequeue = self.recordpipe.get_by_name("filequeue")
        filequeue.get_static_pad("src").add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        self.pipeline.get_by_name("tee").unlink(self.recordpipe)
        filequeue.get_static_pad("sink").send_event(Gst.Event.new_eos())
        print("Stopped recording")

    def probe_block(self, pad, buf):
        print("blocked")
        return True
