"""모든 모드 컬러(look.c) — 1인 대전·무한 대전(허브 없이) 실제 코어 시험. 사용: python3 t_look.py <ROM 환경변수 이름> [fast]"""
import os, sys, json, ctypes as C
import lh, ph, cx
from lh import lg, lst, mem, set_mem, tri, vp_label
rom_key = sys.argv[1] if len(sys.argv) > 1 else 'ROM_KO'; rom = os.environ[rom_key]
fast = len(sys.argv) > 2 and sys.argv[2] == 'fast'
VL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'look_vlab.json')))
def lab(i): return bytes(VL[i * 288:(i + 1) * 288])
res = []; tag = rom_key.lower()
def ok(c, msg): res.append(c); print(('PASS ' if c else 'FAIL ') + msg)
def pal(h, k): return cx.pal(h, k)[1:]
def hx(t): return '/'.join('%03x' % c for c in t)

# ── 0. 꺼 두면 원래 게임 그대로 ──
h = lh.mk(rom, 'tl_off_' + tag, fast); p = h.p
lg.look_enable(0)
ph.to_title(h, row2=False); h.press('A', 4, 200)
p0 = pal(h, 0); h.press('O', 4, 30); h.press('B', 4, 30)
ok(vp_label(h) is None and pal(h, 0) == p0 and p.peek(0x41C0) == 2 and lst()[0] == 0,
   '꺼짐: 캐릭터 고르기 세로 칸·미리보기 색 그대로, OPTION·B 는 게임 그대로(아무 일 없음) [SCR %d]' % p.peek(0x41C0))
del h

# ── 1. 1인 대전 ──
h = lh.mk(rom, 'tl_1p_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
ph.to_title(h, row2=False)
ok(lst()[4] == -1, '타이틀: 경기 컬러 없음')
h.press('A', 4, 200); h.run(4)
ok(p.peek(0x41C0) == 2 and vp_label(h) == lab(0) and lst()[1] == 1,
   '1인 대전 캐릭터 고르기: 오른쪽 세로 칸 = «기본» (look 이 화면을 쥠 %d)' % lst()[1])
cur = p.peek(0x4E3C) >> 2
h.press('O', 4, 10); s = lst()
ok(s[3] == 1 and mem()[cur] == 1 and pal(h, 0) == tri(cur, 0, 1) and vp_label(h) == lab(1) and p.peek(0x41C0) == 2,
   'OPTION 한 번 → «2P색»: 미리보기 = %s 의 2P색 %s, 세로 칸 «2P색», 기억 칸[%d] = %d, 게임 화면 그대로' % (cur, hx(pal(h, 0)), cur, mem()[cur]))
for i in range(8): h.press('O', 4, 6)
s = lst()
ok(s[3] == 9 and pal(h, 0) == tri(cur, 0, 9) and vp_label(h) == lab(9), 'OPTION 여덟 번 더 → «황금»(9): 미리보기 %s' % hx(pal(h, 0)))
# 다른 캐릭터로 — 그 캐릭터 기억(0)
for m in ph.move_seq(cur, 11): h.press(m, 4, 20)
h.run(4)
ok(lst()[3] == 0 and pal(h, 0) == tri(11, 0, 0) and vp_label(h) == lab(0), '우쿄로 옮김: 우쿄 기억 = 기본 · 미리보기 기본색 · 세로 칸 «기본»')
for m in ph.move_seq(11, cur): h.press(m, 4, 20)
h.run(4)
ok(lst()[3] == 9 and pal(h, 0) == tri(cur, 0, 9), '되돌아옴: %d 의 기억 «황금» 그대로 (미리보기 %s)' % (cur, hx(pal(h, 0))))
for m in ph.move_seq(cur, 11): h.press(m, 4, 20)
h.press('O', 4, 6); h.press('O', 4, 6); h.press('O', 4, 6)   # 우쿄 → 쪽빛(2) → 비취(3)
ok(mem()[11] == 3 and lst()[3] == 3, '우쿄 OPTION 세 번 → «비취»(3) [기억 %d]' % mem()[11])
# B = 2P색으로 결정 — 길게 눌러도 검질 고르기에서 뒤로 안 감
h.press('B', 40, 120); s = lst()
ok(p.peek(0x41C0) == 4 and s[3] == 1 and s[6] == 1 and pal(h, 0) == tri(11, 0, 1) and vp_label(h) == lab(1) and mem()[11] == 3,
   'B(40프레임): 2P색으로 캐릭터 결정 → 검질 고르기, 세로 칸 «2P색», 미리보기 우쿄 2P색, 기억은 «비취» 그대로 [SCR %d · 2P %d]' % (p.peek(0x41C0), s[6]))
h.press('B', 4, 60)
ok(p.peek(0x41C0) == 2 and lst()[3] == 3 and lst()[6] == 0, '검질 고르기에서 B = 게임의 뒤로 → 캐릭터 고르기, 2P색 결정 풀림 → «비취»')
h.press('A', 4, 100)
h.press('R', 4, 20); h.run(4)
st = lst()
ok(p.peek(0x41C0) == 4 and st[8] == 1 and pal(h, 0) == tri(11, 1, 3), '검질 고르기 나찰: 미리보기 = 우쿄 나찰의 «비취» %s (본 검질 %d)' % (hx(pal(h, 0)), st[8]))
h.press('O', 4, 10)
ok(lst()[3] == 4 and pal(h, 0) == tri(11, 1, 4) and vp_label(h) == lab(4), '검질 고르기에서 OPTION → «보라»(4)')
h.press('A', 4, 0)
g = 0; base_seen = 0
while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1) and g < 5000:
    if pal(h, 0) == tri(11, 1, 0): base_seen += 1
    if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
    if g % 40 == 20: h.press('A', 4, 0); g += 4; continue
    h.run(1); g += 1
