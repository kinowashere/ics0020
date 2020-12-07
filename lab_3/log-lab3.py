#! /usr/bin/python
# Use "nc ip_address 12345" to communicate
# What to log:
# - BisOps:
#   - local vs remote connection (from local/same system or from the network)
#   - client information (IP address, port)
#   - message received from client
# - TechOps:
#   - start of the application/end of operations
#   - parameters used (IP address, port)
#   - MSGID, for outbound and inbound operations
#   - successful application operations
#   - e.g. a successfully opened socket, received or sent a message
#   - unsuccessful/failures in operations
#   - e.g. OSerror exceptions
# - SecOps:
#   - user using the application
#   - process ID
# Original code for reference:
# import socket, os
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind(('127.0.0.1', 12345))
# sock.listen(5)
#
# while True:
#     connection,address = sock.accept()
#     buf = connection.recv(1024)
#     print buf
#     connection.send(buf)
#     connection.close()
import socket
import os
import logging
import logging.handlers
import argparse
import time
from signal import signal, SIGINT
class CustomFormatter(logging.Formatter):
    # Change time format parser to comply with RFC5424
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            if "%F" in datefmt:
                msec = "%03d" % record.msecs
                datefmt = datefmt.replace("%F", msec)
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s
# Setup logging facility
# Create logger and its severity level
tcpLogger = logging.getLogger("tcpserver")
tcpLogger.setLevel(logging.DEBUG)
# Create syslog handler - commented out during development
# socketHandler = logging.handlers.SysLogHandler(address=('192.168.180.158', 514),
#                                               facility=1, socktype=socket.SOCK_STREAM)
socketHandler = logging.FileHandler('/var/log/testLog', mode='a', encoding="utf-8")
# To not append NUL byte to the message, more compliant with RFC5424
# socketHandler.append_nul = False
# Create a formatter and bind it to the handler
msgFormat = '%(priority)s1 %(asctime)s %(hostip)s ' \
    '%(filename)s %(process)d %(msgid)s ' \
    '[tcpServer@12345 user=%(user)s] %(message)s'
dateFormat = '%Y-%m-%dT%H:%M:%S.%F%z'
logFormatter = CustomFormatter(fmt=msgFormat, datefmt=dateFormat, style='%')
socketHandler.setFormatter(logFormatter)
# Bind handler to logger
tcpLogger.addHandler(socketHandler)
# Variables for log messages
msgid = {'in': 'TCPIN', 'out': 'TCPOUT'}
# Dictionary with hosts' user and IP address
commonExtra = {'user': os.getlogin(), 'hostip': socket.gethostbyname(socket.gethostname())}
# Priority is calculated with the next formula: priority = facility * 8 + severity
priority = {'debug': 15, 'info': 14, 'warn': 12, 'err': 11, 'crit': 10}
# Initialise command line argument parser
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument('-h', '--help', action='store_true')
args, unknown = parser.parse_known_args()
# handle unrecognized arguments
if unknown:
    tcpLogger.info("ERROR: %s", "Unrecognised program argument!",
        extra=dict(**commonExtra, **{'priority': f'<{priority["err"]}>', 'msgid': f'{msgid["in"]}'}))
    tcpLogger.debug("DEBUG: %s '%s'", "Detected unhandled argument: ", unknown,
        extra=dict(**commonExtra, **{'priority': f'<{priority["debug"]}>', 'msgid': f'{msgid["in"]}'}))
    print("Unrecognized arguments: ")
    print(unknown)
    raise SystemExit(0)
if not args.verbose:
    tcpLogger.setLevel(logging.INFO)
if args.help:
    helpMessage = \
        "DESCRIPTION\n" \
        "\tPython server application, accepts TCP connections on port 12345.\n" \
        "\tIt logs all operations (according to the specification) and sends them to the central syslog server.\n" \
        "\n" \
        "OPTIONS\n" \
        "\tGeneric Application Information\n" \
        "\t\t-h, --help\n" \
        "\t\t\tShow application description and its options.\n" \
        "\n" \
        "\tLogging verbosity\n" \
        "\t\t-v, --verbose\n" \
        "\t\t\tForce logging facility to log all events starting from DEBUG (7 for Syslog) level.\n"
    print(helpMessage)
    raise SystemExit(0)
# AF_INET represents protocol family, SOCK_STREAM allows communicating, using TCP
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind(('0.0.0.0', 12346))
# Unite two dictionaries/associative array in extra
tcpLogger.info("INFO: %s", "Server was bound to 0.0.0.0 at 12345",
    extra=dict(**commonExtra, **{'priority': f'<{priority["info"]}>', 'msgid': f'{msgid["in"]}'}))
# Accept connections, parameter specifies how many connections will be allowed before refusing new
tcpSocket.listen(5)
print(f"Started a simple tcp server on localhost port 12345")
# A function that handles interrupt signal by sending out a log
def sigintHandler(signal_received, frame):
    tcpLogger.info("WARNING: %s", "Program execution ended",
        extra=dict(**commonExtra, **{'priority': f'<{priority["warn"]}>', 'msgid': f'{msgid["in"]}'}))
    tcpLogger.debug("DEBUG: %s '%s'", "Signal handler called with signal", signal_received,
        extra=dict(**commonExtra, **{'priority': f'<{priority["debug"]}>', 'msgid': f'{msgid["in"]}'}))
    print(f"Exiting program... If you were not granted clearance to do so, please report yourself to the nearest"
          f"sysadmin affiliated with the establishment, have a good day.")
    raise SystemExit(0)
# bind handler to SIGINT signal
signal(SIGINT, sigintHandler)
while True:
    # Accept connection, returns new client socket object and client/remote address
    clientConnection, clientAddress = tcpSocket.accept()
    print(f"Accepted connection from {clientAddress}")
    # Receive data from the socket, parameter specifies the buffer size, return value is byte object
    buffer = clientConnection.recv(1024)
    print(buffer)
    # Sends the byte object back to client
    clientConnection.send(buffer)
    clientConnection.close()