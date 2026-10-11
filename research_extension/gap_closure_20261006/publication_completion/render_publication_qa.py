"""Render all current delivered PDFs and contacts to a supplied QA directory."""
from pathlib import Path
import sys,json,subprocess,hashlib
from PIL import Image,ImageOps,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def run():
 if len(sys.argv)!=2:raise SystemExit('Supply an output directory with sufficient free space.')
 qa=Path(sys.argv[1]);qa.mkdir(parents=True,exist_ok=True);receipt=json.loads((HERE/'pdf_export_receipt.json').read_text());records=[]
 for row in receipt['outputs']:
  pdf=ROOT/row['pdf'];digest=hashlib.sha256(pdf.read_bytes()).hexdigest();assert digest==row['pdf_sha256'];out=qa/(pdf.stem+'_'+digest[:10]);out.mkdir(exist_ok=True)
  subprocess.run(['pdftoppm','-r','48','-png',str(pdf),str(out/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  pages=sorted(out.glob('page-*.png'));assert len(pages)==row['pages'];contacts=[]
  for start in range(0,len(pages),12):
   thumbs=[]
   for page in pages[start:start+12]:
    im=ImageOps.expand(Image.open(page).convert('RGB'),border=(4,23,4,4),fill='white');ImageDraw.Draw(im).text((8,5),page.stem,fill='black');thumbs.append(im)
   w=max(im.width for im in thumbs);h=max(im.height for im in thumbs);sheet=Image.new('RGB',(3*w,((len(thumbs)+2)//3)*h),'#c0c0c0')
   for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*w,(i//3)*h))
   path=out/f'contact-{start//12+1}.png';sheet.save(path);contacts.append(str(path))
  records.append(dict(pdf=row['pdf'],pdf_sha256=digest,pages=row['pages'],all_page_directory=str(out),contacts=contacts));print(pdf.name,'all pages rendered',flush=True)
 (HERE/'rendered_qa_inventory.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':run()
