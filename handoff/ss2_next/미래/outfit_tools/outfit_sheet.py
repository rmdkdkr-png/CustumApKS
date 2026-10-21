"""아웃핏 그림 도구(시제품) — 캐릭터 몸 포즈 전부를 4색 시트 PNG 로 내보내고, 고친 시트를 바꿈 표(.ss2o)로 되읽는다.
  export <char> <out.png>      : 포즈마다 64x64 칸(8열), 셀 밖은 회색 격자. 같은 이름 .json 에 포즈 목록.
  import <char> <in.png> <out.ss2o> [name]  : 칸 안 화소 → 타일. 같은 타일을 쓰는 포즈끼리 다르게 고치면 '겹침' 경고(많이 그린 쪽).
                                             셀 밖에 그린 화소는 버리고 '셀 밖' 경고(런타임 바꿈은 새 칸을 못 만든다).
색 → 번호: 팔레트 PNG 의 0 투명(배경) · 1 · 2 · 3 (RGB 모드면 가장 가까운 REF 색).
.ss2o v2: 'SS2O' u8 ver=2 u8 char u8 mode(2 = XOR 차이) u8 nlen + name(UTF-8) + u32 crc32(이 캐릭터 타일 묶음 원본) + zlib( u16 n + n*(u16 idx + 16B (새 타일 XOR 롬 타일)) )
  — 파일엔 원래 그림이 없다(롬이 있어야 풀림). crc 가 다르면(다른 롬·다른 해킹판) 쓰지 않는다."""
import sys, os, json, struct, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import poses, posrender
from PIL import Image
REF = [(90, 110, 90), (255, 221, 187), (60, 120, 230), (40, 30, 60)]
CELL = 64; COLS = 8
def body_recs(rom, ch): return [r for r in poses.parse(rom, ch) if not any(f & 0x1F for f, c in r['layout'])]
def export(rom, ch, out):
    recs = body_recs(rom, ch); n = len(recs); rows = (n + COLS - 1) // COLS
    im = Image.new('P', (COLS * CELL, rows * CELL), 0)
    im.putpalette(sum((list(c) for c in REF), []) + [128, 128, 128] * 252)
    px = im.load()
    for k, r in enumerate(recs):
        ox_, oy = (k % COLS) * CELL, (k // COLS) * CELL
        cells = set(c for f, c in r['layout'])
        for y in range(64):
            for x in range(64):
                if ((y >> 3) << 4 | (x >> 3)) not in cells and (x % 8 == 0 or y % 8 == 0): px[ox_ + x, oy + y] = 4  # grey grid = no cell
        pp = posrender.render(rom, ch, r, cols=(None, 1, 2, 3), bg=0) if False else None
        bank = poses.banks(rom)[ch]
        for (f, cell), idx in zip(r['layout'], r['idx']):
            rows8 = posrender.tile_rows(rom, bank, idx); hf, vf = f & 0x40, f & 0x20
            for yy in range(8):
                for xx in range(8):
                    w = rows8[7 - yy if vf else yy]; v = (w >> (14 - 2 * (7 - xx if hf else xx))) & 3
                    px[ox_ + (cell & 15) * 8 + xx, oy + (cell >> 4) * 8 + yy] = v
    im.save(out)
    json.dump([dict(start=r['start'], layout=r['layout'], idx=r['idx']) for r in recs], open(os.path.splitext(out)[0] + '.json', 'w'))
    return n
def import_(rom, ch, path, out, name='outfit'):
    recs = body_recs(rom, ch); im = Image.open(path)
    if im.mode == 'P': get = im.load(); val = lambda x, y: get[x, y] if get[x, y] < 4 else 0
    else:
        im = im.convert('RGB'); get = im.load()
        val = lambda x, y: min(range(4), key=lambda i: sum((a - b) ** 2 for a, b in zip(get[x, y], REF[i])))
    bank = poses.banks(rom)[ch]
    votes = collections.defaultdict(collections.Counter); outside = 0
    for k, r in enumerate(recs):
        ox_, oy = (k % COLS) * CELL, (k // COLS) * CELL
        cells = {c: (f, idx) for (f, c), idx in zip(r['layout'], r['idx'])}
        for y in range(64):
            for x in range(64):
                cell = (y >> 3) << 4 | (x >> 3); v = val(ox_ + x, oy + y)
                if cell not in cells:
                    if v and not (x % 8 == 0 or y % 8 == 0): outside += 1
                    continue
                f, idx = cells[cell]; xx, yy = x & 7, y & 7
                cc = 7 - xx if f & 0x40 else xx; rr = 7 - yy if f & 0x20 else yy
                votes[(idx, rr, cc)][v] += 1
    tiles = {}; conflicts = 0
    for (idx, rr, cc), cnt in votes.items():
        v = cnt.most_common(1)[0][0]; conflicts += len(cnt) > 1
        tiles.setdefault(idx, posrender.tile_rows(rom, bank, idx))
        sh = 14 - 2 * cc; tiles[idx][rr] = (tiles[idx][rr] & ~(3 << sh)) | (v << sh)
    ch_tiles = {i: t for i, t in tiles.items() if t != posrender.tile_rows(rom, bank, i)}
    import zlib
    nm = name.encode(); B = poses.banks(rom)
    crc = zlib.crc32(rom[B[ch] - 0x200000:B[ch + 1] - 0x200000])
    body = struct.pack('<H', len(ch_tiles))
    for i in sorted(ch_tiles):
        o = bank + 16 * i - 0x200000
        new = b''.join(struct.pack('<H', w) for w in ch_tiles[i])
        body += struct.pack('<H', i) + bytes(a ^ b for a, b in zip(new, rom[o:o + 16]))
    blob = b'SS2O' + bytes([2, ch, 2, len(nm)]) + nm + struct.pack('<I', crc) + zlib.compress(body, 9)
    open(out, 'wb').write(blob)
    return len(ch_tiles), conflicts, outside, len(blob)
def load_ss2o(path, rom=None):
    """-> (char, name, {idx: actual 16-byte tile}) ; raises if the ROM bank crc differs"""
    import zlib
    rom = rom or poses.load()
    b = open(path, 'rb').read(); assert b[:4] == b'SS2O' and b[4] == 2
    ch, mode, nl = b[5], b[6], b[7]; name = b[8:8 + nl].decode(); o = 8 + nl
    crc = struct.unpack_from('<I', b, o)[0]; o += 4
    B = poses.banks(rom)
    if zlib.crc32(rom[B[ch] - 0x200000:B[ch + 1] - 0x200000]) != crc: raise ValueError('ROM bank mismatch')
    body = zlib.decompress(b[o:]); n = struct.unpack_from('<H', body, 0)[0]; q = 2; repl = {}
    for _ in range(n):
        i = struct.unpack_from('<H', body, q)[0]; ro = B[ch] + 16 * i - 0x200000
        repl[i] = bytes(x ^ y for x, y in zip(body[q + 2:q + 18], rom[ro:ro + 16])); q += 18
    return ch, name, repl
if __name__ == '__main__':
    rom = poses.load()
    if sys.argv[1] == 'export': print('poses', export(rom, int(sys.argv[2]), sys.argv[3]))
    else: print('changed tiles %d, pixel conflicts %d, pixels outside cells %d, file %d bytes' % import_(rom, int(sys.argv[2]), sys.argv[3], sys.argv[4], *(sys.argv[5:6] or [])))
