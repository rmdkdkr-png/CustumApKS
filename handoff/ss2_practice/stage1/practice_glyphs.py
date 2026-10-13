# 연습 대전 글자 타일 만들기 — NGPC 2bpp 타일(행마다 16비트 LE, 왼쪽 픽셀이 높은 비트)
# 사용: python3 practice_glyphs.py <앱>/app/src/main/cpp/practice_glyphs.h <Galmuri7.ttf> [미리보기.png]
#   글꼴: 갈무리7(Galmuri7 2.40.3, SIL OFL 1.1 — npm galmuri, 앱 assets/fonts/pixel.ttf 갈무리11 과 같은 집안).
#         8px 크기로 그리면 한글이 7줄 × 7칸 — 한글판 타이틀 메뉴 글꼴(«1 인 대전»)과 같은 7px 칠이다.
#   만드는 것
#     PG_MENU_YEONSEUP  타이틀 메뉴 셋째 줄 «2 인» 두 타일(0x1BB·0x1BC) 자리에 그릴 «연습»(16 × 8, 잉크 1 · 바탕 3 — hub_glyphs.py «리그»와 같은 칠)
#     PG_GLYPH          연습 메뉴 창 글자 — 음절 하나 = 타일 하나(잉크 1 · 바탕 3), 라틴 낱말 «CPU»·«MAX» 는 두 타일
#     PG_CURSOR         커서 «▶»(잉크 1) — 뒤집기 비트로 «◀» 도 된다
#     PG_BORDER_*       창 테두리(가로·세로·모서리, 선 = 색 2, 창 안 = 색 3, 창 밖 = 색 0 투명) — 뒤집기 비트로 네 모서리
#     PG_TWO            HUD «COM»(0x049) 자리에 쓸 «2»(게임 «1P» 타일 0x03B 와 같은 칠: 잉크 1 · 테 2 · 바탕 3)
#     PG_TITLE · PG_LABEL · PG_VALUE   메뉴 글줄(칸마다 글자 번호, 0 = 빈칸)
import sys
from PIL import Image, ImageDraw, ImageFont

OUT, FONT = sys.argv[1], sys.argv[2]
PREVIEW = sys.argv[3] if len(sys.argv) > 3 else None
fnt = ImageFont.truetype(FONT, 8)

# ── 메뉴 글(설계 4-마) ───────────────────────────────────────────────
TITLE = '연습 메뉴'
ROWS = [   # (이름, 값들) — 값이 없으면 실행 줄
    ('더미', ['서기', 'CPU']),
    ('가드', ['안 함', '전부', '첫 타 뒤', '랜덤']),
    ('내 분노', ['보통', 'MAX']),
    ('상대 분노', ['보통', 'MAX']),
    ('리셋 위치', ['가운데', '왼쪽 벽', '오른쪽 벽', '지난 위치']),
    ('리셋 좌우', ['그대로', '바꿈']),
    ('숫자', ['대미지', '끔']),
    ('지금 리셋', None),
    ('다시 고르기', None),
    ('타이틀로', None),
]
LATIN = ['CPU', 'MAX']             # 두 타일로 그리는 라틴 낱말
LABEL_W, VALUE_W = 11, 5           # 이름 칸(창 안 5~15칸 — 값 줄은 5칸만 씀) · 값 칸(11~15칸)

def cells(s):
    """글 → 칸 목록(글자 이름, ' ' = 빈칸). 라틴 낱말은 'CPU#0','CPU#1' 두 칸"""
    out = []
    for w in s.split(' '):
        if out: out.append(' ')
        if w in LATIN: out += [w + '#0', w + '#1']
        else: out += list(w)
    return out

glyph_names = []
def gid(name):
    if name == ' ': return 0
    if name not in glyph_names: glyph_names.append(name)
    return glyph_names.index(name) + 1

