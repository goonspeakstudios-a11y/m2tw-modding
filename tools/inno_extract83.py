"""Pull the 83 overwritten mod files straight out of the Inno Setup 7 installer slices.
Read-only on the installer; recovered files land in <scratchpad>/recovered/<path> and are sha256-verified
against the EUREX 1.5 manifest before anything else happens."""
import os,struct,json,hashlib,lzma,time,glob,sys
D=r"D:\SteamLibrary\steamapps\common\Medieval II Total War\mods\EUR_V2.08_Shadows_and_Flame.2(1)"
S=os.path.dirname(os.path.abspath(__file__))
E15=r"D:\SteamLibrary\steamapps\common\Medieval II Total War\mods\EUREX1.5"
t0=time.time()
b2=open(os.path.join(S,"block2.bin"),"rb").read(); n=len(b2)//89
ent=[]
for i in range(n):
    fs,ls,coff,foff,fsz,csz=struct.unpack_from("<IIQQQQ",b2,i*89)
    sha=b2[i*89+40:i*89+72].hex(); ft,vms,vls,opt=struct.unpack_from("<QIIB",b2,i*89+72)
    ent.append((fs,ls,coff,foff,fsz,csz,sha,opt))
print("entries:",n); print("first 3:",ent[:3]); sys.stdout.flush()
man=json.load(open(os.path.join(E15,".EUREX1.5","manifest.json"),encoding="utf-8"))
rec={r["path"].replace("\\","/").lower():r for r in man["files"]}
by_sha={e[6]:e for e in ent}
# sanity: known file 4gb_patch.exe
p4=rec["4gb_patch.exe"]["source"]["sha256"]; print("4gb_patch.exe sha in installer entries:", p4 in by_sha, by_sha.get(p4,(None,)*8)[3:5])
still=json.load(open(os.path.join(S,"..","..","..","..","mod_fix_plan2.json")))["still"] if False else json.load(open(os.path.join(os.environ.get("TMP",""),"mod_fix_plan2.json")))["still"]
wanted={rec[p.lower()]["source"]["sha256"]:p for p in still}
matches=[(by_sha[s][3],by_sha[s][4],p,s) for s,p in wanted.items() if s in by_sha]
missing=[p for s,p in wanted.items() if s not in by_sha]
print(f"wanted {len(wanted)}  matched {len(matches)}  missing {len(missing)} {missing}")
chunks={(by_sha[s][0],by_sha[s][2],by_sha[s][5]) for s,p in wanted.items() if s in by_sha}
print("distinct chunks among matches:",chunks)
if not matches: sys.exit("nothing to extract")
matches.sort(); max_end=max(o+z for o,z,p,s in matches)
print(f"stream range needed: 0 .. {max_end:,} bytes  (first wanted at {matches[0][0]:,})"); sys.stdout.flush()
def payload():
    files=sorted(glob.glob(os.path.join(D,"*.bin")),key=lambda f:int(f.rsplit("-",1)[1].split(".")[0]))
    for i,f in enumerate(files):
        with open(f,"rb") as fh:
            fh.seek(16+(4 if i==0 else 0))
            while True:
                b=fh.read(8*1024*1024)
                if not b: break
                yield b
gen=payload(); first=next(gen)
props=first[0]; dict_size=struct.unpack_from("<I",first,1)[0]; lc=props%9; lp=(props//9)%5; pb=props//45
print(f"solid chunk lzma1: lc={lc} lp={lp} pb={pb} dict={dict_size}")
dec=lzma.LZMADecompressor(format=lzma.FORMAT_RAW,filters=[{"id":lzma.FILTER_LZMA1,"dict_size":dict_size,"lc":lc,"lp":lp,"pb":pb}])
pos=0; pending=list(matches); bufs={}; done=[]
outdir=os.path.join(S,"recovered")
def feed(data):
    global pos
    out=dec.decompress(data,max_length=32*1024*1024)
    while True:
        if out:
            end=pos+len(out)
            for o,z,p,s in pending:
                if o<end and o+z>pos:
                    a=max(o,pos); b=min(o+z,end)
                    bufs.setdefault(p,bytearray()).extend(out[a-pos:b-pos])
                    if b==o+z:
                        data_=bytes(bufs.pop(p)); ok=hashlib.sha256(data_).hexdigest()==s
                        fp=os.path.join(outdir,p.replace("/",os.sep)); os.makedirs(os.path.dirname(fp),exist_ok=True)
                        open(fp,"wb").write(data_); done.append((p,ok)); print(f"  {'OK ' if ok else 'BAD'} {p} ({z:,} B) @ {time.time()-t0:.0f}s"); sys.stdout.flush()
            pending[:]=[m for m in pending if m[2] not in dict(done)]
            pos=end
        if dec.needs_input or dec.eof: break
        out=dec.decompress(b"",max_length=32*1024*1024)
feed(first[5:])
fed=len(first); last=0
for b in gen:
    if not pending or pos>=max_end: break
    feed(b); fed+=len(b)
    if fed-last>=512*1024*1024: last=fed; print(f"  ... {fed/2**30:.2f} GiB compressed read, {pos/2**30:.2f} GiB decompressed, {len(done)}/{len(matches)} files, {time.time()-t0:.0f}s"); sys.stdout.flush()
print(f"DONE: {sum(1 for p,ok in done if ok)} verified, {sum(1 for p,ok in done if not ok)} bad, {len(pending)} not reached; {time.time()-t0:.0f}s")
