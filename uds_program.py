from uds_cantp import *
from ctypes import *


def generate_key(seed_data,level,dll_file):
    # 1. 加载 DLL
    dll = cdll.LoadLibrary(dll_file)

    # 2. 定义函数原型（对应 C typedef）
    AddFunc = CFUNCTYPE(
        c_int,
        POINTER(c_ubyte),   # seed
        c_uint,             # seed_len
        c_uint,             # mode
        c_char_p,           # opt1
        c_char_p,           # opt2
        POINTER(c_ubyte),   # key_out
        c_uint,             # key_out_len
        POINTER(c_uint)     # key_len_out
    )

    # 3. 从 DLL 获取函数
    GenerateKeyExOpt = AddFunc(("GenerateKeyExOpt", dll))

    # ---- 输入数据 ----
    seed_arr = (c_ubyte * len(seed_data))(*seed_data)
    seed_len = len(seed_data)
    mode = level

    # opt1 和 opt2 = NULL
    opt1 = None
    opt2 = None

    # 输出 key buffer，预分配 4 字节空间
    key_out = (c_ubyte * len(seed_data))()
    key_out_len = len(seed_data)

    # 输出长度变量
    key_len_out = c_uint(0)

    # ---- 实际调用 ----
    result = GenerateKeyExOpt(
        seed_arr,
        seed_len,
        mode,
        opt1,
        opt2,
        key_out,
        key_out_len,
        byref(key_len_out)
    )

    return list(key_out)


class uds_request:
    def __init__(self,req_id,resp_id,fd_flag,frame_max_len,dll_file,cantp_sender):
        self.req_id = req_id
        self.resp_id = resp_id
        self.fd_flag = fd_flag
        self.frame_max_len = frame_max_len
        self.dll_file = dll_file
        self.cantp_sender = cantp_sender
    def uds_session_request(self,session_type):
        req_data = [0x10,session_type]
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Session Request Failed!")
    def uds_ecu_reset_request(self,reset_type):
        req_data = [0x11,reset_type]
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS ECU Reset Request Failed!")
    def uds_write_data_request(self,record_number,data_bytes):
        record_number_bytes = [(record_number >> 8) & 0xFF,(record_number) & 0xFF]
        req_data = [0x2E] + record_number_bytes + data_bytes
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Write Data Request Failed!")
    def uds_security_access_request(self,level):
        req_data = [0x27,level]
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Security Access Request Failed!")
        self.seed_data = resp_data[2:]
    def uds_security_access_key_send(self,level):
        key_data = generate_key(self.seed_data,level,self.dll_file)
        req_data = [0x27,level+1] + key_data
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Security Access Key Send Failed!")
    def uds_routine_control_request(self,rc_type,routine_id,data_list):
        routine_id_bytes = [(routine_id >> 8) & 0xFF,(routine_id) & 0xFF]
        req_data = [0x31,rc_type] + routine_id_bytes + data_list
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Routine Control Request Failed!")
    def uds_program_start_request(self,address,length):
        addr_bytes = [(address >> 24) & 0xFF,(address >> 16) & 0xFF,(address >> 8) & 0xFF,(address) & 0xFF]
        length_bytes = [(length >> 24) & 0xFF,(length >> 16) & 0xFF,(length >> 8) & 0xFF,(length) & 0xFF]
        req_data = [0x34,0x00,0x44] + addr_bytes + length_bytes
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Program Start Request Failed!")
        self.block_size = 0
        for index in range(resp_data[1]>>4):
            self.block_size |= resp_data[-1 - index] << (8*index)
        return self.block_size
    def uds_program_data_request(self,prog_cnt,data_bytes):
        req_data = [0x36,prog_cnt] + data_bytes
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Program Data Request Failed!")
    def uds_program_data_transfer_finish(self):
        req_data = [0x37]
        ret_value,resp_data = self.cantp_sender.uds_cantp_send(req_data)
        if ret_value != True:
            self.cantp_sender.bus_shutdown()
            raise ValueError("UDS Program Data Transfer Finish Failed!")
    def uds_program_data_request_process(self,data):
        prog_index = 0
        prog_cnt = 1
        block_net_size = self.block_size - 2 #考虑0x36 和计数器占用的2个字节
        while prog_index < len(data):
            if (len(data) - prog_index) > block_net_size:
                data_bytes = data[prog_index:prog_index + block_net_size]
            else:
                data_bytes = data[prog_index:]
            self.uds_program_data_request(prog_cnt,data_bytes)
            prog_index += len(data_bytes)
            prog_cnt = (prog_cnt + 1) % 256
    def shutdown(self):
        self.cantp_sender.bus_shutdown()