# -*- coding: utf-8 -*-
"""157 리그 인게임 메뉴 — 최종 기획 목업 (결판 띠 + 칼집 + 서랍).

우리 자산만 쓴다:
  - 갈무리11 regular/bold = 앱 assets/fonts/pixel.ttf, pixel_b.ttf (OFL)
  - 갈무리7 (OFL, handoff/ss2_practice/stage1/fonts — practice_glyphs.h 를 굽는 그 글꼴)
  - 고운바탕 Bold = 앱 assets/fonts/ink_b.ttf (OFL) — 낙관 붓글자만
  - 아래 손으로 찍은 픽셀 그림(테두리·커서·낙관·사슬·왕관·알·깃발·붓 획)
게임 그림은 회색 자리표시 블록(롬·스크린샷·상태 파일 없음).

덧판 규칙(NGPC 와 같음): 8×8 칸, 칸마다 4색 팔레트 하나(0 = 투명), 12비트 0x0BGR 를 니블×17 로 펼침.
렌더러가 규칙을 검사하고(팔레트 없는 칸에 잉크 → 오류), 화면마다 고유 타일(H/V 뒤집기 합침)·팔레트 수를 센다.

Usage: python3 -I mock_final.py <outdir>
"""
import sys, os, random, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FD = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/w149/int/app/src/main/assets/fonts/'
F11 = ImageFont.truetype(FD + 'pixel.ttf', 12)
F11B = ImageFont.truetype(FD + 'pixel_b.ttf', 12)
FINK = ImageFont.truetype(FD + 'ink_b.ttf', 120)
F7 = ImageFont.truetype('/home/user/CustumApKS/handoff/ss2_practice/stage1/fonts/Galmuri7.ttf', 8)

W, H, CW, CH = 160, 152, 20, 19


def rgb(c):  # 12-bit 0x0BGR -> (r, g, b), nibble*17 (코어와 같은 규칙)
    return ((c & 15) * 17, ((c >> 4) & 15) * 17, ((c >> 8) & 15) * 17)


# ---------------------------------------------------------------- palettes [투명, c1, c2, c3]
PAL = {
    # 먹·금·주홍 (앱 Theme 먹·금을 12비트로)
    'INK':   [None, 0xCEF, 0x789, 0x012],   # 화선지 글자, 흐린 글자, 옻칠 먹
    'INKZ':  [None, 0xCEF, 0x789, 0x123],   # 줄무늬 줄
    'GOLD':  [None, 0x7DF, 0x5BE, 0x012],   # 금 하이라이트, 금, 먹
    'SEL':   [None, 0xFFF, 0x7DF, 0x46E],   # 고른 줄: 흰 글자, 금 단도, 주홍 막대
    'WARN':  [None, 0x46E, 0x789, 0x012],   # 주홍 글자(기권·위험)
    'SEAL':  [None, 0xFFF, 0x46E, 0x113],   # 낙관: 흰 글자, 주홍, 짙은 빨강 테
    'SEALK': [None, 0xBBB, 0x445, 0x111],   # 진 판 낙관: 잿빛 글자, 먹, 검정 테
    'TAIL':  [None, 0x46E, 0x5BE, 0x012],   # 진 판 LP 막대: 붉은 꼬리, 금, 먹
    'CHART': [None, 0x7DF, 0x456, 0x012],   # LP 선, 흐린 점선, 먹
    'FX':    [None, 0xFFF, 0x7DF, 0x5BE],   # 일섬 칼선
    'FLASH': [None, 0xFFF, 0xFFF, 0xFFF],   # 낙관 번쩍(팔레트만 바꿈)
    'PLATE1': [None, 0xFFF, 0x7DF, 0x135],  # 단상 1위(금)
    'PLATEM': [None, 0xFFF, 0x55F, 0x123],  # 단상 2·3위(무쌍: 흰 글자 + 빨강 그림자)
    'CHAIN': [None, 0x46E, 0x789, 0x012],   # 라이벌 사슬
    'CHAINZ': [None, 0x46E, 0x789, 0x123],
    'WOOD':  [None, 0x5BE, 0x247, 0x123],   # 깃대
    'CLOTH': [None, 0x112, 0x678, 0xCEF],   # 흰 깃발
    'CLOTHK': [None, 0xCEF, 0x789, 0x234],  # 먹 깃발
    'CLOTHR': [None, 0xFFF, 0x7DF, 0x46E],  # 주홍 깃발
    'PIP':   [None, 0x7DF, 0x567, 0x012],
    'LPK':   [None, 0xAFF, 0x07F, 0x012],   # 먹 바탕 위 LP 노랑 + 무사 주황   # 최근 알: 금 찬 알 / 흐린 빈 알
    # 게임의 검은 띠 위(바탕 투명 → 게임 검정이 보임) = 게임 HUD 팔레트 값 (156 VS 띠와 같음)
    'B_NAME': [None, 0xFFF, 0x666, 0x000],
    'B_STY':  [None, 0xFFD, 0xE70, 0x000],
    'B_LP':   [None, 0xAFF, 0x07F, 0x000],
    'B_DIM':  [None, 0x888, 0x444, 0x000],
    'B_HINT': [None, 0xCEF, 0x789, 0x000],
    'B_GOLD': [None, 0x7DF, 0x5BE, 0x000],
}
TIER = {  # 먹 바탕 위 티어 색 (RankVs.TIER_STYLE 과 같은 빛깔)
    'T0': (0x888, 0x444), 'T1': (0xBBB, 0x666), 'T2': (0x07F, 0x035), 'T3': (0xFFF, 0x888),
    'T4': (0xAFF, 0x6AA), 'T5': (0xFE7, 0x993), 'T6': (0x22F, 0x118), 'T7': (0xFFF, 0x00E)}
for k, (a, b) in TIER.items():
    PAL[k] = [None, a, b, 0x012]
    PAL[k + 'Z'] = [None, a, b, 0x123]

_mc = {}


