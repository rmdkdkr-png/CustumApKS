"""치트 시제품 시험 — league.c + practice.c + cheat.c 를 실제 코어 옆에서, 앱 native.c 와 같은 순서로
(retro_run → league_tick_hub → practice_tick → cheat_tick). 일반 세션(연습 허브 켬·둘 다)처럼 돌린다.
사용: env.sh 를 읽고 LEAGUE_HOST_SO=<host_cheat.so> python3 t_cheat.py <롬 키 ko|h1|ko101|jp> [묶음]
묶음: cards perm time hp ko rage cpu diff pow yuga prac league save — 없으면 전부"""
import os, sys, glob, shutil, struct, ctypes as C
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cx
from ph import *
lg.cheat_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.cheat_before_save.argtypes = [C.c_void_p]
ROMK = sys.argv[1]; ROM = cx.ROMS[ROMK]
ONLY = set(sys.argv[2:])
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
def info(s): print('INFO ' + s, flush=True)
def cst():
    v = (C.c_int * 16)(); lg.cheat_status(v); return list(v)
CH = dict(cards=0, time=1, hp1=2, hp2=3, rage1=4, rage2=5, cpu=6, diff=7, pow=8, yuga=9)
def cset(**kw):
    for k, v in kw.items(): lg.cheat_set(CH[k], v)

CUR = [None]
def new_h(name, flash_from=None, hub=True):
    if CUR[0] is not None:
        try:
            if not getattr(CUR[0], 'unloaded', False): CUR[0].p.lib.retro_unload_game()
            CUR[0].p.lib.retro_deinit()
        except Exception as e: info('close: %s' % e)
    W = os.path.join(cx.D, 'tc_%s_%s' % (ROMK, name))
    if os.path.isdir(W): shutil.rmtree(W)
    os.makedirs(W)
    if flash_from: shutil.copy(flash_from, W)
    h = PH(ROM, W); h.W = W
    lg.cheat_reset_all(); lg.practice_forget(); lg.league_hub(0, None, None)
    if hub: lg.league_practice_hub(1, 0); lg.league_hub_dual(1)
    h.post_hook = lambda hh: lg.cheat_tick(hh.p._ramp, hh.p._rams, 0 if hh.passive else hh.user)
    CUR[0] = h
    return h
def own(h): return h.p.peek(0x63BA, 120)
def live(h): p = h.p; return p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0
def wait(h, cond, limit):
    for f in range(limit):
        if cond(): return f
        h.run(1)
    return None
def to_menu(h): h.run(420); h.press('A', 4, 150); h.run(10)
def to_char(h, row=0):
    while h.p.peek(0x624B) != row: h.press('D', 4, 20)
    h.press('A', 4, 0); r = wait(h, lambda: h.p.peek(0x41C0) == 2 and h.p.peek(0x5726) == 6, 400); h.run(120); return r
def take_card(h):
    """카드 화면에서 첫 카드 한 장 받고 그만(받기 → 고르기 → 지정 → 받기 … 안받음)"""
    for b in 'AAAA': h.press(b, 4, 60)
    h.press('R', 4, 30); h.press('A', 4, 60)
def pick_and_go(h, moves='', style='A', want_card=True, limit=6000):
    for m in moves: h.press(m, 4, 30)
    h.press('A', 4, 0); wait(h, lambda: h.p.peek(0x41C0) == 4, 400); h.run(60); h.press(style, 4, 0)
    card = wait(h, lambda: h.p.peek(0x41C0) == 6 or (h.p.peek(0x40A7) == 241), 400)
    had = h.p.peek(0x41C0) == 6 and h.p.peek(0x40A7) == 240
    if had:
        h.run(60); h.shot = os.path.join(h.W, 'card.png'); h.p.shot(h.shot)
        if want_card: take_card(h)
        else: h.press('A', 4, 60); h.press('R', 4, 30); h.press('A', 4, 60)   # 안내 글 → A 로 «받기/안받음/뒤로» → 안받음
    f = wait(h, lambda: live(h), limit)
    return had, f