title_c = [gid(c) for c in cells(TITLE)]
label_c, value_c, nval = [], [], []
for lab, vals in ROWS:
    c = [gid(x) for x in cells(lab)]
    assert len(c) <= (LABEL_W if vals is None else VALUE_W), lab
    label_c.append(c + [0] * (LABEL_W - len(c)))
    vs = []
    for v in (vals or []):
        cv = [gid(x) for x in cells(v)]
        assert len(cv) <= VALUE_W, v
        vs.append(cv + [0] * (VALUE_W - len(cv)))
    nval.append(len(vs))
    value_c.append(vs)
NV = max(nval)

# ── 그리기 ───────────────────────────────────────────────────────────
def render(s, w):
    """갈무리7 8px — 글자 위 끝이 그림 1줄에 오므로 한 줄 올려 0~6줄에. 잉크 마스크 [8][w]"""
    im = Image.new('L', (w + 16, 16), 0)
    ImageDraw.Draw(im).text((0, 0), s, font=fnt, fill=255)
    return [[1 if im.getpixel((x, y + 1)) > 127 else 0 for x in range(w)] for y in range(8)]

def enc(pix):   # 8x8 색 번호 → 16바이트
    b = []
    for y in range(8):
        v = 0
        for x in range(8): v |= (pix[y][x] & 3) << (14 - 2 * x)
        b += [v & 0xFF, v >> 8]
    return b

def ink_tile(mask, ox=0):   # 잉크 1 · 바탕 3
    return [[1 if 0 <= x - ox < len(mask[0]) and mask[y][x - ox] else 3 for x in range(8)] for y in range(8)]

