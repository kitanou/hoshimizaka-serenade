## 星見坂のセレナーデ 体験版 ver.0.97
## 起動 → splashscreen（BIOS風）→ 初回のみ OP → タイトル → label start

label splashscreen:
    $ quick_menu = False
    scene black
    call screen bios_boot
    if not persistent.op_seen:
        call op
    $ quick_menu = True
    return

label start:
    $ quick_menu = True
    $ misaki_aff = 0
    $ touka_aff = 0
    $ joined_astro = False
    $ promised_misaki = False
    $ met_kaede = False
    $ renpy.force_autosave()
    jump prologue

## 日付テロップ
label date_card(txt):
    window hide
    scene black with fade
    play sound audio.page
    show expression Text(txt, size=26, bold=True, color="#ffffff", outlines=[(3, "#2a0f5c", 0, 0)]) as datecard at truecenter
    with dissolve
    $ renpy.pause(1.8)
    hide datecard
    with dissolve
    return
