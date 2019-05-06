#!/usr/bin/env python
import pty
import os
import sys
import select
import socket
import struct


def create_serial():
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)
    print('serial port device name: ', slave_name)
    return master


def tcp_connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        print('tcp server connected:', ip, port)
    except socket.error as msg:
        s.close()
        s = None
        print(msg)
    return s


def rtu_to_tcp(data, pktId):
    pdu = data[:-2]
    length = len(pdu) + 1
    mbap = (pktId, 0x0000, length)
    return struct.pack(">3H", *mbap) + pdu


def tcp_to_rtu(data):
    if len(data) < 8 or len(data) > 20:
        print("tcp data is invalid")
    pdu = data[6:]
    length = struct.unpack('B', data[5:6])
    fmt = ">" + str(length[0]) + "B"
    pdu_data = struct.unpack(fmt, pdu)
    crc = calCRC(pdu_data, len(pdu_data))
    crc = struct.pack("<H", crc)
    return pdu + crc


def calCRC(pck, length):
    """CRC16 for modbus"""
    crc = 0xFFFF
    i = 0
    while i < length:
        crc ^= pck[i]
        i += 1
        j = 0
        while j < 8:
            j += 1
            if (crc & 0x0001) == 1:
                crc = ((crc >> 1) & 0xFFFF) ^ 0xA001
            else:
                crc >>= 1
    return crc


if __name__ == '__main__':
    serial = create_serial()
    cnt = 0
    net = tcp_connect(sys.argv[1], int(sys.argv[2]))
    if net is None:
        sys.exit(1)
    while True:
        rl, wl, el = select.select([serial, net], [], [], 1)
        for io in rl:
            if io == serial:
                rtu_data = os.read(io, 128)
                # print("request  rtu_data:" + str(list(rtu_data)))
                cnt = cnt + 1
                tcp_data = rtu_to_tcp(rtu_data, cnt)
                net.send(tcp_data)
            else:
                tcp_data = net.recv(1024)
                # print("response tcp_data:" + str(list(tcp_data)))
                rtu_data = tcp_to_rtu(tcp_data)
                if rtu_data:
                    os.write(serial, rtu_data)