def kill_round(h, who=0x5A46, limit=12000, until=lambda h: False):
    for f in range(limit):
        if live(h): h.p.poke(who, 0)
        h.run(1)
        if until(h): return f
    return None
def unload_flash(h):
    h.p.lib.retro_unload_game(); h.unloaded = True
    fs = glob.glob(os.path.join(h.W, '*.flash'))
    if not fs: return None, None
    vid, blocks = cx.parse_flash(fs[0])
    return fs[0], blocks
def flash_cards(blocks):
    """가장 마지막(주소가 가장 큰) 세이브 칸의 카드 120칸 — 코어가 붙어 있는 칸들을 한 블록으로 합쳐 남기므로 256바이트씩 나눠 본다"""
    slots = []
    for a, d in blocks:
        for o in range(0, len(d) - 0xFF, 0x100):
            if d[o:o + 15] == b'SAMPLE SAVE PRG': slots.append((a + o, d[o:o + 0x100]))
    a, d = max(slots, key=lambda b: b[0])
    return a, d[0x60:0x60 + 120]
def rom_latest_slot_cards():
    r = open(ROM, 'rb').read(); last = None
    for off in range(0x1F0000, 0x200000, 0x100):
        if r[off:off + 15] == b'SAMPLE SAVE PRG': last = r[off:off + 0x100]
    return last[0x60:0x60 + 120]

# ════ C-1 올카드 이번만 — 창 안 8 · 카드 화면 · 떠나면 원래 · 이어하기 화면엔 안 씀 · 게임오버 세이브에 안 남음 ════
if not ONLY or 'cards' in ONLY:
    h = new_h('cards'); p = h.p
    base = rom_latest_slot_cards(); info('세이브(롬 마지막 칸) 카드 합 %d' % sum(base))
    cset(cards=1); to_menu(h)
    ok(sum(own(h)) == sum(base), '타이틀: 램 카드 = 세이브 값(%d)' % sum(own(h)))
    to_char(h); h.run(5)
    ok(own(h) == bytes([8]) * 120 and cst()[3] == 1, '캐릭터 고르기(0x5726=06): 120칸 모두 8 · 창 안')
    had, f = pick_and_go(h)
    ok(had, '카드 화면이 뜸(올카드라 어느 캐릭터든)')
    ok(f is not None and own(h) == base, '카드 화면을 떠난 뒤 원래 값으로 되돌림(합 %d) · 창 밖 %s' % (sum(own(h)), cst()[3] == 0))
    ok(p.peek(0x57DC) != 0xFF and p.peek16(0x57D8) != 0x100 or p.peek16(0x57DA) != 0x100,
       '되돌려도 고른 카드는 싸움에 먹음: 57DC %02X · 57D8 %04X · 57DA %04X' % (p.peek(0x57DC), p.peek16(0x57D8), p.peek16(0x57DA)))
    # 지기 → 이어하기 화면(SCR 2 · 0x5726 0C) 동안 안 씀
    cont = []
    def until_cont(hh):
        if hh.p.peek(0x40A7) == 240 and hh.p.peek(0x41C0) == 2: cont.append(own(hh)); return len(cont) > 120
        return False
    kill_round(h, 0x5A46, 9000, until_cont)
    ok(len(cont) > 0 and all(c == base for c in cont) and p.peek(0x5726) == 0x0C, '이어하기 화면(SCR 2 · 0x5726 %02X): 소유 개수 원래 값 그대로 %d프레임' % (p.peek(0x5726), len(cont)))
    st_cont = h.serialize()
    # (가) 예 → 다시 고르기 → 창 다시
    h.press('A', 4, 0); f = wait(h, lambda: p.peek(0x5726) == 6 and p.peek(0x41C0) == 2, 600); h.run(120)
    ok(f is not None and own(h) == bytes([8]) * 120, '이어하기 «예» → 캐릭터 고르기에서 다시 8')
    had2, f2 = pick_and_go(h, want_card=False)
    ok(had2 and own(h) == base, '이어한 판도 카드 화면(%s) · 떠나면 원래 값(합 %d, 싸움 %s, MODE %d SCR %d sub %02X)' % (had2, sum(own(h)), f2, p.peek(0x40A7), p.peek(0x41C0), p.peek(0x5726)))
    # (나) 기다림 → 게임오버 세이브 → .flash
    h.unserialize(st_cont); lg.cheat_forget()
    wait(h, lambda: p.peek(0x57C6) == 0x03 and p.peek(0x40A7) == 240, 3000); h.run(30)
    fl, blocks = unload_flash(h)
    ok(fl is not None, '게임오버에서 게임이 세이브를 씀(.flash %s)' % (blocks and ['%06X' % a for a, d in blocks]))
    if fl:
        a, fc = flash_cards(blocks)
        ok(fc == base, '세이브 칸 %06X 의 카드 = 원래 값(합 %d, 8 의 개수 %d) — 올카드가 안 남음' % (a, sum(fc), fc.count(8)))

