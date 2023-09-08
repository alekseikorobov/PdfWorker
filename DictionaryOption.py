import chardet
import sys

class DictionaryOption:
    def __init__(self, debug = False) -> None:
        self.debug = debug

    def debug_print(self,text):
        call_method = sys._getframe(1).f_code.co_name
        if self.debug: print(f'[{call_method}]', text)
        
    def to_str(self, bytes_data: bytes):
        result = chardet.detect(bytes_data)
        detected_encoding = result['encoding']
        if detected_encoding is None:
            return bytes_data
        decoded_string = bytes_data.decode(detected_encoding)
        return decoded_string
        
        # try:
        #     return str(b,'utf-8')
        # except:
        #     pass
        # try:
        #     return b.decode('utf16')
        # except:
        #     pass
        
        # return b
        
        
    def parse_dict(self, byte_line:bytes):
        obj = {}
        self.debug_print('----start parse_dict')
        
        is_start_char = False
        is_start_sub_params = False
        start_param_value = False
        is_start_array = False    
        
        assert byte_line.startswith(b'<<'), f'line must be start with <<, now {byte_line=}'
        assert byte_line.endswith(b'>>'), f'line must be end with >>, now {byte_line=}'

        s = byte_line[2:-2]
        self.debug_print(f'{s=}')
        param = b''
        param_value = b''
        params = b''
        N = len(s)
        curr = 0
        deep_bracker = 0
        arra_object = None
        is_start_char_for_array = False
        while curr < N:
            c = s[curr]
            c = c.to_bytes(1, 'little')
            #print(f"{c=}, {c == b'/'}")
            if c == b'/' and not is_start_sub_params:
                if not is_start_array:
                    if is_start_char:
                        self.debug_print(f'1. {param=}')
                        param_line = param.split(b' ',1)
                        obj[str(param_line[0],'utf-8')] = self.to_str(param_line[1]) if len(param_line)>1 and param_line[1] != '' else True
                        param = b''  
                    is_start_char = True
                else:
                    if is_start_char_for_array:
                        obj_item = self.parse_dict(b'<<'+params+b'>>')
                        params = b''
                        arra_object.append(obj_item)
                    else:
                        is_start_char_for_array = True

            if c == b'<' and s[curr+1].to_bytes(1, 'little') == b'<':
                self.debug_print('is_start_sub_params')
                is_start_sub_params = True
                is_start_char = False
                deep_bracker += 1
                #curr += 1
            
            if is_start_sub_params:
                #print(f'{c=}')
                params += c
            
            if not is_start_sub_params and c == b')':
                start_param_value = False
                param_str = ''
                try:
                    param_str = str(param,'utf-8')
                except Exception as ex:
                    print(ex)
                obj[param_str] = self.to_str(param_value.strip())
                param_value = b''
                param = b''
                
            if not is_start_sub_params and start_param_value and not is_start_array:
                param_value += c

            # if is_start_array:
            #     pass
                
            if not is_start_sub_params and c == b'[':
                is_start_array = True
                is_start_char = False
                if arra_object is None:
                    arra_object = []
                
            if not is_start_sub_params and c == b'(':
                start_param_value = c == b'('
                is_start_char = False

            if not is_start_sub_params and is_start_char and not is_start_array:
                param += c
                
            if not is_start_sub_params and c == b']':
                self.debug_print(f'end array')
                self.debug_print(f'{params=}')
                if params != b'':                    
                    obj_item = self.parse_dict(b'<<'+params+b'>>')
                    params = b''
                    arra_object.append(obj_item)
                
                is_start_char_for_array = False         
                
                obj[str(param,'utf-8')] = arra_object
                param = b''
                is_start_array = False
                arra_object = None
            
            if is_start_char_for_array and not is_start_sub_params:
                params += c
                
            if c == b'>' and s[curr+1].to_bytes(1, 'little') == b'>':
                deep_bracker -= 1
                params += s[curr+1].to_bytes(1, 'little')
                if deep_bracker == 0:
                    is_start_sub_params = False
                    if not is_start_char_for_array:
                        self.debug_print(f'{param=}')
                        self.debug_print(f'{params=}')
                        obj[str(param,'utf-8')] = self.parse_dict(params)
                        param = b''
                        params = b''
                    #is_start_char = False
                curr += 1
            curr+=1
            
        if param != b'':
            self.debug_print(f'{param=}')
            param_line = param.split(b' ',1)
            obj[str(param_line[0],'utf-8')] = self.to_str(param_line[1]) if len(param_line)>1 else True
            self.debug_print(param)
        self.debug_print('----end parse_dict')
        
        return obj    