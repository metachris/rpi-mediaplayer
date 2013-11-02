Stand-Alone Mediaplayer for the Raspberry Pi

* Web-based config tool
* Synchronized playback service with custom omxplayer

playerd
-------
Runs at boot, plays media from playlist, listens to socket connections
(control commands from web_frontend, etc)

Setup
=====

Raspberry OS
------------

    $ sudo raspi-config
    -> memory split: 128

    # Set fast ntp settings (eg via router, or disable ntp for faster bootup)


Software
--------
    # Get the source
    $ sudo chown pi:pi /opt
    $ cd /opt
    $ git clone https://github.com/metachris/rpi-mediaplayer.git rpi_mediaplayer

    # Install dependencies
    $ cd rpi_mediaplayer
    $ sudo pip install -r dependencies.txt

