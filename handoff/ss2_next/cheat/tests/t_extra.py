"""치트 구현 뒤 더한 호스트 시험(설계 10-나 H-3~H-8 + 구현에서 고친 것) — t_cheat.py 와 같은 하네스(앱 native.c 순서: retro_run → league_tick_hub →
practice_tick → cheat_tick), 일반 세션처럼 연습 허브·둘 다를 켠 채.
사용: source env.sh; LEAGUE_WORK=… python3 t_extra.py <롬 키 ko|h1|ko101|jp> <묶음…>
묶음: determ_on determ_off(H-3 — 두 번 돌려 determ_cmp) · stload(H-4) · yugasurv13 · yugastory(H-5) · pow3(H-6) · pracyuga(H-7) · autosave(H-8)
      pracblock(연습 흐름: 경기 전부터 경기 치트 쉼 · 나가면 다시) · stfight(싸움 중 상태 저장·불러오기) · permoff(세이브에 남기기를 끄면 램 되돌림 · 세이브에 8 안 남음) · tempperm(이번만 창 안에서 세이브에 남기기로)"""
import os, sys, hashlib, ctypes as C
HERE = os.path.dirname(os.path.abspath(__file__))
ROMK = sys.argv[1]; GROUPS = sys.argv[2:]
sys.argv = ['t_cheat.py', ROMK, '__none__']
exec(open(os.path.join(HERE, 't_cheat.py'), encoding='utf-8').read().split('# ════ C-1')[0])
import ph
p16 = lambda p, a: p.peek16(a)

def bot(h, f):
    p = h.p
    g = abs(p.peek16(0x4E78) - p.peek16(0x4E38))
    fw = 'L' if p.peek(0x4E54) == 1 else 'R'
    return bits(fw) if g > 40 else (bits('A') if f % 40 < 4 else 0)

# ════ H-3 결정성 — 치트 모두 끔이면 cheat_tick 이 한 바이트도 안 쓴다: 부팅 → 카드 모음집 → 게임 설정 → 무한 대전 싸움, 1만 2천 프레임 ════
for grp in [g for g in GROUPS if g in ('determ_on', 'determ_off')]:
    on = grp == 'determ_on'
    h = new_h(grp); p = h.p
    out = []
    def hook(hh):
        if on: lg.cheat_tick(hh.p._ramp, hh.p._rams, hh.user)
        out.append(hashlib.md5(hh.p.ram()).hexdigest()[:10])
    h.post_hook = hook
    to_menu(h)
    while p.peek(0x624B) != 3: h.press('D', 4, 20)              # 카드 모음집
    h.press('A', 4, 150); h.press('A', 4, 150); h.press('R', 4, 60); h.press('D', 4, 60)
    for i in range(6): h.press('B', 4, 60)
    wait(h, lambda: p.peek(0x57C6) == 0x03, 400); h.run(30)
    mark1 = len(out)
    while p.peek(0x624B) != 4: h.press('D', 4, 20)              # 게임 설정 — 바꾸지 않고 나가기
    h.press('A', 4, 150)
    for i in range(7): h.press('D', 4, 30)
    h.press('A', 4, 200)
    wait(h, lambda: p.peek(0x57C6) == 0x03, 400); h.run(30)
    mark2 = len(out)
    to_char(h, row=1)                                            # 무한 대전
    pick_and_go(h, want_card=False)
    ff = 0
    while len(out) < 12000:
        h.user = bot(h, ff) if live(h) else (bits('A') if ff % 30 < 3 else 0); h.run(1); ff += 1
    h.user = 0
    open(os.path.join(cx.D, '%s_%s.txt' % (grp, ROMK)), 'w').write('\n'.join(out))
    info('%s: %d프레임 (모음집 끝 %d · 설정 끝 %d) · 끝 prog %02X MODE %d 연승 %d · 치트 상태 %s' % (grp, len(out), mark1, mark2, p.peek(0x57C6), p.peek(0x40A7), p.peek(0x580B), cst()[:8]))
