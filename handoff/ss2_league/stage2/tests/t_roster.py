"""2단계 명단 12명 실제 경기 확인 — 앱과 같은 무장(올카드 + 메뉴 자동 진입)으로 1인 대전 첫 경기를 열고,
상대 블록·실효 포인트/시간·CPU 단계/배율·최종 결과가 명단대로인지, CPU 가 실제로 싸우는지(가만히 있는 P1 이 맞는지) 본다.
사용: python3 t_roster.py <롬> [상대id …]   (PYTHONPATH 에 handoff/ss2_league 와 stage1/tests — hosttest·ss2probe)
출력: 상대마다 한 줄 + 화면 캡처(LEAGUE_WORK/roster_<롬>_<id>.png, 첫 라운드 시작 뒤 90프레임)"""
import os, sys, hosttest as T
ROSTER = [  # League.ROSTER 와 같게 — id, 닉네임, 캐릭터, 검질, 난도
    ("o01", "칼끝노인", 11, 0, 1), ("o02", "퇴근후한판", 3, 1, 1), ("o03", "달빛나코", 4, 0, 0), ("o04", "새벽검객", 2, 0, 1),
    ("o05", "장미기사", 9, 1, 1), ("o06", "얼음요정", 5, 0, 0), ("o07", "그늘닌자", 6, 0, 0), ("o08", "독수리산책", 7, 0, 0),
    ("o09", "불꽃형님", 0, 1, 2), ("o10", "검은달", 8, 1, 2), ("o11", "꽃잎칼날", 13, 0, 2), ("o12", "끝판왕", 14, 1, 2)]
MULT = {0: (0x00C0, 0x0140), 1: (0x00D9, 0x0126), 2: (0x00F3, 0x010C)}   # 0단계 «CPU 난도» — 1인 대전 첫 경기
ROM = sys.argv[1]; want_ids = sys.argv[2:]
tag = os.path.splitext(os.path.basename(ROM))[0]
fails = 0
for k, (oid, nick, ch, sty, diff) in enumerate(ROSTER):
    if want_ids and oid not in want_ids: continue
    h = T.Harness(ROM, T.work('roster_%s_%s' % (tag, oid)))
    T.lg.league_arm(ch, sty, diff, 2, 60, 2 | 4)            # 앱과 같게: LEAGUE_ALLCARDS | LEAGUE_AUTONAV
    f = 0
    while f < 900:                                          # 메뉴 자동 진입이 손을 뗄 때까지
        h.run(1); f += 1
        if T.C.c_int.in_dll(T.lg, 'league_ovr_on').value == 0 and f > 70: break
    h.press('A', 4, 200); h.press('A', 4, 200)              # 사용자: 캐릭터(커서 그대로)·유파(수라) 확정
    h.run(240); h.press('A', 4, 240); h.press('R', 4, 30); h.press('A', 4, 200)   # 카드 화면: 안 받음
    # 첫 라운드 시작까지
    f = 0
    while f < 6000 and not T.status()[3]:
        p = h.p
        if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
        else: h.run(1)
        f += 1
    st0 = T.status(); p = h.p
    h.run(90); p.shot(T.work('roster_%s_%s.png' % (tag, oid)))
    # CPU 가 싸우나: P1 은 가만히 1800프레임, 맞을 때마다 깎인 양을 더한다(쓰러지지 않게 채움)
    dmg = 0; hits = 0; prev = p.peek(0x5A46)
    for i in range(1800):
        h.run(1); hp = p.peek(0x5A46)
        if hp < prev: dmg += prev - hp; hits += 1
        if hp < 48: p.poke(0x5A46, 128); hp = 128
        prev = hp
        if T.status()[4]: break
    # 결판: 짝수 번째 상대는 P1 승, 홀수 번째는 P2 승
    who = 'W' if k % 2 == 0 else 'L'
    f = 0; wait = None
    while f < 30000 and not T.status()[4]:
        if p.peek(0x40A7) == 241 and p.peek(0x5824) == 0 and p.peek(0x5A46) > 0 and p.peek(0x5C46) > 0:
            if wait is None: wait = f + 120
            if f >= wait: p.poke(0x5C46 if who == 'W' else 0x5A46, 0); wait = None
        if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
        else: h.run(1)
        f += 1
    st = T.status()
    wantblk = (ch << 4) | (sty << 3)
    got = 'W' if st[5] & 0x40 else 'L' if st[5] & 0x20 else 'D'
    checks = {
        'started': st0[3] == 1,
        'p2@start': (st[12] & 0xF8) == wantblk,
        'p2@end': (st[11] & 0xF8) == wantblk,
        'need/time': st[9] == 2 and st[17] == 60,
        'cpu_lv': st[18] == 1 + 3 * diff,
        'cpu_mult': (st[19], st[20]) == MULT[diff],
        'result': st[4] == 1 and got == who and (st[6], st[7]) == ((2, 0) if who == 'W' else (0, 2)),
        'fights': hits >= 2 and dmg >= 20,
    }
    bad = [k2 for k2, v in checks.items() if not v]
    fails += bool(bad)
    print('%s %-5s %-6s ch%2d sty%d diff%d | P1 %02X P2 start %02X end %02X | need %d time %d | lv %d mult %04X/%04X | %s %d:%d | idle P1 hit %d dmg %d | %s'
          % (tag, oid, nick, ch, sty, diff, st[10], st[12], st[11], st[9], st[17], st[18], st[19], st[20], got, st[6], st[7], hits, dmg,
             'OK' if not bad else 'FAIL ' + ','.join(bad)), flush=True)
print('%s: %s' % (tag, 'ALL OK' if not fails else '%d FAIL' % fails))
