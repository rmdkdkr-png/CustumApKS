"""[컬러판 — 시제품 lh.py 에서 look_status 14칸 · look_set_custom/look_edit(검질 인자 없음) · look_triples 만 더함]
look.c 호스트 하네스 — ph.PH 에 look_tick 을 더한다(앱 native.c 에 넣을 순서와 같게:
   retro_run → league_vram(→ look_vram) → league_palremap_fn(→ look_palremap_fn) → league_tick_hub → look_tick(ctx = league_hub_owns_select) → practice_*).
   입력 콜백 = ovr ? mask : (user & ~(league_in_block|practice_in_block|look_in_block)) | league_in_or | practice_in_or | look_in_or"""
import os, sys, ctypes as C
import ph, cx
from ph import PH, gi, BIT
lg = ph.lg
lg.look_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int, C.c_int]
lg.look_blob.argtypes = [C.c_void_p, C.c_size_t]; lg.look_blob.restype = C.c_size_t
lg.look_resume.argtypes = [C.c_void_p, C.c_size_t]
lg.look_set_mem.argtypes = [C.c_char_p, C.c_int]
lg.look_get_mem.argtypes = [C.c_char_p, C.c_int]
lg.look_set_custom.argtypes = [C.c_int] * 5
lg.look_edit.argtypes = [C.c_int] * 4
lg.look_triples.argtypes = [C.c_int, C.c_int, C.c_void_p]
def triples(ch, sty):
    v = (C.c_int * 54)(); lg.look_triples(ch, sty, v); return [tuple(v[i * 3:i * 3 + 3]) for i in range(18)]
NSTAT = 14
def lst():
    v = (C.c_int * NSTAT)(); lg.look_status(v); return list(v)
def mem():
    b = C.create_string_buffer(16); lg.look_get_mem(b, 16); return [x if x < 128 else x - 256 for x in b.raw]
def set_mem(m):
    lg.look_set_mem(bytes((x & 0xFF) for x in m), len(m))
class LH(PH):
    look = True
    def run(self, n=1):
        for _ in range(n):
            on = gi('league_ovr_on')
            blk = gi('league_in_block') | gi('practice_in_block') | gi('look_in_block')
            orr = gi('league_in_or') | gi('practice_in_or') | gi('look_in_or')
            if self.user & BIT['O']: blk |= gi('practice_opt_mask')
            m = gi('league_ovr_mask') if on else ((self.user & ~blk) | orr)
            self.p.mask = m
            self.p.run(1); self.frames += 1
            if self.pre_hook: self.pre_hook(self)
            lg.league_vram(self.chr, self.scr, self.pal); lg.league_palremap_fn(self.prf)
            u = self.user
            lg.league_tick_hub(self.p._ramp, self.p._rams, u)
            if self.look: lg.look_tick(self.p._ramp, self.p._rams, u, lg.league_hub_owns_select())
            lg.practice_vram(self.chr, self.scr, self.pal, self.spr); lg.practice_tick(self.p._ramp, self.p._rams, u)
            ex = lg.practice_take_exit()
            if ex:
                self.p.lib.retro_reset(); lg.league_practice_return(1 if ex == 2 else 0); lg.practice_forget()
            if self.post_hook: self.post_hook(self)
def mk(rom, name, fast=True):
    import hosttest
    hosttest.Harness.__init__.__defaults__ = (not fast,)
    h = LH(rom, os.path.join(cx.W, name))
    L = h.p.lib; L.retro_ngp_spritecol.restype = C.c_void_p; h.col = L.retro_ngp_spritecol()
    return h
# 표(생성기와 같은 값) — 시험은 C 표를 다시 계산하지 않고 colorgen 으로 같은지 본다
import colorgen as G
def tri(ch, sty, idx):
    if ch == 14: B = (0xEEE, 0x666, 0x000); return G.FINAL[idx][1](B, B)
    return G.preset(idx, ch, sty)
VT0 = 0x130
def vp_label(h):
    """세로 칸 18칸이 0x130~ 을 가리키면 그 18타일 그림, 아니면 None"""
    for i in range(18):
        if (h.ent(1, 3 + i // 2, 17 + (i & 1)) & 0x1FF) != VT0 + i: return None
    return b''.join(h.tile(VT0 + i) for i in range(18))
