"""tile-local pattern transforms on 2bpp rows (same math the core hook would use)
row word: u16 LE, pixel c (0 = left) at bits 15-2c..14-2c"""
PATS = {
 # name: (from_idx, to_idx, mask(c, r) -> bool)
 'stripe_h':  (2, 3, lambda c, r: r % 4 == 3),             # 가로 줄무늬
 'stripe_v':  (2, 3, lambda c, r: c % 4 == 1),             # 세로 줄무늬
 'check':     (2, 1, lambda c, r: ((c >> 1) + (r >> 1)) % 2 == 0 and (c % 2 == 0) and (r % 2 == 0)),
 'check2':    (2, 3, lambda c, r: ((c >> 2) + (r >> 2)) % 2 == 0 and ((c + r) % 2 == 0)),  # 격자 체크(디더)
 'dots':      (2, 1, lambda c, r: (c % 4 == 1 and r % 4 == 1) or (c % 4 == 3 and r % 4 == 3)),
 'diag':      (2, 3, lambda c, r: (c + r) % 4 == 0),         # 사선
 'asanoha':   (2, 1, lambda c, r: (c + r) % 4 == 0 or (c - r) % 4 == 0),   # 마름모 격자
 'plaid':     (2, 3, lambda c, r: r % 4 == 0 or c % 4 == 0),
 'shade':     (2, 3, lambda c, r: (c + r) % 2 == 0),       # 50% 디더 = 어두운 옷
 'light':     (2, 1, lambda c, r: (c + r) % 2 == 0),       # 50% 디더 = 밝은 옷
}
def xform_row(w, r, pat):
    f, t, m = PATS[pat]
    for c in range(8):
        sh = 14 - 2 * c
        if ((w >> sh) & 3) == f and m(c, r):
            w = (w & ~(3 << sh)) | (t << sh)
    return w
def xform_tile(b16, pat):
    out = bytearray(16)
    for r in range(8):
        w = b16[2*r] | (b16[2*r+1] << 8)
        w = xform_row(w, r, pat)
        out[2*r] = w & 0xFF; out[2*r+1] = w >> 8
    return bytes(out)
def xform_chr(chr_, lo, hi, pat):
    b = bytearray(chr_)
    for t in range(lo, hi):
        b[t*16:t*16+16] = xform_tile(bytes(b[t*16:t*16+16]), pat)
    return bytes(b)
