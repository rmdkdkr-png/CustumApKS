#!/usr/bin/env python3
"""ss2probe — 사무쇼2(NGPC) 램 탐색용 libretro 구동기 (가상리그 0단계).

ss2-sp-core 코어(.so)를 ctypes 로 직접 돌린다. 프레임 생성은 끈다(원래 게임 그대로).
  p = Probe(core, rom, workdir)
  p.run(n) · p.press('A', 8) · p.hold('R') · p.release() · p.peek(0x5A46) · p.poke(0x5C46, 0)
  p.save('x.st') · p.load('x.st') · p.ram() (16KB, 0x4000~0x7FFF) · p.shot('a.png')
  p.log_ram(n) → [bytes, ...] (프레임마다 16KB)
  lk = Link(core, rom, workdir) — 링크 케이블로 이은 두 대(lk.a = 1P 기기, lk.b = 2P 기기), lk.run(n) 은 번갈아 한 프레임씩
주소는 CPU 주소(0x4000~0x7FFF)로 받는다 — 코어 SYSTEM_RAM 오프셋 = 주소 − 0x4000.
버튼: U D L R A B O(Option) — A·B 는 NGPC 버튼 이름 그대로(코어 libretro 매핑 B↔A 를 여기서 바꿈).
"""
import ctypes as C, os, struct, zlib