def mask(s, font):
    key = (s, id(font))
    if key in _mc:
        return _mc[key]
    im = Image.new('L', (len(s) * 14 + 8, 16), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((0, -1), s, font=font, fill=255)
    bb = im.getbbox()
    wdt = bb[2] if bb else 0
    m = [[1 if im.getpixel((x, y)) > 127 else 0 for x in range(wdt)] for y in range(14)]
    _mc[key] = m
    return m


def tw(s, font=F7):
    m = mask(s, font)
    return len(m[0]) if m and m[0] else 0


# ---------------------------------------------------------------- our small glyphs
MINI3 = {  # 3×5 숫자
    '0': ["111", "101", "101", "101", "111"], '1': ["010", "110", "010", "010", "111"],
    '2': ["111", "001", "111", "100", "111"], '3': ["111", "001", "011", "001", "111"],
    '4': ["101", "101", "111", "001", "001"], '5': ["111", "100", "111", "001", "111"],
    '6': ["111", "100", "111", "101", "111"], '7': ["111", "001", "010", "010", "010"],
    '8': ["111", "101", "111", "101", "111"], '9': ["111", "101", "111", "001", "111"],
    '/': ["001", "001", "010", "100", "100"], '+': ["000", "010", "111", "010", "000"],
    '-': ["000", "000", "111", "000", "000"], ',': ["000", "000", "000", "010", "100"],
}
MINI4 = [  # 4×7 숫자 (RankVs 와 같은 그림)
    [".##.", "#..#", "#..#", "#..#", "#..#", "#..#", ".##."], [".#..", "##..", ".#..", ".#..", ".#..", ".#..", "###."],
    [".##.", "#..#", "...#", "..#.", ".#..", "#...", "####"], [".##.", "#..#", "...#", "..#.", "...#", "#..#", ".##."],
    ["..#.", ".##.", "#.#.", "#.#.", "####", "..#.", "..#."], ["####", "#...", "###.", "...#", "...#", "#..#", ".##."],
    [".##.", "#...", "###.", "#..#", "#..#", "#..#", ".##."], ["####", "...#", "..#.", "..#.", ".#..", ".#..", ".#.."],
    [".##.", "#..#", "#..#", ".##.", "#..#", "#..#", ".##."], [".##.", "#..#", "#..#", ".###", "...#", "...#", ".##."],
]
STAR5 = ["..#..", ".###.", "#####", ".###.", ".#.#."]
KATANA = ["........", "2.......", "22......", "22111111", "22......", "2.......", "........"]
CHAINB = ["........", ".11..11.", "1..11..1", "1..11..1", ".11..11.", "........"]
CROWN = ["1..1..1", "1.121.1", "1122211", "2222222", "2121212"]
PIPW = [".1111.", "111111", "111111", "111111", "111111", ".1111."]
PIPL = [".2222.", "2....2", "2....2", "2....2", "2....2", ".2222."]
TRI_UP = ["..1..", ".111.", "11111"]
TRI_DN = ["11111", ".111.", "..1.."]
ARROW_L = ["...1", "..11", ".111", "1111", ".111", "..11", "...1"]
ARROW_R = [r[::-1] for r in ARROW_L]
CREST = ["...33...", "..3113..", ".311113.", "31122113", "31122113", ".311113.", "..3113..", "...33..."]


# ---------------------------------------------------------------- placeholder game pictures (게임 그림 아님)
def tiny(img, s, x, y, col):
    d = ImageDraw.Draw(img)
    d.fontmode = '1'
    d.text((x, y - 1), s, font=F7, fill=col)


def ph_stage(img, y0, y1):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y0, 159, y1], fill=(60, 66, 80))
    for i, x in enumerate(range(0, 160, 20)):
        d.rectangle([x + 2, y0 + 30 - (i % 3) * 6, x + 16, y0 + 70], fill=(72, 78, 92))
    d.rectangle([0, y0 + 72, 159, y1], fill=(86, 86, 86))
    for x in range(-40, 160, 16):
        d.line([x, y0 + 72, x + 24, y1], fill=(98, 98, 98))


def ph_latch(img, winner_left=True):
    """걸쇠 화면 배치(실측 6/6): 0~31 검정 · 32~135 무대와 두 캐릭터 · 136~151 검정."""
    ph_stage(img, 32, 135)
    d = ImageDraw.Draw(img)
    if winner_left:
        d.rectangle([26, 64, 48, 126], fill=(140, 140, 140))
        d.rectangle([31, 54, 43, 63], fill=(140, 140, 140))
        d.rectangle([104, 112, 140, 126], fill=(112, 112, 112))
        tiny(img, 'P1', 31, 88, (50, 50, 50))
        tiny(img, 'CPU', 110, 116, (50, 50, 50))
    else:
        d.rectangle([26, 64, 48, 126], fill=(128, 128, 128))
        d.rectangle([31, 54, 43, 63], fill=(128, 128, 128))
        d.rectangle([104, 112, 140, 126], fill=(112, 112, 112))
        tiny(img, 'CPU', 27, 88, (50, 50, 50))
        tiny(img, 'P1', 114, 116, (50, 50, 50))


def ph_fight(img):
    ph_stage(img, 0, 151)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 159, 31], fill=(44, 48, 60))
    d.rectangle([4, 4, 70, 9], fill=(150, 150, 150))
    d.rectangle([89, 4, 155, 9], fill=(150, 150, 150))
    d.rectangle([74, 2, 85, 13], fill=(120, 120, 120))
    d.rectangle([4, 13, 40, 17], fill=(110, 110, 110))
    d.rectangle([119, 13, 155, 17], fill=(110, 110, 110))
    tiny(img, 'HUD', 44, 13, (30, 30, 30))
    d.rectangle([40, 86, 62, 140], fill=(140, 140, 140))
    d.rectangle([98, 84, 120, 140], fill=(120, 120, 120))
    tiny(img, 'P1', 45, 104, (50, 50, 50))
    tiny(img, 'CPU', 101, 104, (50, 50, 50))


