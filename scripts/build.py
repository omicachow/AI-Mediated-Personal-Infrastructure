"""Build the manuscript PDF and citation metadata from the sole Markdown source.

No network access, private-project access, or publishing operations.
Original publishing utility by Omica Chow; see ../LICENSE.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date
from html import escape
from pathlib import Path

import mistune
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                               Flowable, KeepTogether)
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'paper' / 'AMPI-v0.1.md'
PDF = SOURCE.with_suffix('.pdf')
WIDTH = A4[0] - 2 * 55
ACCENT = colors.HexColor('#20495c')

def font(name: str, variable: str, default: str):
    location = Path(os.environ.get(variable, str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / default)))
    if not location.is_file():
        raise FileNotFoundError(f'Provide a licensed font through {variable}; font is missing.')
    pdfmetrics.registerFont(TTFont(name, str(location), subfontIndex=0))

def register_fonts():
    for args in [('Body','AMPI_SERIF','georgia.ttf'), ('Body-Bold','AMPI_SERIF_BOLD','georgiab.ttf'),
                 ('Body-Italic','AMPI_SERIF_ITALIC','georgiai.ttf'), ('Sans','AMPI_SANS','calibri.ttf'),
                 ('Sans-Bold','AMPI_SANS_BOLD','calibrib.ttf'), ('CJK','AMPI_CJK','msyh.ttc')]:
        font(*args)
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic', boldItalic='Body-Bold')
    pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-Bold', italic='Sans', boldItalic='Sans-Bold')
    pdfmetrics.registerFontFamily('CJK', normal='CJK', bold='CJK', italic='CJK', boldItalic='CJK')

class Figure(Flowable):
    def __init__(self, file: Path):
        super().__init__()
        drawing = svg2rlg(str(file))
        if drawing is None:
            raise ValueError('SVG conversion failed')
        factor = WIDTH / drawing.width
        drawing.scale(factor, factor)
        self.width, self.height = WIDTH, drawing.height * factor
        drawing.width, drawing.height = self.width, self.height
        self.drawing = drawing
    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)

def inline(tokens: list[dict]) -> str:
    out = []
    for token in tokens:
        kind = token['type']
        if kind == 'text':
            for part in re.split(r'([\u3400-\u9fff]+)',token['raw']):
                escaped=escape(part)
                out.append(f'<font name="CJK">{escaped}</font>' if has_cjk(part) else escaped)
        elif kind in ('strong', 'emphasis'):
            tag = 'b' if kind == 'strong' else 'i'
            out.append(f'<{tag}>{inline(token["children"])}</{tag}>')
        elif kind == 'link':
            url = token['attrs']['url']
            if not url.startswith('https://'):
                raise ValueError(f'Unexpected manuscript link: {url}')
            out.append(f'<link href="{escape(url,quote=True)}" color="#20495c"><u>{inline(token["children"])}</u></link>')
        elif kind == 'codespan':
            out.append(f'<font name="Sans">{escape(token["raw"])}</font>')
        elif kind in ('softbreak','linebreak'):
            out.append('<br/>' if kind == 'linebreak' else ' ')
        else:
            raise ValueError(f'Unsupported inline token: {kind}')
    return ''.join(out)

def has_cjk(text: str) -> bool:
    return bool(re.search(r'[\u3400-\u9fff]', text))

def parse_source():
    text = SOURCE.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError('Manuscript front matter is required')
    header, body = text[4:].split('\n---\n',1)
    metadata = yaml.safe_load(header)
    tokens = mistune.create_markdown(renderer='ast')(body)
    return metadata, body, tokens

def citation_metadata(m: dict):
    authors = [{'given-names':m['given_name'], 'family-names':m['family_name']}]
    published = m.get('publication_date')
    note = f'{m["genre"]}. {m["status"]}.'
    cff = {'cff-version':'1.2.0', 'message':'Please cite the concept note in preferred-citation. ' + note,
           'title':m['title'], 'authors':authors, 'version':m['version'], 'license':'CC-BY-4.0',
           'abstract':'A design framework for coordinating existing specialized software around personal goals through semantic interpretation, persistent state, scoped authority, and verifiable execution. AcademicWorkspace provides a sanitized implementation-informed case.',
           'keywords':['AI-mediated personal infrastructure','semantic coordination','personal computing',
                       'persistent state','human authority','GUI agents'],
           'preferred-citation':{'type':'report','title':m['title'],'authors':authors,
                                 'version':m['version'],'notes':note}}
    csl = [{'id':'chow-ampi-v0.1', 'type':'report', 'title':m['title'],
            'author':[{'given':m['given_name'],'family':m['family_name']}],
            'version':m['version'], 'genre':m['genre'], 'language':m['language'], 'note':m['status']}]
    fields = {'author':f'{m["family_name"]}, {m["given_name"]}', 'title':m['title'],
              'type':'Concept note / position statement', 'version':m['version'], 'note':note}
    if published:
        d = date.fromisoformat(str(published))
        cff['date-released'] = d.isoformat()
        cff['preferred-citation']['year'] = d.year
        cff['preferred-citation']['date-published'] = d.isoformat()
        csl[0]['issued'] = {'date-parts':[[d.year,d.month,d.day]]}
        fields['year'] = str(d.year)
    if m.get('doi'):
        for target in (cff,cff['preferred-citation']):
            target['doi'] = m['doi']
        csl[0]['DOI'] = m['doi']
        fields['doi'] = m['doi']
    if m.get('public_url'):
        cff['url'] = m['public_url']
        cff['preferred-citation']['url'] = m['public_url']
        csl[0]['URL'] = m['public_url']
        fields['url'] = m['public_url']
    (ROOT/'CITATION.cff').write_text(yaml.safe_dump(cff,sort_keys=False,allow_unicode=True),encoding='utf-8',newline='\n')
    folder=ROOT/'citation'
    folder.mkdir(exist_ok=True)
    (folder/'AMPI-v0.1.csl.json').write_text(json.dumps(csl,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    def bib_escape(value):
        return str(value).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
    bib='@techreport{chow-ampi-v0.1,\n'+',\n'.join(f'  {key} = {{{bib_escape(value)}}}' for key,value in fields.items())+'\n}\n'
    (folder/'AMPI-v0.1.bib').write_text(bib,encoding='utf-8',newline='\n')

def build(m: dict, tokens: list[dict]):
    register_fonts()
    body_style = ParagraphStyle('Body',fontName='Body',fontSize=10.5,leading=15.4,
                                spaceAfter=8,alignment=TA_LEFT,allowWidows=0,allowOrphans=0)
    cjk_style = ParagraphStyle('Chinese',parent=body_style,fontName='CJK',fontSize=10.0,
                               leading=16.7,wordWrap='CJK')
    refs_style = ParagraphStyle('References',parent=body_style,fontSize=9.1,leading=13.1,spaceAfter=7)
    caption_style = ParagraphStyle('Caption',parent=body_style,fontName='Sans',fontSize=9,leading=12.3,
                                   textColor=colors.HexColor('#40535e'),spaceAfter=12)
    quote_style = ParagraphStyle('Definition',parent=body_style,fontSize=11,leading=16.5,
                                 backColor=colors.HexColor('#edf4f6'),borderPadding=10,
                                 leftIndent=10,rightIndent=10,spaceBefore=5,spaceAfter=16)
    styles={
        1:ParagraphStyle('Title',parent=body_style,fontName='Sans-Bold',fontSize=24,leading=28,
                         textColor=ACCENT,spaceAfter=7,keepWithNext=True),
        2:ParagraphStyle('Heading',parent=body_style,fontName='Sans-Bold',fontSize=13.5,leading=17,
                         textColor=ACCENT,spaceBefore=15,spaceAfter=7,keepWithNext=True),
        3:ParagraphStyle('Subheading',parent=body_style,fontName='Sans-Bold',fontSize=11.5,leading=15.5,
                         textColor=ACCENT,spaceBefore=10,spaceAfter=6,keepWithNext=True)}
    story=[]
    in_refs=False
    in_chinese=False
    title_seen=False
    for block in tokens:
        kind=block['type']
        if kind=='blank_line':
            continue
        if kind=='heading':
            text=inline(block['children'])
            level=block['attrs']['level']
            if text=='References':
                in_refs=True
            if '中文摘要' in text:
                in_chinese=True
                in_refs=False
            style=styles[level]
            if level==2 and not title_seen:
                style=ParagraphStyle('Subtitle',parent=style,fontName='Sans',fontSize=15,
                                     leading=20,spaceBefore=0,spaceAfter=13)
                title_seen=True
            if has_cjk(text):
                style=ParagraphStyle('CJKHeading',parent=style,fontName='CJK',wordWrap='CJK')
            story.append(Paragraph(text,style))
        elif kind=='paragraph':
            if len(block['children'])==1 and block['children'][0]['type']=='image':
                image=block['children'][0]
                path=(SOURCE.parent/image['attrs']['url']).resolve()
                if path.parent!=ROOT/'assets' or path.suffix!='.svg':
                    raise ValueError('Only the local original SVG is permitted')
                story.append(Figure(path))
                continue
            text=inline(block['children'])
            style=cjk_style if in_chinese else refs_style if in_refs else body_style
            if text.startswith('<i>Figure '):
                style=caption_style
            story.append(Paragraph(text,style))
        elif kind=='block_quote':
            children=block['children']
            if len(children)!=1 or children[0]['type']!='paragraph':
                raise ValueError('Unsupported quotation structure')
            story.append(Paragraph(inline(children[0]['children']),quote_style))
        elif kind=='list':
            for index,item in enumerate(block['children'],block.get('attrs',{}).get('start',1)):
                texts=[]
                for child in item['children']:
                    if child['type'] not in ('block_text','paragraph'):
                        raise ValueError('Nested lists are not used in this manuscript')
                    texts.append(inline(child['children']))
                style=cjk_style if in_chinese else refs_style if in_refs else body_style
                label=f'{index}.' if block['attrs'].get('ordered') else '-'
                style=ParagraphStyle(f'List{index}',parent=style,leftIndent=15,firstLineIndent=-15)
                story.append(Paragraph(label+' '+ '<br/>'.join(texts),style))
        else:
            raise ValueError(f'Unsupported block: {kind}')
    def page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#536672'))
        canvas.setFont('Sans',8.5)
        canvas.drawString(55,A4[1]-33,f'AMPI | Omica Chow | v{m["version"]}')
        canvas.setStrokeColor(colors.HexColor('#d5e0e5'))
        canvas.line(55,A4[1]-40,A4[0]-55,A4[1]-40)
        canvas.drawString(55,28,m['status'])
        canvas.drawRightString(A4[0]-55,28,str(doc.page))
        canvas.restoreState()
    doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=55,leftMargin=55,topMargin=56,bottomMargin=48,
                          title=m['title'],author=m['author'],subject=m['genre'],
                          creator='AMPI manuscript publishing utility',pageCompression=1)
    doc.build(story,onFirstPage=page,onLaterPages=page)

def main():
    m,body,tokens=parse_source()
    build(m,tokens)
    citation_metadata(m)
    english=body.split('## References')[0]
    english=re.sub(r'!\[[^\]]*\]\([^)]*\)','',english)
    count=len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*",english))
    print(json.dumps({'pdf':PDF.name,'english_words_before_references':count,'text_source':SOURCE.name}))

if __name__=='__main__':
    main()
