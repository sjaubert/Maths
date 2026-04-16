import zipfile, xml.etree.ElementTree as ET, re, sys

path = 'CCF_modele.docx'
with zipfile.ZipFile(path) as z:
    with z.open('word/document.xml') as f:
        content = f.read().decode('utf-8')
    # Read relationship file
    with z.open('word/_rels/document.xml.rels') as f:
        rels_content = f.read().decode('utf-8')

# Parse relationships
rels = {}
rels_tree = ET.fromstring(rels_content)
for rel in rels_tree:
    rid = rel.get('Id', '')
    target = rel.get('Target', '')
    rtype = rel.get('Type', '')
    rels[rid] = {'target': target, 'type': rtype}

# Find objects in XML
objs = re.findall(r'<w:object[^>]*>.*?</w:object>', content, re.DOTALL)
print(f'Found {len(objs)} OLE objects (formulas)')
for i, o in enumerate(objs):
    rids = re.findall(r'r:id="([^"]+)"', o)
    print(f'--- Formula {i+1}: rIds={rids}')
    for rid in rids:
        if rid in rels:
            print(f'   -> {rels[rid]}')
    # Also show surrounding text
    pos = content.find(o[:50])
    ctx_start = max(0, pos - 300)
    ctx = content[ctx_start:pos]
    # Extract text from context
    texts = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', ctx)
    print(f'   Context text: {"".join(texts)[-100:]}')
    print()