s = lst()
ok(s[4] == 4 and s[5] == 11 and p.peek(0x5B51) == 0xB8 and pal(h, 0) == tri(11, 1, 4) and vp_label(h) is None,
   '경기: P1 우쿄 나찰(%02x) = «보라» %s · 세로 칸 원래대로 · 경기 컬러 %d' % (p.peek(0x5B51), hx(pal(h, 0)), s[4]))
ok(base_seen == 0, '고르기 → 이야기 → 라운드 소개까지 팔레트 0 에 원래 색이 보인 프레임 %d' % base_seen)
im = cx.fb_img(h); im.save(os.path.join(cx.W, 'tl_%s_fight.png' % tag))
# 경기 내내 원래 색이 새지 않음 (2라운드 + 사이 연출)
n_base = 0; n_tgt = 0
for r in range(2):
    g = 0
    while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0) and g < 3000: h.run(1); g += 1
    for k in range(400):
        h.press('R' if (k // 30) % 2 else 'A', 1, 0)
        c = pal(h, 0)
        if c == tri(11, 1, 0): n_base += 1
        if c == tri(11, 1, 4): n_tgt += 1
    p.poke(0x5C46, 0)
    for k in range(300):
        h.run(1)
        if pal(h, 0) == tri(11, 1, 0): n_base += 1
ok(n_base == 0 and n_tgt > 600, '두 라운드 + 사이 연출: 원래 색 프레임 %d · 고른 색 프레임 %d' % (n_base, n_tgt))
# 상태 저장 옆 blob → 새 판에서 이어 하기
blob = C.create_string_buffer(64); bn = lg.look_blob(blob, 64)
lg.league_hub_before_save(); lg.look_before_save()          # native.c nativeSaveState 와 같은 순서
raw = h.serialize()
ok(bn == 16, '상태 저장 옆 .look 16바이트')
del h
h2 = lh.mk(rom, 'tl_1p2_' + tag, fast); p2 = h2.p
lg.look_forget(); lg.look_enable(1)
h2.unserialize(raw); lg.look_resume(blob, bn); h2.run(3)
ok(lst()[4] == 4 and pal(h2, 0) == tri(11, 1, 4), '불러온 뒤(.look 되돌림): 바로 «보라» %s' % hx(pal(h2, 0)))
lg.look_forget(); lg.look_enable(1)
h2.unserialize(raw); lg.look_resume(None, 0); h2.run(60)
ok(lst()[4] == -1 and pal(h2, 0) == tri(11, 1, 0), '.look 없이 불러오면 원래 색(옛 상태) %s' % hx(pal(h2, 0)))
del h2

# ── 2. 이어하기 화면(SCR 2 인데 고르기 아님)·타이틀로 ──
h = lh.mk(rom, 'tl_cont_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
ph.to_title(h, row2=False); h.press('A', 4, 200)
cur = p.peek(0x4E3C) >> 2
for m in ph.move_seq(cur, 2): h.press(m, 4, 20)
for i in range(13): h.press('O', 4, 6)           # 하오마루 → 그림자(13)
ok(lst()[3] == 13, '하오마루 «그림자»(13)')
f = cx.pick_and_fight(h, 2, 0)
for r in range(4):                               # 질 때까지(포인트 설정이 1 인 세이브도 있어 결판 비트로 본다)
    g = 0
    while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0) and g < 3000: h.run(1); g += 1
    h.run(10); p.poke(0x5A46, 0); h.run(30)
    if p.peek(0x5824) & 0x80: break
g = 0
while not (p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2) and g < 2000: h.run(1); g += 1
h.run(60)
blk = lh.gi('look_in_block')
ok(blk & 8 == 0 and lst()[1] == 0 and vp_label(h) is None and pal(h, 0) == tri(2, 0, 13),
   '이어하기 화면(SCR 2 · 세로 칸 없음): OPTION 을 막지 않음·화면 안 쥠, 쓰러진 P1 도 «그림자» %s' % hx(pal(h, 0)))
h.press('A', 4, 0)
g = 0
while not (p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2 and lst()[1] == 1) and g < 600: h.run(1); g += 1
ok(lst()[1] == 1 and vp_label(h) == lab(13), '이어하기 A → 캐릭터 고르기 다시: 세로 칸 «그림자»(%d프레임)' % g)
lg.league_practice_title()
h.p.lib.retro_reset(); ph.to_title(h, row2=False)
ok(lst()[4] == -1, '리셋 → 타이틀 메뉴: 경기 컬러 잊음(데모·인트로에 안 샘)')
# 데모·인트로(9000프레임) 동안 고르기 화면을 쥐거나 표를 넣지 않음
n_owned = 0
for k in range(3000):
    h.run(1); n_owned += lst()[1]
ok(n_owned == 0, '타이틀에서 3000프레임(인트로·데모): look 이 화면을 쥔 프레임 %d' % n_owned)
del h

# ── 3. 무한 대전 · 무작위 칸 ──
h = lh.mk(rom, 'tl_surv_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
ph.to_title(h, row2=False); h.press('D', 4, 30); h.press('A', 4, 200); h.run(4)
cur = p.peek(0x4E3C) >> 2
ok(p.peek(0x624B) == 1 and vp_label(h) == lab(0), '무한 대전 캐릭터 고르기: 세로 칸 «기본»')
for m in ph.move_seq(cur, 15): h.press(m, 4, 20)
h.run(4); kb = pal(h, 0)
for i in range(9): h.press('O', 4, 6)            # 무작위 칸: 2P 없음 → 기본 → 쪽빛 … 9번 = ?
s = lst(); idx = s[3]
ok(mem()[15] == idx and idx >= 2 and pal(h, 0) == tri(14, 0, idx), '가운데 무작위 칸(쿠로코): 2P색을 건너뛰고 «%s»(%d), 쿠로코 미리보기 %s → %s' % (lh.G.FINAL[idx][0], idx, hx(kb), hx(pal(h, 0))))
h.press('A', 4, 100); h.press('A', 4, 0)
g = 0
while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1) and g < 5000:
    if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
    if g % 40 == 20: h.press('A', 4, 0); g += 4; continue
    h.run(1); g += 1
h.run(20)
b1 = p.peek(0x5B51); ch, sty = b1 >> 4, (b1 >> 3) & 1
ok(p.peek(0x57D5) == ch and pal(h, 0) == tri(ch, sty, idx), '무작위로 뽑힌 P1 %s %s(0x57D5 %d) = «%s» %s' % (ch, sty, p.peek(0x57D5), lh.G.FINAL[idx][0], hx(pal(h, 0))))
cx.fb_img(h).save(os.path.join(cx.W, 'tl_%s_surv.png' % tag))
del h

# ── 4. 미러전(같은 캐릭터·검질) — 2P색을 고르면 P2 는 기본 색 ──
h = lh.mk(rom, 'tl_mir_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
ph.to_title(h, row2=False); h.press('A', 4, 200)
lg.league_arm(4, 0, -1, 0, 0, 0)                 # 첫 상대를 나코루루 수라로(시험용 대진 덮어쓰기)
cur = p.peek(0x4E3C) >> 2
for m in ph.move_seq(cur, 4): h.press(m, 4, 20)
h.press('B', 6, 120); h.press('A', 4, 0)
g = 0
while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1) and g < 5000:
    if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
    if g % 40 == 20: h.press('A', 4, 0); g += 4; continue
    h.run(1); g += 1
h.run(20)
ok(p.peek(0x5B51) == 0x40 and p.peek(0x5D51) == 0x44 and pal(h, 0) == tri(4, 0, 1) and pal(h, 5) == tri(4, 0, 0),
   '미러전 나코루루 수라(P2 블록 %02x): B 2P색 → P1 = 2P색 %s · P2 = 기본 색 %s' % (p.peek(0x5D51), hx(pal(h, 0)), hx(pal(h, 5))))
cx.fb_img(h).save(os.path.join(cx.W, 'tl_%s_mirror.png' % tag))
lg.league_disarm()
print('== %d/%d 통과 (%s)' % (sum(res), len(res), rom_key))