# ════ C-2 카드 모음집 — 들어간 동안 120종/960장, 나오면 원래 ════
if not ONLY or 'cards' in ONLY:
    h = new_h('coll'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1); to_menu(h)
    while p.peek(0x624B) != 3: h.press('D', 4, 20)
    h.press('A', 4, 150); p.shot(os.path.join(h.W, 'coll.png'))
    ok(p.peek(0x57C6) == 0x12 and own(h) == bytes([8]) * 120, '카드 모음집(0x57C6=12): 120칸 8')
    h.press('A', 4, 150); p.shot(os.path.join(h.W, 'coll_view.png'))
    for i in range(4): h.press('B', 4, 60)
    wait(h, lambda: p.peek(0x57C6) == 0x03, 300); h.run(4)
    ok(own(h) == base, '모음집을 나오면 원래 값(합 %d)' % sum(own(h)))
    fl, blocks = unload_flash(h)
    ok(fl is None or flash_cards(blocks)[1] == base, '모음집 드나듦은 세이브를 안 씀(.flash %s)' % ('없음' if fl is None else '있음'))

# ════ C-3 올카드 세이브에 — 게임오버 세이브에 남고, 다시 켜면 «세이브에 들어감» ════
if not ONLY or 'perm' in ONLY:
    h = new_h('perm'); p = h.p
    cset(cards=2); to_menu(h); to_char(h)
    pick_and_go(h, want_card=False)
    ok(own(h) == bytes([8]) * 120, '세이브에: 싸움 중에도 8')
    r = kill_round(h, 0x5A46, 12000, lambda hh: hh.p.peek(0x57C6) == 0x03 and hh.p.peek(0x40A7) == 240)
    info('게임오버까지 %s프레임 · MODE %d SCR %d prog %02X sub %02X res %02X' % (r, p.peek(0x40A7), p.peek(0x41C0), p.peek(0x57C6), p.peek(0x5726), p.peek(0x5824)))
    h.run(30)
    fl, blocks = unload_flash(h)
    ok(fl is not None and flash_cards(blocks)[1] == bytes([8]) * 120, '게임오버 세이브 칸 카드 120칸 모두 8 (.flash %s %s)' % (fl, blocks and [('%06X' % a, d[0x60:0x60+120].count(8)) for a, d in blocks]))
    if fl:
        h2 = new_h('perm2', flash_from=fl); cset(cards=0)
        to_menu(h2); h2.run(5)
        ok(cst()[5] == 1 and own(h2) == bytes([8]) * 120, '다시 켬(치트 끔): 부팅 때 읽은 카드 모두 8 → «세이브에 들어감» 표시 %d' % cst()[5])

# ════ 싸움 상태 하나 만들기(1인 대전 첫 판, 치트 없이) ════
FIGHT = None
def fight_state():
    global FIGHT
    if FIGHT: return FIGHT
    h = new_h('fight'); to_menu(h); to_char(h); pick_and_go(h, want_card=False)
    FIGHT = (h, h.serialize())
    return FIGHT
def fresh_fight(**kw):
    h, st = fight_state(); h.unserialize(st); lg.cheat_reset_all(); lg.cheat_forget(); cset(**kw); return h

