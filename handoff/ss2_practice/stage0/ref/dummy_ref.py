"""Reference implementation of the practice-mode P2 dummy (RAM pokes only), for porting to C.

Mechanism (verified, see REPORT.md):
  0x57D4 = game mode (0 1P PLAY, 1 VS/link, 2 SURVIVAL). While it is 1 the fight tick takes the VS input path:
      P1 pad <- 0x570D, P2 pad <- 0x5715 (raw NGP pad bits, &0x7F), P2's command ring is processed,
      and both players take the human branch (the AI call is skipped).
  0x5BCB bit0 = P2 "is CPU" (0x59CB for P1). Must be 0 too: the human movement code (0x2285D6) only reads
      the pad of a player whose bit0 is 0.
  Gate on MODE 0x40A7==241 && 0x411A==1 && 0x5824==0 (round live) so the round-setup code never sees 0x57D4=1.
"""
U, D, L, R, A, B, OPT = 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40

class Dummy:
    def __init__(self):
        self.active = False
        self.saved_mode = 0
    @staticmethod
    def live(peek):
        return peek(0x40A7) == 241 and peek(0x411A) == 1 and peek(0x5824) == 0
    @staticmethod
    def back(peek):        # "away from P1" for P2: P2 facing byte 0x4E94, 1 = faces left
        return R if peek(0x4E94) == 1 else L
    @staticmethod
    def fwd(peek):
        return L if peek(0x4E94) == 1 else R
    def step(self, peek, poke, p1_pad, p2_pad):
        """call once per frame. p1_pad = the user's final pad for the frame (ideally written BEFORE retro_run,
        see REPORT 'latency'); p2_pad = what the dummy should hold (no OPT bit)."""
        if self.live(peek):
            if not self.active:
                self.saved_mode = peek(0x57D4) if peek(0x57D4) != 1 else 0
                self.active = True
            poke(0x57D4, 1)
            poke(0x5BCB, peek(0x5BCB) & ~1)
            poke(0x570D, p1_pad & 0x7F)
            poke(0x5715, p2_pad & 0x3F)
        elif self.active:
            self.release(peek, poke)
    def release(self, peek, poke):
        poke(0x57D4, self.saved_mode)
        poke(0x5BCB, peek(0x5BCB) | 1)
        self.active = False

def p1_attacking(peek):
    a = peek(0x4E3E) | (peek(0x4E3F) << 8)
    return 0x50 <= a < 0x100 or a >= 0x180

def guard_all_pad(peek, low=False):
    """hold back only while P1 attacks or P2 is in guard stun -> blocks everything without walking away"""
    a2 = peek(0x4E7E) | (peek(0x4E7F) << 8)
    if p1_attacking(peek) or a2 in (0x38, 0x3C):
        return Dummy.back(peek) | (D if low else 0)
    return 0
