## ---- ルート進入判定の純関数（#43）----
## 方針: 分岐条件を脚本（menu の if）へ直書きせず、このファイルの純関数に集約する。
## 条件そのものは docs/route-flow.md §1.4・§3 に先に明記済み（#28/#43 の指示順: docs→code→test）。
## testcase route_logic がこの関数だけを直接叩いて境界値・真理表・到達不能検査を行う。

init python:
    ## 好感度ゲート: 個別ルート进入に必要な最低好感度（day5 選択⑥・ミサキ/冬華共通）
    AFF_GATE = 4

    ## 1プレイで共通ルート(①〜⑤)で獲得できる好感度の合計上限。
    ## ①day1 / ②day2 / ③day3場所 / ④day3約束(④a=ミサキ+1, ④b=冬華+1, ④c=0) / ⑤day4週末(0含む)
    ## の5回それぞれがどちらか一方へ +1 まで → 配分和は常に AFF_BUDGET 以下。
    AFF_BUDGET = 5

    def gate_misaki(promised_misaki, misaki_aff):
        """day5⑥「ミサキ（流星群の夜へ）」ゲート: ④aの約束フラグ ∧ 好感度>=AFF_GATE"""
        return bool(promised_misaki) and misaki_aff >= AFF_GATE

    def gate_touka(joined_astro, touka_aff):
        """day5⑥「冬華（屋上の観測夜へ）」ゲート: 天文部参加フラグ ∧ 好感度>=AFF_GATE"""
        return bool(joined_astro) and touka_aff >= AFF_GATE

    def gate_true(endings_seen):
        """day5⑥「みんなの丘」ゲート: 両 GOOD END 視聴済み（persistent.endings_seen）。
        好感度は要求しない（route-flow §3 実装条件そのまま）"""
        return ("misaki_good" in endings_seen) and ("touka_good" in endings_seen)
