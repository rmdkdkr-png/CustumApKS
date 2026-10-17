"""프레임 데이터 추적기 — 참조 구현(파이썬). practice.c 의 fd_tick() 이 이것을 그대로 옮긴다(design.md 5장).
진짜 프레임마다 retro_run 뒤(practice_tick 안, game_writes 앞) 한 번 step(peek) 를 부른다. 라운드 진행·일시정지 아님일 때만.

칸 종류(K_*) — 프레임 미터 한 칸
  0 IDLE      움직일 수 있음(땅)                       — 빈칸(어두운 회색)
  1 MOVE      움직일 수 있음(공중) · 대시                — 회색
  2 STARTUP   내 동작, 아직 판정 전                       — 초록(SF6 발동)
  3 ACTIVE    공격 판정이 닿을 수 있음                    — 빨강(SF6 지속)
  4 RECOVERY  판정이 끝난 뒤 · 가드당한 반동              — 파랑(SF6 경직)
  5 ACTION    판정 없는 동작(튕겨내기·도발 등)            — 청록
  6 HITSTUN   맞고 경직(잡힘 포함)                        — 노랑
  7 BLOCKSTUN 가드 경직                                   — 주황
  8 DOWN      다운·기상(0x10)                             — 보라
  플래그 0x40 PARRY(자세 bit0·1 = 튕겨내기 판정) · 0x80 PROJ(내 장풍이 닿을 수 있음)
"""
K_IDLE, K_MOVE, K_STARTUP, K_ACTIVE, K_RECOVERY, K_ACTION, K_HITSTUN, K_BLOCKSTUN, K_DOWN = range(9)
F_PARRY, F_PROJ = 0x40, 0x80
K_GAP = 9                                     # 줄임 칸 — 장풍만 날아가는 동안 · 한 사람은 움직일 수 있고 다른 사람은 같은 경직이 RUN_MAX 넘게 이어질 때
KCH = '.-SAR=hbd|'
VIEW = 80
RUN_MAX = 8                                   # 같은 칸 짝이 이만큼 이어진 뒤부터는 줄임(다운 100F 가 미터를 덮지 않게)
PB = (0x5980, 0x5B80)
OBJ = lambda k: 0x4E30 + k * 0x40
C_HIT, C_BLOCK, C_THROW, C_OTHER, C_DOWN = 1, 2, 3, 4, 5
KIND_NAME = {0: '헛침', C_HIT: '히트', C_BLOCK: '가드', C_THROW: '잡기', C_OTHER: '상쇄', C_DOWN: '다운'}

class Act:
    """한 동작(움직일 수 있음에서 시작 · 또는 보통 공격을 필살로 캔슬)"""
    def __init__(s, key, start):
        s.key = key; s.start = start; s.n = 0; s.first = None; s.last = None; s.proj = False; s.contact = 0
        s.dash = False; s.contact_at = None; s.pfirst = None; s.plast = None
    def summary(s):
        par = None if s.pfirst is None else (s.pfirst + 1, s.plast - s.pfirst + 1)
        if s.first is None: return dict(key=s.key, total=s.n, startup=None, active=None, recovery=None, proj=s.proj, contact=s.contact, parry=par)
        return dict(key=s.key, total=s.n, startup=s.first + 1, active=(s.last - s.first + 1) if not s.proj else None,
                    recovery=s.n - 1 - s.last, proj=s.proj, contact=s.contact, contact_at=s.contact_at, parry=par)

