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
