"""모든 모드 컬러(look.c) — 설계 9-나 «실제 판에서 더할 시험» 항목. 실제 코어 · 앱 순서(lh.LH).
내 색(캐릭터마다 · 두 검질 같이) · 안 만든 칸 건너뜀 · OPTION 길게 = 만들기 요청(컬러 안 바뀜) · 만들기 창 동안 입력 전부 막음·미리보기 그 색·끝내면 원래 ·
쿠로코·무작위 칸은 만들기 안 됨 · 겹침 건너뛰기(아수라) · 고르기 화면에서 상태 저장 → 불러오기 · 꺼짐 = 세로 칸 되돌림 · 옛 코어(palremap 없음) INFO.
사용: python3 t_look2.py <ROM 환경변수 이름> [fast]"""
import os, sys, json, ctypes as C
import lh, ph, cx
from lh import lg, lst, mem, set_mem, tri, vp_label, triples
rom_key = sys.argv[1] if len(sys.argv) > 1 else 'ROM_KO'; rom = os.environ[rom_key]
fast = len(sys.argv) > 2 and sys.argv[2] == 'fast'
VL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'look_vlab.json')))
def lab(i): return bytes(VL[i * 288:(i + 1) * 288])
res = []; tag = rom_key.lower()
def ok(c, msg): res.append(bool(c)); print(('PASS ' if c else 'FAIL ') + msg, flush=True)
def info(msg): print('INFO ' + msg, flush=True)
def pal(h, k): return cx.pal(h, k)[1:]
def hx(t): return '/'.join('%03x' % c for c in t)
def clear_custom():
    for ch in range(14):
        for k in range(2): lg.look_set_custom(ch, k, -1, 0, 0)
def to_csel(h):
    ph.to_title(h, row2=False); h.press('A', 4, 200); h.run(4)
def goto(h, ch):
    cur = h.p.peek(0x4E3C) >> 2
    for m in ph.move_seq(cur, ch): h.press(m, 4, 20)
    h.run(4)
def fight_wait(h, limit=5000):
    p = h.p; g = 0
    while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1) and g < limit:
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
        if g % 40 == 20: h.press('A', 4, 0); g += 4; continue
        h.run(1); g += 1
    return g