# ════ C-4 시간 무한 ════
if not ONLY or 'time' in ONLY:
    h = fresh_fight(time=1, hp1=1, hp2=1); p = h.p
    t0 = p.peek(0x636C); tl = []
    for f in range(4000): h.run(1); tl.append(p.peek16(0x582F))
    p.shot(os.path.join(h.W, 'time_inf.png'))
    ok(p.peek(0x5824) == 0 and all(t == 0xFFFF for t in tl[2:]) and p.peek(0x5812) == 0x80,
       '시간 무한 4000프레임: 라운드 안 끝남 · 타이머 0xFFFF · 0x5812 = 80')
    cset(time=0); h.run(4)
    ok(p.peek(0x5812) == t0, '끄면 이번 경기 시간을 옵션 값으로(0x5812 = %d, 옵션 %d) — 지금 라운드는 ∞ 그대로, 다음 라운드부터' % (p.peek(0x5812), t0))
    h2 = fresh_fight(hp1=1, hp2=1); t = []
    for f in range(4000):
        h.run(1); t.append(p.peek16(0x582F))
        if p.peek(0x5823): break
    if t0 == 0x80: info('옵션 시간이 ∞(%02X) 인 세이브 — 대조(시간 끝) 생략' % t0)
    else: ok(p.peek(0x5823) == 0x84, '대조(치트 없음): 시간 끝(0x5823 = 84) %d프레임' % len(t))

# ════ C-5 내 체력 무한 · C-6/7 한 방 ════
if not ONLY or 'hp' in ONLY:
    h = fresh_fight(hp1=1, diff=5); p = h.p; mn = 128
    def pre(hh): global mn; mn = min(mn, hh.p.peek(0x5A46))
    h.pre_hook = pre
    for f in range(4000):
        h.run(1)
        if p.peek(0x5824): break
    h.pre_hook = None
    ok(p.peek(0x5824) == 0 or p.peek(0x5823) == 0x84, '내 체력 무한 + CPU 최강 4000프레임: KO 없음 · 게임이 깎은 가장 낮은 값 %d · 되돌림 %d번' % (mn, cst()[11]))
    ok(p.peek(0x5A46) == 128 and p.peek(0x5A4A) == 128, '체력·표시 체력 128')
if not ONLY or 'ko' in ONLY:
    for who, key, cause in ((1, 'hp2', 0x88), (0, 'hp1', 0x90)):
        h = fresh_fight(**{key: 2}); p = h.p
        w0 = (p.peek(0x5821), p.peek(0x5822)); f_hit = None
        for f in range(3000):
            if who == 1:                         # P1 이 다가가 벤다
                g = p.peek16(0x4E78) - p.peek16(0x4E38)
                h.user = bits('R') if g > 40 else (bits('A') if f % 40 < 4 else 0)
            else: h.user = 0
            h.run(1)
            if p.peek(0x5823): break
        h.user = 0
        ok(p.peek(0x5823) == cause, '%s 한 방: 첫 대미지에 KO(0x5823 = %02X) %d프레임' % ('상대' if who else '나', p.peek(0x5823), f))
        wait(h, lambda: p.peek(0x5824) != 0, 200)
        r = wait(h, lambda: live(h) or (p.peek(0x5824) & 0x80) != 0, 2000)
        ok(r is not None, '그 뒤 다음 라운드(또는 결판)로 정상 진행 — 승수 %s → %s' % (w0, (p.peek(0x5821), p.peek(0x5822))))

