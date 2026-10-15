"""outfit experiments — shared helpers (scratch only).
Uses ph.PH (real core + app native code). VRAM views:
  chr  = character RAM 0xA000 (512 tiles x 16 B, 2bpp, row = u16 LE, pixel 0 = bits 15..14)
  spr  = sprite VRAM 0x8800 (64 x 4 B: tile lo, flags, x, y)
  col  = sprite palette index table 0x8C00 (64 B, low 4 bits)
  pal  = palette RAM 0x8200 (sprite 16 x 4 x u16, then scroll1, scroll2)
"""
import os, ctypes as C, random, struct, zlib
import ph
from ph import PH
W = os.environ['LEAGUE_WORK']
os.makedirs(W, exist_ok=True)
GRID = ph.GRID
NAMES = ['카즈키', '소게츠', '하오마루', '겐쥬로', '나코루루', '리무루루', '한조', '갈포드', '아수라', '샬럿', '모로즈미', '우쿄', '주베이', '시키', '유가']
EN = ['kazuki', 'sogetsu', 'haohmaru', 'genjuro', 'nakoruru', 'rimururu', 'hanzo', 'galford', 'asura', 'charlotte', 'morozumi', 'ukyo', 'jubei', 'shiki', 'yuga']

def mk(rom, name, runahead=False):
    import hosttest
    hosttest.Harness.__init__.__defaults__ = (runahead,)
    h = PH(rom, os.path.join(W, name))
    L = h.p.lib
    L.retro_ngp_spritecol.restype = C.c_void_p
    h.col = L.retro_ngp_spritecol()
    return h

def pal(h, k):
    b = C.string_at(h.pal + k * 8, 8); return tuple(b[2 * j] | (b[2 * j + 1] << 8) for j in range(4))
def hx(t): return '/'.join('%03x' % c for c in t)

def snap(h):
    """one frame of VRAM: (spr256, col64, chr8192, pal512)"""
    return (C.string_at(h.spr, 256), C.string_at(h.col, 64), C.string_at(h.chr, 8192), C.string_at(h.pal, 512))

def sprites(spr, col):
    """resolve chains -> list of dict(i, tile, hf, vf, pr, pal, x, y) for all 64 (pr 0 = hidden)"""
    out = []; lx = ly = 0
    for i in range(64):
        b0, b1, sx, sy = spr[4*i:4*i+4]
        x, y = sx, sy
        if b1 & 0x04: x = (lx + sx) & 0xFF
        if b1 & 0x02: y = (ly + sy) & 0xFF
        lx, ly = x, y
        out.append(dict(i=i, tile=b0 | ((b1 & 1) << 8), hf=(b1 >> 7) & 1, vf=(b1 >> 6) & 1, pr=(b1 >> 3) & 3,
                        hch=(b1 >> 2) & 1, vch=(b1 >> 1) & 1, pal=col[i] & 15, x=x, y=y))
    return out

def c12(v):
    return ((v & 15) * 17, ((v >> 4) & 15) * 17, ((v >> 8) & 15) * 17)

def tile_px(chr_, t):
    """8x8 list of color indices"""
    rows = []
    for r in range(8):
        v = chr_[t*16 + 2*r] | (chr_[t*16 + 2*r + 1] << 8)
        rows.append([(v >> (14 - 2*c)) & 3 for c in range(8)])
    return rows

def render_sprites(fr, only=None, bg=(40, 40, 40), size=(160, 152), palover=None):
    """render sprites only (no planes). only = set of palettes to draw (None = all). palover: {pal: (c1,c2,c3)} 12-bit"""
    from PIL import Image
    spr, col, chr_, pram = fr
    im = Image.new('RGB', size, bg); px = im.load()
    ss = sprites(spr, col)
    # K2GE: lower index drawn on top within same priority -> draw from 63 down to 0, higher pr later
    order = sorted([s for s in ss if s['pr']], key=lambda s: (s['pr'], -s['i']))
    for s in order:
        if only is not None and s['pal'] not in only: continue
        pt = tile_px(chr_, s['tile'])
        cols = [tuple(pram[s['pal']*8 + 2*j:s['pal']*8 + 2*j + 2]) for j in range(4)]
        cols = [c[0] | (c[1] << 8) for c in cols]
        if palover and s['pal'] in palover: cols = [0] + list(palover[s['pal']])
        for r in range(8):
            for c in range(8):
                v = pt[7 - r if s['vf'] else r][7 - c if s['hf'] else c]
                if not v: continue
                X = (s['x'] + c) & 0xFF; Y = (s['y'] + r) & 0xFF
                if X >= 0xF8: X -= 256
                if Y >= 0xF8: Y -= 256
                if 0 <= X < size[0] and 0 <= Y < size[1]: px[X, Y] = c12(cols[v])
    return im

