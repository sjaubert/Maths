import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_text(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            res = []
            for paragraph in tree.iter(WORD_NAMESPACE + 'p'):
                texts = [node.text for node in paragraph.iter(WORD_NAMESPACE + 't') if node.text]
                if texts:
                    res.append(''.join(texts))
            return '\n'.join(res)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    text = extract_text(sys.argv[1])
    with open("extract_out.txt", "w", encoding="utf-8") as f:
        f.write(text)
