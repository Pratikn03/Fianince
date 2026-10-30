"""Exact arithmetic witness; optional Lean checks for seven scalar certificates."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,math,os,platform,subprocess,tarfile,urllib.request

LEAN_SHA='6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe'
LEAN_URL='https://github.com/leanprover/lean4/releases/download/v4.19.0/lean-4.19.0-linux.tar.zst'
def witness():
    z=F(21,10);var=F(3,4000);s=F(11,400);eps=2*z*s
    I=F(449,100);b=F(1,500)+F(1,1752);d=F(1,5000);fee=F(8,125);premium=F(2,25)
    gbar=20*(1-F(19,20)**60)
    exponential_lower=sum((z*z/2)**j/math.factorial(j) for j in range(9))
    # pi>3 and sqrt(6)>12/5; Mills' normal-tail bound is a written analytic step.
    tail_upper=1/(z*F(12,5)*exponential_lower)
    stress=I*(5+eps)/25+b*I+d*I**2+fee
    prefund=100*I+b*I+d*I**2+fee
    capcheck=F(131,100)*gbar/25+b*F(131,100)+d*F(131,100)**2
    nd_upper=(premium-b)*(F(39,40)*F(131,100)+F(1,40)*10)
    lower=F(19,20)*((premium-b)*I-d*I**2)-fee-nd_upper
    inequalities={
      'se_upper':(var,s*s),
      'normal_tail_budget':(tail_upper,F(1,40)),
      'stress_reserve_safe':(stress,F(1)),
      'prefunding_safe':(prefund,F(1000)),
      'no_data_cap_upper':(F(1),capcheck),
      'positive_net_value':(F(7,50),lower),
      'positive_asset_price':(gbar/25,F(100))}
    for name,(a,c) in inequalities.items():assert a<c,name
    def encode(x):return dict(numerator=x.numerator,denominator=x.denominator,decimal=float(x))
    return dict(inequalities={n:dict(left=encode(a),right=encode(c)) for n,(a,c) in inequalities.items()},
        net_information_advantage_lower=encode(lower),statement='For the declared primary contract, a conservative Gaussian margin has net information value > 0.14 in hypothetical model dollars.',
        scope='Exact numerical witness only. Gaussian Mills inequality, market dynamics, statistical implication, general theorem and novelty are NOT Lean formalized here.')

def lean_source(w):
    lines=['import Init','set_option maxRecDepth 10000','set_option maxHeartbeats 4000000',
           '-- Seven concrete rational inequality certificates, not a formal market theorem.','namespace CostWitness']
    for name,v in w['inequalities'].items():
        a=v['left'];b=v['right']
        # Positive denominators turn a rational inequality into this integer product comparison.
        lines.append(f'theorem {name} : ({a["numerator"]} : Nat) * {b["denominator"]} < {b["numerator"]} * {a["denominator"]} := by decide')
        lines.append(f'#print axioms {name}')
    lines.append('end CostWitness')
    return '\n'.join(lines)+'\n'

def run(out,enable_lean=True,cache=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);w=witness()
    (out/'exact_witness.json').write_text(json.dumps(w,indent=2)+'\n')
    source=out/'CostWitness.lean';source.write_text(lean_source(w))
    receipt=dict(status='NOT_RUN' if not enable_lean else 'PENDING',theorem_count=7,full_paper_formalized=False,
       scope=w['scope'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),toolchain='leanprover/lean4:v4.19.0')
    if enable_lean:
      try:
        if platform.system()!='Linux' or platform.machine() not in ['x86_64','AMD64']:raise RuntimeError('Pinned compiler is Linux x86_64 only')
        cache=Path(cache or Path.home()/'.cache/machine_markets_lean');cache.mkdir(parents=True,exist_ok=True)
        archive=cache/'lean-4.19.0-linux.tar.zst';compiler=cache/'lean-4.19.0-linux/bin/lean'
        if not compiler.exists():
            if not archive.exists():
                temp=archive.with_suffix('.part')
                with urllib.request.urlopen(LEAN_URL,timeout=60) as r,temp.open('wb') as f:
                    while True:
                        b=r.read(1024*1024)
                        if not b:break
                        f.write(b)
                os.replace(temp,archive)
            h=hashlib.sha256(archive.read_bytes()).hexdigest()
            if h!=LEAN_SHA:raise RuntimeError('Compiler archive checksum mismatch')
            subprocess.run(['tar','--no-same-owner','--zstd','-xf',str(archive),'-C',str(cache)],check=True,capture_output=True,timeout=240)
        # Never silently accept a proof failure. A host-path compatibility
        # shim is used only for this container's observed /proc/PID/exe issue.
        env=os.environ.copy();probe=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,timeout=30,env=env)
        shim_used=False
        if probe.returncode and any(s in (probe.stderr+probe.stdout).lower() for s in ['executable path','failed to find','lookup self','get executable','failed to locate application']):
            c=cache/'host_path_compat.c';so=cache/'host_path_compat.so'
            c.write_text('#define _GNU_SOURCE\n#include <dlfcn.h>\n#include <unistd.h>\n#include <stdio.h>\n#include <string.h>\nssize_t readlink(const char *p,char *b,size_t n){static ssize_t(*f)(const char*,char*,size_t);if(!f)f=dlsym(RTLD_NEXT,"readlink");char s[80];snprintf(s,sizeof(s),"/proc/%ld/exe",(long)getpid());if(!strcmp(p,s))p="/proc/self/exe";return f(p,b,n);}\n')
            subprocess.run(['cc','-shared','-fPIC',str(c),'-ldl','-o',str(so)],check=True,capture_output=True,timeout=30)
            env['LD_PRELOAD']=str(so);shim_used=True
            (out/'host_path_compat.c').write_bytes(c.read_bytes())
            probe=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,timeout=30,env=env)
        if probe.returncode:raise RuntimeError('Compiler version probe failed: '+probe.stderr)
        proc=subprocess.run([str(compiler),str(source)],capture_output=True,text=True,timeout=180,env=env)
        (out/'lean_output.log').write_text(proc.stdout+proc.stderr)
        no_axioms=proc.stdout.count('does not depend on any axioms')==7
        receipt.update(status='PASS_SCALAR_CERTIFICATES' if proc.returncode==0 and no_axioms else 'FAILED',
            returncode=proc.returncode,axioms_verified_absent=no_axioms,version=probe.stdout.strip(),host_path_shim=shim_used,
            archive_sha256=LEAN_SHA)
      except Exception as e:receipt.update(status='FAILED',error=str(e))
    (out/'lean_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path);p.add_argument('--skip-lean',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.out,not a.skip_lean,a.cache),indent=2))
