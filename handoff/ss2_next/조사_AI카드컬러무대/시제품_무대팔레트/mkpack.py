"""build a 2MB+pack test image (scratch) with a 'new' stage at HIROM 0x800000 made from entry-1 data (mirrored layout),
and the overlay list that wires it in (stage entry 8, palset 8 list, palettes in padding 0x25A9D8, bout table)."""
import os, json
import rs
W = os.environ['LEAGUE_WORK']
rom = bytearray(open(os.environ['ROM_KO'], 'rb').read())
src = rs.stage(1)
bm0 = src['bm'] - 2
hdr = bytes([rs.r8(bm0), rs.r8(bm0 + 1)])
blk = [rs.r8(src['bm'] + i) for i in range(40)]
# mirror the whole stage: reverse columns, toggle metatile H-flip bit 7
mir = []
for y in range(4):
    row = blk[y * 10:(y + 1) * 10][::-1]
    mir += [b ^ 0x80 for b in row]
nmt = max(b & 0x7F for b in blk) + 1
mt = bytes(rom[src['mt'] - 0x200000: src['mt'] - 0x200000 + nmt * 32])
tiles = bytes(rom[src['tp'] - 0x200000: src['tp'] - 0x200000 + src['cnt']])
pack = bytearray(b'\xFF' * 0x2000)
pack[0:2] = hdr; pack[2:42] = bytes(mir); pack[0x40:0x40 + len(mt)] = mt; pack[0x1000 - 0x1000 + 0x1000 - 0x1000:0] = b''
TILE_OFF = 0x1000
BASE = int(os.environ.get('PACK_BASE', '0x800000'), 16)
if BASE >= 0x800000:
    img = bytearray(rom) + bytearray(b'\xFF' * 0x10000); fo = 0x200000 + (BASE - 0x800000); name = 'ko_plus_pack.ngc'
else:
    img = bytearray(rom); fo = BASE - 0x200000; name = 'ko_hole_pack.ngc'
    assert all(x == 0xFF for x in img[fo:fo + TILE_OFF + len(tiles)]), 'target not free (FF)'
img[fo:fo + 0x40 + len(mt)] = pack[:0x40 + len(mt)]
img[fo + TILE_OFF:fo + TILE_OFF + len(tiles)] = tiles
open(W + '/' + name, 'wb').write(img)
if BASE >= 0x800000: open(W + '/hirom_pack.bin', 'wb').write(bytes(img[0x200000:]))
# overlays
ov = []
tp = BASE + TILE_OFF
ent = bytes([src['cnt'] & 0xFF, src['cnt'] >> 8, tp & 0xFF, (tp >> 8) & 0xFF, tp >> 16, 8]) + (BASE - tp & 0xFFFF).to_bytes(2, 'little') + (BASE + 0x40 - tp & 0xFFFF).to_bytes(2, 'little') + bytes([src['cnt'] & 0xFF, src['cnt'] >> 8, 4, 0, 0, 0])
ov.append((0x2CA0E2 + 16 * 8, ent))
# new palettes in padding: entry-1 palettes with R<->G swapped ("aurora" test colours)
def sw(c): r, g, b = c & 15, (c >> 4) & 15, (c >> 8) & 15; return g | r << 4 | b << 8
PAD = 0x25A9D8
pal = b''
for p in src['pals']:
    pal += b''.join(bytes(((x if j == 0 else sw(x)) & 0xFF, (x if j == 0 else sw(x)) >> 8)) for j, x in enumerate(p))
ov.append((PAD, pal))
lst = bytes([0x86]) + sw(src['bg']).to_bytes(2, 'little') + b''.join((PAD - rs.PALTAB + 8 * k).to_bytes(2, 'little') for k in range(len(src['pals']))) + b'\xFF\xFF'
ov.append((0x2D8193 - 3, lst))
ov.append((0x239056, bytes([0x80, 0, 1, 0, 0x80, 0, 1, 0])))   # bout 0 -> entry 8 in all rounds
json.dump([(a, b.hex()) for a, b in ov], open(W + '/pack_overlay.json', 'w'))
print('image', len(img), 'tiles', len(tiles), 'metatiles', nmt, 'entry8', ent.hex(), 'palset list', lst.hex())