class FrameData:
    def __init__(s):
        s.reset_all()
    def reset_keep_mem(s):
        """practice.c fd_reset(1) — 리셋(순간이동)·새 경기: 기술 기억만 남긴다"""
        m = s.mem
        s.reset_all(); s.mem = m
    def reset_all(s):
        s.prev = None; s.f = 0
        s.mode = [0, 0]; s.stun = [0, 0]; s.downseen = [0, 0]; s.boxq = [[0, 0], [0, 0]]; s.projq = [[0, 0], [0, 0]]
        s.act = [None, None]; s.done = []           # 끝난 동작 요약(시험용 기록)
        s.seq_on = False; s.seq_id = 0; s.len = 0; s.cell = [[0xFF] * VIEW for _ in range(2)]; s.gap_open = False; s.gap_n = 0; s.run = 0; s.last_pair = None
        s.wait = None; s.contact_f = 0; s.last_kind = 0; s.att = -1
        s.adv = None; s.adv_kind = 0; s.events = []
        s.mem = {}                                  # 동작 열쇠 → {startup, active, recovery(헛침), hit, block, throw}
        s.frozen_n = 0; s.ckey = [None, None]; s.focus = -1
        s.armed = {}                                # 물체 칸 → 주인(동작 중에 공격 상자를 켠 것 = 장풍)
        s.armq = [[0, 0], [0, 0]]
    # ── 램 읽기 ──
    def _rd(s, pk):
        r = {'hs': pk(0x5DC7)}
        for p in (0, 1):
            b = PB[p]
            r[p] = dict(ctrl=pk(b + 0x4E), st=pk(b + 0x49), y=pk(b + 0x5A) | pk(b + 0x5B) << 8, combo=pk(b + 0x117),
                        box=pk(OBJ(p) + 0x1C) != 0xFF, act=pk(OBJ(p) + 0x0E) | pk(OBJ(p) + 0x0F) << 8,
                        key=(pk(b + 0x1D1), pk(OBJ(p) + 0x0E) | pk(OBJ(p) + 0x0F) << 8, pk(b + 0x4C) | pk(b + 0x4D) << 8))
            r[p]['proj'] = False
        # 물체: 0x4180 활성 목록(칸 번호, 정렬 값) × 0x41C2 개 — 0~3 은 싸움꾼·그림자. 공격 물체 = 살아 있음(+06 != FF) 이고 공격 상자(+1E · +1C) 가 FF 아님.
        # 베기 잔상·불꽃 같은 효과 물체는 둘 다 FF(e21). 갈포드 개(파피)·나코루루 매처럼 늘 있는 물체는 주인이 걸을 때도 상자를 켜므로(e23) 주인이 «동작 중»에 켠 것만 장풍으로 친다(arm).
        r['objs'] = {}
        n = min(pk(0x41C2), 30)
        for i in range(n):
            k = pk(0x4180 + 2 * i)
            if k < 4 or k > 31: continue
            o = OBJ(k)
            cap = pk(o + 0x06) != 0xFF and (pk(o + 0x1E) != 0xFF or pk(o + 0x1C) != 0xFF)
            r['objs'][k] = (cap, pk(o + 0x27))
        return r
    def step(s, pk):
        s.f += 1
        r = s._rd(pk); pv = s.prev; s.prev = r
        if pv is None: return
        hs = r['hs']; frozen = hs != 0 and pv['hs'] != 0
        # ── 닿음(combat_ref 와 같은 규칙) ──
        contact = None
        if hs and not pv['hs']:
            d = next((q for q in (0, 1) if r[q]['combo'] > pv[q]['combo']), None)
            kind = C_HIT if d is not None else 0
            if d is None:
                d = next((q for q in (0, 1) if r[q]['st'] & 0x18), None)
                kind = C_BLOCK if d is not None else 0
            if d is None:
                d = next((q for q in (0, 1) if r[q]['st'] & 0x03), None)
                kind = C_OTHER
            contact = (kind, d)
        elif not hs:
            d = next((q for q in (0, 1) if r[q]['combo'] > pv[q]['combo']), None)
            if d is not None: contact = (C_THROW if pv[d]['combo'] == 0 else (s.last_kind or C_HIT), d)   # 이어지는 타(히트스톱 없는 다단)는 잡기가 아니다
        if contact:
            kind, d = contact
            s.wait = [None, None]; s.contact_f = s.f; s.last_kind = kind; s.att = (1 - d) if d is not None else -1
            if d is not None:
                s.mode[d] = 2; s.stun[d] = C_BLOCK if kind == C_BLOCK else C_HIT
                a = s.act[1 - d]
                if a is not None and not a.contact: a.contact = kind; a.contact_at = a.n
                if a is not None: s.ckey[1 - d] = a.key        # 유불리를 기억할 기술 = 닿을 때 공격한 쪽이 하던 동작
        for k in list(s.armed):
            if k not in r['objs'] or not r['objs'][k][0]: del s.armed[k]
        for k, (cap, ow) in r['objs'].items():
            pcap = pv['objs'].get(k, (False, 0))[0]
            if cap and not pcap and ow in (0, 1) and s.mode[ow] == 1: s.armed[k] = ow
        for p in (0, 1): r[p]['proj'] = any(ow == p for ow in s.armed.values())
        if frozen:
            s.frozen_n += 1
            s._adv(r, hs)                             # practice.c 도 얼린 프레임에 유불리 칸(시간 넘김·다운 표시)은 본다
            return
        # ── 칸 정하기 ──
        cls = [0, 0]
        for p in (0, 1):
            q = r[p]; ctrl = q['ctrl']
            act_now = s.boxq[p][1]; s.boxq[p][1] = s.boxq[p][0]; s.boxq[p][0] = 1 if q['box'] else 0
            proj_now = s.armq[p][1]; s.armq[p][1] = s.armq[p][0]; s.armq[p][0] = 1 if q['proj'] else 0
            flags = (F_PARRY if q['st'] & 0x03 else 0) | (F_PROJ if proj_now else 0)
            if ctrl == 0:
                s._end(p, 0)
                s.mode[p] = 0; s.downseen[p] = 0
                c = K_MOVE if q['y'] < 128 else K_IDLE
            elif s.mode[p] == 2 or ctrl in (0x0A, 0x0C, 0x10, 0x12):
                if s.mode[p] != 2: s.stun[p] = C_BLOCK if ctrl == 0x12 else C_HIT; s.downseen[p] = 0
                s._end(p, 1)
                s.mode[p] = 2
                if ctrl == 0x10: s.downseen[p] = 1
                c = K_DOWN if s.downseen[p] else K_BLOCKSTUN if (s.stun[p] == C_BLOCK or ctrl == 0x12) else K_HITSTUN
            elif ctrl in (0x04, 0x06, 0x08):              # 대시(04·06)·점프(08) — 움직이는 중. 여기서 공격하면 새 동작(점프 공격의 발동은 버튼부터)
                s._end(p, 0)
                s.mode[p] = 0
                c = K_MOVE
            else:
                pq = pv[p]
                cancel = s.mode[p] == 1 and pq['ctrl'] == 0x02 and q['act'] >= 0x180 and q['act'] != pq['act']
                if s.mode[p] != 1 or cancel:
                    s._end(p, 2)
                    s.act[p] = Act(q['key'], s.len)
                    act_now = 0; s.boxq[p] = [1 if q['box'] else 0, 0]       # 캔슬 — 앞 동작의 상자가 지연 줄에 남아 있으면 지운다
                    proj_now = 0; s.armq[p] = [1 if q['proj'] else 0, 0]
                s.mode[p] = 1
                a = s.act[p]
                if ctrl in (0x04, 0x06) and a.first is None:
                    a.dash = True; c = K_MOVE
                elif act_now:
                    if a.first is None: a.first = a.n
                    a.last = a.n; c = K_ACTIVE
                elif proj_now and a.first is None:
                    a.first = a.last = a.n; a.proj = True; c = K_ACTIVE
                elif a.first is not None:
                    c = K_RECOVERY
                else:
                    c = K_STARTUP
                if q['st'] & 0x03:
                    if a.pfirst is None: a.pfirst = a.n
                    a.plast = a.n
                a.n += 1
            cls[p] = c | flags
        # ── 순서(시퀀스) ──
        actor = any((c & 0x0F) != K_IDLE for c in cls)
        flying = any(r[p]['proj'] for p in (0, 1))
        busy = actor or flying
        if not s.seq_on and busy:
            s.seq_on = True; s.seq_id += 1; s.len = 0; s.cell = [[0xFF] * VIEW for _ in range(2)]; s.gap_open = False; s.gap_n = 0; s.run = 0; s.last_pair = None; s.frozen_n = 0
            for p in (0, 1):
                if s.act[p] is not None and s.mode[p] == 1: s.act[p].start = 0
        if s.seq_on:
            pair = (cls[0], cls[1])
            s.run = s.run + 1 if pair == s.last_pair else 1
            s.last_pair = pair
            waitrun = actor and s.run > RUN_MAX and any((c & 0x0F) == K_IDLE for c in pair) and any((c & 0x0F) in (K_HITSTUN, K_BLOCKSTUN, K_DOWN) for c in pair)
            if actor and not waitrun:
                for p in (0, 1): s.cell[p][s.len % VIEW] = cls[p]
                s.len += 1; s.gap_open = False
            elif waitrun:                             # 기다리기만 하는 긴 줄(다운·긴 경직) — 한 칸만 남기고 센다
                if not s.gap_open:
                    for p in (0, 1): s.cell[p][s.len % VIEW] = K_GAP
                    s.len += 1; s.gap_open = True
                s.gap_n += 1
            elif flying:                              # 장풍만 날아가는 중 — 한 칸(K_GAP)만 남기고 센다
                if not s.gap_open:
                    for p in (0, 1): s.cell[p][s.len % VIEW] = K_GAP | (cls[p] & F_PROJ)
                    s.len += 1; s.gap_open = True
                s.gap_n += 1
            else:
                s.seq_on = False
        s._adv(r, hs)
    def _adv(s, r, hs):
        # ── 유불리: 닿은 뒤 각자 처음 움직일 수 있게 된 프레임(히트스톱 0) ──
        if s.wait is not None and s.f - s.contact_f > 400: s.wait = None
        if s.wait is not None and s.att in (0, 1) and r[1 - s.att]['ctrl'] == 0x10 and s.last_kind == C_HIT: s.last_kind = C_DOWN
        if s.wait is not None and not hs:
            for p in (0, 1):
                if s.wait[p] is None and r[p]['ctrl'] == 0: s.wait[p] = s.f
            if None not in s.wait:
                s.adv = s.wait[1] - s.wait[0]; s.adv_kind = s.last_kind
                s.events.append(dict(f=s.f, adv=s.adv, kind=s.last_kind, att=s.att, free=tuple(s.wait)))
                if s.att in (0, 1) and s.ckey[s.att] is not None and s.last_kind in (C_HIT, C_BLOCK, C_THROW, C_DOWN):
                        m = s.mem.setdefault(s.ckey[s.att], {})
                        adv_att = s.adv if s.att == 0 else -s.adv
                        m[{C_HIT: 'hit', C_BLOCK: 'block', C_THROW: 'throw', C_DOWN: 'down'}.get(s.last_kind, 'other')] = adv_att
                s.wait = None
    def _last_contact_act(s, p):
        for d in reversed(s.done):
            if d['p'] == p and d['contact']: return d['_act']
        a = s.act[p]
        return a if a is not None and a.contact else None
    def _end(s, p, why):
        a = s.act[p]
        if a is None: return
        s.act[p] = None
        if a.first is None and not a.dash:            # 판정 없이 끝난 동작 — 보이는 칸을 ACTION 으로 고쳐 칠한다
            for i in range(a.n):
                j = a.start + i
                if 0 <= j < s.len and s.len - j <= VIEW:
                    c = s.cell[p][j % VIEW]
                    if c != 0xFF and (c & 0x0F) == K_STARTUP: s.cell[p][j % VIEW] = (c & 0xF0) | K_ACTION
        d = a.summary(); d['p'] = p; d['why'] = why; d['_act'] = a
        if p == 0 or a.contact: s.focus = p
        s.done.append(d)
        if a.first is not None:
            m = s.mem.setdefault(a.key, {})
            m['startup'] = d['startup']
            if not a.contact and why == 0: m['active'] = d['active']; m['recovery'] = d['recovery']; m['total'] = d['total']
    def meter(s, p):
        """보이는 80칸(감긴 순서 그대로) — 문자열"""
        return ''.join(' ' if c == 0xFF else (KCH[c & 0x0F] if not (c & F_PROJ) else '*') for c in s.cell[p])
    def line(s, p=0):
        """숫자 줄 — 마지막으로 끝난 P1 동작 + 기억"""
        d = next((d for d in reversed(s.done) if d['p'] == p), None)
        if d is None: return ''
        if d['startup'] is None:
            if d.get('parry'): return '튕겨내기 발동 %dF · 지속 %dF · 전체 %dF' % (d['parry'][0], d['parry'][1], d['total'])
            return '동작 %dF' % d['total']
        m = s.mem.get(d['key'], {})
        parts = ['발동 %dF' % d['startup']]
        if d['proj']: parts.append('장풍')
        elif d['contact']: 
            if 'active' in m: parts.append('지속 %dF · 경직 %dF' % (m['active'], m['recovery']))
        else: parts.append('지속 %dF · 경직 %dF' % (d['active'], d['recovery']))
        for k, nm in (('hit', '히트'), ('down', '다운'), ('block', '가드'), ('throw', '잡기')):
            if k in m: parts.append('%s %+d' % (nm, m[k]))
        return ' · '.join(parts).replace('+0', '±0').replace('-', '−')
