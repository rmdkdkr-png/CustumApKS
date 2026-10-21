"""Practice-mode state writers (reference implementation in Python; port to C)."""
from rs import setw
P = (0x5980, 0x5B80)      # per-player block base (P2 = P1 + 0x200)
def set_pos(p, who, x, y=128):
    b = P[who]
    setw(p, b+0x54, 0); setw(p, b+0x56, x)      # X 16.16: frac 0x59D4, int 0x59D6
    setw(p, b+0x64, 0); setw(p, b+0x66, x)      # previous X 0x59E4/0x59E6
    setw(p, b+0x58, 0); setw(p, b+0x5A, y)      # Y 16.16: frac 0x59D8, int 0x59DA (ground 128)
    for a in range(b+0x5C, b+0x60): p.poke(a, 0)   # vertical velocity 0x59DC (s32 16.16, + = up)
def set_cam(p, cam):
    cam = max(0, min(159, cam))
    for a in (0x5FA0, 0x576C, 0x4880): setw(p, a, cam << 8)
def cam_for(x1, x2):
    return max(0, min(159, (x1 + x2) // 2 - 80))
def teleport(p, x1, x2, cam=None, objs=False, facing=False):
    """objs=True also writes the display objects (0x4E38/0x4E78) -> no one-tick push-apart against the old spot;
    facing=True writes facing in block (+0x52/+0x53) and object (+0x24) -> no turn animation when sides swap.
    practice_ref.py does both (complete recipe)."""
    set_pos(p, 0, x1); set_pos(p, 1, x2); set_cam(p, cam_for(x1, x2) if cam is None else cam)
    if objs:
        setw(p, 0x4E38, x1); setw(p, 0x4E3A, 128); setw(p, 0x4E78, x2); setw(p, 0x4E7A, 128)
    if facing:
        f1 = 1 if x1 > x2 else 0; f2 = 1 - f1
        for b, o, f in ((0x5980, 0x4E30, f1), (0x5B80, 0x4E70, f2)):
            p.poke(b+0x52, f); p.poke(b+0x53, f); p.poke(o+0x24, f)
def set_hp(p, who, hp):
    b = P[who]; p.poke(b+0xC6, hp); p.poke(b+0xCA, hp)   # 0x5A46 HP, 0x5A4A displayed HP
def set_rage(p, who, v):
    b = P[who]; p.poke(b+0xC7, v); p.poke(b+0xCB, v)     # 0x5A47 rage, 0x5A4B displayed rage
def set_max(p, who, timer=0x3000):
    b = P[who]
    p.poke(b+0xC7, 0x30); p.poke(b+0xCB, 0x30)            # rage + displayed rage full
    setw(p, b+0xC8, timer)                                # MAX hold timer 0x5A48 (16-bit, counts down)
    p.poke(b+0x4A, p.peek(b+0x4A) | 0x04)                 # 0x59CA bit2 = MAX active
def clear_max(p, who):
    b = P[who]
    p.poke(b+0x4A, p.peek(b+0x4A) & ~0x04); setw(p, b+0xC8, 0)
    p.poke(b+0xC7, 0); p.poke(b+0xCB, 0)
