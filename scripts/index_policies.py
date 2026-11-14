#!/usr/bin/env python3
"""Fetch ONLY public official PDFs from catalogue pages and build a local index.
Run from checkout: .venv/bin/python scripts/index_policies.py [--source 'JSP 752']
No personal queries or profiles are transmitted. TLS verification stays enabled.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag
import hashlib
import io
import json
import requests
from pypdf import PdfReader
from policy_engine import CATALOGUE, DATA_DIR, write_index

ALLOWED = {'www.gov.uk','assets.publishing.service.gov.uk','www.publishing.service.gov.uk'}
MAX_BYTES = 45 * 1024 * 1024

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'):
            self.links.append(attrs['href'])


def fetch(url):
    url=urldefrag(url)[0]
    for _ in range(5):
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.hostname not in ALLOWED or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('Refusing non-official or insecure source URL')
        with requests.get(url, timeout=(10,40), stream=True, allow_redirects=False) as response:
            if response.is_redirect:
                url=urljoin(url,response.headers['Location']);continue
            response.raise_for_status()
            chunks=[];length=0
            for chunk in response.iter_content(65536):
                length+=len(chunk)
                if length>MAX_BYTES:raise ValueError('Official document exceeds size limit')
                chunks.append(chunk)
            return b''.join(chunks),url
    raise ValueError('Too many redirects')


def refresh(output=DATA_DIR, sources=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    documents=[];errors=[]
    for source_id,(title,landing) in CATALOGUE.items():
        if sources and source_id not in sources:continue
        try:
            html,_=fetch(landing);parser=Links();parser.feed(html.decode('utf-8'))
            pdfs=sorted({urljoin(landing,u) for u in parser.links if urlsplit(u).path.lower().endswith('.pdf')})
            if not pdfs:raise ValueError('No public PDF found on official publication page')
            for url in pdfs[:12]:
                try:
                    data,url=fetch(url)
                    if not data.startswith(b'%PDF'):raise ValueError('Source is not a PDF')
                    reader=PdfReader(io.BytesIO(data))
                    pages=[p.extract_text() or '' for p in reader.pages]
                    if sum(map(len,pages))<200:raise ValueError('PDF has no usable text; OCR/review required')
                    digest=hashlib.sha256(data).hexdigest()
                    documents.append(dict(source_id=source_id,document_id=digest,title=title+' — '+urlsplit(url).path.rsplit('/',1)[-1],url=url,landing_url=landing,retrieved_at=datetime.now(timezone.utc).isoformat(),sha256=digest,pages=pages))
                    (output/(digest+'.pdf')).write_bytes(data)
                except Exception as exc:
                    # Per-document errors remain visible; never substitute invented text.
                    errors.append({'source':source_id,'url':url,'error':type(exc).__name__+': '+str(exc)[:180]})
        except Exception as exc:
            errors.append({'source':source_id,'url':landing,'error':type(exc).__name__+': '+str(exc)[:180]})
    # A failed refresh must not discard previously usable documents.
    if documents:
        old_documents=[]
        if (output/'manifest.json').exists():
            try:old_documents=json.loads((output/'manifest.json').read_text()).get('documents',[])
            except (ValueError,OSError):pass
        updated={d['source_id'] for d in documents}
        retained=[d for d in old_documents if d['source_id'] not in updated]
        write_index(output/'index.sqlite3',documents,retain_existing=True)
        manifest={'state':'ready' if not errors else 'partial','documents':retained+[{k:v for k,v in d.items() if k!='pages'} for d in documents],'errors':errors,'checked_at':datetime.now(timezone.utc).isoformat()}
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    else:
        manifest={'state':'unavailable','documents':[],'errors':errors,'checked_at':datetime.now(timezone.utc).isoformat()}
        # Preserve the previous manifest too. Report the failed refresh separately.
        (output/'last_refresh.json').write_text(json.dumps(manifest,indent=2))
        if not (output/'manifest.json').exists():(output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='append',choices=list(CATALOGUE));parser.add_argument('--output',type=Path,default=DATA_DIR)
    args=parser.parse_args();result=refresh(args.output,args.source)
    print(json.dumps(result,indent=2));sys.exit(0 if result['state']=='ready' else 1)
