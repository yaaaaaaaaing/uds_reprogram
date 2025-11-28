import can
import time
from datetime import datetime
import os

class uds_cantp:
    def __init__(self,req_id,resp_id,fd_flag,frame_max_len):
        self.bus = can.interface.Bus(interface='vector', channel= 0,fd=True,data_bitrate=2000000, bitrate=500000,sjw_abr= 2, tseg1_abr= 7, tseg2_abr= 2, sam_abr= 1, sjw_dbr= 2, tseg1_dbr= 7, tseg2_dbr= 2, output_mode= 1,app_name="pythonUds")
        self.req_id = req_id
        self.resp_id = resp_id
        self.fd_flag = fd_flag
        self.frame_max_len = frame_max_len
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3].replace(":","_").replace("-","_").replace(" ","_")
        log_path = "./log/"
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        self.log = open(os.path.join(log_path,"log_"+log_time+".txt"),"w+")
    def uds_cantp_resp_recv(self,req_data):
        start_time = time.time()
        while True:
            msg_recv = self.bus.recv(timeout = 0.005)
            if msg_recv is not None and msg_recv.arbitration_id == self.resp_id:
                msg_tp_resp = msg_recv
                tp_data = list(msg_tp_resp.data)
                if len(tp_data) > 8:
                    tp_data_len = tp_data[1]
                    resp_data = tp_data[2:2+tp_data_len]
                else:
                    tp_data_len = tp_data[0]
                    resp_data = tp_data[1:1+tp_data_len]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.log.write(now  + "   " + hex(self.resp_id)  + "  " + ' '.join([hex(data)[2:].zfill(2) for data in tp_data])+"\n")
                if resp_data[0] == req_data[0] + 0x40:
                    return True, resp_data
                elif resp_data[0] == 0x7F and resp_data[2] != 0x78:
                    return False, resp_data
                elif resp_data[0] == 0x7F and resp_data[2] == 0x78:
                    start_time = time.time()
            if time.time() - start_time >= 5.0:
                raise TimeoutError("Response Timeout!")
    def uds_cantp_fc_recv(self):
        start_time = time.time()
        while True:
            msg_recv = self.bus.recv(timeout = 0.005)
            if msg_recv is not None and msg_recv.arbitration_id == self.resp_id:
                msg_tp_resp = msg_recv
                resp_data = list(msg_tp_resp.data)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.log.write(now  + "   " + hex(self.resp_id)  + "  " + ' '.join([hex(data)[2:].zfill(2) for data in resp_data]) +"\n")
                if resp_data[0] == 0x30:
                    return resp_data[2]
                else:
                    raise ValueError("Flow Control Frame Receive Error!")
            if time.time() - start_time >= 5.0:
                raise TimeoutError("Response Timeout!")
    def uds_cantp_single_frame_send(self,req_data):
        data_send = req_data[:]
        if len(req_data) > 8:
            data_send.insert(0,0)
            data_send.insert(1,len(req_data))
        else:
            data_send.insert(0,len(req_data))
        
        # 填充到至少8byte
        if len(data_send) < 8:
            data_send += [0x00] * (8 - len(data_send))
            
        msg_snapshot_req = can.Message(arbitration_id=self.req_id, data=data_send, is_extended_id=False,is_fd=self.fd_flag)
        self.bus.send(msg_snapshot_req)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.log.write(now  + "   " + hex(self.req_id)  + "  " + ' '.join([hex(data)[2:].zfill(2) for data in data_send]) +"\n")
    
    def uds_cantp_first_frame_send(self,req_data): 
        data_send = req_data[:]
        data_send.insert(0,0x10|((len(req_data) >> 8) & 0x0F))
        data_send.insert(1,len(req_data)%256)
        data_send = data_send[0:self.frame_max_len]
        msg_snapshot_req = can.Message(arbitration_id=self.req_id, data=data_send, is_extended_id=False,is_fd=self.fd_flag)
        self.bus.send(msg_snapshot_req)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.log.write(now  + "   " + hex(self.req_id)  + "  " + ' '.join([hex(data)[2:].zfill(2) for data in data_send]) +"\n")
        return self.frame_max_len-2

    def uds_cantp_cons_frame_send(self,req_data,cons_frame_index,cf_gap_timer):
        cons_frame_cnt = 0x21
        while(cons_frame_index < len(req_data)): 
            if (len(req_data) - cons_frame_index ) > self.frame_max_len - 1:
                data_send = req_data[cons_frame_index:cons_frame_index + (self.frame_max_len-1)]
            else:
                data_send = req_data[cons_frame_index:]
            cons_frame_index += (self.frame_max_len-1)
            data_send.insert(0,cons_frame_cnt)

            # 填充到至少8byte
            if len(data_send) < 8:
                data_send += [0x00] * (8 - len(data_send))

            msg_snapshot_req = can.Message(arbitration_id=self.req_id, data=data_send, is_extended_id=False,is_fd=self.fd_flag)
            self.bus.send(msg_snapshot_req)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.log.write(now  + "   " + hex(self.req_id)  + "  " + ' '.join([hex(data)[2:].zfill(2) for data in data_send]) +"\n")
            if cons_frame_cnt < 0x2F:
                cons_frame_cnt += 1
            else:
                cons_frame_cnt = 0x20
            time.sleep(cf_gap_timer/1000.0)

    def uds_cantp_send(self,req_data):
        if self.frame_max_len > 16:
            max_single_frame_len = self.frame_max_len - 2
        else:   
            max_single_frame_len = self.frame_max_len - 1
        if len(req_data) <= max_single_frame_len:
            self.uds_cantp_single_frame_send(req_data)
            ret_value,resp_data = self.uds_cantp_resp_recv(req_data)
        else:
            cons_frame_index = self.uds_cantp_first_frame_send(req_data)
            cf_gap_timer = self.uds_cantp_fc_recv()
            self.uds_cantp_cons_frame_send(req_data,cons_frame_index,cf_gap_timer)
            ret_value,resp_data = self.uds_cantp_resp_recv(req_data)

        return ret_value,resp_data
    
    def bus_shutdown(self):
        self.bus.shutdown()
        self.log.close()