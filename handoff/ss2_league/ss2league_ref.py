#!/usr/bin/env python3
"""ss2league_ref — 가상리그 0단계 결과로 만든 «결과 감지 + 대진 덮어쓰기 + 카드 무력화» 참조 구현.

앱(코어 바깥)이 매 프레임 SYSTEM RAM 을 읽고 쓸 수 있다고 보고 그 규칙만 옮긴 것이다. 주소는 CPU 주소(0x4000~).
  league = League(schedule=[(2,1),(9,0),(13,1)])     # (상대 번호 0~14, 유파 0 수라 / 1 나찰)
  매 프레임: ev = league.step(peek, poke)            # 매치가 결판난 프레임에만 dict 를 돌려준다
규칙(0단계 검증 — handoff/ss2_league/0단계_주소탐색_결과.md):
  · 결과: 0x5824 bit7 이 0→1 로 바뀌는 첫 프레임 1회. 승자 = 0x40 P1 / 0x20 P2 / 둘 다 없으면 무승부(0x90, P1 은 이어하기 화면).
    붙은 뒤 bit7 을 한 번 0 으로 본 다음부터만 센다(지난 매치의 남은 값으로 잘못 쏘지 않게).
  · 대진: 0x57DF(상대)·0x57E0(유파)를 매 프레임 목표값으로 쓰고, 목표는 결판 프레임에만 다음 것으로 바꾼다.
    (게임이 다음 상대를 뽑는 프레임에 덮어쓰고, 매치 중에 바꾸면 다음 라운드부터 상대가 바뀌기 때문)
  · 카드: 0x57DC·0x57DD = 0xFF (카드 없음) 를 결판 프레임부터 다음 전투 로드 전까지 — 여기서는 매 프레임.
"""
OPP, STY = 0x57DF, 0x57E0
RES, W1, W2, NEED = 0x5824, 0x5821, 0x5822, 0x5813
CARD1, CARD2 = 0x57DC, 0x57DD
SAFE_IDS = range(0, 15)           # 15 간다라·16 이상은 멈추거나 깨짐(0단계 검증)

class League:
    def __init__(self, schedule, no_cards=True):
        for i, s in schedule:
            assert i in SAFE_IDS and s in (0, 1), (i, s)
        self.schedule = list(schedule)
        self.k = 0                 # 지금 목표로 쓰는 대진 번호
        self.armed = False         # bit7 을 0 으로 본 뒤에만 쏜다
        self.no_cards = no_cards
        self.results = []

    def target(self):
        return self.schedule[min(self.k, len(self.schedule) - 1)]

    def step(self, peek, poke):
        r = peek(RES)
        ev = None
        if not (r & 0x80):
            self.armed = True
        elif self.armed:
            self.armed = False
            win = 'P1' if r & 0x40 else ('P2' if r & 0x20 else 'DRAW')
            ev = {'match': self.k, 'opp': self.target(), 'winner': win, 'bits': r,
                  'score': (peek(W1), peek(W2)), 'need': peek(NEED)}
            self.results.append(ev)
            self.k += 1            # 다음 판 목표로 — 게임의 뽑기 프레임 뒤에도 매 프레임 쓰고 있으므로 이긴다
        i, s = self.target()
        poke(OPP, i); poke(STY, s)
        if self.no_cards:
            poke(CARD1, 0xFF); poke(CARD2, 0xFF)
        return ev