# ── 1. 내 색 · OPTION 길게 · 만들기 창 ──
h = lh.mk(rom, 'tl2_cus_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 11)                                          # 우쿄
seen = []
for i in range(16): h.press('O', 4, 6); seen.append(lst()[3])
ok(sorted(seen) == list(range(16)) and lst()[3] == 0, '내 색이 없으면 OPTION 16번에 0~15 한 바퀴 — 내 색 1·2 건너뜀 %s' % seen)
CUS1 = (0x0F0, 0x00F, 0xF00)
lg.look_set_custom(11, 0, *CUS1)
m = mem(); m[11] = 15; set_mem(m); h.run(3)
ok(lst()[3] == 15 and pal(h, 0) == tri(11, 0, 15), '기억 «유령»(15) 미리보기 %s' % hx(pal(h, 0)))
h.press('O', 4, 8)
ok(lst()[3] == 16 and pal(h, 0) == CUS1 and vp_label(h) == lab(16) and mem()[11] == 16,
   '내 색 1 을 만들어 두면 OPTION → «내 색 1»(16): 미리보기 %s · 세로 칸 «내 색 1» · 기억 16' % hx(pal(h, 0)))
tr = triples(11, 1)
ok(tr[16] == CUS1 and tr[17] == tri(11, 1, 0) and tr[9] == tri(11, 1, 9), 'look_triples(우쿄, 나찰): 내 색 1 = 두 검질 같이 · 안 만든 내 색 2 = 기본 · 프리셋 = 표')
h.press('O', 4, 8)
ok(lst()[3] == 0 and pal(h, 0) == tri(11, 0, 0), '안 만든 내 색 2 는 건너뛰고 «기본»(0)')
s0 = lst(); m0 = mem()
h.press('O', 45, 10); s1 = lst()
ok(s1[7] == s0[7] + 1 and s1[3] == s0[3] and mem() == m0 and s1[12] == 11,
   'OPTION 길게(45프레임) → 만들기 요청 %d → %d · 컬러 그대로(%d) · 기억 그대로 · 만들 캐릭터 = 우쿄(%d)' % (s0[7], s1[7], s1[3], s1[12]))
h.press('O', 20, 10)
ok(lst()[7] == s1[7] and lst()[3] == 1, '짧게(20프레임) 누르면 요청 없이 다음 컬러(2P색)')
hov = p.peek(0x4E3C); ED = (0x111, 0x2A4, 0x335)
lg.look_edit(1, *ED); h.run(4)
ok(pal(h, 0) == ED and vp_label(h) == lab(16) and lh.gi('look_in_block') == 0xFFF and lst()[10] == 1,
   '만들기 창(look_edit 1): 미리보기 = 만드는 색 %s · 세로 칸 «내 색 1» · 게임 입력 전부 막음(%03x)' % (hx(pal(h, 0)), lh.gi('look_in_block')))
h.press('R', 4, 20); h.press('A', 4, 60); h.press('O', 4, 10); h.press('B', 4, 20)
ok(p.peek(0x4E3C) == hov and p.peek(0x41C0) == 2 and lst()[3] == 1 and pal(h, 0) == ED,
   '창이 열린 동안 → · A · OPTION · B 를 눌러도 커서·화면·컬러 그대로(게임이 못 받음)')
ED2 = (0xFFF, 0x0A0, 0x050)
lg.look_edit(1, *ED2); h.run(3)
ok(pal(h, 0) == ED2, '창에서 색을 바꾸면 미리보기가 바로 그 색 %s' % hx(pal(h, 0)))
lg.look_edit(0, 0, 0, 0)
del h

h = lh.mk(rom, 'tl2_ed2_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
lg.look_set_custom(11, 0, *CUS1)
to_csel(h); goto(h, 11)
lg.look_edit(1, *ED); h.run(4)
lg.look_edit(0, 0, 0, 0); h.run(4)
ok(pal(h, 0) == tri(11, 0, 0) and vp_label(h) == lab(0) and lh.gi('look_in_block') & 0x1 == 0, '창을 닫으면(look_edit 0) 미리보기·세로 칸이 보이는 컬러(«기본»)로, 입력 다시 받음')
m = mem(); m[11] = 16; set_mem(m); h.run(2)
h.press('A', 4, 120); h.press('R', 4, 30); h.run(4)
ok(p.peek(0x41C0) == 4 and lst()[3] == 16 and pal(h, 0) == CUS1, '검질 고르기 나찰에서도 «내 색 1» 은 같은 세 색 %s (두 검질 같이)' % hx(pal(h, 0)))
lg.look_edit(1, *ED); h.run(3)
ok(pal(h, 0) == ED and lst()[12] == 11, '검질 고르기에서도 만들기 창 미리보기 %s' % hx(pal(h, 0)))
lg.look_edit(0, 0, 0, 0); h.run(3)
h.press('A', 4, 0); fight_wait(h); h.run(30)
b1 = p.peek(0x5B51)
ok(b1 >> 4 == 11 and pal(h, 0) == CUS1 and lst()[4] == 16, '경기: 우쿄 %s 의 몸 = 내 색 1 %s (경기 컬러 %d)' % ('나찰' if b1 & 8 else '수라', hx(pal(h, 0)), lst()[4]))
n_base = 0
for k in range(600):
    h.press('R' if (k // 30) % 2 else 'A', 1, 0)
    if pal(h, 0) == tri(11, (b1 >> 3) & 1, 0): n_base += 1
ok(n_base == 0, '내 색 경기 600프레임 동안 원래 색 프레임 %d' % n_base)
del h

# ── 2. 쿠로코·무작위 칸은 만들기 안 됨 ──
h = lh.mk(rom, 'tl2_kur_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 15)
s0 = lst(); h.press('O', 45, 10); s1 = lst()
ok(s1[7] == s0[7] and s1[12] == -1 and s1[1] == 1, '가운데 무작위 칸(쿠로코): OPTION 길게 → 만들기 요청 없음 · 만들 캐릭터 −1')
g = 0
while p.peek(0x41C0) != 4 and g < 600:                          # 무작위 칸 A — 게임이 뽑기 연출 뒤 검질 고르기로(몇 번 눌러야 할 때도)
    if g % 60 == 0: h.press('A', 4, 0); g += 4
    else: h.run(1); g += 1
h.run(4); s2 = lst()
ok(p.peek(0x41C0) == 4 and s2[12] == -1, '무작위로 결정한 검질 고르기: 만들 캐릭터 −1 (기억 칸이 무작위 칸)')
del h

# ── 3. 겹침 건너뛰기 — 아수라(8): 수라 먹빛 ≈ 기본 · 나찰 보라 ≈ 2P색 ──
h = lh.mk(rom, 'tl2_dup_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 8)
m = mem(); m[8] = 3; set_mem(m); h.run(2); h.press('O', 4, 8); a1 = lst()[3]
m = mem(); m[8] = 6; set_mem(m); h.run(2); h.press('O', 4, 8); a2 = lst()[3]
ok(a1 == 4 and a2 == 7, '캐릭터 고르기에선 한 검질만 겹치는 것은 안 건너뜀: 비취 → 보라(%d) · 분홍 → 먹빛(%d)' % (a1, a2))
m = mem(); m[8] = 3; set_mem(m); h.run(2)
h.press('A', 4, 120); h.press('R', 4, 30); h.run(4)
st = lst(); h.press('O', 4, 8); a3 = lst()[3]
ok(p.peek(0x41C0) == 4 and st[8] == 1 and a3 == 5, '검질 고르기 나찰: 비취 → 다홍(%d) — 보라(≈2P색) 건너뜀' % a3)
h.press('L', 4, 30)
m = mem(); m[8] = 6; set_mem(m); h.run(2); h.press('O', 4, 8); a4 = lst()[3]
ok(lst()[8] == 0 and a4 == 8, '검질 고르기 수라: 분홍 → 흰옷(%d) — 먹빛(≈기본) 건너뜀' % a4)
del h

# ── 4. 고르기 화면에서 상태 저장 → 불러오기 ──
h = lh.mk(rom, 'tl2_sv_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 11)
m = mem(); m[11] = 9; set_mem(m); h.run(3)
ok(pal(h, 0) == tri(11, 0, 9) and vp_label(h) == lab(9), '우쿄 «황금» 미리보기·세로 칸')
blob = C.create_string_buffer(64); bn = lg.look_blob(blob, 64)
lg.league_hub_before_save(); lg.look_before_save()
pv = pal(h, 0); vl = vp_label(h)
raw = h.serialize()
ok(pv == tri(11, 0, 0) and vl is None and bn == 16, '저장 직전: 미리보기 = 원래 색 %s · 세로 칸 원래 이름(우리 타일 아님) · .look 16바이트' % hx(pv))
h.run(1)
ok(pal(h, 0) == tri(11, 0, 9) and vp_label(h) == lab(9), '다음 프레임: 다시 «황금»·세로 칸')
del h
h2 = lh.mk(rom, 'tl2_sv2_' + tag, fast)
lg.look_forget(); lg.look_enable(1)
h2.unserialize(raw); lg.look_forget(); lg.look_resume(blob, bn); h2.run(3)
ok(lst()[1] == 1 and pal(h2, 0) == tri(11, 0, 9) and vp_label(h2) == lab(9), '불러온 뒤(native 와 같은 순서 look_forget → look_resume): 바로 «황금»·세로 칸')
lg.look_enable(0); h2.run(2)
ok(vp_label(h2) is None and lh.gi('look_in_block') == 0 and lst()[1] == 0, '꺼짐(look_enable 0): 세로 칸 원래대로 · 막는 입력 없음')
del h2

# ── 5. 옛 코어(palremap 없음) — 프레임 뒤 고쳐 쓰기만 ──
h = lh.mk(rom, 'tl2_old_' + tag, fast); p = h.p
h.prf = None
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 2)
m = mem(); m[2] = 4; set_mem(m); h.run(3)
ok(pal(h, 0) == tri(2, 0, 4), '옛 코어: 고르기 미리보기 «보라» %s (프레임 뒤 고쳐 쓰기)' % hx(pal(h, 0)))
h.press('A', 4, 120); h.press('A', 4, 0); fight_wait(h); h.run(20)
seen = {'base': 0, 'tgt': 0}
def pre(hh):                                                     # retro_run 바로 뒤(틱 전) = 그 프레임에 화면에 그려진 팔레트
    c = pal(hh, 0)
    if c == tri(2, 0, 0): seen['base'] += 1
    if c == tri(2, 0, 4): seen['tgt'] += 1
h.pre_hook = pre
for k in range(1500): h.press('R' if (k // 30) % 2 else 'A', 1, 0)
h.pre_hook = None
ok(seen['tgt'] > 1000, '옛 코어 경기 1500프레임: 화면에 고른 색 %d프레임' % seen['tgt'])
info('옛 코어 경기 1500프레임 동안 화면에 원래 색이 그려진 프레임 %d (palremap 없으면 게임이 팔레트를 다시 쓴 프레임 — 프레임 뒤 고쳐 쓰기만)' % seen['base'])
del h
h = lh.mk(rom, 'tl2_new_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16); clear_custom()
to_csel(h); goto(h, 2)
m = mem(); m[2] = 4; set_mem(m); h.run(3)
h.press('A', 4, 120); h.press('A', 4, 0); fight_wait(h); h.run(20)
seen = {'base': 0, 'tgt': 0}
h.pre_hook = pre
for k in range(1500): h.press('R' if (k // 30) % 2 else 'A', 1, 0)
h.pre_hook = None
ok(seen['base'] == 0 and seen['tgt'] > 1000, '지금 코어(palremap): 같은 1500프레임 화면에 원래 색 %d프레임 · 고른 색 %d프레임' % (seen['base'], seen['tgt']))
print('== %d/%d 통과 (%s)' % (sum(res), len(res), rom_key))