if 'determ_cmp' in GROUPS:
    a = open(os.path.join(cx.D, 'determ_on_%s.txt' % ROMK)).read().split('\n'); b = open(os.path.join(cx.D, 'determ_off_%s.txt' % ROMK)).read().split('\n')
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    ok(len(a) == len(b) >= 12000 and not diff, 'H-3 치트 모두 끔: cheat_tick 있음/없음 %d프레임(모음집·게임 설정·무한 대전) 작업 램 해시 다른 프레임 %d%s'
       % (len(a), len(diff), (' (처음 %d)' % diff[0]) if diff else ''))

# ════ H-4 고르기 창에서 저장(before_save) → 치트 끈 세션에서 불러오기 → 게임오버 → 세이브 카드 = 원래 ════
if 'stload' in GROUPS:
    h = new_h('stload'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1); to_menu(h); to_char(h); h.run(5)
    ok(own(h) == bytes([8]) * 120, '고르기 창: 120칸 8')
    lg.cheat_before_save(p._ramp); st = h.serialize()
    h2 = new_h('stload2'); p2 = h2.p                               # 새 세션(치트 모두 끔 — new_h 가 cheat_reset_all)
    h2.unserialize(st); lg.cheat_forget()
    ok(own(h2) == base, '불러온 상태의 소유 개수 = 원래 값(합 %d)' % sum(own(h2)))
    pick_and_go(h2, want_card=False)
    r = kill_round(h2, 0x5A46, 12000, lambda hh: hh.p.peek(0x57C6) == 0x03 and hh.p.peek(0x40A7) == 240)
    h2.run(30)
    fl, blocks = unload_flash(h2)
    ok(fl is not None and flash_cards(blocks)[1] == base, '치트 끈 세션 게임오버 세이브 카드 = 원래(%s · %s프레임)' % (fl and ('합 %d' % sum(flash_cards(blocks)[1])), r))

# ════ H-5 유가 + 무한 대전 13연승 · 유가 + 스토리 7장 ════
if 'yugasurv13' in GROUPS:
    h = new_h('yugasurv13'); p = h.p
    cset(yuga=1, hp1=1, hp2=2); to_menu(h); to_char(h, row=1)
    pick_and_go(h, moves='D', want_card=False)
    p1s, p2s = [], []; ff = 0; last_live = False; stuck = 0; last_streak = -1; since = 0
    while ff < 90000 and p.peek(0x580B) < 13:
        lv = live(h)
        if lv and not last_live: p1s.append(p.peek(0x5B51)); p2s.append(p.peek(0x5D51))
        last_live = lv
        h.user = bot(h, ff) if lv else (bits('A') if ff % 30 < 3 else 0)
        h.run(1); ff += 1
        if p.peek(0x580B) != last_streak: last_streak = p.peek(0x580B); since = 0
        else: since += 1
        stuck = max(stuck, since)
    h.user = 0
    ok(p.peek(0x580B) >= 13 and all(b == 0xE0 for b in p1s), '유가 수라 + 무한 대전 %d연승(%d프레임 · 연승 사이 가장 긴 %d프레임): 판마다 P1 블록 E0 %s'
       % (p.peek(0x580B), ff, stuck, sorted(set('%02X' % b for b in p1s))))
    info('상대 P2 블록 %s · 유가(E?) 상대 %s' % (' '.join('%02X' % b for b in p2s), any(b >> 4 == 14 for b in p2s)))
if 'yugastory' in GROUPS:
    h = new_h('yugastory'); p = h.p
    cset(yuga=2, hp1=1, hp2=2); to_menu(h); to_char(h); pick_and_go(h, moves='D', want_card=False)
    p.poke(0x57FE, 6)                                               # 장 당기기 — 7장부터
    ff = 0; seen199 = False; p1s, p2s = [], []; last_live = False; modes = set()
    while ff < 60000 and not (seen199 and p.peek(0x57C6) == 0x03 and p.peek(0x40A7) == 240):
        lv = live(h)
        if lv and not last_live: p1s.append(p.peek(0x5B51)); p2s.append(p.peek(0x5D51))
        last_live = lv
        h.user = bot(h, ff) if lv else (bits('A') if ff % 30 < 3 and p.peek(0x40A7) not in (197, 199) else 0)
        h.run(1); ff += 1; seen199 = seen199 or p.peek(0x40A7) == 199; modes.add(p.peek(0x40A7))
    h.user = 0
    ok(seen199 and p.peek(0x57C6) == 0x03 and all(b == 0xE8 for b in p1s) and len(p1s) >= 3,
       '유가 나찰 + 스토리 7장부터: 엔딩 → 타이틀(%d프레임, 판 %d개) · 판마다 P1 블록 %s' % (ff, len(p1s), sorted(set('%02X' % b for b in p1s))))
    info('상대 P2 블록 %s · MODE %s' % (' '.join('%02X' % b for b in p2s), sorted(modes)))

