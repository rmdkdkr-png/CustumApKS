# -*- coding: utf-8 -*-
"""대형 일러 수확 — 상태파일의 VRAM에서 12x12 타일 일러를 뽑아
   타일별 롬 주소표로 바꾼다(아이콘 방식). 그림은 배포물에 없다 — 주소와 팔레트뿐.
   사용: harvest_art.py <state> <라벨>  →  art_<라벨>.json + art_<라벨>.png (롬 재렌더 검증)"""
import struct, sys, zlib, json

ROM = open("/home/user/rom/ss2.ngc","rb").read()

def ext(d, name):
    i = d.find(name.encode())
    if i < 0: raise SystemExit("섹션 없음: "+name)
    sz = struct.unpack("<I", d[i+len(name):i+len(name)+4])[0]
    return d[i+len(name)+4:i+len(name)+4+sz]

def harvest(state_path, label, rows=range(3,15), cols=range(1,13)):
    d = open(state_path,"rb").read()
    sv = ext(d,"ScrollVRAM"); cr = ext(d,"CharacterRAM"); pl = ext(d,"ColorPaletteRAM")
    cells = []          # (rom_addr, palno, hflip, vflip) — addr<0 = 롬에서 못 찾음
    pals  = {}
    W = len(list(cols)); H = len(list(rows))
    for row in rows:
        for col in cols:
            e = sv[(row*32+col)*2] | (sv[(row*32+col)*2+1]<<8)
            t = e & 0x1FF; pn = (e>>9)&0xF; hf = 1 if e&0x8000 else 0; vf = 1 if e&0x4000 else 0
            pat = bytes(cr[t*16:(t+1)*16])
            a = ROM.find(pat)
            cells.append((a, pn, hf, vf))
            if pn not in pals:
                pals[pn] = [pl[0x000+pn*8+ci*2] | (pl[0x000+pn*8+ci*2+1]<<8) for ci in range(4)]
    found = sum(1 for a,_,_,_ in cells if a>=0)
    json.dump({"label":label,"w":W,"h":H,"cells":cells,"pals":pals}, open("art_%s.json"%label,"w"))
    # 검증 렌더 — **롬만** 보고 다시 그린다
    px=[(255,0,255)]*(W*8*H*8)
    for i,(a,pn,hf,vf) in enumerate(cells):
        ty,tx = divmod(i,W)
        for ry in range(8):
            sy = 7-ry if vf else ry
            if a>=0: w2 = ROM[a+sy*2] | (ROM[a+sy*2+1]<<8)
            else: w2 = 0
            for rx in range(8):
                sx = 7-rx if hf else rx
                ci = (w2 >> ((7-sx)*2)) & 3
                v = pals[pn][ci]
                r=(v&0xF)*17; g=((v>>4)&0xF)*17; b=((v>>8)&0xF)*17
                px[(ty*8+ry)*(W*8) + tx*8+rx] = (r,g,b)
    Wp,Hp = W*8,H*8
    raw=b"".join(bytes([*px[y*Wp+x]]) for y in range(Hp) for x in range(Wp))
    rows_b=b"".join(b"\x00"+raw[y*Wp*3:(y+1)*Wp*3] for y in range(Hp))
    def ch(t,dd):
        c=t+dd; return struct.pack(">I",len(dd))+c+struct.pack(">I",zlib.crc32(c)&0xffffffff)
    open("art_%s.png"%label,"wb").write(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",Wp,Hp,8,2,0,0,0))+ch(b"IDAT",zlib.compress(rows_b,6))+ch(b"IEND",b""))
    print("%s: %d/%d 타일 롬에서 발견 → art_%s.png" % (label, found, len(cells), label))

if __name__ == "__main__":
    harvest(sys.argv[1], sys.argv[2])
