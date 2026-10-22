import struct,sys
base=r"D:\SteamLibrary\steamapps\common\Medieval II Total War\mods\Divide_and_Conquer_EUR\data\world\maps\base\\"
def tga(path):
    b=open(path,'rb').read(); idl,cmt,typ=b[0],b[1],b[2]
    w,h=struct.unpack('<HH',b[12:16]); bpp=b[16]; desc=b[17]; off=18+idl
    if cmt: off+=struct.unpack('<H',b[5:7])[0]*(b[7]//8)
    n=bpp//8; px=bytearray(); i=off
    if typ in (2,3): px=bytearray(b[off:off+w*h*n])
    else:
        while len(px)<w*h*n:
            p=b[i]; i+=1; c=(p&127)+1
            if p&128: px+=b[i:i+n]*c; i+=n
            else: px+=b[i:i+n*c]; i+=n*c
    top=bool(desc&32)
    def get(x,y):
        row=(h-1-y) if top else y
        j=(row*w+x)*n; v=px[j:j+n]
        return tuple(v[:3][::-1]) if n>=3 else v[0]
    return w,h,get
rw,rh,reg=tga(base+"map_regions.tga")
gw,gh,gt=tga(base+"map_ground_types.tga")
hw,hh,ht=tga(base+"map_heights.tga")
print("regions",rw,rh,"ground",gw,gh,"heights",hw,hh)
def town(col):
    for y in range(rh):
        for x in range(rw):
            if reg(x,y)==(0,0,0):
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    if 0<=x+dx<rw and 0<=y+dy<rh and reg(x+dx,y+dy)==col: return x,y
for name,col in (("Sarnur",(8,12,52)),("Nan_i_Naugrim/Thorins",(91,112,124)),("Kheledul",(8,12,44))):
    t=town(col); print(name,"town tile",t)
    if not t: continue
    x0,y0=t
    print(" region colours 11x11 (N up):")
    for y in range(y0+5,y0-6,-1):
        print("  ", " ".join(("TT" if (x,y)==(x0,y0) else ("##" if reg(x,y)==(0,0,0) else ("%02x"%(sum(reg(x,y))%256)))) for x in range(x0-5,x0+6)))
    print(" ground types 11x11 (map_ground_types is 2x+1 res):")
    for y in range(y0+5,y0-6,-1):
        print("  ", " ".join("%-11s"%str(gt(2*x+1,2*y+1)) for x in range(x0-5,x0+6)))
    print(" heights (raw):")
    for y in range(y0+5,y0-6,-1):
        v=[ht(2*x+1,2*y+1) for x in range(x0-5,x0+6)]
        print("  ", " ".join("%-11s"%str(a) for a in v))
