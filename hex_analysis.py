from intelhex import IntelHex

def load_hex_file(hex_file_path):
    ih = IntelHex(hex_file_path)
    hex_segment_list = []
    for start, end in ih.segments():
        data = ih.tobinarray(start=start, size=end - start)
        segment_info = {'start_address': start, 'end_address': end, 'data': list(data)}
        hex_segment_list.append(segment_info)

    return hex_segment_list