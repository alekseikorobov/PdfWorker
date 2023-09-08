
import unittest
import PdfReader as pdr
import importlib
importlib.reload(pdr)

import DictionaryOption as pd
import importlib
importlib.reload(pd)


# import PdfReader as pdr
# import importlib
# importlib.reload(pdr)

# def test_split_line():
#     line_part=b'90793 0 obj\r<</Linearized>>\rendobj\r \r90824 0 obj\r<</DecodeParms<</Columns 12>>/Filter/FlateDecode/ID[<4><7>]/Index[3 4]/Info 2 0 R/Length 5/Prev 7/Root 4 0 R/Size 7/Type/XRef/W[1 3 1]>>stream\r\n'

#     r = pdr.PdfReader()
#     count_line = len(r.line_iterator(line_part))
    
#     assert count_line == 8

class TestCalculator(unittest.TestCase):
    
    
    
    def test_split_line(self):
        line_part=b'90793 0 obj\r<</Linearized>>\rendobj\r \r90824 0 obj\r<</DecodeParms<</Columns 12>>/Filter/FlateDecode/ID[<4><7>]/Index[3 4]/Info 2 0 R/Length 5/Prev 7/Root 4 0 R/Size 7/Type/XRef/W[1 3 1]>>stream\r\n'        
        print('-'*100)
        r = pdr.PdfReader()
        res = list(r.line_iterator(line_part))
        print(res)
        count_line = len(res)
        
        self.assertEqual(count_line, 6)
        
        self.assertEqual(res[-1], b'stream')
        
    def test_get_count_chars(self):
        r = pdr.PdfReader()        
        self.assertEqual(r.get_count_chars(b'<<1212<<12323<<',b'<<'), 3)
        self.assertEqual(r.get_count_chars(b'<<1212<<12323',b'<<'), 2)
        self.assertEqual(r.get_count_chars(b'1212<<12323',b'<<'), 1)
        self.assertEqual(r.get_count_chars(b'121212323',b'<<'), 0)
        
        
    def test_parse_dict(self):
        dictionaryOption = pd.DictionaryOption(True);
        line=b'<</De<</Cs 5/Pr 12>>/Fil/Fl/ID[<4><7>]/Ix[3 4]/Io 2 0 R/Lh 185/Prev 7/Root 4 0 R/Size 7/Type/XRef/W[1 3 1]>>'
        
        curr_obj_dict = dictionaryOption.parse_dict(line)
        
        