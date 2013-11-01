import os
import sys
import signal
import time
import logging
import yaml

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



# Each connected client gets a TCPConnection object
class TCPConnection(object):
    def __init__(self, stream, address):
        logger.debug('- new connection from %s' % repr(address))
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
        response = self.handle_msg(data)
        if response:
            self.stream.write("%s\n" % response.strip())

        # Continue reading on this connection
        self.stream.read_until('\n', self._on_read_line)

    def _on_write_complete(self):
        pass

    def _on_close(self):
        logger.debug('- client quit %s' % repr(self.address))

    def handle_msg(self, msg):
        logger.info("msg: %s" % msg)


# The main server class
class MyTCPServer(TCPServer):
    def __init__(self, io_loop=None, ssl_options=None, **kwargs):
        TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)

    def handle_stream(self, stream, address):
        TCPConnection(stream, address)


class PlayerThread(Thread):
    is_cancelled = False
    is_finished = False
    def __init__(self):
        # If is_replaceable is True and another timeout with the same command is added, the
        # existing timeout will be suspended and only the new one executed.
        Thread.__init__(self)

    def run(self):
        while True:
            for fn in playlist["playlist"]:
                if not os.path.isfile(fn):
                    logger.error("Could not find file '%s'" % fn)
                    continue
                ext = fn.split(".")[-1]
                if ext in player_settings["media_extensions"]["video"]:
                    cmd = player_settings["playback_commands"]["video"]
                elif ext in player_settings["media_extensions"]["audio"]:
                    cmd = player_settings["playback_commands"]["audio"]
                elif ext in player_settings["media_extensions"]["image"]:
                    cmd = player_settings["playback_commands"]["image"]
                cmd = cmd.replace("$1", fn)
                logger.info("Execute: %s" % cmd)

                time.sleep(5)


class MyDaemon(Daemon):
    def run(self):
        try:
            server = MyTCPServer()
            server.listen(player_settings["zmq"]["port"])
            IOLoop.instance().start()
#            logger.info("Daemon started")

        except SystemExit:
            logger.info("Shutting down via signal")

        except Exception as e:
            logger.exception(e)

        finally:
            logger.info("Daemon stopped")


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
