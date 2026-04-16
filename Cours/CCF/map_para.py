import zipfile
import xml.etree.ElementTree as ET
import sys

path = 'CCF_modele.docx'
with zipfile.ZipFile(path) as z:
    with z.open('word/document.xml') as f:
        content = f.read().decode('utf-8')

tree = ET.fromstring(content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

body = tree.find('.//w:body', ns)
paras = body.findall('w:p', ns)

print(f'Total paragraphs: {len(paras)}')
for i, para in enumerate(paras):
    has_obj = para.find('.//w:object', ns) is not None
    has_draw = para.find('.//w:drawing', ns) is not None

    texts = [t.text or '' for t in para.findall('.//w:t', ns)]
    fulltext = ''.join(texts)

    if has_obj or has_draw or fulltext.strip():
        marker = '[OBJ]' if has_obj else '[DRW]' if has_draw else '     '
        print(f'{i:3d} {marker} {fulltext[:150]}')
