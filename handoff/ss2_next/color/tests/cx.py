"""color experiments helpers"""
import os, ctypes as C, ph
from ph import PH, pst, hub
W = os.environ['LEAGUE_WORK']
def mk(rom, name, fast=True):
    import hosttest
    hosttest.Harness.__init__.__defaults__ = (not fast,)
    h = PH(rom, os.path.join(W, name))
    L = h.p.lib
    L.retro_ngp_spritecol.restype = C.c_void_p
    h.col = L.retro_ngp_spritecol()
    return h
def pal(h, k):
    b = C.string_at(h.pal + k * 8, 8); return tuple(b[2 * j] | (b[2 * j + 1] << 8) for j in range(4))
def pals(h, base=0, n=16):
    return [pal(h, base + k) for k in range(n)]
def spr_usage(h):
    """visible sprites → {palette: count}, and per-palette tile set"""
    s = C.string_at(h.spr, 256); c = C.string_at(h.col, 64)
    use = {}
    for i in range(64):
        b0, b1, x, y = s[4*i:4*i+4]
        pr = (b1 >> 3) & 3
        if pr == 0: continue
        p = c[i] & 15
        use[p] = use.get(p, 0) + 1
    return use
def scr_pal_usage(h, plane):
    s = C.string_at(h.scr + plane * 0x800, 0x800); u = {}
    for i in range(1024):
        v = s[2*i] | (s[2*i+1] << 8); p = (v >> 9) & 15; t = v & 0x1FF
        if t: u[p] = u.get(p, 0) + 1
    return u
def hx(t): return '/'.join('%03x' % c for c in t)
def pick_and_fight(h, ch, sty=0, limit=4000, csel_btn='A'):
    """from char select (cursor anywhere): move to ch, pick, style (A=수라: cursor default? use L/R), skip cards/story → first round controllable"""
    p = h.p
    cur = p.peek(0x4E3C) >> 2
    for m in ph.move_seq(cur, ch): h.press(m, 4, 20)
    h.run(10); h.press(csel_btn, 4, 100)
    # style select SCR 4: default cursor? choose by L/R then A
    if sty: h.press('R', 4, 20)
    h.press('A', 4, 0)
    f = 0
    while f < limit:
        if p.peek(0x40A7) == 241 and p.peek(0x411A) == 1: break
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and f % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); f += 8; continue
        if f % 40 == 20 and not (p.peek(0x40A7) == 241): h.press('A', 4, 0); f += 4; continue
        h.run(1); f += 1
    return f
import ctypes as _C
def set_remap(h, palidx, frm, to, slot=0):
    """core retro_ngp_palremap for palette palidx colors 1..3 (frm/to = 3-tuples) + immediate write if currently frm"""
    f = h.p.lib.retro_ngp_palremap
    for j in range(3): f(palidx * 4 + 1 + j, slot, frm[j], to[j])
    cur = pal(h, palidx)[1:]
    if tuple(cur) == tuple(frm): wr_pal(h, palidx, to)
def clr_remap(h): h.p.lib.retro_ngp_palremap(-1, 0, 0, 0)
def wr_pal(h, k, c3):
    b = bytearray(_C.string_at(h.pal + k * 8, 8))
    for j in range(3): b[2 + 2*j] = c3[j] & 0xFF; b[3 + 2*j] = c3[j] >> 8
    _C.memmove(h.pal + k * 8, bytes(b), 8)
def fb_img(h):
    from PIL import Image
    p = h.p; im = Image.new('RGB', (160, 152)); px = im.load()
    for y in range(152):
        for x in range(160):
            v = p.fb[(y*160+x)*2] | (p.fb[(y*160+x)*2+1] << 8)
            px[x, y] = (((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31)
    return im
def sheet(imgs, cols, scale=2, labels=None):
    from PIL import Image, ImageDraw
    w, hh = imgs[0].size; rows = (len(imgs) + cols - 1) // cols
    out = Image.new('RGB', (cols * w * scale, rows * hh * scale), (40, 40, 40))
    for i, im in enumerate(imgs):
        out.paste(im.resize((w*scale, hh*scale), Image.NEAREST), ((i % cols) * w * scale, (i // cols) * hh * scale))
    return out
