#!/usr/bin/env python3

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GstRtspServer

GObject.threads_init()
Gst.init(None)

class RTSP_Server:
    ''' Esta classe só funciona com a biblioteca gst-rtsp-server instalada '''

    def __init__(self,ip="0.0.0.0",port="8554",factory="/test",
                 gst_str=" videotestsrc ! x264enc ! rtph264pay name=pay0 pt=96 "):
        self.server = GstRtspServer.RTSPServer.new()
        self.address = ip
        self.port = port

        self.launch_description = gst_str

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        self.server.connect("client-connected", self.client_connected)

        self.factory = GstRtspServer.RTSPMediaFactory().new()
        self.factory.set_launch(self.launch_description)
        #self.factory.set_latency(0)
        self.factory.set_shared(True)
        #self.factory.set_transport_mode(GstRtspServer.RTSPTransportMode.PLAY)
        self.mount_points = self.server.get_mount_points()
        self.mount_points.add_factory(factory, self.factory)

        self.server.attach(None)
        print('Stream ready')
        #self.loop = GObject.MainLoop()
        #self.loop.run()

    def client_connected(self, arg1, arg2):
        print('Client connected')

class RTSP_Server_Password:
    ''' Esta classe só funciona com gstreamer versão 1.14.x '''

    def __init__(self, ip="0.0.0.0",port="8554",factory="/test", user="user", password="123",
                 gst_srt=" videotestsrc ! x264enc ! rtph264pay name=pay0 pt=96 "):
        self.server = GstRtspServer.RTSPServer.new()
        self.address =  ip
        self.port = port
        self.launch_description = gst_srt

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        self.server.connect("client-connected", self.client_connected)

        auth = GstRtspServer.RTSPAuth()
        token = GstRtspServer.RTSPToken()
        token.set_string('media.factory.role', user)
        basic = GstRtspServer.RTSPAuth.make_basic(user, password)
        auth.add_basic(basic, token)
        self.server.set_auth(auth)

        self.permissions = GstRtspServer.RTSPPermissions()
        self.permissions.add_permission_for_role(user, "media.factory.access", True)
        self.permissions.add_permission_for_role(user, "media.factory.construct", True)

        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_permissions(self.permissions)
        self.factory.set_launch(self.launch_description)
        self.factory.set_shared(True)
        self.factory.set_transport_mode(GstRtspServer.RTSPTransportMode.PLAY)
        self.mount_points = self.server.get_mount_points()
        self.mount_points.add_factory(factory, self.factory)

        self.server.attach(None)
        print('Stream ready')
        #self.loop = GObject.MainLoop()
        #self.loop.run()

    def client_connected(self, arg1, arg2):
        print('Client connected')


