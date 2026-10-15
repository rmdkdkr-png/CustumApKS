"""render pose records straight from ROM (no emulator) — layout cell = (row<<4)|col on an 8px grid"""
import poses
from PIL import Image
def tile_rows(rom, bank, idx):
    o = bank + idx * 16 - 0x200000
    return [rom[o + 2*r] | (rom[o + 2*r + 1] << 8) for r in range(8)]
def render(rom, ch, rec, cols=(None, (255, 230, 190), (60, 120, 230), (40, 30, 60)), scale=1, grid=False, tiles=None, bg=(90, 110, 90)):
    """tiles: optional dict idx -> 8 row words overriding ROM (for edited previews)"""
    bank = poses.banks(rom)[ch]
    W, H = 8 * 8, 8 * 8
    im = Image.new('RGB', (W, H), bg); px = im.load()
    for (f, cell), idx in zip(rec['layout'], rec['idx']):
        r0, c0 = (cell >> 4) * 8, (cell & 15) * 8
        rows = tiles[idx] if tiles and idx in tiles else tile_rows(rom, bank, idx)
        hf, vf = f & 0x40, f & 0x20
        for r in range(8):
            w = rows[7 - r if vf else r]
            for c in range(8):
                v = (w >> (14 - 2 * (7 - c if hf else c))) & 3
                if v: px[c0 + c, r0 + r] = cols[v]
    if grid:
        for (f, cell) in rec['layout']:
            r0, c0 = (cell >> 4) * 8, (cell & 15) * 8
            for k in range(8):
                for (x, y) in ((c0 + k, r0), (c0, r0 + k)):
                    if px[x, y] == bg: px[x, y] = (110, 130, 110)
    if scale != 1: im = im.resize((W * scale, H * scale), Image.NEAREST)
    return im