# ---------------------------------------------------------------- frame = 게임 그림 + 덧판 한 층
class Frame:
    def __init__(self, scene='latch', **kw):
        self.base = Image.new('RGB', (W, H), (0, 0, 0))
        self.idx = [[0] * W for _ in range(H)]
        self.pal = [[None] * CW for _ in range(CH)]
        self.shake = (0, 0)
        if scene == 'latch':
            ph_latch(self.base, kw.get('winner_left', True))
        elif scene == 'fight':
            ph_fight(self.base)
        elif scene == 'fill':
            self.base = Image.new('RGB', (W, H), rgb(0x012))   # 덧판 바탕 처리 «먹 채움»

    def setpal(self, c0, r0, c1, r1, p):
        for r in range(max(0, r0), min(CH, r1 + 1)):
            for c in range(max(0, c0), min(CW, c1 + 1)):
                self.pal[r][c] = p

    def px(self, x, y, i):
        if 0 <= x < W and 0 <= y < H:
            self.idx[y][x] = i

    def fill(self, x0, y0, x1, y1, i):
        for y in range(max(0, y0), min(H, y1 + 1)):
            for x in range(max(0, x0), min(W, x1 + 1)):
                self.idx[y][x] = i

    def text(self, s, x, y, i, font=F7, shadow=None, align='l'):
        """y = 한글 몸통 맨 위(갈무리7 7px, 갈무리11 11px)."""
        m = mask(s, font)
        bw = len(m[0]) if m and m[0] else 0
        if align == 'r':
            x -= bw
        elif align == 'c':
            x -= bw // 2
        if shadow is not None:
            for yy, row in enumerate(m):
                for xx, v in enumerate(row):
                    if v and self.idx[y + yy + 1][min(W - 1, x + xx + 1)] in (0, 3):
                        self.px(x + xx + 1, y + yy + 1, shadow)
        for yy, row in enumerate(m):
            for xx, v in enumerate(row):
                if v:
                    self.px(x + xx, y + yy, i)
        return x + bw

    def art(self, rows, x, y, mp):
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                if ch in mp:
                    self.px(x + xx, y + yy, mp[ch])

    def mini3(self, s, x, y, i, align='l'):
        wdt = sum(4 if c in MINI3 else 2 for c in s) - 1
        if align == 'r':
            x -= wdt
        elif align == 'c':
            x -= wdt // 2
        for c in s:
            g = MINI3.get(c)
            if g is None:
                x += 2
                continue
            self.art([r.replace('1', 'a') for r in g], x, y, {'a': i})
            x += 4
        return x

    def mini4(self, s, x, y, i, sh=None, align='l'):
        def gw(c):
            return 5 if c == '*' else 4
        wdt = sum(gw(c) + 1 for c in s) - 1
        if align == 'r':
            x -= wdt
        for c in s:
            g = STAR5 if c == '*' else MINI4[int(c)]
            oy = y + (1 if c == '*' else 0)
            if sh is not None:
                self.art([r.replace('#', 's') for r in g], x + 1, oy + 1, {'s': sh})
            self.art(g, x, oy, {'#': i})
            x += gw(c) + 1
        return x

    # 바탕 처리(코어 그림은 안 바꾸고 합성 단계에서만)
    def dim(self, y0, y1, k):
        p = self.base.load()
        for y in range(y0, y1 + 1):
            for x in range(W):
                p[x, y] = tuple(((round(v / 17) * k) // 4) * 17 for v in p[x, y])

    def shift_rows(self, y0, y1, dx):
        src = self.base.copy().load()
        p = self.base.load()
        for y in range(y0, y1 + 1):
            for x in range(W):
                sx = x - dx
                p[x, y] = src[sx, y] if 0 <= sx < W else (0, 0, 0)

    def flash_base(self, y0, y1, k):
        p = self.base.load()
        for y in range(y0, y1 + 1):
            for x in range(W):
                p[x, y] = tuple(int(v + (255 - v) * k) for v in p[x, y])

    def shift_cells(self, c0, r0, c1, r1, dc):
        """덧판 층 가로 이동(칸 단위로만 — 실제로는 층 오프셋·줄 표로 1px 단위)."""
        idx = [row[:] for row in self.idx]
        pal = [row[:] for row in self.pal]
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                self.pal[r][c] = None
            for y in range(r * 8, r * 8 + 8):
                for x in range(c0 * 8, c1 * 8 + 8):
                    self.idx[y][x] = 0
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                nc = c + dc
                if c0 <= nc < CW:
                    self.pal[r][nc] = pal[r][c]
                    for y in range(r * 8, r * 8 + 8):
                        for xx in range(8):
                            self.idx[y][nc * 8 + xx] = idx[y][c * 8 + xx]

    def render(self):
        im = self.base.copy()
        p = im.load()
        for y in range(H):
            for x in range(W):
                i = self.idx[y][x]
                if i:
                    pn = self.pal[y // 8][x // 8]
                    if pn is None:
                        raise SystemExit('ink without palette at %d,%d' % (x, y))
                    p[x, y] = rgb(PAL[pn][i])
        if self.shake != (0, 0):
            sh = Image.new('RGB', (W, H), (0, 0, 0))
            sh.paste(im, self.shake)
            im = sh
        return im

    def stats(self):
        seen, pals, cells = set(), set(), 0
        for r in range(CH):
            for c in range(CW):
                t = tuple(tuple(self.idx[r * 8 + y][c * 8 + x] for x in range(8)) for y in range(8))
                if all(v == 0 for row in t for v in row):
                    continue
                cells += 1
                pals.add(self.pal[r][c])
                hf = tuple(tuple(reversed(row)) for row in t)
                vf = tuple(reversed(t))
                hv = tuple(reversed(hf))
                if not ({t, hf, vf, hv} & seen):
                    seen.add(t)
        assert len(pals) <= 16, 'palettes > 16'
        return {'cells': cells, 'tiles': len(seen), 'palettes': len(pals)}


# ---------------------------------------------------------------- our art pieces
def brush_glyph(ch, size, grow=5, thr=100):
    im = Image.new('L', (170, 170), 0)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), ch, font=FINK)
    d.text(((170 - (bb[2] - bb[0])) // 2 - bb[0], (170 - (bb[3] - bb[1])) // 2 - bb[1]), ch, font=FINK, fill=255)
    if grow >= 3:
        im = im.filter(ImageFilter.MaxFilter(grow))
    bb = im.getbbox()
    side = max(bb[2] - bb[0], bb[3] - bb[1])
    sq = Image.new('L', (side, side), 0)
    sq.paste(im.crop(bb), ((side - (bb[2] - bb[0])) // 2, (side - (bb[3] - bb[1])) // 2))
    sm = sq.resize((size, size), Image.LANCZOS)
    return [[1 if sm.getpixel((x, y)) > thr else 0 for x in range(size)] for y in range(size)]


def seal(fr, x, y, n, ch, pal='SEAL'):
    """n×n 이 빠진 낙관 — 붓글자는 고운바탕 Bold(앱 ink_b.ttf, OFL)를 줄여 1비트로."""
    rnd = random.Random(ord(ch) * 7 + n)
    fr.setpal(x // 8, y // 8, (x + n - 1) // 8, (y + n - 1) // 8, pal)
    fr.fill(x, y, x + n - 1, y + n - 1, 2)
    for k in range(n):
        for (xx, yy) in ((x + k, y + n - 1), (x + n - 1, y + k)):
            fr.px(xx, yy, 3)
    for _ in range(n // 2):
        side = rnd.randint(0, 3)
        k = rnd.randint(1, n - 2)
        fr.px(*((x + k, y), (x + k, y + n - 1), (x, y + k), (x + n - 1, y + k))[side], 0)
    for (cx, cy) in ((x, y), (x + n - 1, y), (x, y + n - 1), (x + n - 1, y + n - 1)):
        fr.px(cx, cy, 0)
    g = brush_glyph(ch, n - 6, grow=5 if ch in '승' else 3)
    for yy, row in enumerate(g):
        for xx, v in enumerate(row):
            if v:
                fr.px(x + 3 + xx, y + 3 + yy, 1)


def seal8(fr, c, r, ch):
    x, y = c * 8, r * 8
    fr.setpal(c, r, c, r, 'SEAL')
    fr.fill(x, y, x + 7, y + 7, 2)
    for (cx, cy) in ((x, y), (x + 7, y), (x, y + 7), (x + 7, y + 7)):
        fr.px(cx, cy, 0)
    m = mask(ch, F7)
    for yy, row in enumerate(m[:7]):
        for xx, v in enumerate(row[:7]):
            if v:
                fr.px(x + xx, y + yy, 1)


def seal16(fr, x, y, ch):
    fr.setpal(x // 8, y // 8, x // 8 + 1, y // 8 + 1, 'SEAL')
    fr.fill(x, y, x + 15, y + 15, 2)
    fr.fill(x + 1, y + 15, x + 15, y + 15, 3)
    fr.fill(x + 15, y + 1, x + 15, y + 15, 3)
    for (cx, cy) in ((x, y), (x + 15, y), (x, y + 15), (x + 15, y + 15), (x + 6, y), (x, y + 9), (x + 15, y + 5), (x + 11, y + 15)):
        fr.px(cx, cy, 0)
    fr.text(ch, x + 2, y + 2, 1, F11B)


def brush_stroke(fr, x0, x1, y, ink, hi=None, seed=3, head=3):
    rnd = random.Random(seed)
    n = x1 - x0
    for i in range(n + 1):
        t = i / max(1, n)
        th = max(1, round(head * (1 - t) ** 0.7 + 0.4))
        for k in range(th):
            if t > 0.6 and rnd.random() < (t - 0.55) * 1.1:
                continue
            fr.px(x0 + i, y - th // 2 + k, ink)
        if hi and th >= 2:
            fr.px(x0 + i, y - th // 2, hi)


def gauge(fr, x0, x1, y, frac, tail_to=None):
    """LP 막대 6px: 금 테, 찬 몫 = 하이라이트 줄 + 금, 빈 몫 = 먹. tail_to = 진 판에 잃은 몫(붉은 꼬리, c1)."""
    for x in range(x0, x1 + 1):
        fr.px(x, y, 2)
        fr.px(x, y + 5, 2)
    for yy in range(y, y + 6):
        fr.px(x0, yy, 2)
        fr.px(x1, yy, 2)
    fx = x0 + 1 + int((x1 - x0 - 1) * frac)
    for x in range(x0 + 1, fx):
        fr.px(x, y + 1, 1 if tail_to is None else 2)
        for yy in (2, 3, 4):
            fr.px(x, y + yy, 2)
    if tail_to is not None:
        tx = x0 + 1 + int((x1 - x0 - 1) * tail_to)
        for x in range(fx, tx):
            for yy in (1, 2, 3, 4):
                fr.px(x, y + yy, 1)


# ---------------------------------------------------------------- 결판 띠 (위 검은 띠 = 156 VS 띠와 같은 칸 배치)
def band_result(fr, win=True, my_tier=('무사', 4, 'T2'), my_lp='1935', opp_tier=('무사', 5, 'T2'), opp_lp='2140',
                score='2 : 1', seal_ch=None, flash=False, names=True, stats=True):
    me_lit, op_lit = (True, False) if win else (False, True)
    if names:
        fr.setpal(0, 0, 1, 1, 'B_NAME' if me_lit else 'B_DIM')
        nw = fr.text('나', 2, 2, 1, F11, shadow=2) - 2
        sx = (2 + nw + 3 + 7) // 8 * 8
        fr.setpal(sx // 8, 0, 7, 1, 'B_STY' if me_lit else 'B_DIM')
        fr.text('수라', sx, 2, 2, F11, shadow=1 if me_lit else None)
        fr.setpal(12, 0, 19, 1, 'B_NAME' if op_lit else 'B_DIM')
        fr.text('ChillBee', 157, 2, 1, F11, shadow=2, align='r')
    if stats:
        # 왼쪽 [티어 ★n][LP] — 64px 안(가운데 낙관 칸 c8~11 비움)
        name, st, _ = my_tier
        fr.setpal(0, 2, 7, 3, 'B_LP' if me_lit else 'B_DIM')
        x = fr.text(name, 2, 18, 2, F11)
        x = fr.mini4('*' + str(st), x + 2, 20, 2)
        fr.mini4(my_lp, (x + 2 + 7) // 8 * 8, 20, 1, sh=2)
        # 오른쪽 [LP][티어 ★n]
        name, st, _ = opp_tier
        fr.setpal(12, 2, 19, 3, 'B_LP' if op_lit else 'B_DIM')
        tw_ = tw(name, F11) + 2 + 10
        tx = 157 - tw_
        x = fr.text(name, tx, 18, 2, F11)
        fr.mini4('*' + str(st), x + 2, 20, 2)
        fr.mini4(opp_lp, (tx // 8) * 8 - 2, 20, 1, sh=2, align='r')
    if seal_ch:
        seal(fr, 68, 0, 24, seal_ch, 'FLASH' if flash else ('SEAL' if win else 'SEALK'))
        fr.setpal(8, 3, 11, 3, 'B_NAME')
        fr.text(score, 80, 25, 1, F7, align='c')


# ---------------------------------------------------------------- 칼집 (명령창, 오른쪽 c11~19 = x88~159)
PX = 80


def sheath(fr, r0, r1):
    """옻칠 칼집 패널: 왼쪽 금 테(코이구치 장식), 위 금 줄."""
    fr.fill(PX + 1, r0 * 8, 159, r1 * 8 + 7, 3)
    fr.setpal(11, r0, 19, r1, 'INK')
    fr.setpal(10, r0, 10, r1, 'GOLD')
    for y in range(r0 * 8, r1 * 8 + 8):
        fr.px(PX + 1, y, 2)
        fr.px(PX + 2, y, 1 if (y // 4) % 4 else 2)
    # 위·아래 금 마개
    fr.fill(PX, r0 * 8, PX + 6, r0 * 8 + 2, 2)
    fr.fill(PX + 1, r0 * 8, PX + 5, r0 * 8, 1)
    fr.fill(PX, r1 * 8 + 5, PX + 6, r1 * 8 + 7, 2)
    for x in range(PX + 1, 160):
        fr.px(x, r0 * 8, 2)


def cmd_row(fr, k, label, sel=False, right=None, warn=False, dim=False, r_top=6):
    r = r_top + 2 * k
    y = r * 8
    if sel:
        fr.setpal(11, r, 19, r + 1, 'SEL')
        fr.fill(88, y + 1, 159, y + 15, 3)
        fr.art(KATANA, 89, y + 4, {'1': 1, '2': 2})
        fr.text(label, 99, y + 3, 1, F11)
        if right:
            if right.isascii():
                fr.mini3(right, 155, y + 6, 1, align='r')
            else:
                fr.text(right, 155, y + 5, 2, align='r')
    else:
        fr.setpal(11, r, 19, r + 1, 'WARN' if warn else 'INK')
        fr.text(label, 99, y + 3, 2 if dim else 1, F11)
        if right:
            if right.isascii():
                fr.mini3(right, 155, y + 6, 1 if warn else 2, align='r')
            else:
                fr.text(right, 155, y + 5, 2, align='r')


def stage_row(fr, r, label):
    fr.setpal(11, r, 11, r, 'GOLD')
    fr.setpal(18, r, 19, r, 'GOLD')
    fr.setpal(12, r, 17, r, 'INK')
    fr.art(ARROW_L, 90, r * 8, {'1': 1})
    fr.art(ARROW_R, 150, r * 8, {'1': 1})
    w = tw('무대 ' + label)
    x = 122 - w // 2
    x = fr.text('무대', x, r * 8, 2)
    fr.text(label, x + 4, r * 8, 1)


def band_bottom(fr, tags, rank, desc, hint):
    """아래 검은 띠: 줄 17 = 꼬리표 도장 + 순위, 줄 18 = 고른 줄 설명 + 버튼 안내."""
    c = 0
    for (ch, txt, pal) in tags:
        seal8(fr, c, 17, ch)
        n = (tw(txt) + 4 + 7) // 8
        fr.setpal(c + 1, 17, c + n, 17, pal)
        fr.text(txt, (c + 1) * 8 + 2, 137, 1)
        c += 1 + n + 1
    if rank:
        txt, delta, up = rank
        x1 = 157
        fr.setpal(12, 17, 19, 17, 'B_GOLD')
        x = fr.mini3(delta, x1, 138, 1, align='r')
        fr.art(TRI_UP if up else TRI_DN, x1 - (len(delta) * 4 - 1) - 7, 138, {'1': 1 if up else 2})
        fr.text(txt, x1 - (len(delta) * 4 - 1) - 10, 137, 2, align='r')
    fr.setpal(0, 18, 10, 18, 'B_DIM')
    fr.text(desc, 2, 145, 1)
    fr.setpal(11, 18, 19, 18, 'B_HINT')
    fr.text(hint, 157, 145, 2, align='r')


def ribbon(fr, r, text, x1=82, sub=None, xoff=0):
    """호명 띠(16px): 주홍 바탕, 오른쪽 사선 끝 — 오른쪽에서 채찍처럼 들어와 24f 머문 뒤 아래 도장으로."""
    y0 = r * 8
    fr.setpal(0, r, (x1 + 7) // 8, r + 1, 'SEAL')
    for y in range(y0 + 1, y0 + 15):
        e = x1 - (y - y0) // 2
        fr.fill(max(0, xoff), y, min(e, 159), y, 2)
    fr.fill(max(0, xoff), y0 + 14, x1 - 7, y0 + 14, 3)
    fr.text(text, xoff + 4, y0 + 3, 1, F11B, shadow=3)


# =========================================================================================================
# P1 결판 (이긴 판)
# =========================================================================================================
def result_win(t='final'):
    fr = Frame('latch', winner_left=True)
    fr.dim(32, 135, 3)
    band_result(fr, win=True, seal_ch='승')
    ribbon(fr, 4, '★4 올라감!', x1=76)
    sheath(fr, 4, 16)
    # 머리: LP 막대 + 지금/다음★ + 변화량
    fr.setpal(11, 4, 19, 5, 'GOLD')
    gauge(fr, 89, 127, 36, (1935 - 1850) / 200)
    fr.mini3('1935/2050', 89, 43, 2)
    fr.text('+95', 156, 36, 1, F11B, align='r')
    cmd_row(fr, 0, '다음 상대', sel=True)
    cmd_row(fr, 1, '재대결', right='2/3')
    cmd_row(fr, 2, '새 캐릭터')
    cmd_row(fr, 3, '순위·전적')
    cmd_row(fr, 4, '그만하기')
    stage_row(fr, 16, '랜덤')
    band_bottom(fr, [('연', '3연승', 'B_HINT'), ('첫', '+30', 'B_HINT')], ('12,483위', '212', True),
                '새 상대와 바로 한 판', 'A 결정 B 그만')
    return fr


# =========================================================================================================
# P1b 결판 (진 판) — 먹 낙관, 붉은 꼬리, 기본 커서 «설욕전»
# =========================================================================================================
def result_loss():
    fr = Frame('latch', winner_left=False)
    fr.dim(32, 135, 3)
    band_result(fr, win=False, my_tier=('무사', 3, 'T2'), my_lp='1802', score='1 : 2', seal_ch='패')
    sheath(fr, 4, 16)
    fr.setpal(11, 4, 19, 5, 'TAIL')
    gauge(fr, 89, 127, 36, (1802 - 1650) / 200, tail_to=(1840 - 1650) / 200)
    fr.mini3('1802/1850', 89, 43, 2)
    fr.text('-38', 156, 36, 1, F11B, align='r')
    cmd_row(fr, 0, '설욕전', sel=True, right='1/3')
    cmd_row(fr, 1, '다음 상대')
    cmd_row(fr, 2, '새 캐릭터')
    cmd_row(fr, 3, '순위·전적')
    cmd_row(fr, 4, '그만하기')
    stage_row(fr, 16, '랜덤')
    band_bottom(fr, [('설', '이기면 +62', 'B_HINT')], ('12,511위', '28', False),
                '같은 상대와 바로 다시', 'A 결정 B 그만')
    return fr


# =========================================================================================================
# P5 그만할까? — 칼집 안 목록만 칼 휘두름으로 바뀜
# =========================================================================================================
def quit_sub():
    fr = Frame('latch', winner_left=True)
    fr.dim(32, 135, 3)
    band_result(fr, win=True, seal_ch='승')
    sheath(fr, 4, 16)
    fr.setpal(11, 4, 19, 5, 'GOLD')
    fr.text('그만할까요?', 90, 36, 1, F11B)
    cmd_row(fr, 0, '타이틀로', sel=True)
    cmd_row(fr, 1, '리그 화면')
    cmd_row(fr, 2, '내 게임')
    cmd_row(fr, 3, '게임 목록')
    cmd_row(fr, 4, '취소', dim=True)
    fr.setpal(11, 16, 19, 16, 'INK')
    fr.text('오늘 4승 1패', 90, 128, 2)
    fr.mini3('+152', 155, 129, 1, align='r')
    band_bottom(fr, [('연', '3연승', 'B_HINT'), ('첫', '+30', 'B_HINT')], ('12,483위', '212', True),
                '리그는 켠 채 · A로 다시', 'A 결정 B 취소')
    return fr


# =========================================================================================================
# P2 쉼 (경기 중 OPTION) — HUD 는 그대로, 무대만 어둡게, 왼쪽 위 판 정보 패
# =========================================================================================================
def info_plate(fr):
    fr.fill(0, 32, 79, 71, 3)
    fr.setpal(0, 4, 9, 5, 'INK')
    fr.text('vs', 4, 36, 2, F7)
    fr.text('ChillBee', 16, 34, 1, F11)
    fr.setpal(0, 6, 9, 6, 'LPK')
    x = fr.text('무사', 4, 49, 2)
    fr.art([r.replace('#', 'a') for r in STAR5], x + 1, 50, {'a': 2})
    x = fr.text('5', x + 7, 49, 2)
    fr.mini3('2140', x + 6, 50, 1)
    seal8(fr, 0, 7, '설')
    fr.setpal(1, 7, 9, 7, 'INK')
    fr.text('나와 4-6 · 설욕전', 10, 57, 1)
    fr.setpal(0, 8, 9, 8, 'INK')
    fr.text('이기면', 4, 65, 2)
    fr.mini3('+31', 31, 66, 1)
    fr.text('지면', 48, 65, 2)
    fr.mini3('-18', 66, 66, 1)
    # 금 아래 줄
    fr.setpal(0, 9, 9, 9, 'GOLD')
    fr.fill(0, 72, 79, 72, 2)
    fr.fill(0, 73, 76, 73, 1)
    for x in range(77, 80):
        fr.px(x, 73, 0)


def pause(confirm=False):
    fr = Frame('fight')
    fr.dim(32, 151, 2)
    info_plate(fr)
    r_end = 16 if confirm else 14
    sheath(fr, 4, r_end)
    fr.setpal(11, 4, 19, 5, 'GOLD')
    fr.text('쉼', 90, 36, 1, F11B)
    fr.text('2라운드 1:0', 156, 38, 2, align='r')
    cmd_row(fr, 0, '이어하기', sel=not confirm)
    cmd_row(fr, 1, '순위·전적')
    cmd_row(fr, 2, '나중에', right='저장')
    cmd_row(fr, 3, '기권', sel=confirm, warn=not confirm, right='-18')
    if confirm:
        fr.setpal(11, 14, 19, 14, 'WARN')
        fr.text('정말 기권할까요?', 90, 113, 1)
        fr.setpal(11, 15, 15, 15, 'SEL')
        fr.fill(88, 120, 127, 127, 3)
        fr.art(KATANA, 89, 121, {'1': 1, '2': 2})
        fr.text('아니오', 100, 121, 1)
        fr.setpal(16, 15, 19, 15, 'INK')
        fr.text('기권', 136, 121, 2)
    # 아래 먹 띠(불투명) — 위 금 줄
    fr.setpal(0, 16, 10, 16, 'GOLD')
    if not confirm:
        fr.setpal(11, 16, 19, 16, 'GOLD')
    fr.fill(0, 135, 87 if confirm else 159, 135, 2)
    fr.fill(0, 136, 159, 151, 3)
    fr.setpal(0, 17, 19, 18, 'INK')
    if confirm:
        fr.text('패배로 기록 · -18 LP · 연승 끊김', 2, 137, 1)
        fr.text('◀▶ 고르기  A 확정  B 취소', 157, 145, 2, align='r')
    else:
        fr.text('멈춘 곳에서 바로 이어서', 2, 137, 1)
        fr.text('오늘 2승 1패', 157, 137, 2, align='r')
        fr.text('A 결정 · B/OPTION 이어하기', 157, 145, 2, align='r')
    return fr


# =========================================================================================================
# 서랍 공통: 머리(낙관 + 제목 + CPU 칩) · 탭 줄
# =========================================================================================================
TABS = [('순위', 1), ('라이벌', 4), ('전적', 8), ('상대', 11), ('최근', 14), ('설정', 17)]


def drawer_head(fr, seal_ch, title, right1, right2, r2pal='INK', cpu=True):
    seal16(fr, 2, 0, seal_ch)
    fr.setpal(2, 0, 7, 1, 'GOLD')
    x = fr.text(title, 21, 2, 1, F11B, shadow=2)
    if cpu:
        cx = (x + 4 + 7) // 8 * 8
        fr.setpal(cx // 8, 0, cx // 8 + 2, 1, 'INK')
        fr.fill(cx, 3, cx + 18, 12, 2)
        fr.text('CPU', cx + 2, 4, 3)
    fr.setpal(11, 0, 19, 0, 'INK')
    fr.text(right1, 157, 0, 2, align='r')
    fr.setpal(11, 1, 19, 1, r2pal)
    fr.text(right2, 157, 8, 1 if r2pal != 'INK' else 2, align='r')


def tab_row(fr, cur):
    r = 2
    for (name, c) in TABS:
        n = (tw(name) + 7) // 8
        if name == cur:
            fr.setpal(c, r, c + n - 1, r, 'SEL')
            fr.fill(c * 8 - 0, 16, (c + n) * 8 - 1, 23, 3)
            fr.fill(c * 8, 23, (c + n) * 8 - 1, 23, 2)
            fr.text(name, c * 8 + (n * 8 - tw(name)) // 2, 16, 1)
        else:
            fr.setpal(c, r, c + n - 1, r, 'INK')
            fr.text(name, c * 8 + (n * 8 - tw(name)) // 2, 16, 2)
    fr.setpal(0, r, 0, r, 'GOLD')
    fr.setpal(19, r, 19, r, 'GOLD')
    fr.art(ARROW_L, 1, 16, {'1': 2})
    fr.art(ARROW_R, 155, 16, {'1': 2})


# =========================================================================================================
# P3 순위표 «내 주변» (+ 위 3명 단상)
# =========================================================================================================
BOARD = [  # rank, icon, nick, tier, star, lp
    ('12,479', '', '목검소년', '무사', 4, 1958),
    ('12,480', '', 'hanabi_77', '무사', 4, 1951),
    ('12,481', 'c', '새벽검객', '무사', 4, 1946),
    ('12,482', '', '밤샘수련', '무사', 4, 1940),
    ('12,483', 'me', '나', '무사', 4, 1935),
    ('12,484', '', '도시낭인53', '무사', 4, 1931),
    ('12,485', 'c', '달빛나코', '무사', 4, 1922),
    ('12,486', '', 'galfordfan', '무사', 4, 1915),
    ('12,487', '', '나코사랑12', '무사', 4, 1907),
]


def board():
    fr = Frame('fill')
    drawer_head(fr, '순', '순위표', '시즌 3', 'AI 검객 40,312')
    tab_row(fr, '순위')
    # 단상 3장 (r3~5): 2위 c0-5 · 1위 c6-13 · 3위 c14-19
    plates = [(0, 5, '2위', 'Sakura77', '1871', 'PLATEM'), (6, 13, '1위', '백야', '1934', 'PLATE1'),
              (14, 19, '3위', '무명검', '1850', 'PLATEM')]
    for (c0, c1, rk, nick, mr, pal) in plates:
        x0, x1 = c0 * 8, c1 * 8 + 7
        fr.setpal(c0, 3, c1, 5, pal)
        fr.fill(x0 + 1, 25, x1 - 1, 46, 3)
        fr.fill(x0 + 1, 25, x1 - 1, 25, 2)
        cx = (x0 + x1 + 1) // 2
        if rk == '1위':
            fr.art(CROWN, x0 + 4, 27, {'1': 1, '2': 2})
            x = fr.text('1위', x0 + 13, 26, 2)
            fr.text('무쌍', x1 - 3, 26, 1, shadow=None, align='r')
        else:
            fr.text(rk, x0 + 3, 26, 2)
            fr.text('무쌍', x1 - 3, 26, 1, align='r')
        fr.text(nick, cx, 33, 1, align='c')
        fr.text('MR', cx - 11, 40, 2, align='c')
        fr.mini3(mr, cx - 3, 41, 1)
    # 열 머리 (r6)
    fr.setpal(0, 6, 19, 6, 'INK')
    fr.text('순위', 6, 49, 2)
    fr.text('이름', 42, 49, 2)
    fr.text('티어', 100, 49, 2)
    fr.text('LP', 155, 49, 2, align='r')
    for x in range(2, 158):
        if x % 2 == 0:
            fr.px(x, 56 + 0, 0)
    # 목록 (r7~15) — 내 줄은 가운데(r11)에 고정
    for k, (rk, icon, nick, tn, st, lp) in enumerate(BOARD):
        r = 7 + k
        y = r * 8
        me = icon == 'me'
        z = (k % 2 == 1)
        if me:
            fr.setpal(0, r, 19, r, 'SEL')
            fr.fill(0, y, 159, y + 7, 3)
            fr.mini3(rk, 29, y + 1, 1, align='r')
            fr.art(KATANA, 32, y, {'1': 1, '2': 2})
            fr.text(nick, 42, y, 1)
            x = fr.text(tn, 100, y, 1)
            fr.art([r_.replace('#', 'a') for r_ in STAR5], x + 1, y + 1, {'a': 2})
            fr.text(str(st), x + 7, y, 1)
            fr.mini3(str(lp), 155, y + 1, 1, align='r')
            continue
        base = 'INKZ' if z else 'INK'
        fr.setpal(0, r, 11, r, base)
        fr.setpal(16, r, 19, r, base)
        if z:
            fr.fill(0, y, 159, y + 7, 3)
        fr.mini3(rk, 29, y + 1, 2, align='r')
        if icon == 'c':
            fr.setpal(4, r, 4, r, 'CHAINZ' if z else 'CHAIN')
            fr.art(CHAINB, 32, y + 1, {'1': 1})
        fr.text(nick, 42, y, 1)
        fr.setpal(12, r, 15, r, 'T2Z' if z else 'T2')
        x = fr.text(tn, 100, y, 1)
        fr.art([r_.replace('#', 'a') for r_ in STAR5], x + 1, y + 1, {'a': 1})
        fr.text(str(st), x + 7, y, 1)
        fr.mini3(str(lp), 155, y + 1, 1, align='r')
    # 붓 획 (r16) · 요약 (r17) · 안내 (r18)
    fr.setpal(0, 16, 19, 16, 'GOLD')
    brush_stroke(fr, 4, 155, 131, 2, hi=1, seed=11)
    fr.setpal(0, 17, 19, 17, 'INK')
    x = fr.text('전국 12,483위', 2, 137, 1)
    x = fr.text('/ 40,312 · 상위 31%', x + 3, 137, 2)
    fr.setpal(16, 17, 19, 17, 'GOLD')
    fr.art(TRI_UP, 137, 139, {'1': 1})
    fr.mini3('212', 155, 138, 1, align='r')
    fr.setpal(0, 18, 19, 18, 'INK')
    fr.text('▲▼ 넘기기  A 프로필  ◀▶ 탭  B 뒤로', 80, 145, 2, align='c')
    return fr


# =========================================================================================================
# P4 전적 «요약» — 노보리 깃발 셋 + 최근 10 + LP 흐름(★ 경계 점선)
# =========================================================================================================
def banner(fr, c, r0, r1, cloth, label, num, small):
    x0 = (c + 1) * 8
    x1 = x0 + 31
    fr.setpal(c, r0, c, r1, 'WOOD')
    fr.fill(c * 8 + 5, r0 * 8 + 2, c * 8 + 6, r1 * 8 + 7, 2)
    fr.fill(c * 8 + 5, r0 * 8 + 2, c * 8 + 5, r1 * 8 + 7, 1)
    fr.fill(c * 8 + 4, r0 * 8, c * 8 + 7, r0 * 8 + 1, 1)
    fr.fill(c * 8 + 7, r0 * 8 + 3, c * 8 + 7, r0 * 8 + 3, 1)
    fr.setpal(c + 1, r0, c + 4, r1, cloth)
    yb = r1 * 8 + 7
    fr.fill(x0, r0 * 8 + 1, x1, yb, 3)
    fr.fill(x0, r0 * 8 + 1, x1, r0 * 8 + 2, 2)
    for x in range(x0, x1 + 1):
        d = abs((x - x0) - 15.5)
        cut = int(6 - d / 2.6)
        for y in range(yb - max(0, cut), yb + 1):
            fr.px(x, y, 0)
    cx = (x0 + x1) // 2 + 1
    fr.text(label, cx, r0 * 8 + 5, 1, F7, align='c')
    fr.text(num, cx, r0 * 8 + 15, 1, F11B, align='c')
    fr.text(small, cx, r0 * 8 + 29, 2, F7, align='c')


def record():
    fr = Frame('fill')
    drawer_head(fr, '전', '전적', '시즌 3 · 41전', '무사★4 · 1935', r2pal='T2', cpu=False)
    tab_row(fr, '전적')
    banner(fr, 1, 3, 7, 'CLOTH', '승', '25', '61%')
    banner(fr, 7, 3, 7, 'CLOTHK', '패', '15', '1무')
    banner(fr, 13, 3, 7, 'CLOTHR', '연승', '3', '최고 7')
    # 최근 10 (r8)
    fr.setpal(0, 8, 3, 8, 'INK')
    fr.text('최근 10', 2, 65, 2)
    fr.setpal(4, 8, 15, 8, 'PIP')
    res = 'WWLWWWLLWW'
    for k, ch in enumerate(res):
        fr.art(PIPW if ch == 'W' else PIPL, 34 + k * 9, 65, {'1': 1, '2': 2})
    fr.setpal(16, 8, 19, 8, 'GOLD')
    fr.text('7-3', 157, 65, 1, align='r')
    # 오늘 (r9)
    fr.setpal(0, 9, 19, 9, 'INK')
    x = fr.text('오늘 4승 1패', 2, 73, 1)
    x = fr.text('· +152 LP · 첫 승 받음', x + 3, 73, 2)
    # LP 흐름 (r10~15) — 금 선, ★ 경계 점선, 오른쪽 눈금
    fr.setpal(0, 10, 19, 10, 'INK')
    fr.text('LP 흐름 · 최근 20판', 2, 82, 2)
    fr.setpal(0, 11, 19, 15, 'CHART')
    lo, hi, ytop, ybot = 1630, 1960, 92, 124
    def yv(v):
        return ybot - int((v - lo) * (ybot - ytop) / (hi - lo))
    for th, lab in ((1850, '★4'), (1650, '★3')):
        y = yv(th)
        for x in range(4, 126, 3):
            fr.px(x, y, 2)
        fr.text(lab, 126, y - 3, 2)
        fr.mini3(str(th), 157, y - 2, 2, align='r')
    pts = [1655, 1690, 1668, 1702, 1735, 1712, 1690, 1722, 1751, 1780, 1756, 1771, 1802, 1786, 1812, 1840, 1818, 1802, 1840, 1935]
    prev = None
    for k, v in enumerate(pts):
        x = 6 + k * 6
        y = yv(v)
        if prev:
            px_, py_ = prev
            n = max(abs(x - px_), abs(y - py_))
            for i in range(n + 1):
                fr.px(px_ + (x - px_) * i // n, py_ + (y - py_) * i // n, 1)
        prev = (x, y)
    fr.fill(prev[0] - 1, prev[1] - 1, prev[0] + 1, prev[1] + 1, 1)
    fr.mini3('1935', prev[0] + 4, prev[1] - 2, 1)
    # 통산·최고 (r16) · 라이벌 (r17) · 안내 (r18)
    fr.setpal(0, 16, 19, 16, 'INK')
    fr.text('통산 203승 188패 · 최고 검호★1', 2, 129, 2)
    fr.setpal(0, 17, 0, 17, 'CHAIN')
    fr.art(CHAINB, 1, 138, {'1': 1})
    fr.setpal(1, 17, 19, 17, 'INK')
    x = fr.text('라이벌 ChillBee 4-6', 11, 137, 1)
    fr.text('· 설욕 대기', x + 3, 137, 2)
    fr.setpal(0, 18, 19, 18, 'INK')
    fr.text('◀▶ 탭  ▲ 시즌/통산  A 경기  B 뒤로', 80, 145, 2, align='c')
    return fr


# =========================================================================================================
# P6 스토리보드 — 결판 여는 순간 (60Hz 프레임)
# =========================================================================================================
def sb_frames():
    out = []
    f = Frame('latch')
    out.append(('① 0f 걸쇠 — 멈춘 승리 포즈', f))
    # 일섬 (사건 판만: ★·승급·설욕, 또는 설정 «길게»)
    f = Frame('latch')
    f.dim(32, 135, 3)
    f.shift_rows(32, 83, -4)
    f.shift_rows(84, 135, 4)
    f.flash_base(32, 135, 0.5)
    f.setpal(0, 10, 19, 10, 'FX')
    f.fill(0, 83, 159, 83, 2)
    f.fill(0, 84, 159, 84, 1)
    f.fill(0, 85, 159, 85, 3)
    out.append(('② 일섬 0–12f — ★·승급·설욕 판만', f))
    # 낙관 쾅
    f = Frame('latch')
    f.dim(32, 135, 3)
    band_result(f, win=True, seal_ch='승', flash=True, stats=False)
    f.shake = (0, 2)
    out.append(('③ 낙관 쾅 4f — 흰 번쩍·흔들 2px', f))
    # 칼집이 들어옴 (줄 오프셋 감속: 72→…→0)
    f = result_win()
    for r in range(4, 17):
        for c in range(0, 10):
            f.pal[r][c] = None
        for y in range(r * 8, r * 8 + 8):
            for x in range(0, 80):
                f.idx[y][x] = 0
    f.shift_cells(10, 4, 19, 16, 5)
    for c in range(0, 6):
        for r in range(17, 19):
            pass
    out.append(('④ 칼집 6–16f — 감속하며 들어옴', f))
    # LP 차오름 + 호명 띠
    f = result_win()
    for y in range(36, 48):
        for x in range(88, 160):
            f.idx[y][x] = 3
    gauge(f, 89, 127, 36, 1.0)
    f.mini3('1850/1850', 89, 43, 2)
    f.text('+10', 156, 36, 1, F11B, align='r')
    out.append(('⑤ LP 10–30f — ★ 문턱에서 번쩍', f))
    f = result_win()
    out.append(('⑥ 36f 끝 — 약 0.6초, 입력 대기', f))
    # 다음 상대 → 칼집 닫히듯 띠가 닫힘
    f = Frame('latch')
    band_result(f, win=True, seal_ch='승')
    f.setpal(0, 4, 19, 16, 'INK')
    f.fill(0, 32, 159, 75, 3)
    f.fill(0, 92, 159, 135, 3)
    f.setpal(0, 9, 19, 9, 'GOLD')
    f.fill(0, 75, 159, 75, 2)
    f.setpal(0, 11, 19, 11, 'GOLD')
    f.fill(0, 92, 159, 92, 2)
    f.setpal(4, 10, 15, 10, 'INK')
    f.text('상대 찾는 중 …', 80, 80, 1, align='c')
    out.append(('⑦ 다음 상대 — 띠가 칼집 닫히듯 6f', f))
    return out


# =========================================================================================================
def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def label_img(text, w, h=18):
    im = Image.new('RGB', (w, h), (16, 14, 12))
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((4, 2), text, font=F11, fill=(0xEF, 0xE4, 0xC9))
    return im


SW = [
    ('창 · 칼집 (먹·금·주홍)', [('먹', 0x012), ('먹 줄무늬', 0x123), ('화선지 글자', 0xCEF), ('흐린 글자', 0x789),
                          ('금', 0x5BE), ('금 빛', 0x7DF), ('주홍', 0x46E), ('짙은 빨강', 0x113)]),
    ('결판 띠 (게임 HUD 팔레트 값 = VS 띠)', [('검정', 0x000), ('흰', 0xFFF), ('회', 0x666), ('주황', 0x07F),
                          ('연노랑', 0xAFF), ('파랑', 0xE70), ('흐림', 0x888), ('흐림 그림자', 0x444)]),
    ('티어 (RankVs.TIER_STYLE)', [('수련생', 0x888), ('낭인', 0xBBB), ('무사', 0x07F), ('검객', 0xFFF),
                          ('검호', 0xAFF), ('달인', 0xFE7), ('검성', 0x22F), ('무쌍', 0x00E)]),
    ('특수', [('진 판 낙관', 0x445), ('잿빛', 0xBBB), ('LP 선', 0x7DF), ('점선', 0x456),
              ('흰 깃발', 0xCEF), ('먹 깃발', 0x234), ('깃대', 0x247), ('번쩍', 0xFFF)]),
]


def swatch(path):
    cw, ch, lab = 74, 22, 18
    im = Image.new("RGB", (12 + 8 * cw, 14 + len(SW) * (lab + ch + 24)), (16, 14, 12))
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    y = 8
    for title, chips in SW:
        d.text((8, y), title, font=F11, fill=(0xEF, 0xE4, 0xC9))
        y += lab
        for k, (name, c) in enumerate(chips):
            x = 8 + k * cw
            d.rectangle([x, y, x + cw - 6, y + ch], fill=rgb(c), outline=(90, 84, 70))
            d.text((x, y + ch + 3), name, font=F7, fill=(0xCC, 0xC4, 0xB0))
            d.text((x, y + ch + 12), '%03X' % c, font=F7, fill=(0x88, 0x84, 0x78))
        y += ch + 24
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(path)


def main():
    report = {}
    screens = [
        ('p1_result_win', '결판 · 이긴 판', result_win()),
        ('p1b_result_loss', '결판 · 진 판', result_loss()),
        ('p2_pause', '쉼 · 경기 중 OPTION', pause(False)),
        ('p2b_pause_forfeit', '쉼 · 기권 두 번 묻기', pause(True)),
        ('p3_board', '서랍 · 순위표', board()),
        ('p4_record', '서랍 · 전적 요약', record()),
        ('p5_quit', '결판 · 그만할까요?', quit_sub()),
    ]
    imgs = []
    for name, label, fr in screens:
        im = fr.render()
        im.save(os.path.join(OUT, name + '_1x.png'))
        up(im, 4).save(os.path.join(OUT, name + '_4x.png'))
        report[name] = fr.stats()
        imgs.append((label, im))
    # 한눈에 보기 (2배)
    cols = 4
    cw, chh = W * 2 + 12, H * 2 + 30
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw + 12, rows * chh + 12), (16, 14, 12))
    for i, (label, im) in enumerate(imgs):
        x = 12 + (i % cols) * cw
        y = 12 + (i // cols) * chh
        sheet.paste(label_img(label, W * 2), (x, y))
        sheet.paste(up(im, 2), (x, y + 20))
    sheet.save(os.path.join(OUT, 'p0_overview.png'))
    # 스토리보드 (2배)
    fr_list = sb_frames()
    cols = 4
    rows = (len(fr_list) + cols - 1) // cols
    sb = Image.new('RGB', (cols * cw + 12, rows * chh + 12), (16, 14, 12))
    for i, (label, f) in enumerate(fr_list):
        x = 12 + (i % cols) * cw
        y = 12 + (i // cols) * chh
        sb.paste(label_img(label, W * 2), (x, y))
        sb.paste(up(f.render(), 2), (x, y + 20))
    sb.save(os.path.join(OUT, 'p6_storyboard.png'))
    swatch(os.path.join(OUT, 'p7_palette.png'))
    with open(os.path.join(OUT, 'tile_report.json'), 'w') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
