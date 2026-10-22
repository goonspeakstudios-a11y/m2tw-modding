import os,struct,glob,lzma,binascii
D=r"D:\SteamLibrary\steamapps\common\Medieval II Total War\mods\EUR_V2.08_Shadows_and_Flame.2(1)"
S=os.path.dirname(os.path.abspath(__file__))
exe=open(os.path.join(D,"EPic Unity Rework.exe"),"rb").read()
def read_block(off):
    crc,size,comp=struct.unpack_from("<IQB",exe,off)
    calc=binascii.crc32(exe[off+4:off+13])&0xffffffff
    print(f"block @ {off} (0x{off:x}): hdrcrc={crc:08x} calc={calc:08x} stored_size={size} compressed={comp}")
    p=off+13; end=p+size; out=bytearray(); n=0; bad=0
    while p<end:
        ccrc=struct.unpack_from("<I",exe,p)[0]; p+=4
        take=min(4096,end-p); chunk=exe[p:p+take]; p+=take
        if (binascii.crc32(chunk)&0xffffffff)!=ccrc: bad+=1
        out+=chunk; n+=1
    print(f"  {n} chunks ({bad} bad crc), {len(out)} raw bytes, head {bytes(out[:8]).hex()}")
    return bytes(out),comp,end
def decomp(raw,comp):
    if not comp: return raw
    props=raw[0]; dict_size=struct.unpack_from("<I",raw,1)[0]; lc=props%9; lp=(props//9)%5; pb=props//45
    d=lzma.LZMADecompressor(format=lzma.FORMAT_RAW,filters=[{"id":lzma.FILTER_LZMA1,"dict_size":dict_size,"lc":lc,"lp":lp,"pb":pb}])
    out=d.decompress(raw[5:]); print(f"  lzma1 lc={lc} lp={lp} pb={pb} dict={dict_size} -> {len(out)} bytes, eof={d.eof}")
    return out
b1,c1,end1=read_block(0x11c475); d1=decomp(b1,c1)
print("block1 head:",d1[:200]); open(os.path.join(S,"block1.bin"),"wb").write(d1)
b2,c2,end2=read_block(end1); d2=decomp(b2,c2)
print("block2 head hex:"); 
for i in range(0,256,32): print(f"  {i:4d}: {d2[i:i+32].hex(' ')}")
open(os.path.join(S,"block2.bin"),"wb").write(d2)
print("end2",end2,"exe len",len(exe),"remaining",len(exe)-end2)
# period detection in block2: first_slice (small int) repeating
L=len(d2); cands=[]
for P in range(40,160):
    ok=all(d2[i*P]<=6 and d2[i*P+1]==0 and d2[i*P+2]==0 and d2[i*P+3]==0 for i in range(1,2000) if (i*P+4)<L)
    if ok: cands.append(P)
print("period candidates:",cands, "block2 len",L, {P:L/P for P in cands})
for f in sorted(glob.glob(os.path.join(D,"*.bin"))):
    with open(f,"rb") as fh: head=fh.read(32)
    print(os.path.basename(f), os.path.getsize(f), head[:12], head[12:32].hex(' '))
f=sorted(glob.glob(os.path.join(D,"*.bin")))[0]
data=open(f,"rb").read(); n=data.count(b"zlb\x1a"); first=data.find(b"zlb\x1a")
print("zlb magic count in slice1:",n,"first at",first, data[first:first+24].hex(' ') if first!=-1 else "")