# ════ C-8 분노 MAX ════
if not ONLY or 'rage' in ONLY:
    h = fresh_fight(rage1=1, cpu=1); p = h.p; h.run(10)
    ok(p.peek(0x59CA) & 4 and p.peek(0x5A47) == 0x30 and p.peek16(0x5A48) >= 0x1000, '내 분노 MAX: 0x59CA bit2 · 분노 30 · 타이머 %04X' % p.peek16(0x5A48))
    acts = set(); spent = False; rearm = None
    motion(h, ['B', 'F', 'D'], 'A')
    for f in range(500):
        h.run(1); acts.add(p.peek16(0x4E3E))
        if not p.peek(0x59CA) & 4: spent = True
        elif spent and rearm is None: rearm = f
    ok(spent and rearm is not None, 'MAX 기술(←→↓+A) 뒤 MAX 가 꺼졌다가 다시 켜짐(%s프레임) · ACT %s' % (rearm, ' '.join('%X' % a for a in sorted(acts) if a >= 0x1C0)))
    cset(rage1=0); h.run(30)
    ok(not (p.peek(0x59CA) & 4), '끄면 움직일 수 있을 때 MAX 를 거둠')

# ════ C-9 상대 가만히 ════
if not ONLY or 'cpu' in ONLY:
    h = fresh_fight(cpu=1); p = h.p
    for f in range(2400): h.run(1)
    ok(p.peek(0x5A46) == 128 and not (p.peek(0x5BCB) & 1), '상대 가만히 2400프레임: 내 체력 128 · P2 CPU 비트 꺼짐')
    cset(cpu=0); h.run(2)
    ok(p.peek(0x5BCB) & 1, '끄면 CPU 비트 다시 켬')
    for f in range(2400):
        h.run(1)
        if p.peek(0x5A46) < 128: break
    ok(p.peek(0x5A46) < 128, 'CPU 가 다시 때림(%d프레임)' % f)

# ════ C-10 CPU 세기 · C-11 내 공격력 ════
if not ONLY or 'diff' in ONLY:
    h = fresh_fight(diff=5); p = h.p; lv = set(); OPT_D = p.peek(0x636A)
    for f in range(1200): h.run(1); lv.add(p.peek(0x5CF5))
    ok(p.peek(0x5814) == 10 and p.peek(0x5815) == 15 and p.peek16(0x57E2) == 0x119 and p.peek16(0x57E4) == 0xE6 and max(lv) <= 15 and p.peek(0x636A) == OPT_D,
       'CPU 세기 최강: 5814/5815 = %d/%d · 배율 %04X/%04X · P2 단계 %s · 옵션 0x636A 그대로 %d' % (p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4), sorted(lv), p.peek(0x636A)))
if not ONLY or 'pow' in ONLY:
    res = {}
    for k in (0, 2, 3):
        h = fresh_fight(pow=k, cpu=1); p = h.p; first = None
        for f in range(700):
            g = p.peek16(0x4E78) - p.peek16(0x4E38)
            h.user = bits('R') if g > 40 else (bits('A') if f % 40 < 4 else 0)
            h.run(1)
            if first is None and p.peek(0x5C46) < 128: first = 128 - p.peek(0x5C46)
        h.user = 0; res[k] = (first, p.peek(0x5C46), p.peek16(0x57D8))
    ok(abs(res[2][0] - 2 * res[0][0]) <= 1 and abs(res[3][0] - 3 * res[0][0]) <= 1, '내 공격력: 첫 대미지 보통 %s · 2배 %s · 3배 %s (57D8 %04X/%04X)' % (res[0][0], res[2][0], res[3][0], res[2][2], res[3][2]))
    ok(all(0 <= r[1] <= 128 for r in res.values()), '3배여도 체력이 0 아래로 돌지 않음 %s' % [r[1] for r in res.values()])

# ════ C-12 유가 ════
if not ONLY or 'yuga' in ONLY:
    for sty in (1, 2):
        h = new_h('yuga%d' % sty); p = h.p
        cset(yuga=sty); to_menu(h); to_char(h)
        had, f = pick_and_go(h, moves='D', want_card=False)
        b = p.peek(0x5B51)
        ok(b >> 4 == 14 and ((b >> 3) & 1) == (sty == 2), '가운데 칸 → 유가 %s: P1 블록 %02X' % ('수라' if sty == 1 else '나찰', b))
        x0 = p.peek16(0x59D6); h.press('R', 30, 0); ok(p.peek16(0x59D6) > x0, '유가가 움직임(X %d → %d)' % (x0, p.peek16(0x59D6)))
    h = new_h('yuga_off'); p = h.p; cset(yuga=1); to_menu(h); to_char(h); pick_and_go(h, moves='', want_card=False)
    ok(p.peek(0x5B51) >> 4 == 8, '다른 칸(아수라)은 그대로: P1 블록 %02X' % p.peek(0x5B51))

