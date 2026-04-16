import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_docx_text(path):
    with zipfile.ZipFile(path) as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
        # Also read styles
        styles_map = {}
        try:
            with z.open('word/styles.xml') as sf:
                stree = ET.parse(sf)
            sns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for style in stree.findall('.//w:style', sns):
                sid = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId', '')
                name_el = style.find('w:name', sns)
                if name_el is not None:
                    styles_map[sid] = name_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', sid)
        except:
            pass

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    root = tree.getroot()
    body = root.find('.//w:body', ns)

    result = []
    for para in body.findall('w:p', ns):
        pPr = para.find('w:pPr', ns)
        style_id = ''
        indent = ''
        num_info = ''
        spacing = ''

        if pPr is not None:
            pStyle = pPr.find('w:pStyle', ns)
            if pStyle is not None:
                style_id = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')

            numPr = pPr.find('w:numPr', ns)
            if numPr is not None:
                ilvl_el = numPr.find('w:ilvl', ns)
                numId_el = numPr.find('w:numId', ns)
                if ilvl_el is not None and numId_el is not None:
                    ilvl = ilvl_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
                    nid = numId_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
                    num_info = f'[LIST ilvl={ilvl} numId={nid}]'

            ind_el = pPr.find('w:ind', ns)
            if ind_el is not None:
                left = ind_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', '')
                if left:
                    indent = f'[indent={left}]'

            jc_el = pPr.find('w:jc', ns)
            align = ''
            if jc_el is not None:
                align = jc_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')

        runs = []
        for r in para.findall('w:r', ns):
            rPr = r.find('w:rPr', ns)
            bold = False
            italic = False
            underline = False
            color = ''
            size = ''
            font = ''

            if rPr is not None:
                b_el = rPr.find('w:b', ns)
                bold = b_el is not None and b_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1') != '0'

                i_el = rPr.find('w:i', ns)
                italic = i_el is not None and i_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '1') != '0'

                u_el = rPr.find('w:u', ns)
                underline = u_el is not None and u_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'single') != 'none'

                c_el = rPr.find('w:color', ns)
                if c_el is not None:
                    color = c_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')

                sz_el = rPr.find('w:sz', ns)
                if sz_el is not None:
                    size = sz_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')

                f_el = rPr.find('w:rFonts', ns)
                if f_el is not None:
                    font = f_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii', '')

            text_parts = []
            for child in r:
                tag = child.tag.split('}')[-1]
                if tag == 't':
                    text_parts.append(child.text or '')
                elif tag == 'br':
                    text_parts.append('\n')
                elif tag == 'tab':
                    text_parts.append('\t')

            text = ''.join(text_parts)
            if not text:
                continue

            flags = []
            if bold: flags.append('B')
            if italic: flags.append('I')
            if underline: flags.append('U')
            if color and color != 'auto': flags.append(f'color={color}')
            if size: flags.append(f'sz={size}')
            if font: flags.append(f'font={font}')

            if flags:
                runs.append(f'<{",".join(flags)}>{text}</{",".join(flags)}>')
            else:
                runs.append(text)

        line = ''.join(runs)
        style_name = styles_map.get(style_id, style_id)
        header = f'[{style_name}]{indent}{num_info}'
        result.append(f'{header} | {line}')

    return '\n'.join(result)


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'CCF_modele.docx'
    print(extract_docx_text(path))
