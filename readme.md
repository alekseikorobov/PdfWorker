# Pdf Worker

Проект для работы с pdf файлами, написанный на чистом python без сторонних библиотек.


## Read PDF
Для чтения pdf используется класс `PdfReader`
примеры использования:

```python
from PdfReader import PdfReader
reader = PdfReader()
reader.extract_text('data/test2.pdf')

```
результат:
```
['т', 'ест2', ' ']
```

так же можно сделать вывод отладочной информации:
```python
from PdfReader import PdfReader
reader = PdfReader(debug=True)
reader.extract_text('data/test2.pdf')

```
результат:
```
[extract_text] b'%PDF-1.7\r\n'
[extract_text] b'%\xb5\xb5\xb5\xb5\r\n'
[extract_text] b'1 0 obj\r\n'
[extract_text] b'<</Type/Catalog/Pages 2 0 R/Lang(ru-RU) /StructTreeRoot 15 0 R/MarkInfo<</Marked true>>/Metadata 27 0 R/ViewerPreferences 28 0 R>>\r\n'
[extract_text] line=b'<</Type/Catalog/Pages 2 0 R/Lang(ru-RU) /StructTreeRoot 15 0 R/MarkInfo<</Marked true>>/Metadata 27 0 R/ViewerPreferences 28 0 R>>'
[parse_dict] ----start parse_dict
[parse_dict] s=b'/Type/Catalog/Pages 2 0 R/Lang(ru-RU) /StructTreeRoot 15 0 R/MarkInfo<</Marked true>>/Metadata 27 0 R/ViewerPreferences 28 0 R'
[parse_dict] 1. param=b'/Type'
[parse_dict] 1. param=b'/Catalog'
[parse_dict] 1. param=b'/Pages 2 0 R'
[parse_dict] 1. param=b'/StructTreeRoot 15 0 R'
[parse_dict] is_start_sub_params
[parse_dict] param=b'/MarkInfo'
[parse_dict] params=b'<</Marked true>>'
...
```

Так же можно получить сырой файл pdf с попыткой распоковки вложенных объектов:

```python
from PdfReader import PdfReader
reader = PdfReader()
reader.print_raw_pdf('data/test2.pdf')

```
результат:
```
b'%PDF-1.7'
b'%\xb5\xb5\xb5\xb5'
b'1 0 obj'
	curr_obj_dict={'/Type': True, '/Catalog': True, '/Pages': '2 0 R', '/Lang': 'ru-RU', '/StructTreeRoot': '15 0 R', '/MarkInfo': {'/Marked': 'true'}, '/Metadata': '27 0 R', '/ViewerPreferences': '28 0 R'}
b'endobj'
b'2 0 obj'
	curr_obj_dict={'/Type': True, '/Pages': True, '/Count': '1', '/Kids': []}
b'endobj'
b'3 0 obj'
	curr_obj_dict={'/Type': True, '/Page': True, '/Parent': '2 0 R', '/Resources': {'/Font': {'/F1': '5 0 R', '/F2': '12 0 R'}, '/ExtGState': {'/GS10': '10 0 R', '/GS11': '11 0 R'}, '/ProcSet': [{'/PDF': True}, {'/Text': True}, {'/ImageB': True}, {'/ImageC': True}, {'/ImageI': True}]}, '/MediaBox': [], '/Contents': '4 0 R', '/Group': {'/Type': True, '/Group': True, '/S': True, '/Transparency': True, '/CS': True, '/DeviceRGB': True}, '/Tabs': True, '/S': True, '/StructParents': '0'}
b'endobj'
b'4 0 obj'
	curr_obj_dict={'/Filter': True, '/FlateDecode': True, '/Length': '183'}
b'stream'
	b'x\x9c\xad\x8e=\x0b\xc20\x10\x86\xf7@\xfe\xc3;\xaa`z\x97\xa46\x85\xd2\xa1\x9f(\x14\x14\x0b\x0e\xe2\xa8\x9d\x14\xd4\xff\x0f\xa6V\x84\x82Nz\xcbqw/\xf7<\x08\xd6H\x92\xa0\xc9\x97\x05(M\x91\x159\xaeR\x90\xa2\xbe\x9c\x8b\x18\x840\x0e\x95\xd1p\x96U\xacq;J\xb1\x9b\xe1"E\xd6J\x11T\x0cfE\x16\xedI\x8a>M'...
	----try uncompress----------
		res=' /P <</MCID 0>> BDC q\r\n0.000008871 0 595.32 841.92 re\r\nW* n\r\nBT\r\n/F1 11.04 Tf\r\n1 0 0 1 85.104 774.84 Tm\r\n/GS10 gs\r\n0 g\r\n/GS11 gs\r\n0 G\r\n[<032F>] TJ\r\nET\r\nQ\r\nq\r\n0.000008871 0 595.32 841.92 re\r\nW* n\r\nBT\r\n/F1 11.04 Tf\r\n1 0 0 1 89.424 774.84 Tm\r\n0 g\r\n0 G\r\n[<0316032D>8<032F>-3<03EE>] TJ\r\nET\r\nQ\r\nq\r\n0.000008871 0 595.32 841.92 re\r\nW* n\r\nBT\r\n/F2 11.04 Tf\r\n1 0 0 1 109.34 774.84 Tm\r\n0 g\r\n0 G\r\n[( )] TJ\r\nET\r\nQ\r\n EMC '
	 ----------
b'endstream'
b'endobj'
```
