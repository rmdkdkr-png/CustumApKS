"""치트 조사 공용 — ss2probe 를 직접(허브 없이 = 일반 세션) 돌린다. 프레임 생성·런어헤드 끔."""
import os, shutil, glob, struct, ss2probe
S = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad'
D = os.environ.get('LEAGUE_WORK', S + '/impl/cheat-tests/work')   # 작업 폴더(찍힌 화면·상태 — 롬에서 나온 것이라 저장소 밖)
CORE = os.environ['LEAGUE_CORE']
ROMS = {'ko': os.environ['ROMKO'], 'ko101': os.environ['ROMKO101'], 'h1': os.environ['ROMH1'], 'jp': os.environ['ROMJP']}
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
def wdir(name, fresh=True, flash_from=None):
    w = os.path.join(D, name)
    if fresh and os.path.isdir(w): shutil.rmtree(w)
    os.makedirs(w, exist_ok=True)
    if flash_from: 
        for f in glob.glob(os.path.join(flash_from, '*.flash')): shutil.copy(f, w)
    return w
def probe(rom='ko', name='x', fresh=True, flash_from=None):
    w = wdir(name, fresh, flash_from)
    p = ss2probe.Probe(CORE, ROMS.get(rom, rom), w)
    p.wd = w
    return p
def st(p): return (p.peek(0x40A7), p.peek(0x41C0), p.peek(0x411A))
def to_menu(p):
    p.run(420); p.press('A', 4, 150); p.run(10)
def menu_row(p, row):
    while p.peek(0x624B) != row:
        p.press('D', 4, 20)
def own(p): return p.peek(0x63BA, 120)
def unload(p):
    p.lib.retro_unload_game()
    fs = glob.glob(os.path.join(p.wd, '*.flash'))
    return fs[0] if fs else None
def parse_flash(path):
    b = open(path, 'rb').read()
    vid, cnt, tot = struct.unpack_from('<HHI', b, 0)
    o = 8; out = []
    for i in range(cnt):
        a, n = struct.unpack_from('<IH', b, o); o += 8   # 구조체 패딩: 4+2(+2)
        out.append((a, b[o:o + n])); o += n
    return vid, out