def fb_img(h):
    from PIL import Image
    p = h.p; im = Image.new('RGB', (160, 152)); px = im.load()
    for y in range(152):
        for x in range(160):
            v = p.fb[(y*160+x)*2] | (p.fb[(y*160+x)*2+1] << 8)
            px[x, y] = (((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31)
    return im

def sheet(imgs, cols, scale=2, labels=None, pad=0):
    from PIL import Image, ImageDraw
    w, hh = imgs[0].size; rows = (len(imgs) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w * scale + pad), rows * (hh * scale + pad)), (20, 20, 20))
    d = ImageDraw.Draw(out)
    for i, im in enumerate(imgs):
        X = (i % cols) * (w * scale + pad); Y = (i // cols) * (hh * scale + pad)
        out.paste(im.resize((w*scale, hh*scale), Image.NEAREST), (X, Y))
        if labels: d.text((X + 2, Y + 2), labels[i], fill=(255, 255, 0))
    return out

def pick_and_fight(h, ch, sty=0, limit=4000):
    """1P mode char select -> first controllable frame of round 1"""
    p = h.p
    cur = p.peek(0x4E3C) >> 2
    for m in ph.move_seq(cur, ch): h.press(m, 4, 20)
    h.run(10); h.press('A', 4, 100)
    if sty: h.press('R', 4, 20)
    else: h.press('L', 4, 20)
    h.press('A', 4, 0)
    f = 0
    while f < limit:
        if p.peek(0x40A7) == 241 and p.peek(0x411A) == 1: break
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and f % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); f += 8; continue
        if f % 40 == 20 and not (p.peek(0x40A7) == 241): h.press('A', 4, 0); f += 4; continue
        h.run(1); f += 1
    return f

def fight_state(rom, ch, sty=0, tag='ko'):
    """make/load a clean 1P fight state for (ch, sty)"""
    path = os.path.join(W, 'fight_%s_%d_%d.st' % (tag, ch, sty))
    h = mk(rom, 'f_%s_%d_%d' % (tag, ch, sty))
    if os.path.exists(path):
        h.p.load(path); return h
    ph.to_title(h, row2=False); h.press('A', 4, 200)
    pick_and_fight(h, ch, sty); h.run(40)
    h.p.save(path)
    return h

def keep_alive(h):
    p = h.p
    p.poke(0x5A46, 128); p.poke(0x5C46, 128)
    p.poke(0x582F, 0xFF); p.poke(0x5830, 0x0F)   # timer high (not inf)

MOVES = [('D,DF,F', 'A'), ('F,D,DF', 'A'), ('D,DB,B', 'A'), ('D,DF,F', 'B'), ('B,DB,D,DF,F', 'A'), ('', 'AB'),
         ('', 'A'), ('', 'B'), ('D', 'A'), ('D', 'B'), ('U', 'A'), ('UF', 'B'), ('F,F', ''), ('B,B', ''), ('F', 'A'), ('B', 'B'),
         ('D,DB,B', 'B'), ('B,DB,D,DF,F', 'B'), ('F,DF,D,DB,B', 'A'), ('F,DF,D,DB,B', 'B'), ('B,F', 'A'), ('D,U', 'A'), ('', 'AB')]

def random_play(h, frames, seed=1, cb=None, alive=True):
    """random moves/specials; cb(h, frame) after each frame"""
    rnd = random.Random(seed)
    f = 0
    while f < frames:
        mv, btn = rnd.choice(MOVES)
        seq = [s for s in mv.split(',') if s]
        for s in seq:
            h.hold(ph.rel(h, s.replace('DF', 'DF').replace('DB', 'DB')) if s else '')
            for _ in range(3):
                h.run(1); f += 1
                if alive: keep_alive(h)
                if cb: cb(h, f)
        if btn:
            h.hold(btn)
            for _ in range(4):
                h.run(1); f += 1
                if alive: keep_alive(h)
                if cb: cb(h, f)
        h.user = 0
        for _ in range(rnd.randint(10, 50)):
            h.run(1); f += 1
            if alive: keep_alive(h)
            if cb: cb(h, f)
    return f

def png(path, im): im.save(path)
