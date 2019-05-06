
#!/usr/bin/python
#coding:utf-8
 
import socket
import struct
from random import randint
 
 
def checksum(data):
    s = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        s += ord(data[i]) + (ord(data[i + 1]) << 8)
    if n:
        s += ord(data[i + 1])
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xffff
    return s
 
 
class IP(object):
    def __init__(self, source, destination, payload='', proto=socket.IPPROTO_TCP):
        self.version = 4
        self.ihl = 5  # Internet Header Length
        self.tos = 0  # Type of Service
        self.tl = 20 + len(payload)
        self.id = 0  # random.randint(0, 65535)
        self.flags = 0  # Don't fragment
        self.offset = 0
        self.ttl = 255
        self.protocol = proto
        self.checksum = 2  # will be filled by kernel
        self.source = socket.inet_aton(source)
        self.destination = socket.inet_aton(destination)
 
    def pack(self):
        ver_ihl = (self.version << 4) + self.ihl
        flags_offset = (self.flags << 13) + self.offset
        ip_header = struct.pack("!BBHHHBBH4s4s",
                                ver_ihl,
                                self.tos,
                                self.tl,
                                self.id,
                                flags_offset,
                                self.ttl,
                                self.protocol,
                                self.checksum,
                                self.source,
                                self.destination)
        self.checksum = checksum(ip_header)
        ip_header = struct.pack("!BBHHHBBH4s4s",
                                ver_ihl,
                                self.tos,
                                self.tl,
                                self.id,
                                flags_offset,
                                self.ttl,
                                self.protocol,
                                socket.htons(self.checksum),
                                self.source,
                                self.destination)
        return ip_header
 
 
class UDP(object):
    def __init__(self, src, dst, payload=''):
    # def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.payload = payload
        self.checksum = 0
        self.length = 8  # UDP Header length
 
    def pack(self, src, dst, proto=socket.IPPROTO_UDP):
        length = self.length + len(self.payload)
        pseudo_header = struct.pack('!4s4sBBH',
                                    socket.inet_aton(src), socket.inet_aton(dst), 0,
                                    proto, length)
        self.checksum = checksum(pseudo_header)
        packet = struct.pack('!HHHH',
                             self.src, self.dst, length, 0)
        return packet
 
 
s = socket.socket(socket.AF_INET,
                      socket.SOCK_RAW,
                      socket.IPPROTO_RAW)
 
fakesrc = "10.1.1.1"
dst = "175.155.234.155"
dstport = 1900
payload = "UDP fake packet test"
# packobj = UDP(fakesrc, dst, payload)
# packet = packobj.pack(fakesrc, dst)
# s.sendto(packet, (dst, dstport))
 
udp = UDP(randint(1, 65535), dstport, payload).pack(fakesrc, dst)
ip = IP(fakesrc, dst, udp, proto=socket.IPPROTO_UDP).pack()
s.sendto(ip + udp + payload, (dst, dstport))
