import struct
from collections import deque
base=r"D:\SteamLibrary\steamapps\common\Medieval II Total War\mods\Divide_and_Conquer_EUR\data\world\maps\base\\"
def tga(path):
    b=open(path,'rb').read(); idl,cmt,typ=b[0],b[1],b[2]
    w,h=struct.unpack('<HH',b[12:16]); bpp=b[16]; desc=b[17]; off=18+idl
    n=bpp//8; px=bytearray(); i=off
    if typ in (2,3): px=bytearray(b[off:off+w*h*n])
    else:
        while len(px)<w*h*n:
            p=b[i]; i+=1; c=(p&127)+1
            if p&128: px+=b[i:i+n]*c; i+=n
            else: px+=b[i:i+n*c]; i+=n*c
    top=bool(desc&32)
    def get(x,y):
        row=(h-1-y) if top else y; j=(row*w+x)*n; v=px[j:j+n]
        return tuple(v[:3][::-1]) if n>=3 else v[0]
    return w,h,get
rw,rh,reg=tga(base+"map_regions.tga"); gw,gh,gt=tga(base+"map_ground_types.tga"); fw,fh,ft=tga(base+"map_features.tga")
HIGH=(98,65,65); SEA={(64,0,0),(128,0,0),(196,0,0),(255,0,0),(0,0,64),(0,0,128)}
def passable(x,y):
    c=gt(2*x+1,2*y+1)
    return c!=HIGH and c not in SEA and c[0]!=64 and not (c[1]==0 and c[2]==0 and c[0]>=64)
start=(67,406); target=(66,433)
seen={start}; q=deque([start]); parent={}
while q:
    x,y=q.popleft()
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if not dx and not dy: continue
            nx,ny=x+dx,y+dy
            if 0<=nx<rw and 0<=ny<rh and (nx,ny) not in seen and passable(nx,ny):
                seen.add((nx,ny)); parent[(nx,ny)]=(x,y); q.append((nx,ny))
                if len(seen)>4000: q.clear(); break
print("reachable tiles from Sarnur (capped 4000):",len(seen))
print("Thorin's Halls reachable:",target in seen)
# nearest reachable tile not in Sarnur region
sar=reg(68,406)
print("Sarnur region colour sample",sar, "regions touched:", sorted({reg(x,y) for x,y in seen})[:12])
if target in seen:
    p=[target]
    while p[-1]!=start: p.append(parent[p[-1]])
    p=p[::-1]; print("path len",len(p)); print(p)
    print("ground along path:",[gt(2*x+1,2*y+1) for x,y in p])
    print("features along path:",[ft(2*x+1,2*y+1) for x,y in p])
# neighbours of Sarnur
print("Sarnur neighbours passable:",[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1) if (dx or dy) and passable(67+dx,406+dy)])
print("Sarnur tile ground:",gt(135,813),"feature:",ft(135,813))
