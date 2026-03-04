from uds_program import *

class uds_process:
    def __init__(self,segment_list,signiture_file,flash_drv_flag,uds_requester):
        self.uds_requester = uds_requester
        self.segment_list = segment_list
        self.signiture_file = signiture_file
        self.flash_drv_flag = flash_drv_flag
    def uds_reprogramming_pre_process(self): 
        self.uds_requester.uds_session_request(0x03,True)
        self.uds_requester.uds_session_request(0x02,True)
        self.uds_requester.uds_security_access_request(0x07,False)
        self.uds_requester.uds_security_access_key_send(0x07,False)
        self.uds_requester.uds_write_data_request(0xF15a,[0x25,0x11,0x11,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09],False)
    def uds_reprogramming_process(self):
        erase_start_address = 0xFFFFFFFF
        erase_end_address = 0x00000000
        for segment in self.segment_list:
            erase_start_address = min(erase_start_address,segment['start_address'])
            erase_end_address = max(erase_end_address,segment['end_address'])
        erase_length = erase_end_address - erase_start_address
        erase_data_list = [0x44]
        erase_data_list += [(erase_start_address >> 24) & 0xFF,(erase_start_address >> 16) & 0xFF,(erase_start_address >> 8) & 0xFF,(erase_start_address) & 0xFF]
        erase_data_list += [(erase_length >> 24) & 0xFF,(erase_length >> 16) & 0xFF,(erase_length >> 8) & 0xFF,(erase_length) & 0xFF]
        if self.flash_drv_flag == False:
            self.uds_requester.uds_routine_control_request(0x01,0xFF00,erase_data_list,False)
        for segment in self.segment_list:
            address = segment['start_address']
            length = segment['end_address'] - segment['start_address']
            data = segment['data']
            self.uds_requester.uds_program_start_request(address,length)
            self.uds_requester.uds_program_data_request_process(data)
            self.uds_requester.uds_program_data_transfer_finish()
    def uds_reprogramming_post_process(self):
        with open(self.signiture_file,'rb') as sig_file:
            signiture_str = sig_file.read().decode('utf-8')
            signiture_str_list = signiture_str.split(",")
            signiture_data_list = [int(x, 16) for x in signiture_str_list]
        self.uds_requester.uds_routine_control_request(0x01,0x0202,signiture_data_list,False)
        if self.flash_drv_flag == False:
            self.uds_requester.uds_routine_control_request(0x01,0xFF01,[],False)
    def shutdown(self):
        self.uds_requester.shutdown()
