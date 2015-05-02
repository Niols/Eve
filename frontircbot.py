#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#                                  FrontIRCBot                                 #
#                                                                              #
#  Niols wrote this file.                                                      #
#                                                                              #
################################################################################

import irc.client, irc.schedule
import threading
import sys

if sys.version[0] == '2': import Queue as queue
else: import queue

DEFAULT_PORT = 6667
"Default port for IRC servers."

DEFAULT_TIME_BETWEEN_MESSAGES = 1
"Default number of seconds between each message sent to a target."

DEFAULT_NICKNAME = 'FrontIRCBot'
"Default name of the bot."



def parse_server(server, as_string=False):
    """
    Returns a (server, port) tuple filled with informations taken from the
    *server* argument. If *as_string* is set to True, returns a `server:port`
    string instead.
    """
    
    if as_string:
        return '%s:%d' % parse_server(server)

    if not isinstance(server, (list, tuple)):
        return parse_server(server.split(':'))
        
    if   len(server) == 1: return (server[0], DEFAULT_PORT)
    elif len(server) == 2: return (server[0], int(server[1]))
    else:
        raise Exception('parse_server: Didn\'t know what to do with `%s`.' %
                        str(server))


    
class _FrontBot(irc.client.SimpleIRCClient):

    def __init__(self, server, nickname, message_queues):
        irc.client.SimpleIRCClient.__init__(self)
        self.server = server
        self.channels = []
        self.nickname = nickname
        self.message_queues = message_queues

    def on_welcome(self, connection, event):
        connection.execute_every(DEFAULT_TIME_BETWEEN_MESSAGES, self.privmsg_loop)

    def privmsg_loop(self):
        for target in self.message_queues:
            if irc.client.is_channel(target) and target not in self.channels:
                self.connection.join(target)
                self.channels.append(target)
            try:
                self.connection.privmsg(target, self.message_queues[target].get_nowait())
            except queue.Empty:
                pass

    def is_on_channel(self, channel):
        return channel in self.channels


    
class _FrontBotThread(threading.Thread):

    def __init__(self, server, nickname, message_queues):
        threading.Thread.__init__(self)
        self.server = parse_server(server)
        self.nickname = nickname
        self.message_queues = message_queues
    
    def run(self):
        self.bot = _FrontBot(self.server, self.nickname, self.message_queues)
        try:
            self.bot.connect(self.server[0], self.server[1], self.nickname)
        except irc.client.ServerConnectionError as x:
            sys.exit(1)
        self.bot.start()



class FrontIRCBot:
    """
    """

    _message_queues = {}
    # server:port → target → Queue
    # Messages are put in the queue, and poped each second to avoid server's flood.

    def __init__(self, nickname = DEFAULT_NICKNAME):
        self.nickname = nickname

    def privmsg(self, server, target, message):
        """
        Sends the given *message* to the given *target* on the given *server*.
        """
        server = parse_server(server)

        if not server in self._message_queues:
            self._message_queues[server] = {}
            _FrontBotThread(server, self.nickname, self._message_queues[server]).start()
        
        if not target in self._message_queues[server]:
            self._message_queues[server][target] = queue.Queue()

        self._message_queues[server][target].put(message)
