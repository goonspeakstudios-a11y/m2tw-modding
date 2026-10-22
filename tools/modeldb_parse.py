"""Strict parser for battle_models.modeldb using the grammar in the mod team's own annotated dump
(from_modeldb/battle_models.txt). Reports the first entry that breaks the grammar."""
import re,sys
class P:
    def __init__(s,b): s.b=b; s.i=0
    def ws(s):
        while s.i<len(s.b) and s.b[s.i] in b" \r\n\t": s.i+=1
    def num(s):
        s.ws(); m=re.compile(rb"-?\d+(?:\.\d+)?").match(s.b,s.i)
        if not m: raise ValueError(f"expected number at {s.i}: {s.b[s.i:s.i+40]!r}")
        s.i=m.end(); t=m.group(0); return float(t) if b"." in t else int(t)
    def str_(s):
        n=s.num()
        if not isinstance(n,int) or n<0: raise ValueError(f"bad string length {n} at {s.i}")
        if n==0: return ""
        if s.b[s.i:s.i+1]!=b" ": raise ValueError(f"expected space before string at {s.i}: {s.b[s.i:s.i+40]!r}")
        s.i+=1; v=s.b[s.i:s.i+n]; s.i+=n
        if s.b[s.i:s.i+1] not in (b" ",b"\r",b"\n",b""): raise ValueError(f"string length {n} does not end at a delimiter at {s.i}: {s.b[s.i-n:s.i+20]!r}")
        return v.decode("latin-1")
def parse(path,verbose=False):
    b=open(path,"rb").read(); p=P(b)
    hdr=b.split(b"\n",1)[0].rstrip(b"\r").split(); N=int(hdr[7]); p.i=len(b.split(b"\n",1)[0])+1
    # entry 0 'blank' is one special line (boost 'first time' pads) - skip it
    line_end=b.find(b"\n",p.i); assert b[p.i:p.i+7]==b"5 blank", b[p.i:p.i+20]; p.i=line_end+1
    entries=[("blank",0,{})]
    try:
        while True:
            p.ws()
            if p.i>=len(b): break
            start=p.i; e={}
            e["name"]=p.str_(); e["scale"]=p.num(); nl=p.num(); e["lods"]=[(p.str_(),p.num()) for _ in range(nl)]
            nt=p.num(); e["tex"]=[(p.str_(),p.str_(),p.str_(),p.str_()) for _ in range(nt)]
            na=p.num(); e["att"]=[(p.str_(),p.str_(),p.str_(),p.str_()) for _ in range(na)]
            nm=p.num(); mts=[]
            for _ in range(nm):
                mt=p.str_(); prim=p.str_(); sec=p.str_()
                npw=p.num(); pw=[p.str_() for _ in range(npw)]; nsw=p.num(); sw=[p.str_() for _ in range(nsw)]
                mts.append((mt,prim,sec,pw,sw))
            e["mounts"]=mts; e["torch"]=p.num(); e["off"]=[p.num() for _ in range(6)]
            entries.append((e["name"],start,e))
    except Exception as ex:
        last=entries[-1][0]; line=b.count(b"\n",0,p.i)+1
        print(f"PARSE FAILURE in {path}\n  after {len(entries)} entries (header says {N}); last good entry: {last!r}; failing entry starts at byte {start} (line {b.count(b'\n',0,start)+1}): {b[start:start+60]!r}\n  error at line {line}: {ex}")
        return entries,False,N
    print(f"{path}: parsed {len(entries)} entries cleanly to EOF (header says {N})")
    return entries,True,N
if __name__=="__main__":
    for f in sys.argv[1:]: parse(f)