RAM_BASE = 0x4000
W, H = 160, 152
_ENV_SET_PIXEL_FORMAT, _ENV_GET_VARIABLE, _ENV_GET_VARIABLE_UPDATE = 10, 15, 17
_ENV_GET_SYSTEM_DIRECTORY, _ENV_GET_SAVE_DIRECTORY = 9, 31
_ENV_GET_AUDIO_VIDEO_ENABLE, _ENV_GET_CAN_DUPE = 47 | 0x10000, 3
_ENV_SET_MESSAGE, _ENV_GET_TARGET_REFRESH_RATE, _ENV_SET_SYSTEM_AV_INFO = 6, 50, 32
# libretro joypad ids
_JP = {'B': 0, 'O': 3, 'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 8}   # NGPC A = libretro B(0)? 아래 _MAP 참고
_MAP = {'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 0, 'B': 8, 'O': 3}  # fgrom 과 같은 매핑: NGPC A→JOYPAD_B(0), NGPC B→JOYPAD_A(8)

class _Var(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
class _GameInfo(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]

ENV_T = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VID_T = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUD_T = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDB_T = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_T = C.CFUNCTYPE(None)
INST_T = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)

OPTIONS = {b'ngp_framegen': b'off', b'ngp_runahead': b'0', b'ngp_framegen_idle': b'off', b'ngp_framegen_motion': b'off'}

class Probe:
    def __init__(self, core, rom, workdir, link=None):
        """link=(읽을 파이프, 쓸 파이프) 를 주면 코어를 workdir 에 복사해 따로 올린다
        (같은 경로를 두 번 열면 같은 인스턴스가 와서 램·링크 상태를 나눠 쓴다)."""
        os.makedirs(workdir, exist_ok=True)
        self.workdir = os.path.abspath(workdir).encode()
        self._wd = C.c_char_p(self.workdir)
        if link:
            import shutil
            cp = os.path.join(os.path.abspath(workdir), '_linkcore.so')
            shutil.copyfile(core, cp); core = cp
        self.lib = C.CDLL(os.path.abspath(core))
        self.mask = 0
        self.frame = 0
        self.fb = bytearray(W * H * 2)
        self._keep = []
        self._varvals = {k: C.c_char_p(v) for k, v in OPTIONS.items()}
        L = self.lib
        self._env = ENV_T(self._env_cb); self._vid = VID_T(self._vid_cb)
        self._aud = AUD_T(lambda l, r: None); self._audb = AUDB_T(lambda d, n: n)
        self._poll = POLL_T(lambda: None); self._inst = INST_T(self._in_cb)
        L.retro_set_environment(self._env); L.retro_set_video_refresh(self._vid)
        L.retro_set_audio_sample(self._aud); L.retro_set_audio_sample_batch(self._audb)
        L.retro_set_input_poll(self._poll); L.retro_set_input_state(self._inst)
        if link:   # 코어는 retro_init 순간의 환경변수로 파이프를 잡는다
            os.environ['NGP_LINK_IN'], os.environ['NGP_LINK_OUT'] = link
        L.retro_init()
        if link:
            del os.environ['NGP_LINK_IN'], os.environ['NGP_LINK_OUT']
        data = open(rom, 'rb').read()
        self._rom = C.create_string_buffer(data, len(data))
        gi = _GameInfo(os.path.abspath(rom).encode(), C.cast(self._rom, C.c_void_p), len(data), None)
        if not L.retro_load_game(C.byref(gi)):
            raise RuntimeError('retro_load_game 실패')
        L.retro_get_memory_data.restype = C.c_void_p
        L.retro_get_memory_size.restype = C.c_size_t
        L.retro_serialize_size.restype = C.c_size_t
        self._ramp = L.retro_get_memory_data(2)
        self._rams = L.retro_get_memory_size(2)
        assert self._ramp and self._rams == 16384, ('SYSTEM_RAM', self._rams)
        self.rambuf = (C.c_uint8 * self._rams).from_address(self._ramp)

    # ── libretro 콜백 ──
    def _env_cb(self, cmd, data):
        cmd &= 0xFFFF if cmd < 0x10000 else 0xFFFFFFFF
        if cmd == _ENV_SET_PIXEL_FORMAT:
            return C.cast(data, C.POINTER(C.c_int))[0] == 2      # RGB565
        if cmd == _ENV_GET_VARIABLE:
            v = C.cast(data, C.POINTER(_Var))[0]
            val = self._varvals.get(v.key)
            if val is None: return False
            C.cast(data, C.POINTER(_Var))[0].value = val.value
            return True
        if cmd == _ENV_GET_VARIABLE_UPDATE:
            C.cast(data, C.POINTER(C.c_bool))[0] = False; return True
        if cmd in (_ENV_GET_SYSTEM_DIRECTORY, _ENV_GET_SAVE_DIRECTORY):
            C.cast(data, C.POINTER(C.c_char_p))[0] = self._wd.value; return True
        if cmd == 47:   # GET_AUDIO_VIDEO_ENABLE (EXPERIMENTAL flag 떼고)
            C.cast(data, C.POINTER(C.c_int))[0] = 3; return True
        if cmd == _ENV_GET_CAN_DUPE:
            C.cast(data, C.POINTER(C.c_bool))[0] = True; return True
        if cmd == _ENV_GET_TARGET_REFRESH_RATE:
            C.cast(data, C.POINTER(C.c_float))[0] = 60.0; return True
        if cmd in (_ENV_SET_MESSAGE, _ENV_SET_SYSTEM_AV_INFO):
            return True
        return False

    def _vid_cb(self, data, w, h, pitch):
        if not data: return
        w = min(w, W); h = min(h, H)
        src = (C.c_uint8 * (pitch * h)).from_address(data)
        for y in range(h):
            self.fb[y * W * 2:(y * W + w) * 2] = bytes(src[y * pitch:y * pitch + w * 2])

    def _in_cb(self, port, dev, idx, id_):
        if port != 0 or dev != 1: return 0
        if id_ == 256: return self.mask
        return (self.mask >> id_) & 1 if id_ < 16 else 0

    # ── 조작 ──
    def run(self, n=1):
        for _ in range(n):
            self.lib.retro_run(); self.frame += 1
    def hold(self, *btns):
        for b in btns: self.mask |= 1 << _MAP[b]
    def release(self, *btns):
        if not btns: self.mask = 0
        for b in btns: self.mask &= ~(1 << _MAP[b])
    def press(self, btns, frames=6, after=0):
        """btns: 'A' 또는 'DR' 처럼 여러 글자 = 동시에"""
        self.hold(*btns); self.run(frames); self.release(*btns); self.run(after)

    # ── 램 ──
    def peek(self, addr, n=1):
        o = addr - RAM_BASE
        if n == 1: return self.rambuf[o]
        return bytes(self.rambuf[o:o + n])
    def peek16(self, addr):
        o = addr - RAM_BASE; return self.rambuf[o] | (self.rambuf[o + 1] << 8)
    def poke(self, addr, val):
        self.rambuf[addr - RAM_BASE] = val & 0xFF
    def ram(self):
        return bytes(self.rambuf)
    def log_ram(self, n, hold=None):
        out = []
        for _ in range(n):
            self.run(1); out.append(bytes(self.rambuf))
        return out

    # ── 상태 ──
    def save(self, path):
        n = self.lib.retro_serialize_size()
        b = C.create_string_buffer(n)
        if not self.lib.retro_serialize(b, n): raise RuntimeError('serialize 실패')
        open(path, 'wb').write(b.raw)
    def load(self, path):
        d = open(path, 'rb').read()
        b = C.create_string_buffer(d, len(d))
        if not self.lib.retro_unserialize(b, len(d)): raise RuntimeError('unserialize 실패: ' + path)

    # ── 화면 ──
    def shot(self, path, scale=2):
        rows = []
        for y in range(H):
            row = bytearray(b'\0')
            for x in range(W):
                v = self.fb[(y * W + x) * 2] | (self.fb[(y * W + x) * 2 + 1] << 8)
                px = bytes((((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31))
                row += px * scale
            rows += [bytes(row)] * scale
        def ch(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W * scale, H * scale, 8, 2, 0, 0, 0))
                               + ch(b'IDAT', zlib.compress(b''.join(rows), 6)) + ch(b'IEND', b''))


class Link:
    """링크 케이블로 이은 두 대. 실제 기기처럼 같은 박자로 돌아야 악수가 되므로 한 프레임씩 번갈아 돌린다
    (ss2-sp-core tools/svc/linkrun.c 와 같은 방식)."""
    def __init__(self, core, rom, workdir):
        wd = os.path.abspath(workdir); os.makedirs(wd, exist_ok=True)
        a2b, b2a = os.path.join(wd, 'a2b.fifo'), os.path.join(wd, 'b2a.fifo')
        for f in (a2b, b2a):
            if os.path.exists(f): os.unlink(f)
            os.mkfifo(f, 0o600)
        self.a = Probe(core, rom, os.path.join(wd, 'a'), link=(b2a, a2b))
        self.b = Probe(core, rom, os.path.join(wd, 'b'), link=(a2b, b2a))
    def run(self, n=1):
        for _ in range(n):
            self.a.run(1); self.b.run(1)
    def press(self, who, btns, frames=6, after=0):
        """who: 'a' / 'b' / 'ab'(둘 다 같이)"""
        ps = [getattr(self, w) for w in who]
        for p in ps: p.hold(*btns)
        self.run(frames)
        for p in ps: p.release(*btns)
        self.run(after)


# ── 명령줄: 감시(watch) — ngp_state 의 watch 와 같은 용도 ──
WATCH_DEFAULT = '0x40A7,0x41C0,0x5A46,0x5C46,0x5821,0x5822,0x5823,0x5824,0x5825,0x57DF,0x57E0,0x5D51,0x57FE'

def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(description='ss2probe watch — 상태를 불러와 N 프레임 돌리며 주소 값이 바뀔 때마다 찍는다')
    ap.add_argument('cmd', choices=['watch'])
    ap.add_argument('--core', required=True); ap.add_argument('--rom', required=True)
    ap.add_argument('--state', help='시작 상태(.st) — 없으면 전원 켠 직후부터')
    ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--addrs', default=WATCH_DEFAULT, help='쉼표로 구분한 CPU 주소')
    ap.add_argument('--poke', action='append', default=[], help='프레임:주소=값 (예: 150:0x5C46=0) — 여러 번')
    ap.add_argument('--press', action='append', default=[], help='프레임:버튼[:길이] (예: 20:A:8)')
    ap.add_argument('--workdir', default='./_probe')
    a = ap.parse_args(argv)
    p = Probe(a.core, a.rom, a.workdir)
    if a.state: p.load(a.state)
    addrs = [int(x, 16) for x in a.addrs.split(',')]
    pokes = {}
    for s in a.poke:
        f, kv = s.split(':', 1); ad, v = kv.split('=')
        pokes.setdefault(int(f), []).append((int(ad, 16), int(v, 0)))
    presses = {}
    for s in a.press:
        q = s.split(':'); presses[int(q[0])] = (q[1], int(q[2]) if len(q) > 2 else 8)
    held = {}
    prev = None
    print('frame ' + ' '.join('%04X' % ad for ad in addrs))
    for f in range(a.frames):
        for ad, v in pokes.get(f, []): p.poke(ad, v)
        if f in presses: b, n = presses[f]; p.hold(*b); held[f + n] = b
        if f in held: p.release(*held.pop(f))
        p.run(1)
        cur = tuple(p.peek(ad) for ad in addrs)
        if cur != prev:
            print('%5d ' % f + ' '.join('%4d' % v for v in cur)); prev = cur

if __name__ == '__main__':
    import sys
    _main(sys.argv[1:])
