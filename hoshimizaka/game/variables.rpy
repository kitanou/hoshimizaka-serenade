## 変数。default で宣言した変数はセーブ・ロールバックの対象になる。
## ※ ラベル名（label）はデモ配布後に改名しないこと（旧セーブが壊れる）。

default misaki_aff = 0         # ミサキ好感度
default touka_aff = 0          # 冬華好感度
default joined_astro = False   # 天文部に入部した
default promised_misaki = False  # 流星群の約束をした（ミサキ）
default met_kaede = False      # 楓と会った

# day4/day5（#25・製品版拡張）。ラベル改名と同様、追加済み default の削除改名はしない
default weekend_plan = ""      # day4 週末⑤: "misaki" / "touka" / "none"
default hill_memory = False    # 1989年の丘の記憶に触れた（⑤a/⑤c）
default fathernote = False     # 父の1966年観測ノートを見た（⑤b）。TRUE END 布石（#28）

default persistent.op_seen = False
default persistent.endings_seen = set()
default persistent.crt = True

default preferences.skip_unseen = False
