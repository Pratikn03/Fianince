"""Build the NEW standalone logical core, with an explicit partial-coverage receipt."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,tarfile,urllib.request

VERSION='4.19.0'
ARCHIVE_SHA256='6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe'
URL=f'https://github.com/leanprover/lean4/releases/download/v{VERSION}/lean-{VERSION}-linux.tar.zst'


def verify(out,install=False,cache=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parent
    source=root/'formal/DecisionCore.lean'
    receipt=dict(status='NOT_RUN',full_manuscript_formalization_complete=False,
      scope='Eight standard conditional decision-logic lemmas only; not Gaussian coverage, market dynamics, minimax rates, utility optimality or welfare.',
      source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),toolchain='leanprover/lean4:v'+VERSION,
      new_theorem_count=8)
    cache=Path(cache or Path.home()/'.cache/mm-decision-lean')
    lean=cache/f'lean-{VERSION}-linux/bin/lean'
    if not lean.exists() and install:
        cache.mkdir(parents=True,exist_ok=True);archive=cache/'lean.tar.zst'
        if not archive.exists():
            with urllib.request.urlopen(URL,timeout=120) as r,archive.open('wb') as f:shutil.copyfileobj(r,f)
        sha=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
        if sha!=ARCHIVE_SHA256:raise ValueError('Lean archive checksum mismatch')
        import zstandard
        with archive.open('rb') as raw,zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with tarfile.open(fileobj=stream,mode='r|') as tf:
                for m in tf:
                    parts=Path(m.name).parts
                    if len(parts)>1 and (parts[1]=='lib' or '/'.join(parts[1:])=='bin/lean'):
                        tf.extract(m,cache,filter='data')
        receipt['download_sha256']=sha
    if not lean.exists():
        candidate=shutil.which('lean')
        if candidate:lean=Path(candidate)
    if lean.exists():
        env=os.environ.copy()
        version=subprocess.run([str(lean),'--version'],capture_output=True,text=True,timeout=30,env=env)
        receipt['version_stderr']=version.stderr.strip()
        if 'failed to locate application' in version.stderr and shutil.which('gcc'):
            # Same-process /proc path alias; preserves Lean kernel binary and proof source.
            shim_src=root/'formal/host_path_compat.c';shim=out/'host_path_compat.so'
            subprocess.run(['gcc','-shared','-fPIC','-o',str(shim),str(shim_src),'-ldl'],check=True,capture_output=True)
            env['LD_PRELOAD']=str(shim.resolve())
            version=subprocess.run([str(lean),'--version'],capture_output=True,text=True,timeout=30,env=env)
            receipt['host_path_compatibility_used']=True
            receipt['host_path_source_sha256']=hashlib.sha256(shim_src.read_bytes()).hexdigest()
            receipt['host_path_binary_sha256']=hashlib.sha256(shim.read_bytes()).hexdigest()
        receipt['version_output']=version.stdout.strip()
        if f'version {VERSION}' not in version.stdout:
            receipt['status']='WRONG_TOOLCHAIN'
        else:
            import re
            code=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
            if re.search(r'\b(sorry|admit|axiom|unsafe)\b',code):raise ValueError('unchecked proof token')
            r=subprocess.run([str(lean),str(source)],capture_output=True,text=True,timeout=180,env=env)
            (out/'lean_stdout.log').write_text(r.stdout);(out/'lean_stderr.log').write_text(r.stderr)
            receipt.update(status='PASS_PARTIAL_LOGICAL_CORE' if r.returncode==0 else 'FAILED',returncode=r.returncode)
    (out/'lean_receipt.json').write_text(json.dumps(receipt,indent=2))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--install',action='store_true');p.add_argument('--cache')
    a=p.parse_args();print(json.dumps(verify(a.out,a.install,a.cache),indent=2))
