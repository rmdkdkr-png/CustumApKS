# 게임 속 리그 글자 타일 만들기 — NGPC 2bpp 타일(행마다 16비트 LE, 왼쪽 픽셀이 높은 비트)
import sys, json
RI_GEU = [   # 메뉴 «리그» 16x8 (원래 «2 인» 자리, 7px 글꼴 · 잉크 1 · 바탕 3)
 "####..#..######.",
 "...#..#.......#.",
 "####..#.......#.",
 "#.....#.........",
 "####..#.#######.",
 "......#.........",
 "......#.........",
 "................",
]
SANG_DAE = [  # 머리말 «상대» 잉크 마스크(11줄) — 바깥테 자동, 48x16 자리(원래 «캐릭터»)
 "...#.....#.....###.#.#..",
 "..#.#....#.....#...#.#..",
 ".#...#...##....#...#.#..",
 "#.....#..#.....#...###..",
 ".........#.....#...#.#..",
 "...............###.#.#..",
 "...#####...........#.#..",
 "..#.....#..........#.#..",
 "..#.....#..........#.#..",
 "..#.....#..........#.#..",
 "...#####................",
]
SEON_TAEK = [  # 머리말 «선택» 잉크 마스크(11줄) — 순정판 «選択» 32x16 자리(한글판은 원래 «선택» 이 있어 안 씀)
 "...#....#...######.#.#",
 "..#.#...#...#......#.#",
 ".#...#.###..######.###",
 "#.....#.#...#......#.#",
 "........#...######.#.#",
 "...................#.#",
 "..#.........########..",
 "..#..............#....",
 "..#..............#....",
 "..#..............#....",
 "..########.......#....",
]
def enc_tiles(pix, w, h):   # pix[y][x] in 0..3 -> list of tiles (row-major tiles), each 16 bytes
    out=[]
    for ty in range(h//8):
        for tx in range(w//8):
            b=[]
            for y in range(8):
                v=0
                for x in range(8): v |= (pix[ty*8+y][tx*8+x] & 3) << (14-2*x)
                b += [v & 0xFF, v >> 8]
            out.append(b)
    return out
menu=[[ (1 if c=='#' else 3) for c in row] for row in RI_GEU]
def outlined(mask, W, H, ox, oy):   # 잉크 1 · 바깥테 3 · 바탕 0 (원래 머리말 글꼴과 같은 칠)
    ink=[[0]*W for _ in range(H)]
    for y,row in enumerate(mask):
        for x,c in enumerate(row):
            if c=='#': ink[oy+y][ox+x]=1
    out=[[0]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if ink[y][x]: out[y][x]=1
            elif any(0<=y+dy<H and 0<=x+dx<W and ink[y+dy][x+dx] for dy in (-1,0,1) for dx in (-1,0,1)): out[y][x]=3
    return out
hdr=outlined(SANG_DAE,48,16,8,2); sel=outlined(SEON_TAEK,32,16,4,2)
mt=enc_tiles(menu,16,8); ht=enc_tiles(hdr,48,16); st=enc_tiles(sel,32,16)   # ht: 위 6타일 뒤 아래 6타일 · st: 위 4 뒤 아래 4
def carr(name, tiles):
    flat=[x for t in tiles for x in t]
    s='static const uint8_t %s[%d] = {\n' % (name, len(flat))
    for i in range(0,len(flat),16): s+='   '+', '.join('0x%02X'%b for b in flat[i:i+16])+',\n'
    return s+'};\n'
open(sys.argv[1],'w').write('/* hub_glyphs.py 로 만든 글자 타일 — 「리그」(타이틀 메뉴 2번째 줄 앞 두 타일) · 「상대」(캐릭터 고르기 머리말 앞 6칸 × 2줄) · 「선택」(순정판 머리말 뒤 4칸 × 2줄) */\n'
   + carr('HUB_MENU_RIGEU', mt) + carr('HUB_HDR_SANGDAE', ht) + carr('HUB_HDR_SEONTAEK', st))
json.dump({'menu':mt,'hdr':ht,'sel':st}, open(sys.argv[2],'w'))
for row in menu: print(''.join('.#+@'[v] for v in row))
for row in hdr: print(''.join('.#+@'[v] for v in row))
for row in sel: print(''.join('.#+@'[v] for v in row))
