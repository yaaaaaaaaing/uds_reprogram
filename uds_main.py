from hex_analysis import *
from uds_process import *
   
def uds_program_main(req_id,resp_id,fd_flag,frame_max_len,dll_file,flashdrv_file_path,flashdrv_signiture_file,target_file_path,target_signiture_file):
    hex_flashdrv_segment_list = load_hex_file(flashdrv_file_path)
    uds_flashdrv_processer = uds_process(req_id,resp_id,fd_flag,frame_max_len,dll_file,hex_flashdrv_segment_list,flashdrv_signiture_file,True)
    uds_flashdrv_processer.uds_reprogramming_pre_process()
    uds_flashdrv_processer.uds_reprogramming_process()
    uds_flashdrv_processer.uds_reprogramming_post_process()

    hex_target_segment_list = load_hex_file(target_file_path)
    uds_target_processer = uds_process(req_id,resp_id,fd_flag,frame_max_len,dll_file,hex_target_segment_list,target_signiture_file,False)
    uds_target_processer.uds_reprogramming_process()
    uds_target_processer.uds_reprogramming_post_process()

    uds_target_processer.shutdown()


if __name__ == "__main__":
    can_type = input("Please input can type(C(Classic) or F(CanFD)):")
    frame_max_len = int(input("Please input can frame length:"))
    if can_type == 'C':
        fd_flag = False
    elif can_type == 'F':
        fd_flag = True
    req_id = 0x60e
    resp_id = 0x68e
    flashdrv_file_path = "./input/FlashDrv.hex"
    flashdrv_signiture_file = "./input/FlashDrv_PEU_F.sig"
    target_file_path = "./input/P0334985 XX APP.hex"
    target_signiture_file = "./input/P0334985 XX APP.sig"
    dll_file = "./input/PEU_seed&key.dll"
    
    uds_program_main(req_id,resp_id,fd_flag,frame_max_len,dll_file,flashdrv_file_path,flashdrv_signiture_file,target_file_path,target_signiture_file)

# 目前response识别只能识别byte1(目前不支持需要长度超过8的uds resp内容)
# 目前刷写只支持0x44的报文格式