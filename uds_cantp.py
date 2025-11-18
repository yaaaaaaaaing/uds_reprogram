import can
import time

def uds_cantp_resp_recv(bus,resp_id,req_data):
    start_time = time.time()
    while True:
        msg_recv = bus.recv(timeout = 0.5)
        if msg_recv is not None and msg_recv.arbitration_id == resp_id:
            msg_tp_resp = msg_recv
            tp_data = list(msg_tp_resp.data)
            if len(tp_data) > 8:
                tp_data_len = tp_data[1]
                resp_data = tp_data[2:2+tp_data_len]
            else:
                tp_data_len = tp_data[0]
                resp_data = tp_data[1:1+tp_data_len]
            if resp_data[0] == req_data[0] + 0x40:
                return True, resp_data
            elif resp_data[0] == 0x7F and resp_data[2] != 0x78:
                return False, resp_data
            elif resp_data[0] == 0x7F and resp_data[2] == 0x78:
                start_time = time.time()
        if time.time() - start_time >= 5.0:
            raise TimeoutError("Response Timeout!")

def uds_cantp_fc_recv(bus,resp_id,req_data):
    start_time = time.time()
    while True:
        msg_recv = bus.recv(timeout = 0.5)
        if msg_recv is not None and msg_recv.arbitration_id == resp_id:
            msg_tp_resp = msg_recv
            resp_data = list(msg_tp_resp.data)
            if resp_data[0] == 0x30:
                return resp_data[2]
            else:
                raise ValueError("Flow Control Frame Receive Error!")
        if time.time() - start_time >= 5.0:
            raise TimeoutError("Response Timeout!")
            
def uds_cantp_single_frame_send(bus,req_id,req_data,fd_flag):
    data_send = req_data[:]
    if len(req_data) > 8:
        data_send.insert(0,0)
        data_send.insert(1,len(req_data))
    else:
        data_send.insert(0,len(req_data))
    
    # 填充到至少8byte
    if len(data_send) < 8:
        data_send += [0x00] * (8 - len(data_send))
        
    msg_snapshot_req = can.Message(arbitration_id=req_id, data=data_send, is_extended_id=False,is_fd=fd_flag)
    bus.send(msg_snapshot_req)

def uds_cantp_first_frame_send(bus,req_id,req_data,fd_flag,frame_max_len): 
    data_send = req_data[:]
    data_send.insert(0,0x10|((len(req_data) >> 8) & 0x0F))
    data_send.insert(1,len(req_data)%256)
    data_send = data_send[0:frame_max_len]
    msg_snapshot_req = can.Message(arbitration_id=req_id, data=data_send, is_extended_id=False,is_fd=fd_flag)
    bus.send(msg_snapshot_req)
    return frame_max_len-2

def uds_cantp_cons_frame_send(bus,req_id,req_data,fd_flag,frame_max_len,cons_frame_index,cf_gap_timer):
    cons_frame_cnt = 0x21
    while(cons_frame_index < len(req_data)): 
        if (len(req_data) - cons_frame_index ) > frame_max_len - 1:
            data_send = req_data[cons_frame_index:cons_frame_index + (frame_max_len-1)]
        else:
            data_send = req_data[cons_frame_index:]
        cons_frame_index += (frame_max_len-1)
        data_send.insert(0,cons_frame_cnt)

        # 填充到至少8byte
        if len(data_send) < 8:
            data_send += [0x00] * (8 - len(data_send))

        msg_snapshot_req = can.Message(arbitration_id=req_id, data=data_send, is_extended_id=False,is_fd=fd_flag)
        bus.send(msg_snapshot_req)
        if cons_frame_cnt < 0x2F:
            cons_frame_cnt += 1
        else:
            cons_frame_cnt = 0x20
        time.sleep(cf_gap_timer/1000.0)

def uds_cantp_send(bus,req_id,resp_id,req_data,fd_flag,frame_max_len):
    if frame_max_len > 16:
        max_single_frame_len = frame_max_len - 2
    else:   
        max_single_frame_len = frame_max_len - 1
    if len(req_data) <= max_single_frame_len:
        uds_cantp_single_frame_send(bus,req_id,req_data,fd_flag)
        ret_value,resp_data = uds_cantp_resp_recv(bus,resp_id,req_data)
    else:
        cons_frame_index = uds_cantp_first_frame_send(bus,req_id,req_data,fd_flag,frame_max_len)
        cf_gap_timer = uds_cantp_fc_recv(bus,resp_id,req_data)
        uds_cantp_cons_frame_send(bus,req_id,req_data,fd_flag,frame_max_len,cons_frame_index,cf_gap_timer)
        ret_value,resp_data = uds_cantp_resp_recv(bus,resp_id,req_data)

    return ret_value,resp_data