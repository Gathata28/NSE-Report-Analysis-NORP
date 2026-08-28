# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from pathlib import Path
import subprocess, shutil
BASE=Path(__import__('os').environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
ROOT=BASE/'data'/'retrieved' if (BASE/'data'/'retrieved').exists() else BASE
PDFTOPPM=shutil.which('pdftoppm')
TESSERACT=shutil.which('tesseract')
if PDFTOPPM is None or TESSERACT is None:
    missing=', '.join(name for name,path in [('pdftoppm',PDFTOPPM),('tesseract',TESSERACT)] if path is None)
    raise RuntimeError(f'Missing OCR system dependency: {missing}. Install poppler-utils and tesseract-ocr, then retry.')
for pdf in sorted((ROOT/'kenya_orchards').glob('*.pdf')):
    outdir=pdf.parent/(pdf.stem+'_ocr')
    outdir.mkdir(exist_ok=True)
    subprocess.run([PDFTOPPM,'-jpeg','-r','150',str(pdf),str(outdir/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    pages=[]
    for image in sorted(outdir.glob('page-*.jpg')):
        txt=image.with_suffix('.txt')
        subprocess.run([TESSERACT,str(image),str(txt.with_suffix('')), '-l','eng'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
        pages.append(txt.read_text(errors='replace') if txt.exists() else '')
    pdf.with_suffix('.ocr.txt').write_text('\f'.join(pages),encoding='utf-8')
    print(pdf.name, 'pages=',len(pages),'chars=',sum(map(len,pages)))
