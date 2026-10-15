"""[컬러판 시험용 사본 — 원본 handoff/ss2_practice/stage1/tests/ph.py 에 look_tick(앱 native.c 순서)·look 입력 비트만 더함.
 기존 시험(t_practice·t_fix1·t_resume·t_dual)을 «컬러가 켜진 채» 한 번 더 돌려 look 이 연습·리그 흐름을 안 건드리는지 본다. 기억 0 = 기본 색]
연습 대전 호스트 하네스 — 앱 native.c 와 같은 순서(입력 콜백: ovr ? mask : (user & ~(league_in_block|practice_in_block)) | league_in_or | practice_in_or,
retro_run 뒤 league_vram → league_tick_hub → practice_vram → practice_tick → 나가기 요청이면 retro_reset + league_practice_return)."""
import os, ctypes as C, hosttest as T
lg = T.lg
lg.league_tick_hub.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.league_vram.argtypes = [C.c_void_p, C.c_void_p, C.c_void_p]
lg.league_palremap_fn.argtypes = [C.c_void_p]
lg.practice_vram.argtypes = [C.c_void_p, C.c_void_p, C.c_void_p, C.c_void_p]
lg.practice_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.practice_state_size.restype = C.c_size_t
lg.practice_state_get.argtypes = [C.c_void_p]; lg.practice_state_set.argtypes = [C.c_void_p]
lg.look_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int, C.c_int]
lg.look_set_mem.argtypes = [C.c_char_p, C.c_int]
lg.look_forget(); lg.look_enable(1); lg.look_set_mem(bytes(16), 16)
print('INFO lookph: 컬러(look) 켠 하네스', flush=True)
def gi(name): return C.c_int.in_dll(lg, name).value
def hub():
    v = (C.c_int * 12)(); lg.league_hub_status(v); return list(v)
def pst():
    v = (C.c_int * 24)(); lg.practice_status(v); return list(v)
U, D, L, R, A, B, O = 'U', 'D', 'L', 'R', 'A', 'B', 'O'
BIT = {'A': 1 << 0, 'O': 1 << 3, 'U': 1 << 4, 'D': 1 << 5, 'L': 1 << 6, 'R': 1 << 7, 'B': 1 << 8}
def bits(s): return sum(BIT[c] for c in s)
class PH(T.Harness):
    def __init__(self, rom, wd):
        super().__init__(rom, wd)
        Lb = self.p.lib
        for f in ('retro_ngp_charram', 'retro_ngp_scrollram', 'retro_ngp_palram', 'retro_ngp_spriteram'): getattr(Lb, f).restype = C.c_void_p
        self.prf = C.cast(Lb.retro_ngp_palremap, C.c_void_p).value if hasattr(Lb, 'retro_ngp_palremap') else None
        self.chr = Lb.retro_ngp_charram(); self.scr = Lb.retro_ngp_scrollram(); self.pal = Lb.retro_ngp_palram(); self.spr = Lb.retro_ngp_spriteram()
        self.rec = None; self.replay = None; self.pre_hook = None; self.post_hook = None; self.frames = 0; self.passive = False
    def run(self, n=1):
        for _ in range(n):
            if self.replay is not None:
                m = self.replay.pop(0)
            else:
                on = gi('league_ovr_on')
                blk = gi('league_in_block') | gi('practice_in_block') | gi('look_in_block'); orr = gi('league_in_or') | gi('practice_in_or') | gi('look_in_or')
                if self.user & BIT['O']: blk |= gi('practice_opt_mask')   # native.c 입력 콜백과 같게(Option 과 같은 프레임의 방향·A·B)
                m = gi('league_ovr_mask') if on else ((self.user & ~blk) | orr)
            self.p.mask = m
            if self.rec is not None: self.rec.append(m)
            self.p.run(1); self.frames += 1
            if self.pre_hook: self.pre_hook(self)
            lg.league_vram(self.chr, self.scr, self.pal); lg.league_palremap_fn(self.prf)
            u = 0 if self.passive else self.user
            lg.league_tick_hub(self.p._ramp, self.p._rams, u)
            lg.look_tick(self.p._ramp, self.p._rams, u, lg.league_hub_owns_select())
            lg.practice_vram(self.chr, self.scr, self.pal, self.spr); lg.practice_tick(self.p._ramp, self.p._rams, u)
            ex = lg.practice_take_exit()
            if ex:
                self.p.lib.retro_reset(); lg.league_practice_return(1 if ex == 2 else 0); lg.practice_forget(); lg.look_forget()
            if self.post_hook: self.post_hook(self)
    def hold(self, s): self.user = bits(s)
    def press(self, s, frames=6, after=0):
        self.user = bits(s); self.run(frames); self.user = 0; self.run(after)
    # 화면 램
    def chr_(self): return C.string_at(self.chr, 8192)
    def scr_(self): return C.string_at(self.scr, 4096)
    def pal_(self): return C.string_at(self.pal, 512)
    def spr_(self): return C.string_at(self.spr, 256)
    def vram(self): return (self.chr_(), self.scr_(), self.spr_(), self.pal_())
    def ent(self, pl, r, c):
        o = self.scr + pl * 0x800 + (r * 32 + c) * 2; b = C.string_at(o, 2); return b[0] | (b[1] << 8)
    def tile(self, t): return C.string_at(self.chr + t * 16, 16)
    def pstate(self):
        n = lg.practice_state_size(); b = C.create_string_buffer(n); lg.practice_state_get(b); return b.raw
    def pstate_set(self, raw):
        b = C.create_string_buffer(raw, len(raw)); lg.practice_state_set(b)
    def serialize(self):
        L = self.p.lib; n = L.retro_serialize_size(); b = C.create_string_buffer(n)
        assert L.retro_serialize(b, n); return b.raw
    def unserialize(self, raw):
        b = C.create_string_buffer(raw, len(raw)); assert self.p.lib.retro_unserialize(b, len(raw))

