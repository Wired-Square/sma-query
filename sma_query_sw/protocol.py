import logging
import time
import ctypes
import binascii

from ctypes import LittleEndianStructure
from asyncio import DatagramProtocol

from .commands import commands


_LOGGER = logging.getLogger(__name__)

APP_ID = 125
ANY_SERIAL = 0xFFFFFFFF
ANY_SUSYID = 0xFFFF

# Login Timeout in seconds
LOGIN_TIMEOUT = 900

# Create a reverse index based command lookup
ril_index = {f"ril-{value['first']:X}": value for (key, value) in commands.items() if "first" in value}


def get_encoded_pw(password, installer=False):
    # user=0x88, installer=0xBB
    byte_password = bytearray(password.encode("ascii"))

    if installer:
        login_code = 0xBB
    else:
        login_code = 0x88

    encodedpw = bytearray(12)

    for index in range(0, 12):
        if index < len(byte_password):
            encodedpw[index] = (login_code + byte_password[index]) % 256
        else:
            encodedpw[index] = login_code

    return encodedpw


class SpeedwireFrame:
    _frame_sequence = 1
    _id = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"SMA\x00"))
    _tag0 = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x04\x02\xA0"))
    _group1 = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x00\x00\x01"))
    _eth_sig = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x10\x60\x65"))
    _ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))
    _ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))

    _data_length = 0  # Placeholder value
    _longwords = 0  # Placeholder value
    _ctrl = 0  # Placeholder value

    class FrameHeader(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("id", ctypes.c_ubyte * 4),
            ("tag0", ctypes.c_ubyte * 4),
            ("group1", ctypes.c_ubyte * 4),
            ("data_length", ctypes.c_uint16),
            ("eth_sig", ctypes.c_ubyte * 4),
            ("longwords", ctypes.c_ubyte),
            ("ctrl", ctypes.c_ubyte),
        ]

    class DataHeader(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("dst_sysyid", ctypes.c_uint16),
            ("dst_serial", ctypes.c_uint32),
            ("ctrl2_1", ctypes.c_ubyte * 2),
            ("app_id", ctypes.c_uint16),
            ("app_serial", ctypes.c_uint32),
            ("ctrl2_2", ctypes.c_ubyte * 2),
            ("preamble", ctypes.c_uint32),
            ("sequence", ctypes.c_uint16),
        ]

    class LogoutFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("data_start", ctypes.c_uint32),
            ("data_end", ctypes.c_uint32),
        ]

    class LoginFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("login_type", ctypes.c_uint32),
            ("timeout", ctypes.c_uint32),
            ("time", ctypes.c_uint32),
            ("data_start", ctypes.c_uint32),
            ("user_password", ctypes.c_ubyte * 12),
            ("data_end", ctypes.c_uint32),
        ]

    class QueryFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("first", ctypes.c_uint32),
            ("last", ctypes.c_uint32),
            ("data_end", ctypes.c_uint32)
        ]

    def getLogoutFrame(self, inverter):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.LogoutFrame()

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))

        frame_data.command = commands["logoff"]["command"]
        frame_data.data_start = 0xFFFFFFFF
        frame_data.data_end = 0x00000000

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getLoginFrame(self, inverter, installer):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.LoginFrame()

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))

        frame_data.command = commands["login"]["command"]
        frame_data.login_type = (0x07, 0x0A)[installer]
        frame_data.timeout = LOGIN_TIMEOUT
        frame_data.time = int(time.time())
        frame_data.data_start = 0x00000000  # Data Start
        frame_data.user_password = (ctypes.c_ubyte * 12).from_buffer(get_encoded_pw(inverter["user_password"], installer))
        frame_data.date_end = 0x00000000 # Packet End

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getQueryFrame(self, inverter, command_name):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.QueryFrame()

        command = commands[command_name]

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x00"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x00"))

        frame_data.command = command["command"]
        frame_data.first = command["first"]
        frame_data.last = command["last"]
        frame_data.date_end = 0x00000000

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getFrameHeader(self):
        newFrameHeader = self.FrameHeader()
        newFrameHeader.id = self._id
        newFrameHeader.tag0 = self._tag0
        newFrameHeader.group1 = self._group1
        newFrameHeader.data_length = self._data_length
        newFrameHeader.eth_sig = self._eth_sig
        newFrameHeader.longwords = self._longwords
        newFrameHeader.ctrl = self._ctrl

        return newFrameHeader

    def getDataHeader(self, inverter):
        newDataHeader = self.DataHeader()

        newDataHeader.dst_susyid = ANY_SUSYID
        newDataHeader.dst_serial = ANY_SERIAL
        newDataHeader.ctrl2_1 = self._ctrl2_1
        newDataHeader.app_id = APP_ID
        newDataHeader.app_serial = (inverter["serial"])
        newDataHeader.ctrl2_2 = self._ctrl2_2
        newDataHeader.preamble = 0
        newDataHeader.sequence = (self._frame_sequence | 0x8000)

        self._frame_sequence += 1

        return newDataHeader


class SMAClientProtocol(DatagramProtocol):
    def __init__(self, inverter, on_connection_lost):
        self.speedwire = SpeedwireFrame()
        self.transport = None
        self.inverter = inverter
        self.on_connection_lost = on_connection_lost

    def connection_made(self, transport):
        self.transport = transport

    def start_query(self):
        _LOGGER.debug(f"""Sending login for {self.inverter["serial"]:#08X}""")
        self.send_command(self.speedwire.getLoginFrame(self.inverter, 0))

    def connection_lost(self, exc):
        _LOGGER.debug(f"Connection lost: {exc}")
        self.on_connection_lost.set_result(True)

    def send_command(self, cmd):
        _LOGGER.debug(f"Sending command [{len(cmd)}] -- {binascii.hexlify(cmd).upper()}")
        self.transport.sendto(cmd)

    def get_code(self, data):
        code = int.from_bytes(data[42:46], "little")
        return code

    def get_ril(self, data):
        code = int.from_bytes(data[54:58], "little")
        return code & 0x00FFFF00

    def get_long_value(self, data, offset):
        value = int.from_bytes(data[offset:offset + 4], "little")
        return value

    def get_long_long_value(self, data, offset):
        value = int.from_bytes(data[offset:offset + 8], "little")
        return value

    def send_next_command(self):
        if self.inverter["command_index"] >= len(self.inverter["command_query_list"]):
            self.inverter["command_index"] = 0
        else:
            self.send_command(self.speedwire.getQueryFrame(self.inverter,
                                               self.inverter["command_query_list"][self.inverter["command_index"]]))
            self.inverter["command_index"] += 1

    def datagram_received(self, data, addr):
        code = self.get_code(data)
        ril = self.get_ril(data)
        ril_key = f"ril-{ril:X}"

        _LOGGER.debug(f"{addr} -- [{len(data)}] [{code:X}] [{ril:X}] -- {binascii.hexlify(data).upper()}")

        if code == commands["login"]["response"]:
            self.inverter["data"] = {}
            self.inverter["command_index"] = 0
            self.send_next_command()

        elif len(data) <= 58:
            _LOGGER.error(f"Short datagram received: [{len(data)}] -- {data}")
            return

        elif ril_key in ril_index:
            command = ril_index[ril_key]

            if "registers" in command:
                for register in command["registers"]:
                    if register.get("width") == 8:
                        value = self.get_long_long_value(data, register["offset"])
                    else:
                        value = self.get_long_value(data, register["offset"])

                    if register.get("invalid") == value:
                        value = 0

                    self.inverter["data"][register["name"]] = value

            self.send_next_command()