# ════ H-6 공격력 3배 + 카드 공격 상승 + CPU 최강 → 0x57D8 = 0x133×3, 체력이 0 아래로 안 돎 ════
if 'pow3' in GROUPS:
    h = new_h('pow3'); p = h.p
    cset(cards=1, pow=3, diff=5); to_menu(h); to_char(h)
    had, f = pick_and_go(h, want_card=True)
    h.run(2)
    a = p.peek16(0x57D8)
    ok(had and a == 0x133 * 3 and cst()[9] == 0x133, '카드 공격 상승(0x133) × 3배 = 0x57D8 %04X (기준 %04X) · CPU 배율 %04X/%04X' % (a, cst()[9], p.peek16(0x57E2), p.peek16(0x57E4)))
    hp_bad = []; first = None; rounds = set()
    for ff in range(3000):
        h.user = bot(h, ff) if live(h) else 0
        h.run(1)
        for ad in (0x5A46, 0x5C46):
            v = p.peek(ad)
            if v > 128: hp_bad.append((ff, hex(ad), v))
        if first is None and live(h) and p.peek(0x5C46) < 128: first = 128 - p.peek(0x5C46)
        if live(h): rounds.add((p.peek(0x5821), p.peek(0x5822)))
    h.user = 0
    ok(not hp_bad and first is not None, '3000프레임 체력 0~128 밖으로 안 돎(%s) · 첫 대미지 %s · 라운드 %s · 끝 0x57D8 %04X' % (hp_bad[:3], first, sorted(rounds), p.peek16(0x57D8)))

# ════ H-7 연습 대전에서 내 캐릭터로 가운데 칸 + 유가 → 연습 경기 P1 = 유가, 리셋·대미지 숫자 정상 ════
if 'pracyuga' in GROUPS:
    h = new_h('pracyuga'); p = h.p
    cset(yuga=2, cards=1)
    ph.to_title(h)
    frames = ph.to_fight(h, my_moves='D')
    b = p.peek(0x5B51)
    ok(pst()[0] == 1 and b >> 4 == 14 and (b >> 3) & 1 == 1, '연습 경기 P1 = 유가 나찰(블록 %02X · %d프레임) · 더미 %s' % (b, frames, pst()[22:24]))
    ok(cst()[7] == 3, '연습 경기 중 치트 막힘 이유 3(경기 치트만)')
    n0 = pst()[11]; lg.practice_set(7, -1)
    r = wait(h, lambda: pst()[11] > n0, 600); h.run(30)
    ok(r is not None and pst()[0] == 1, '연습 리셋(%s프레임 · %d → %d번)' % (r, n0, pst()[11]))
    seen = set()
    for ff in range(900):
        h.user = bot(h, ff); h.run(1)
        if pst()[10] >= 0: seen.add(pst()[10])
    h.user = 0
    ok(pst()[0] == 1 and seen and p.peek(0x5824) == 0, '유가로 때리면 대미지 숫자(%s) · 연습 경기 계속' % sorted(seen)[:6])

