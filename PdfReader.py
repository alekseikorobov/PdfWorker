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

        start = b'stream'
        end = b'endstream'
        data = b''
        is_start = False
        curr_obj_dict = {}
        ref_obj_content = b''
        ref_obj_toUnicode_array = []
        is_start_content = False
        is_start_toUnicode = False
        text_to_render = []
        result_text = []
        map_chars = {}
        curr_page_number = 0
        with open(path_file,'rb') as f:
            for line in f.readlines():
                self.debug_print(line)
                line = line.replace(b'\r\n',b'')
                if line.startswith(b'<<'):
                    self.debug_print(f'{line=}')
                    curr_obj_dict = self.dictionaryOption.parse_dict(line)

                    self.debug_print(f'{curr_obj_dict=}')

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

                elif line == end and (is_start_content or is_start_toUnicode):
                    is_start = False

                    if data == b'':
                        self.debug_print('data is empty')
                        continue
                    self.debug_print('-'*10)
                    try:
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

                if is_start:
                    data += line

                if line == start and (is_start_content or is_start_toUnicode):
                    is_start = True

        self.debug_print(f'{map_chars=}')

        for text_line in text_to_render:
            result_texts = self.render_text(text_line, map_chars)
            result_text.extend(result_texts)
            self.debug_print(f'{result_texts=}')

        return result_text

    def print_raw_pdf(self, path_file:str, is_show_all = False):
        '''
        is_show_all - True - показывать всю длину строки, иначе показывать, только первые 100 символов
        '''

        assert os.path.isfile(path_file), f'file not exists {path_file=}'

        start = b'stream'
        end = b'endstream'

        data = b''
        is_start = False
        curr_obj_dict = {}
        line_show = 0
        max_line_show = 5
        with open(path_file,'rb') as f:
            for line in f.readlines():
                line = line.replace(b'\r\n',b'')

                if line.startswith(b'<<'):
                    curr_obj_dict = self.dictionaryOption.parse_dict(line)
                    print(f'\t{curr_obj_dict=}')

                if line == end:
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
                        print('\t-'*10)
                    data = b''

                if not line.startswith(b'<<'):
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

                if line == start:
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
