"""Reference implementation (RAM reads only) of the practice-mode combat tracker, for porting to C (league.c style).

Call CombatTracker.step(peek, frame) once per emulated frame AFTER retro_run. peek(addr) returns a byte (CPU address).
Emits event dicts into self.events:
  {'type': 'contact', 'frame', 'kind': 'hit'|'block'|'deflect'|'other', 'attacker': 0|1, 'defender': 0|1,
   'damage': int, 'hitstop': ticks, 'combo': n}
  (throws have no hitstop: they are reported as kind 'throw' from the defender's combo-counter rise; their damage lands
   later, so read it from the combo_end event)
  {'type': 'combo_end', 'frame', 'defender', 'hits', 'damage'}
  {'type': 'advantage', 'frame', 'adv_p1': frames (60 Hz, + = P1 acts first), 'free': (f_p1, f_p2), 'after': kind}

All addresses verified in /tmp/.../practice/re_hit/REPORT.md.
"""
BLK = (0x59C0, 0x5BC0)          # per-player block base (P2 = P1 + 0x200)
HITSTOP = 0x5DC7                # global hit-freeze ticks (both players frozen while != 0)
OFF_STANCE = 0x09               # B+0x09: 0x20 stand, 0x40 crouch/lying, 0x80 airborne | 0x10 high guard, 0x08 low guard | 0x02/0x01 parry
OFF_CTRL = 0x0E                 # B+0x0E: 0 = full control (actionable). nonzero = busy (02 normal/cancelable, 0A hitstun, 12 blockstun, FF committed ...)
OFF_HP = 0x86                   # B+0x86 = 0x5A46 / 0x5C46
OFF_COMBO = 0xD7                # B+0xD7 = 0x5A97 / 0x5C97: hits taken in the current combo (0 = not in a hit reaction)


def live(peek):
    return peek(0x40A7) == 241 and peek(0x411A) == 1 and peek(0x5824) == 0


class CombatTracker:
    def __init__(self):
        self.prev = None
        self.events = []
        self.wait_free = None          # [free_frame_p1, free_frame_p2] while measuring advantage
        self.last_kind = None
        self.combo_start_hp = [None, None]
        self.combo_hits = [0, 0]
        self.act_start = [None, None]   # frame each side last left full control (ctrl 0 -> nonzero) = action start
        self.contact_frame = None
    ADV_TIMEOUT = 300                   # frames after the contact; give up if a side never regains control (a knockdown takes ~160)

    def _snap(self, peek):
        s = {'hs': peek(HITSTOP)}
        for pl in (0, 1):
            b = BLK[pl]
            s[pl] = dict(stance=peek(b + OFF_STANCE), ctrl=peek(b + OFF_CTRL), hp=peek(b + OFF_HP), combo=peek(b + OFF_COMBO))
        return s

    def step(self, peek, frame):
        if not live(peek):
            self.prev = None; self.wait_free = None
            return
        s = self._snap(peek)
        pv = self.prev
        self.prev = s
        if pv is None:
            return
        for pl in (0, 1):
            if pv[pl]['ctrl'] == 0 and s[pl]['ctrl'] != 0:
                self.act_start[pl] = frame
        # ---- combo bookkeeping (defender side counter) ----
        for d in (0, 1):
            if pv[d]['combo'] == 0 and s[d]['combo'] > 0:
                self.combo_start_hp[d] = pv[d]['hp']
            if pv[d]['combo'] > 0 and s[d]['combo'] == 0:
                self.events.append({'type': 'combo_end', 'frame': frame, 'defender': d, 'hits': pv[d]['combo'],
                                    'damage': (self.combo_start_hp[d] or s[d]['hp']) - s[d]['hp']})
        # ---- contact = rising edge of the global hitstop, or a combo-counter rise without hitstop (throws) ----
        throw_d = next((d for d in (0, 1) if s[d]['combo'] > pv[d]['combo']), None) if s['hs'] == 0 else None
        if throw_d is not None:
            att = 1 - throw_d
            startup = (frame - self.act_start[att]) if self.act_start[att] is not None else None
            self.events.append({'type': 'contact', 'frame': frame, 'kind': 'throw', 'attacker': att, 'defender': throw_d,
                                'damage': pv[throw_d]['hp'] - s[throw_d]['hp'], 'hitstop': 0, 'combo': s[throw_d]['combo'],
                                'startup': startup})
            self.wait_free = [None, None]; self.contact_frame = frame; self.last_kind = 'throw'
        if pv['hs'] == 0 and s['hs'] != 0:
            kind, att, dfn = 'other', None, None
            for d in (0, 1):
                if s[d]['combo'] > pv[d]['combo']:
                    kind, dfn = 'hit', d
            if kind != 'hit':
                for d in (0, 1):
                    if s[d]['stance'] & 0x18:
                        kind, dfn = 'block', d
                    elif s[d]['stance'] & 0x03:
                        kind, dfn = 'deflect', d
            if dfn is not None:
                att = 1 - dfn
            dmg = (pv[dfn]['hp'] - s[dfn]['hp']) if dfn is not None else 0
            if kind == 'hit' and dmg == 0 and s[att]['stance'] & 0x03:
                kind = 'deflect'                   # successful parry: the game scores it as a 0-damage hit on the parried attacker
            startup = (frame - self.act_start[att]) if (att is not None and self.act_start[att] is not None) else None
            self.events.append({'type': 'contact', 'frame': frame, 'kind': kind, 'attacker': att, 'defender': dfn,
                                'damage': dmg, 'hitstop': s['hs'], 'combo': s[dfn]['combo'] if dfn is not None else 0,
                                'startup': startup})
            self.wait_free = [None, None]          # (re)start the advantage measurement
            self.contact_frame = frame
            self.last_kind = kind
        # ---- frame advantage: first frame each side is back to full control (B+0x0E == 0) ----
        if self.wait_free is not None and frame - self.contact_frame > self.ADV_TIMEOUT:
            self.wait_free = None
        if self.wait_free is not None and s['hs'] == 0:
            for pl in (0, 1):
                if self.wait_free[pl] is None and s[pl]['ctrl'] == 0:
                    self.wait_free[pl] = frame
            if None not in self.wait_free:
                f1, f2 = self.wait_free
                self.events.append({'type': 'advantage', 'frame': frame, 'adv_p1': f2 - f1, 'free': (f1, f2), 'after': self.last_kind})
                self.wait_free = None
