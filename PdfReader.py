#%%
import os,sys
from typing import List
import zlib
import DictionaryOption as pd
# import importlib
# importlib.reload(pd)
import re

class PdfReader:
    def __init__(self, debug = False) -> None:
        self.debug = debug
        self.dictionaryOption = pd.DictionaryOption(self.debug)

    def debug_print(self,text):
        call_method = sys._getframe(1).f_code.co_name
        if self.debug: print(f'[{call_method}]', text)

    def extract_text(self, path_file:str)->List[str]:

        assert os.path.isfile(path_file), f'file not exists {path_file=}'

        data = b''
        curr_obj_dict = {}
        ref_obj_content = b''
        ref_obj_toUnicode_array = []
        is_start_content = False
        is_start_toUnicode = False
        text_to_render = []
        result_text = []
        map_chars = {}
        curr_page_number = 0
        is_start_dictionaryOption = False
        count_start_left_angle = 0
        data_for_dict = b''
        for line, is_start_stream, is_end_stream in self.all_line_iterator(path_file):
            self.debug_print(f'{len(line)=}, {line=}, {is_start_stream=}, {is_end_stream=}')

            if line.startswith(b'<</') or line.startswith(b'<< /'):
                count_start_left_angle += self.get_count_chars(line,b'<<')
                is_start_dictionaryOption = True                        
                self.debug_print(f'is start <<, {count_start_left_angle=}')

            if is_start_dictionaryOption:
                data_for_dict += line
                count_start_left_angle -= self.get_count_chars(line,b'<<')
                
                if line.endswith(b'>>'):
                    self.debug_print(f'is end >>, {count_start_left_angle=}')
                    if count_start_left_angle == 0:
                        is_start_dictionaryOption = False
                        self.debug_print(f'{line=}')
                        curr_obj_dict = self.dictionaryOption.parse_dict(data_for_dict)

                        self.debug_print(f'{curr_obj_dict=}')
                        data_for_dict = b''

                        if curr_obj_dict.get('/Type',False) == True and curr_obj_dict.get('/Page',False) == True:
                            curr_page_number += 1
                            if '/Contents' in curr_obj_dict:
                                ref_obj_content = curr_obj_dict['/Contents'].replace(' R',' obj').encode('utf8')
                                self.debug_print(f'{ref_obj_content=}')
                        if '/ToUnicode' in curr_obj_dict:
                            ref_obj_toUnicode = curr_obj_dict['/ToUnicode'].replace(' R',' obj').encode('utf8')
                            ref_obj_toUnicode_array.append(ref_obj_toUnicode)

            elif line == ref_obj_content:
                is_start_content = True
                self.debug_print(f'{is_start_content=}')

            elif line in ref_obj_toUnicode_array:
                is_start_toUnicode = True
                self.debug_print(f'{is_start_toUnicode=}')

            elif is_end_stream and (is_start_content or is_start_toUnicode):
                if data == b'':
                    self.debug_print('data is empty')
                    continue
                self.debug_print('-'*10)
                try:
                    if data.endswith(b'\r\n'):
                       data = data[0:-2]
                    elif data.endswith(b'\n'):
                       data = data[0:-1]

                    res = ''
                    assert int(curr_obj_dict['/Length']) == len(data), f"{curr_obj_dict['/Length']=} != {len(data)=}"
                    self.debug_print(f'{len(data)=}')
                    f = zlib.decompress(data)
                    try:
                        res = f.decode('UTF-8')
                        self.debug_print(f'{res=}')

                        if is_start_content:
                            text_to_render.append(res)
                        if is_start_toUnicode:
                            new_map_chars = self.get_unicode_map_chars(res)
                            map_chars.update(new_map_chars)
                            self.debug_print(f'{len(map_chars)=}')

                    except Exception as ex:
                        print('ERROR convert to UTF-8:')
                        print(ex)
                        res = f
                        print(f'{len(res)=}')
                    self.debug_print(res)
                except Exception as ex:
                    print('ERROR:')
                    print(ex)
                    print(data)
                self.debug_print('-'*10)
                data = b''
                if is_start_content: is_start_content = False
                if is_start_toUnicode: is_start_toUnicode = False

            if is_start_stream and (is_start_content or is_start_toUnicode):
                data += line

        self.debug_print(f'{map_chars=}')

        for text_line in text_to_render:
            result_texts = self.render_text(text_line, map_chars)
            result_text.extend(result_texts)
            self.debug_print(f'{result_texts=}')

        return result_text

    def line_iterator(self, line_part:bytes,is_stream = False):
        
        # if line_part.endswith(b'\r\n'):
        #     line_part = line_part[0:-2]
        # if not is_stream:
        #     if line_part.endswith(b'\n'):
        #         line_part = line_part[0:-1]
        
        if is_stream:
            yield line_part
        else:
            for line in line_part.splitlines():
                r_index = line.rfind(b'>>')
                if r_index == -1:
                    yield line
                else:            
                    if r_index + 2 != len(line):
                        yield line[0:r_index+2]
                        yield line[r_index+2:]
                    else:
                        yield line
            
            # #line_part = line_part.replace(b'\r\n',b'').replace(b'\n',b'')
            # line_split_r = line_part.split(b'\r')
            # #print(f'{line_split_r=}')
            # curr_index = 0
            # N = len(line_split_r)
            # while curr_index < N:
            #     line = line_split_r[curr_index]
            #     r_index = line.rfind(b'>>')
            #     if r_index == -1:
            #         yield line
            #     else:            
            #         if r_index + 2 != len(line):
            #             yield line[0:r_index+2]
            #             yield line[r_index+2:]
            #         else:
            #             yield line
            #     curr_index += 1
    
    def get_count_chars(self,text:bytes,chars:bytes):
        count_result = 0
        left_index = -1
        left_index = text.find(chars)
        while left_index != -1:
            count_result += 1
            left_index = text.find(chars,left_index+1)
        return count_result
        
    
    def print_raw_pdf(self, path_file:str, is_show_all = False):
        '''
        is_show_all - True - показывать всю длину строки, иначе показывать, только первые 100 символов
        '''

        assert os.path.isfile(path_file), f'file not exists {path_file=}'

        start_stream_token = b'stream'
        end_stream_token = b'endstream'

        data = b''
        data_for_dict = b''
        is_start = False
        is_start_dictionaryOption = False
        curr_obj_dict = {}
        line_show = 0
        max_line_show = 5
        count_start_left_angle = 0
        with open(path_file,'rb') as f:
            for line_part in f.readlines():
                self.debug_print(f'{line_part=}')
                for line in self.line_iterator(line_part, is_start):
                    self.debug_print(f'{line=}')
                    if line.startswith(b'<</'):
                        count_start_left_angle += self.get_count_chars(line,b'<<')
                        is_start_dictionaryOption = True                        
                        self.debug_print(f'is start <<, {count_start_left_angle=}')

                    if line == end_stream_token:
                        is_start = False
                        line_show = 0
                        if data == b'':
                            continue
                        if curr_obj_dict.get('/FlateDecode',False) == True:
                            print('\t----try uncompress'+'-'*10)
                            try:
                                res = ''
                                assert int(curr_obj_dict['/Length']) == len(data), f"{curr_obj_dict['/Length']=} != {len(data)=}"
                                f = zlib.decompress(data)
                                try:
                                    res = f.decode('UTF-8')
                                    print(f'\t\t{res=}')
                                except Exception as ex:
                                    print('\t\tERROR convert to UTF-8:')
                                    print('\t\t',ex)
                                    res = f
                                    print(f'\t\t{len(res)=}')
                            except Exception as ex:
                                print('\tERROR:')
                                print('\t',ex)
                            print('\t','-'*10)
                        data = b''

                    start_tab = ''
                    if is_start:
                        start_tab = '\t'
                    if is_show_all:
                        print(f'{line=}')
                    else:
                        more = ''
                        if len(line)>100:
                            more = '...'
                        if line_show < max_line_show:
                            if is_start:
                                line_show+=1
                            print(f'{start_tab}{line[:100]}{more}')

                    if is_start:
                        data += line
                        
                    if is_start_dictionaryOption:
                        if line.endswith(b'\n'):
                            line = line[:-1]
                        data_for_dict += line
                        
                        count_start_left_angle -= self.get_count_chars(line,b'<<')
                        
                        if line.endswith(b'>>'):
                            self.debug_print(f'is end >>, {count_start_left_angle=}')
                            if count_start_left_angle == 0:
                                is_start_dictionaryOption = False
                                curr_obj_dict = self.dictionaryOption.parse_dict(data_for_dict)
                                data_for_dict = b''
                                print(f'\t{curr_obj_dict=}')
                            

                    if line == start_stream_token:
                        is_start = True

    def unicod_to_str(self, unicode_hex):
        utf8_string = ''.join([chr(int(unicode_hex[i:i+4], 16)) for i in range(0, len(unicode_hex), 4)])
        return utf8_string

    def parse_arr_beginbfrange(self, arr_beginbfrange):
        obj = {}
        for i in arr_beginbfrange:
            break_index = i.find('[')
            if break_index == -1:
                left,right,to = [int(c.strip('<>'),16) for c in i.split(' ')]
                #print(f'{(left,right,to)=}')
                for index, char_int in enumerate(range(left, right+1)):
                    #print(f'{char_int=}')
                    unicode_str = '{:04X}'.format(char_int)
                    obj[unicode_str] = chr(index+to)
                #arr_beginbfrange_tup.append((left,right,to))
            else:
                #print(f'{i=}')

                left,right = [int(c.strip('<>'),16) for c in i[0:break_index].strip().split(' ')]
                list_values = [c.strip('<>') for c in i[break_index:].strip(' []').split(' ')]
                assert right - left + 1 == len(list_values),f'count chars from range {right - left + 1=} (where {right=},{left=}) mast be equal {len(list_values)=}, from line {i}'

                for index, char_int in enumerate(range(left,right+1)):
                    unicode_str = '{:04X}'.format(char_int)
                    obj[unicode_str] = self.unicod_to_str(list_values[index])
        return obj

    def get_unicode_map_chars(self, cmap):
        is_start_beginbfchar = False
        is_start_beginbfrange = False
        arr_beginbfchar = []
        arr_beginbfrange = []
        for item in cmap.split('\n'):
            #print(item)
            if item == 'endbfchar':
                is_start_beginbfchar = False
            if item == 'endbfrange':
                is_start_beginbfrange = False
            if is_start_beginbfchar:
                arr_beginbfchar.append(item)
            if is_start_beginbfrange:
                arr_beginbfrange.append(item)
            if 'beginbfchar' in item:
                is_start_beginbfchar = True
            if 'beginbfrange' in item:
                is_start_beginbfrange = True
        #print(f'{arr_beginbfchar=}')
        #print(f'{arr_beginbfrange=}')

        beginbfchar_dict = {}
        for l in arr_beginbfchar:
            key, val = [l.strip('<>') for l in l.split(' ')]
            beginbfchar_dict[key] = chr(int(val,16))

        beginbfrange_dict = self.parse_arr_beginbfrange(arr_beginbfrange)

        beginbfchar_dict.update(beginbfrange_dict)

        return beginbfchar_dict#beginbfchar_dict

    def convet_from_code_to_str(self, map_dict, sec):

        self.debug_print(f'{sec=}')
        all_text = ''
        for res_val in re.finditer('<(.+?)>',sec):
            val_line = res_val.group(1)
            #print(val_line)
            chars = ''.join([map_dict[val_line[i:i+4] ] for i in range(0, len(val_line), 4)])

            all_text += chars

        return all_text

    def render_text_line_from_array(self, text_line:str, map_dict):
        l = text_line.find('[')
        r = text_line.rfind(']')
        text = text_line[l+1:r]
        #print('render_text_line_from_array'.l,r,text)
        text_split_o =  text.split('(')
        result_text = ''
        if len(text_split_o) > 1:
            for chars in text_split_o[1:]:
                i = chars.find(')')
                result_text += chars[0:i]
        if '<' in text and '>' in text:
            result_text += self.convet_from_code_to_str(map_dict, text)
        self.debug_print(f'{result_text=}')
        return result_text

    def render_text_line_from_str(self, text_line:str):
        i = text_line.find(')')
        result_text += text_line[0:i]
        return result_text

    def render_text(self, text:str, map_dict):
        result_text = []
        for line in text.split('\r\n'):
            if line.endswith('TJ'):
                self.debug_print(f'{line=}')
                res = self.render_text_line_from_array(line, map_dict)
                result_text.append(res)
            elif line.endswith('Tj'):
                self.debug_print(f'{line=}')
                res = self.render_text_line_from_str(line)
                result_text.append(res)
        return result_text


    def all_line_iterator(self, path_file:str):
        start_stream_token = b'stream'
        end_stream_token = b'endstream'
        is_start_stream = False
        is_prev_start_stream = False
        is_end_stream = False
        with open(path_file,'rb') as file:
            while True:
                line_part = file.readline()
                if not line_part:
                    break
                
                for line in self.line_iterator(line_part, is_prev_start_stream or is_start_stream):
                    #print(f'{line=}, {is_start_stream=}')
                    if is_prev_start_stream:
                        is_prev_start_stream = False
                        is_start_stream = True

                    if line == start_stream_token:
                        is_prev_start_stream = True

                    if is_end_stream:
                        is_end_stream = False

                    if line.startswith(end_stream_token):
                        is_end_stream = True
                        is_start_stream = False

                    yield line, is_start_stream, is_end_stream

    def extract_images(self, path_file:str)->List[str]:   

        assert os.path.isfile(path_file), f'file not exists {path_file=}'

        data_stream = b''
        curr_obj_dict = {}
        is_start_dictionaryOption = False
        is_jpeg_start_object = False
        count_start_left_angle = 0
        data_for_dict = b''

        for line, is_start_stream, is_end_stream in self.all_line_iterator(path_file):
            self.debug_print(f'{len(line)=}, {line=}, {is_start_stream=}, {is_end_stream=}')

            if line.startswith(b'<</') or line.startswith(b'<< /'):
                count_start_left_angle += self.get_count_chars(line,b'<<')
                is_start_dictionaryOption = True                        
                self.debug_print(f'is start <<, {count_start_left_angle=}')


            if is_start_dictionaryOption:
                data_for_dict += line
                count_start_left_angle -= self.get_count_chars(line,b'<<')
                
                if line.endswith(b'>>'):
                    self.debug_print(f'is end >>, {count_start_left_angle=}')
                    if count_start_left_angle == 0:
                        is_start_dictionaryOption = False
                        self.debug_print(f'{line=}')
                        curr_obj_dict = self.dictionaryOption.parse_dict(data_for_dict)

                        self.debug_print(f'{curr_obj_dict=}')
                        data_for_dict = b''
                        if '/DCTDecode' in curr_obj_dict:
                            is_jpeg_start_object = True
                            self.debug_print(f'{is_jpeg_start_object=}')
            
            
            elif is_end_stream and is_jpeg_start_object:
                if data_stream == b'':
                    self.debug_print('data is empty')
                    continue
                self.debug_print('-'*10)
                try:
                    if data_stream.endswith(b'\r\n'):
                       data_stream = data_stream[0:-2]
                    elif data_stream.endswith(b'\n'):
                       data_stream = data_stream[0:-1]

                    assert int(curr_obj_dict['/Length']) == len(data_stream), f"{curr_obj_dict['/Length']=} != {len(data_stream)=} diff {int(curr_obj_dict['/Length']) - len(data_stream)}"
                    self.debug_print(f'{len(data_stream)=}')

                    yield data_stream

                except Exception as ex:
                    print('ERROR:')
                    print(ex)
                    print(data_stream)
                    return None
                    
                self.debug_print('-'*10)
                data_stream = b''
                if is_jpeg_start_object: is_jpeg_start_object = False


            if is_start_stream and is_jpeg_start_object:
                data_stream += line

#%%