# ════ H-8 올카드 이번만 — 카드 화면 안에서 앱 오토세이브(before_save + 저장) → 다시 열기 ════
if 'autosave' in GROUPS:
    h = new_h('autosave'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1); to_menu(h); to_char(h)
    h.press('A', 4, 0); wait(h, lambda: p.peek(0x41C0) == 4, 400); h.run(60); h.press('A', 4, 0)
    wait(h, lambda: p.peek(0x41C0) == 6, 400); h.run(60)
    ok(p.peek(0x41C0) == 6 and p.peek(0x5726) == 0x0A and own(h) == bytes([8]) * 120 and cst()[3] == 1, '카드 화면(0x5726 0A): 120칸 8 · 창 안')
    lg.cheat_before_save(p._ramp); st = h.serialize()
    h.run(1)
    ok(own(h) == bytes([8]) * 120, '저장 다음 프레임 다시 8')
    h2 = new_h('autosave2'); p2 = h2.p
    cset(cards=1)                                                   # 다시 연 앱 — 로드 뒤 값을 넣는다
    h2.unserialize(st); lg.cheat_forget()
    ok(own(h2) == base, '저장된 상태의 소유 개수 = 원래 값(합 %d)' % sum(own(h2)))
    h2.run(2)
    ok(own(h2) == bytes([8]) * 120 and cst()[3] == 1, '다시 연 뒤 카드 화면이면 다시 8')
    take_card(h2)
    f = wait(h2, lambda: live(h2), 6000)
    ok(f is not None and own(h2) == base, '카드 받고 싸움 — 원래 값으로(합 %d)' % sum(own(h2)))

# ════ 연습 흐름 — 경기 치트는 상대 고르기부터 쉰다(경기 전에 쓴 공격 배율이 연습 경기로 새지 않게) · 연습을 나가면 다시 먹는다 ════
if 'pracblock' in GROUPS:
    h = new_h('pracblock'); p = h.p
    cset(pow=3, diff=5, time=1, hp2=2, cpu=1, rage1=1)
    ph.to_title(h)
    whys = set(); atk_w = set(); t = [0]
    def watch(hh):
        lg.cheat_tick(hh.p._ramp, hh.p._rams, 0 if hh.passive else hh.user)
        hs = hub()[0]
        if hs in (2, 3, 4): whys.add(cst()[7]); atk_w.add(cst()[8])
    h.post_hook = watch
    frames = ph.to_fight(h)
    h.run(300)
    ok(pst()[0] == 1 and whys == {3} and atk_w == {-1} and cst()[2] == 0,
       '연습 흐름(상대 고르기~연습 경기) 내내 막힘 이유 %s · 공격 배율 안 씀 %s · 경기 치트 먹은 적 없음' % (sorted(whys), sorted(atk_w)))
    ok(p.peek16(0x57E2) == 0x100 and p.peek16(0x57E4) == 0x100 and (p.peek(0x5814), p.peek(0x5815)) != (10, 15) and not (p.peek(0x59CA) & 4),
       '연습 경기: CPU 배율 0100/0100(연습) · 단계 %d/%d(치트 최강 아님) · 내 MAX 안 켬 · 0x57D8 %04X' % (p.peek(0x5814), p.peek(0x5815), p.peek16(0x57D8)))
    h.post_hook = lambda hh: lg.cheat_tick(hh.p._ramp, hh.p._rams, 0 if hh.passive else hh.user)
    h.press('O', 3, 0); wait(h, lambda: pst()[1] == 2, 40)            # 연습 메뉴 «타이틀로»
    while pst()[2] != 9: h.press('D', 2, 3)
    h.press('A', 2, 0)
    nf = wait(h, lambda: hub()[0] == 1 and p.peek(0x624B) == 2 and hub()[7] == 0, 2000)
    h.run(10); h.press('U', 4, 30); h.press('U', 4, 30)              # 1인 대전
    h.press('A', 4, 0); wait(h, lambda: p.peek(0x41C0) == 2 and p.peek(0x5726) == 6, 400); h.run(120)
    pick_and_go(h, want_card=False); h.run(5)
    ok(nf is not None and cst()[7] == 0 and p.peek16(0x57D8) == 3 * cst()[9] and p.peek16(0x57E2) == 0x119 and p.peek(0x582F) == 0xFF,
       '연습을 나가 고른 1인 대전: 경기 치트 다시(이유 %d · 0x57D8 %04X = 3 × %04X · CPU 배율 %04X · 타이머 %04X)' % (cst()[7], p.peek16(0x57D8), cst()[9], p.peek16(0x57E2), p.peek16(0x582F)))

