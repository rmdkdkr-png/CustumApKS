"""Reference practice-mode controller (Python, mirrors what league.c would do after each retro_run).
peek/poke are CPU addresses. Call step() once per frame AFTER retro_run."""
HP_FLOOR = 64          # never let HP fall below this between frames -> no single hit can KO (largest hit seen: 36)
REFILL_DELAY = 40      # frames the victim must be actionable before HP refills
def w16(peek, a): return peek(a) | (peek(a + 1) << 8)
def p16(poke, a, v): poke(a, v & 0xFF); poke(a + 1, (v >> 8) & 0xFF)
BLK = (0x5980, 0x5B80); OBJ = (0x4E30, 0x4E70)
def live(peek): return peek(0x40A7) == 241 and peek(0x411A) == 1 and peek(0x5824) == 0
def actionable(peek, who): return w16(peek, OBJ[who] + 0x0E) < 0x50
def neutral(peek):
    return (actionable(peek, 0) and actionable(peek, 1) and w16(peek, 0x59DA) == 128 and w16(peek, 0x5BDA) == 128
            and peek(0x41C2) == 4 and peek(0x5DC7) == 0)
def set_pos(poke, who, x, face_left):
    b, o = BLK[who], OBJ[who]
    for a, v in ((b + 0x54, 0), (b + 0x56, x), (b + 0x64, 0), (b + 0x66, x), (b + 0x58, 0), (b + 0x5A, 128),
                 (b + 0x5C, 0), (b + 0x5E, 0), (o + 0x08, x), (o + 0x0A, 128)):
        p16(poke, a, v)
    poke(b + 0x52, face_left); poke(b + 0x53, face_left); poke(o + 0x24, face_left)
def set_cam(poke, cam):
    cam = max(0, min(159, cam))
    for a in (0x5FA0, 0x576C, 0x4880): p16(poke, a, cam << 8)
class Practice:
    def __init__(self, inf_time=True, hp_refill=True, p1_max=False, p2_max=False, start=(120, 200)):
        self.inf_time, self.hp_refill, self.max = inf_time, hp_refill, (p1_max, p2_max)
        self.start = start; self.calm = [0, 0]; self.reset_req = False; self.resets = 0
    def request_reset(self): self.reset_req = True
    def do_reset(self, peek, poke):
        x1, x2 = self.start
        set_pos(poke, 0, x1, 1 if x1 > x2 else 0); set_pos(poke, 1, x2, 1 if x2 > x1 else 0)
        set_cam(poke, (x1 + x2) // 2 - 80)
        for who in (0, 1):
            b = BLK[who]
            poke(b + 0xC6, 128); poke(b + 0xCA, 128)                    # HP + displayed HP
            if not self.max[who]:
                poke(b + 0x4A, peek(b + 0x4A) & ~0x04); p16(poke, b + 0xC8, 0); poke(b + 0xC7, 0); poke(b + 0xCB, 0)
        self.resets += 1
    def step(self, peek, poke):
        if not live(peek): return
        if self.inf_time: poke(0x582F, 0xFF); poke(0x5830, 0xFF)
        for who in (0, 1):
            b = BLK[who]
            hp = peek(b + 0xC6)
            self.calm[who] = self.calm[who] + 1 if actionable(peek, who) else 0
            if self.hp_refill:
                if hp < HP_FLOOR: poke(b + 0xC6, HP_FLOOR)                # KO guard (display keeps draining down)
                if self.calm[who] >= REFILL_DELAY and hp < 128: poke(b + 0xC6, 128); poke(b + 0xCA, 128)
            if self.max[who]:
                if not (peek(b + 0x4A) & 0x04) and actionable(peek, who):  # re-arm MAX after it was spent/expired
                    poke(b + 0xC7, 0x30); poke(b + 0xCB, 0x30); p16(poke, b + 0xC8, 0x3000); poke(b + 0x4A, peek(b + 0x4A) | 0x04)
                elif peek(b + 0x4A) & 0x04 and w16(peek, b + 0xC8) < 0x1000:
                    p16(poke, b + 0xC8, 0x3000)                            # keep MAX from timing out
        if self.reset_req and neutral(peek):
            self.reset_req = False; self.do_reset(peek, poke)
