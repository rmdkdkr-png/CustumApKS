"""프레임 미터 모양 미리보기(롬 그림 없음) — 실측 칸 줄(dt_*.json)을 앱 색으로 그린다.  python3 mock.py <dt json> <out.png>"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
FONT = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/fgint/app/src/main/assets/fonts/pixel.ttf'
COL = {'.': (38, 38, 43), '-': (107, 115, 128), 'S': (47, 208, 122), 'A': (255, 61, 87), 'R': (58, 130, 255), '=': (53, 201, 201),
       'h': (255, 212, 59), 'b': (255, 158, 44), 'd': (176, 124, 255), '|': (80, 80, 80), '*': (58, 130, 255), 'p': (53, 201, 201)}
data = json.load(open(sys.argv[1]))
names = sys.argv[3].split(',') if len(sys.argv) > 3 else list(data)
CW, CH, GAP, LBL = 9, 14, 1, 40
f = ImageFont.truetype(FONT, 12); fs = ImageFont.truetype(FONT, 11)
W = LBL + 80 * (CW + GAP) + 16; blockH = 2 * CH + 3 * GAP + 24 + 16
img = Image.new('RGB', (W, 12 + blockH * len(names)), (14, 12, 10))
d = ImageDraw.Draw(img)
y = 8
for nm in names:
    r = data[nm]
    d.text((8, y), nm, font=fs, fill=(150, 140, 120)); y += 14
    for row, lab in ((r['m0'], '나'), (r['m1'], '상대')):
        d.text((8, y + 1), lab, font=f, fill=(255, 215, 106))
        for i in range(80):
            ch = row[i] if i < len(row) else ' '
            x = LBL + i * (CW + GAP)
            if ch == ' ':
                d.rectangle([x, y, x + CW - 1, y + CH - 1], outline=(40, 40, 44)); continue
            d.rectangle([x, y, x + CW - 1, y + CH - 1], fill=COL.get(ch, (90, 90, 90)))
            if ch == '*': d.rectangle([x, y + CH - 4, x + CW - 1, y + CH - 1], fill=(255, 61, 87))
            if ch == 'p': d.rectangle([x, y, x + CW - 1, y + 3], fill=(255, 255, 255))
            if ch == '|':
                for k in range(3): d.point((x + 4, y + 3 + k * 4), fill=(200, 200, 200))
        y += CH + GAP
    d.text((LBL, y + 2), (r['line'] or '—').replace('\u2212', '-'), font=f, fill=(255, 235, 200)); y += 32
img.save(sys.argv[2])
print(img.size)