# ════ 세이브에 남기기를 끄면 — 이번 판에서 8 로 덮은 램을 그 전 값으로(게임오버 세이브에 8 이 안 남음) ════
if 'permoff' in GROUPS:
    h = new_h('permoff'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=2); to_menu(h); to_char(h); pick_and_go(h, want_card=False)
    ok(own(h) == bytes([8]) * 120 and cst()[15] == 1, '세이브에 남기기: 싸움 중 8 · 상태[15] 쓰는 중')
    cset(cards=0); h.run(2)
    ok(own(h) == base and cst()[15] == 0, '끄면 램 = 그 전 값(합 %d)' % sum(own(h)))
    r = kill_round(h, 0x5A46, 12000, lambda hh: hh.p.peek(0x57C6) == 0x03 and hh.p.peek(0x40A7) == 240); h.run(30)
    fl, blocks = unload_flash(h)
    ok(fl is not None and flash_cards(blocks)[1] == base, '게임오버 세이브 카드 = 원래(8 안 남음 · %s)' % (fl and ('합 %d' % sum(flash_cards(blocks)[1]))))
if 'tempperm' in GROUPS:
    h = new_h('tempperm'); p = h.p; base = rom_latest_slot_cards()
    cset(cards=1); to_menu(h); to_char(h); h.run(5)
    ok(own(h) == bytes([8]) * 120 and cst()[3] == 1, '이번만: 고르기 창 8')
    cset(cards=2); h.run(2)                                          # 창 안에서 세이브에 남기기로 — 원래 값은 창 보관본
    cset(cards=1); h.run(2)                                          # 다시 이번만 — 창 보관본이 8 로 더럽혀지지 않았나
    pick_and_go(h, want_card=False)
    ok(own(h) == base, '이번만 → 세이브에 남기기 → 이번만(창 안): 창을 떠나면 원래 값(합 %d — 8 로 안 남음)' % sum(own(h)))

# ════ 싸움 중 상태 저장(앱 nativeSaveState = before_save → 저장 → after_save) — 공격 배율·CPU 비트·다음 라운드 시간이 상태에 원래 값으로 ════
if 'stfight' in GROUPS:
    lg.cheat_after_save.argtypes = [C.c_void_p]
    h = new_h('stfight'); p = h.p
    cset(pow=2, cpu=1, time=1); to_menu(h); to_char(h); pick_and_go(h, want_card=False); h.run(30)
    base = cst()[9]; optt = p.peek(0x636C)
    ok(live(h) and p.peek16(0x57D8) == 2 * base and not (p.peek(0x5BCB) & 1) and p.peek(0x5812) == 0x80,
       '싸움 중: 0x57D8 %04X = 2 × %04X · 상대 CPU 비트 꺼짐 · 0x5812 = 80' % (p.peek16(0x57D8), base))
    lg.cheat_before_save(p._ramp)
    saved = (p.peek16(0x57D8), p.peek(0x5BCB) & 1, p.peek(0x5812))
    st = h.serialize(); lg.cheat_after_save(p._ramp)
    back = (p.peek16(0x57D8), p.peek(0x5BCB) & 1, p.peek(0x5812))
    ok(saved == (base, 1, optt) and back == (2 * base, 0, 0x80), '저장되는 상태엔 원래 값 %s · 저장 뒤 바로 치트 값 %s' % (saved, back))
    h.unserialize(st); lg.cheat_forget(); h.run(5)
    ok(p.peek16(0x57D8) == 2 * base and cst()[9] == base and cst()[5] == -1,
       '치트 켠 채 불러오기: 0x57D8 %04X = 2배 그대로(4배로 안 쌓임 · 기준 %04X) · 세이브 올카드 «모름» %d' % (p.peek16(0x57D8), cst()[9], cst()[5]))
    h2 = new_h('stfight2'); p2 = h2.p
    h2.unserialize(st); lg.cheat_forget(); h2.run(5)
    ok(p2.peek16(0x57D8) == base and (p2.peek(0x5BCB) & 1) and p2.peek(0x5812) == optt,
       '치트 끈 세션에서 불러오기: 0x57D8 %04X · CPU 비트 %d · 0x5812 %d(옵션 %d)' % (p2.peek16(0x57D8), p2.peek(0x5BCB) & 1, p2.peek(0x5812), optt))
    f = wait(h2, lambda: p2.peek(0x5A46) < 128, 2400)
    ok(f is not None, '상대가 다시 움직여 때림(%s프레임)' % f)

print('== %s %s: %s' % (ROMK, ' '.join(GROUPS), 'ALL PASS' if not fails else '%d FAIL' % fails))