# ════ C-13 연습 경기에선 경기 치트 안 씀 · 올카드는 먹음 ════
if not ONLY or 'prac' in ONLY:
    h = new_h('prac'); p = h.p
    cset(hp2=2, hp1=2, time=0, cards=1, cpu=0)
    to_menu(h); h.press('D', 4, 30); h.press('D', 4, 30); h.run(10)
    frames = to_fight(h)
    ok(pst()[0] == 1, '연습 경기 시작(%d프레임)' % frames)
    ok(cst()[7] == 3, '치트 상태: 연습 경기라 경기 치트 막힘(이유 3)')
    lg.practice_set(0, 1)   # 더미 CPU
    for f in range(1500):
        g = p.peek16(0x4E78) - p.peek16(0x4E38)
        h.user = bits('R') if g > 40 else (bits('A') if f % 40 < 4 else 0)
        h.run(1)
    h.user = 0
    ok(p.peek(0x5823) == 0 and p.peek(0x5824) == 0, '한 방 KO 를 켜 둬도 연습 경기는 안 끝남(연습 체력 바닥 그대로)')

# ════ C-14 리그 세션(허브 종류 0)에선 아무것도 안 씀 ════
if not ONLY or 'league' in ONLY:
    h = new_h('league', hub=False); p = h.p
    sty = (C.c_byte * 15)(*([0] * 15)); dif = (C.c_byte * 15)(*([1] * 15))
    lg.league_hub(1, sty, dif)
    cset(cards=1, yuga=1)
    to_menu(h)
    lg.league_arm(11, 0, 1, 2, 60, 0)      # 랭크전 무장(카드 없음 플래그 없이)
    to_char(h); h.run(10)
    ok(own(h) == rom_latest_slot_cards() and cst()[7] == 2, '리그 허브·무장 중: 올카드 안 씀(이유 %d)' % cst()[7])
    lg.league_hub(0, None, None); lg.league_disarm()
    lg.cheat_lock(1); cset(cards=1); h.run(10)
    ok(cst()[0] == 1 and cst()[1] == 0, '잠금: cheat_set 을 받지 않음')

# ════ C-15 상태 저장 직전 되돌림 ════
if not ONLY or 'save' in ONLY:
    h = new_h('save'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1); to_menu(h); to_char(h); h.run(5)
    lg.cheat_before_save(p._ramp); raw = h.serialize()
    ok(own(h) == base, 'cheat_before_save: 저장 직전 원래 값(합 %d)' % sum(own(h)))
    h.run(2); ok(own(h) == bytes([8]) * 120, '다음 프레임 다시 8')


# ════ C-16 무한 대전 — 올카드(이번만) + 한 방 KO 로 8연승 → 상 카드 1장이 진짜 개수에 더해지고, 끝 세이브에 8 이 안 남음 ════
def bot(h, f):
    p = h.p
    g = abs(p.peek16(0x4E78) - p.peek16(0x4E38))
    fl = p.peek(0x4E54) == 1
    fw = 'L' if fl else 'R'
    return bits(fw) if g > 40 else (bits('A') if f % 40 < 4 else 0)
