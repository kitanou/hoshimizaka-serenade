## 音。BGM は tools/render_audio.py で生成した OGG（ループ曲は継ぎ目なし）。
define audio.op = "audio/bgm/op.ogg"
define audio.title = "audio/bgm/title.ogg"
define audio.day = "audio/bgm/day.ogg"
define audio.evening = "audio/bgm/evening.ogg"
define audio.touka = "audio/bgm/touka.ogg"
define audio.misaki = "audio/bgm/misaki.ogg"
define audio.tension = "audio/bgm/tension.ogg"

define audio.hit = "audio/se/hit.ogg"
define audio.select = "audio/se/select.ogg"
define audio.cursor = "audio/se/cursor.ogg"
define audio.door = "audio/se/door.ogg"
define audio.chime = "audio/se/chime.ogg"
define audio.footsteps = "audio/se/footsteps.ogg"
define audio.wind = "audio/se/wind.ogg"
define audio.shoot = "audio/se/shoot.ogg"
define audio.page = "audio/se/page.ogg"
define audio.heart = "audio/se/heart.ogg"

define config.sample_sound = "audio/se/select.ogg"
define config.main_menu_music = audio.title
define config.automatic_images = None
define config.has_autosave = True
define config.window_title = "星見坂のセレナーデ　体験版"

## BGM と SE の音量は Ren'Py の mixer（music / sfx）で別々に調整できる。
## 組み込みの確認メッセージを日本語にする
init 10 python:
    layout.QUIT = "ゲームを終了しますか？"
    layout.MAIN_MENU = "タイトルへ戻りますか？\nセーブしていない進行は失われます。"
    layout.LOADING = "ロードすると、セーブしていない進行は失われます。\nよろしいですか？"
    layout.OVERWRITE_SAVE = "このスロットに上書きしますか？"
    layout.DELETE_SAVE = "このセーブを削除しますか？"
    layout.END_REPLAY = "リプレイを終了しますか？"
    layout.SLOW_SKIP = "スキップを開始しますか？"
    layout.FAST_SKIP_SEEN = "次の選択肢までスキップしますか？"
    layout.FAST_SKIP_UNSEEN = "未読の文も含めて、次の選択肢までスキップしますか？"
    layout.ARE_YOU_SURE = "よろしいですか？"
    layout.CONTINUE = "前回の続きから始めますか？"
