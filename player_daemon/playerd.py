#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import signal
import time
import logging
import yaml
import subprocess
import json

from optparse import OptionParser
from threading import Thread

from daemon import Daemon

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer


DIR_SCRIPT = os.path.dirname(os.path.realpath(__file__))

# PID
PIDFILE = os.path.join(DIR_SCRIPT, "rpi_mediaplayerd.pid")

# Setup Logging
LOGFILE = os.path.join(DIR_SCRIPT, "rpi_mediaplayerd.log")
LOGLEVEL = logging.DEBUG
logging.basicConfig(filename=LOGFILE, format='%(levelname)s | %(asctime)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

# Settings and Playlist
PLAYLISTFILE = os.path.join(os.path.abspath(os.path.join(DIR_SCRIPT, os.pardir)), "playlist.yaml")
playlist = yaml.load(open(PLAYLISTFILE))

FN_PLAYER_SETTINGS = os.path.join(os.path.abspath(os.path.join(DIR_SCRIPT, os.pardir)), "player_settings.yaml")
player_settings = yaml.load(open(FN_PLAYER_SETTINGS))

# Catch SIGINT to shut the daemon down (eg. via $ kill -s SIGINT [proc-id])
def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def check_pid(pid):
    """ Check For the existence of a unix pid. Sending signal 0 does nothing bad."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


# Each connected client gets a TCPConnection object
class TCPConnection(object):
    def __init__(self, daemon, stream, address):
        logger.debug('- new connection from %s' % repr(address))
        self.daemon = daemon
        self.stream = stream
        self.address = address
        self.stream.set_close_callback(self._on_close)
        self.stream.read_until('\n', self._on_read_line)

    def _on_read_line(self, data):
        data = data.strip()
        if not data or data == "quit":
            self.stream.close()
            return

        # Process input
        response = self.daemon.handle_msg(data)
        if response:
            r = json.dumps(response)
            self.stream.write("%s\n" % r)

        # Continue reading on this connection
        self.stream.read_until('\n', self._on_read_line)

    def _on_write_complete(self):
        pass

    def _on_close(self):
        logger.debug('- client quit %s' % repr(self.address))


# The main server class
class MyTCPServer(TCPServer):
    def __init__(self, daemon, io_loop=None, ssl_options=None, **kwargs):
        TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)
        self.daemon = daemon

    def handle_stream(self, stream, address):
        TCPConnection(self.daemon, stream, address)


class PlayerThread(Thread):
    files = []
    last_file = None
    current_file = None
    current_pid = None
    cnt_file_current = 0

    # states: 0=stopped, 1=playing
    state = 0

    # thread control flags
    is_cancelled = False
    is_finished = False

    def __init__(self):
        Thread.__init__(self)
        self.files = playlist["playlist"]
        self.cnt_file_current = 0
        self.state = 0  # playing

    def run(self):
        while not self.is_finished and not self.is_cancelled:
            if self.is_finished or self.is_cancelled:
                return

            if self.state == 0:
#                logger.info("PlayerThread paused. Wait 1 sec.")
                time.sleep(1)
                continue

            # Try to play file
            fn = self.files[self.cnt_file_current]
            logger.info("PlayerThread: trying to play file %s (#%s)" % (fn, self.cnt_file_current))
            if not os.path.isfile(fn):
                logger.error("Could not find file '%s'" % fn)
                continue

            # Find the right command
            ext = fn.split(".")[-1]
            if ext in player_settings["media_extensions"]["video"]:
                cmd = player_settings["playback_commands"]["video"]
            elif ext in player_settings["media_extensions"]["audio"]:
                cmd = player_settings["playback_commands"]["audio"]
            elif ext in player_settings["media_extensions"]["image"]:
                cmd = player_settings["playback_commands"]["image"]

            # Prepare command to execute
            self.current_file = fn.strip()
#            if " " in fn and not fn.startswith('"'):
#                fn = '"%s"' % fn
            cmd_list = cmd.split(" ")
            for i in xrange(len(cmd_list)):
                if cmd_list[i] == "$1":
                    cmd_list[i] = fn

            # Execute command and wait for it to finish
            try:
                logger.info("- execute: %s" % (cmd_list))
                pipe = subprocess.Popen(cmd_list)
                self.current_pid = pipe.pid
                logger.info("- pid: %s" % self.current_pid)
                while pipe.poll() is None:
                    time.sleep(0.5)
                self.last_file = self.current_file
                self.current_file = None
                self.current_pid = None
                logger.info("- finished playback of '%s'" % fn)
            except Exception as e:
                logger.exception(e)

            self.cnt_file_current = (self.cnt_file_current + 1) % len(self.files)

    def shutdown(self, kill_player=False):
        """ Shutdown """
        logger.info("PlayerThread: shutdown()")
        self.is_finished = True
        if kill_player:
            self.player_stop()

    def player_stop(self):
        logger.info("PlayerThread: stop()")
        if self.current_pid:
            os.kill(self.current_pid, signal.SIGTERM)
            logger.info("- killed '%s' with pid %s" % (self.current_file, self.current_pid))
            self.cnt_file_current -= 1
        self.current_file = None
        self.current_pid = None
        self.state = 0

    def player_start(self):
        logger.info("PlayerThread: start()")
        if self.current_pid:
            logger.info("- player already running with pid %s" % self.current_pid)
            return
        self.state = 1
        logger.info("- started")

    def player_next(self):
        logger.info("PlayerThread: next()")
        self.player_stop()
        self.cnt_file_current = (self.cnt_file_current + 1) % len(self.files)
        self.player_start()

    def player_prev(self):
        logger.info("PlayerThread: prev()")
        self.player_stop()
        self.cnt_file_current = (self.cnt_file_current - 1) % len(self.files)
        self.player_start()

    def player_first(self):
        logger.info("PlayerThread: next()")
        self.player_stop()
        self.cnt_file_current = 0
        self.player_start()


class MyDaemon(Daemon):
    def run(self):
        try:
            # Start Player Thread
            self.playerthread = PlayerThread()
            self.playerthread.start()

            # Start Tornado
            server = MyTCPServer(self)
            server.listen(player_settings["playerd"]["port"])
            logger.info("Player daemon started")
            IOLoop.instance().start()

        except SystemExit:
            logger.info("Shutting down via signal")

        except Exception as e:
            logger.exception(e)

        finally:
            self.playerthread.shutdown()
            logger.info("Daemon stopped")

    def handle_msg(self, msg):
        # Handle incoming socket messages
        logger.info("msg: %s" % msg)
        if msg == "get_current_file":
            return { "current_file": self.playerthread.current_file }

        elif msg == "get_status":
            return {
                "current_file": self.playerthread.current_file,
                "last_file": self.playerthread.last_file,
                "current_pid": self.playerthread.current_pid,
                "state": self.playerthread.state
            }

        elif msg == "do_play":
            self.playerthread.player_start()

        elif msg == "do_stop":
            self.playerthread.player_stop()

        elif msg == "do_next":
            self.playerthread.player_next()

        elif msg == "do_prev":
            self.playerthread.player_prev()

        elif msg == "do_first":
            self.playerthread.player_first()


# Console start
if __name__ == '__main__':
    # Prepare help and options
    usage = """usage: %prog start|stop|restart"""
    desc="""Media Player Daemon"""
    parser = OptionParser(usage=usage, description=desc)
    (options, args) = parser.parse_args()

    # Setup daemon
    daemon = MyDaemon(PIDFILE)

    # Process startup argument
    if not args:
        parser.print_help()

    elif "start" == args[0]:
        daemon.start()

    elif "stop" == args[0]:
        daemon.stop()

    elif "restart" == args[0]:
        daemon.restart()

    else:
        parser.print_help()
