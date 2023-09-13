
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
        
        self.assertEqual(count_line, 7)
        
        self.assertEqual(res[-1], b'stream')

    def test_split_line_1(self):
        line_part=b'/Rotate 0 >>\n'
        r = pdr.PdfReader()
        res = list(r.line_iterator(line_part))
        print(res)
        count_line = len(res)
        
        self.assertEqual(count_line, 1)
    
    def test_split_line_2(self):
        r = pdr.PdfReader()
        line_part=b'rtre\ndfdsfs\n'
        res = list(r.line_iterator(line_part))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], b'rtre\ndfdsfs')
    def test_split_line_3(self):
        r = pdr.PdfReader()
        line_part=b'rtre\ndfd\rsfs\n'
        res = list(r.line_iterator(line_part, True))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], b'rtre\ndfd\rsfs')
        
        
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

    def test_parse_dict_1(self):
        lines = [
            b'<< /Type /XObject /Subtype /Image /Width 1468 /Height 1987 /Interpolate true\n'
            , b'/ColorSpace 6 0 R /Intent /Perceptual /BitsPerComponent 8 /Length 3155389\n'
            , b'/Filter /DCTDecode >>'
        ]
        for line in lines:
            print(line)
        
        