def to_title(h, row2=True):
    """전원 → 타이틀 메뉴(커서 셋째 줄)"""
    h.run(420); h.press('A', 4, 150)
    if row2: h.press('D', 4, 30); h.press('D', 4, 30)
    h.run(10)
def to_fight(h, opp_moves='', opp_btn='A', stage_presses=0, my_moves='', my_btn='A', style_btn='A', limit=6000):
    """타이틀 셋째 줄에서: 연습 대전 → 상대 고르기(커서 이동 opp_moves, 옵션 stage_presses 번) → opp_btn → 내 캐릭터 → 경기 시작까지. 돌려줌: 검질 고르기부터 연습 시작까지 프레임"""
    p = h.p
    h.press('A', 4, 240); h.run(30)
    for i in range(stage_presses): h.press('O', 4, 20)
    for m in opp_moves: h.press(m, 4, 30)
    h.run(10); h.press(opp_btn, 4, 60)
    for m in my_moves: h.press(m, 4, 30)
    h.run(10); h.press(my_btn, 4, 160); h.press(style_btn, 4, 0)
    f0 = h.frames; f = 0
    while f < limit and not pst()[0]:
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and f % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); f += 8; continue
        h.run(1); f += 1
    return h.frames - f0

GRID = [[3, 13, 8, 10, 2], [7, 4, 15, 5, 6], [12, 1, 9, 0, 11]]
def cell_of(cid):
    for r in range(3):
        for c in range(5):
            if GRID[r][c] == cid: return r, c
def move_seq(cur, target):
    r0, c0 = cell_of(cur); r1, c1 = cell_of(target)
    return ('D' if r1 > r0 else 'U') * abs(r1 - r0) + ('R' if c1 > c0 else 'L') * abs(c1 - c0)
def rel(h, seq):
    """F/B 상대 방향 → 실제(P1 이 보는 쪽)"""
    face_left = h.p.peek(0x4E54) == 1
    F, B_ = ('L', 'R') if face_left else ('R', 'L')
    return seq.replace('F', F).replace('B', B_) if seq else seq
def motion(h, seq, btn, step=3, hold=4):
    for s in seq:
        h.hold(rel(h, s)); h.run(step)
    h.hold(btn); h.run(hold); h.user = 0