if not ONLY or 'surv' in ONLY:
    h = new_h('surv'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1, hp1=1, hp2=2); to_menu(h); to_char(h, row=1)
    had, f = pick_and_go(h, want_card=False)
    ok(p.peek(0x57C6) == 0x0C and had, '무한 대전(0x57C6=0C)도 고르기 창에서 올카드 → 카드 화면')
    p1 = p.peek(0x5B51); idx0 = 8 * (p1 >> 4) + 4 * ((p1 >> 3) & 1)
    streak_max = 0; ff = 0
    while ff < 40000 and p.peek(0x580B) < 9:
        h.user = bot(h, ff) if live(h) else (bits('A') if ff % 30 < 3 else 0)
        h.run(1); ff += 1; streak_max = max(streak_max, p.peek(0x580B))
    h.user = 0
    info('연승 %d (%d프레임) · 램 카드 합 %d (원래 %d)' % (p.peek(0x580B), ff, sum(own(h)), sum(base)))
    got = [i for i in range(120) if own(h)[i] != base[i]]
    ok(streak_max >= 8 and sum(own(h)) == sum(base) + 1 and all(idx0 <= i < idx0 + 4 for i in got), '8연승 상: 진짜 개수에 1장(칸 %s, P1 블록 %02X)' % (got, p1))
    cset(hp1=2)                                    # 이제 져서 끝낸다
    r = wait(h, lambda: p.peek(0x57C6) == 0x03 and p.peek(0x40A7) == 240, 20000)
    h.run(30)
    fl, blocks = unload_flash(h)
    if fl:
        a, fc = flash_cards(blocks)
        ok(sum(fc) == sum(base) + 1 and fc.count(8) <= base.count(8) + 1, '무한 대전 끝 세이브(칸 %06X): 카드 합 %d = 원래+1 · 올카드 안 남음' % (a, sum(fc)))
    else: ok(False, '무한 대전 끝에서 세이브가 안 써짐(%s)' % r)

# ════ C-17 스토리 클리어 — 올카드(이번만) · 장 당기기(0x57FE=8) · 한 방 KO → 엔딩 · 카드 공개 → 세이브에 8 이 안 남음 ════
if not ONLY or 'clear' in ONLY:
    h = new_h('clear'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1, hp1=1, hp2=2); to_menu(h); to_char(h); pick_and_go(h, want_card=False)
    p.poke(0x57FE, 8)
    ff = 0; seen199 = False
    while ff < 40000 and not (seen199 and p.peek(0x57C6) == 0x03 and p.peek(0x40A7) == 240):
        h.user = bot(h, ff) if live(h) else (bits('A') if ff % 30 < 3 and p.peek(0x40A7) not in (197, 199) else 0)
        h.run(1); ff += 1; seen199 = seen199 or p.peek(0x40A7) == 199
    h.user = 0; h.run(30)
    info('엔딩 봄 %s · %d프레임 · 램 카드 합 %d (원래 %d)' % (seen199, ff, sum(own(h)), sum(base)))
    fl, blocks = unload_flash(h)
    ok(seen199 and fl is not None, '스토리 클리어 → 엔딩 → 타이틀, 세이브 씀')
    if fl:
        a, fc = flash_cards(blocks)
        ok(sum(fc) > sum(base) and fc.count(8) < 120 and all(fc[i] >= base[i] for i in range(120)), '클리어 세이브(칸 %06X): 카드 합 %d (원래 %d + 상) · 올카드 안 남음' % (a, sum(fc), sum(base)))

# ════ C-18 유가 + 무한 대전(가운데 칸 — 원래는 이길 때마다 P1 이 바뀌는 모드) — 판마다 P1 = 유가, 멈춤 없음 ════
if not ONLY or 'yugasurv' in ONLY:
    h = new_h('yugasurv'); p = h.p
    cset(yuga=2, hp1=1, hp2=2); to_menu(h); to_char(h, row=1)
    pick_and_go(h, moves='D', want_card=False)
    blks = []; ff = 0; last_live = False
    while ff < 30000 and p.peek(0x580B) < 4:
        lv = live(h)
        if lv and not last_live: blks.append(p.peek(0x5B51))
        last_live = lv
        h.user = bot(h, ff) if lv else (bits('A') if ff % 30 < 3 else 0)
        h.run(1); ff += 1
    h.user = 0
    ok(len(blks) >= 4 and all(b == 0xE8 for b in blks), '무한 대전 가운데 칸 + 유가 나찰: 판마다 P1 블록 %s · 연승 %d (%d프레임)' % (['%02X' % b for b in blks], p.peek(0x580B), ff))

print('== %s: %s' % (ROMK, 'ALL PASS' if not fails else '%d FAIL' % fails))