tiles = {}
for name in glyph_names:
    if '#' in name:                                   # 라틴 낱말 두 칸 — 글자 사이 1px, 16px 가운데
        word, k = name.split('#')
        if word not in tiles:
            letters = [render(ch, 8) for ch in word]
            widths = [max([x + 1 for y in range(8) for x in range(8) if m[y][x]] or [0]) for m in letters]
            strip = [[0] * 16 for _ in range(8)]
            total = sum(widths) + len(widths) - 1
            x0 = max(0, (16 - total) // 2)
            for m, w in zip(letters, widths):
                for y in range(8):
                    for x in range(w):
                        if m[y][x] and x0 + x < 16: strip[y][x0 + x] = 1
                x0 += w + 1
            tiles[word] = strip
        strip = tiles[word]
        half = [row[int(k) * 8:int(k) * 8 + 8] for row in strip]
        tiles[name] = ink_tile(half)
    else:
        m = render(name, 8)
        assert not any(m[y][7] for y in range(8)), name    # 8칸째(사이)는 비어야
        assert not any(m[7]), name                          # 7줄째(줄 사이)도
        tiles[name] = ink_tile(m)

menu = render('연습', 16)                                # 타이틀 메뉴 «연습» 16 × 8
menu_pix = [[1 if menu[y][x] else 3 for x in range(16)] for y in range(8)]
menu_tiles = [enc([row[0:8] for row in menu_pix]), enc([row[8:16] for row in menu_pix])]

CUR = ["........",
       ".#......",
       ".##.....",
       ".###....",
       ".####...",
       ".###....",
       ".##.....",
       ".#......"]
cursor = [[1 if CUR[y][x] == '#' else 3 for x in range(8)] for y in range(8)]

L = 3   # 테두리 선 자리(타일 안 3번째 줄·칸) — 바깥 0~2 는 투명(색 0), 선 = 색 2, 안 = 색 3
bh = [[0 if y < L else 2 if y == L else 3 for x in range(8)] for y in range(8)]
bv = [[0 if x < L else 2 if x == L else 3 for x in range(8)] for y in range(8)]
bc = [[0 if (x < L or y < L) else 2 if (x == L or y == L) else 3 for x in range(8)] for y in range(8)]
bc[L][L] = 0; bc[L + 1][L + 1] = 2                      # 모서리 한 점 둥글게

# «2» — 게임 «1P» 의 «1»(0x03B: 잉크 1 은 3~5칸 1~6줄, 둘레 8방향 테 2, 나머지 3)과 같은 자리·칠
TWO = ["........",
       "...##...",
       "..#..#..",
       ".....#..",
       "....#...",
       "...#....",
       "..####..",
       "........"]
two = [[3] * 8 for _ in range(8)]
for y in range(8):
    for x in range(8):
        if TWO[y][x] == '#': two[y][x] = 1
for y in range(8):
    for x in range(8):
        if two[y][x] == 3 and any(0 <= y + dy < 8 and 0 <= x + dx < 8 and TWO[y + dy][x + dx] == '#'
                                  for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
            two[y][x] = 2

# ── 머리말 쓰기 ──────────────────────────────────────────────────────
def carr(name, flat, per=16):
    s = 'static const uint8_t %s[%d] = {\n' % (name, len(flat))
    for i in range(0, len(flat), per): s += '   ' + ', '.join('0x%02X' % b for b in flat[i:i + per]) + ',\n'
    return s + '};\n'
def tbl(name, rows, w):
    s = 'static const uint8_t %s[%d][%d] = {\n' % (name, len(rows), w)
    for r in rows: s += '   { ' + ', '.join('%d' % v for v in r) + ' },\n'
    return s + '};\n'

h = ['/* practice_glyphs.py 로 만든 연습 대전 글자 타일 — 손으로 고치지 말 것.\n'
     '   한글·라틴 글자 그림은 갈무리7(Galmuri7 2.40.3, Copyright 2019–2025 Lee Minseo, SIL Open Font License 1.1 — 앱 assets/fonts/OFL-Galmuri.md)을\n'
     '   8px 로 그린 것이다. 타일은 NGPC 2bpp(행마다 16비트 LE, 왼쪽 픽셀이 높은 비트). */\n',
     '#pragma once\n#include <stdint.h>\n\n']
h.append('/* 타이틀 메뉴 셋째 줄 «2 인 대전» 의 «2 인» 두 타일(0x1BB·0x1BC) 자리 — «연습»(잉크 1 · 바탕 3) */\n')
h.append(carr('PG_MENU_YEONSEUP', menu_tiles[0] + menu_tiles[1]))
h.append('\n/* 연습 메뉴 창 글자 %d개(번호 1~%d, 0 = 빈칸): %s */\n' % (len(glyph_names), len(glyph_names),
         ' '.join('%d=%s' % (i + 1, n.replace('#0', '(왼)').replace('#1', '(오른)')) for i, n in enumerate(glyph_names))))
h.append('#define PG_N %d\n' % len(glyph_names))
h.append(carr('PG_GLYPH', [b for n in glyph_names for b in enc(tiles[n])]))
h.append('\n/* 커서 «▶»(잉크 1 · 바탕 3) */\n' + carr('PG_CURSOR', enc(cursor)))
h.append('\n/* 창 테두리 — 가로(위; 아래는 세로 뒤집기)·세로(왼쪽; 오른쪽은 가로 뒤집기)·모서리(왼쪽 위; 나머지는 뒤집기). 선 = 색 2 · 창 안 = 색 3 · 바깥 = 색 0(투명) */\n')
h.append(carr('PG_BORDER_H', enc(bh)) + carr('PG_BORDER_V', enc(bv)) + carr('PG_BORDER_C', enc(bc)))
h.append('\n/* HUD «COM» 첫 타일(0x049) 자리에 쓸 «2» — 둘째 타일(0x04A)에는 게임 «1P» 의 «P»(0x03C)를 그대로 베낀다 */\n' + carr('PG_TWO', enc(two)))
h.append('\n/* 메뉴 글줄 — 칸마다 글자 번호(0 = 빈칸).\n   제목 «%s» · 줄: %s */\n' % (TITLE, ' · '.join(
    '%s%s' % (lab, (' [' + ' / '.join(v) + ']') if v else '') for lab, v in ROWS)))
h.append('#define PG_TITLE_W %d\n' % len(title_c))
h.append('static const uint8_t PG_TITLE[%d] = { %s };\n' % (len(title_c), ', '.join(map(str, title_c))))
h.append('#define PG_ROWS %d\n#define PG_LABEL_W %d\n#define PG_VALUE_W %d\n#define PG_NV %d\n' % (len(ROWS), LABEL_W, VALUE_W, NV))
h.append(tbl('PG_LABEL', label_c, LABEL_W))
h.append('static const uint8_t PG_NVAL[%d] = { %s };   /* 줄마다 값 개수(0 = 실행 줄) */\n' % (len(ROWS), ', '.join(map(str, nval))))
s = 'static const uint8_t PG_VALUE[%d][%d][%d] = {\n' % (len(ROWS), NV, VALUE_W)
for vs in value_c:
    vv = vs + [[0] * VALUE_W] * (NV - len(vs))
    s += '   { ' + ', '.join('{ ' + ', '.join(map(str, r)) + ' }' for r in vv) + ' },\n'
h.append(s + '};\n')
open(OUT, 'w').write(''.join(h))

# 가장 많이 쓰는 경우(제목 + 이름 + 값 조합 중 가장 많은 서로 다른 글자) — 빌린 타일 수 어림
import itertools
base = set(title_c) | {g for r in label_c for g in r}
worst = 0
for combo in itertools.product(*[range(n) if n else [None] for n in nval]):
    s = set(base)
    for r, k in enumerate(combo):
        if k is not None: s |= set(value_c[r][k])
    s.discard(0); worst = max(worst, len(s))
print('glyphs %d, worst visible %d (+ cursor 1 + border 3 = %d tiles)' % (len(glyph_names), worst, worst + 4))

if PREVIEW:   # 미리보기: 창 모양(가운데 값들) · 글자 표
    COL = {0: (40, 90, 40), 1: (255, 255, 255), 2: (200, 150, 40), 3: (24, 20, 72)}
    def put(img, pix, X, Y, pal=COL):
        for y in range(8):
            for x in range(8): img.putpixel((X + x, Y + y), pal[pix[y][x]])
    W, H = 14 * 8, 13 * 8 + 8 + ((len(glyph_names) + 13) // 14) * 8
    img = Image.new('RGB', (W, H), (40, 90, 40))
    def flip(p, hf, vf):
        p = [row[::-1] for row in p] if hf else p
        return p[::-1] if vf else p
    for r in range(13):
        for c in range(14):
            if r in (0, 12) and c in (0, 13): t = flip(bc, c == 13, r == 12)
            elif r in (0, 12): t = flip(bh, False, r == 12)
            elif c in (0, 13): t = flip(bv, c == 13, False)
            else: t = [[3] * 8 for _ in range(8)]
            put(img, t, c * 8, r * 8)
    for i, g in enumerate(title_c):
        if g: put(img, tiles[glyph_names[g - 1]], (4 + i) * 8, 1 * 8)
    YEL = dict(COL); YEL[1] = (255, 230, 90)
    for r, (lab, vals) in enumerate(ROWS):
        pal = YEL if r == 0 else COL
        if r == 0: put(img, cursor, 1 * 8, (2 + r) * 8, YEL)
        for i, g in enumerate(label_c[r]):
            if g: put(img, tiles[glyph_names[g - 1]], (2 + i) * 8, (2 + r) * 8, pal)
        if vals:
            k = min(len(vals) - 1, 2 if r == 4 else 1 if r in (1, 3) else 0)
            for i, g in enumerate(value_c[r][k]):
                if g: put(img, tiles[glyph_names[g - 1]], (8 + i) * 8, (2 + r) * 8, pal)
    for i, n in enumerate(glyph_names):
        put(img, tiles[n], (i % 14) * 8, 13 * 8 + 8 + (i // 14) * 8)
    img = img.resize((W * 6, H * 6), Image.NEAREST)
    img.save(PREVIEW)
