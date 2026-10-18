init python:
    from renpy.display.core import absolute
    from line_displayable import LineDisplayable
    import math

    # Screen dimensions & center coordinates
    screen_x, screen_y = config.screen_width, config.screen_height
    xloc = screen_x / 2 
    yloc = screen_y / 2

    # Click / motion control
    click_flag = False

    def play_motion(motion_name):
        try:
            if motion_name == "idle":
                motion_name = "m01"
            renpy.store.current_motion = motion_name
            renpy.show("hiyori {}".format(motion_name))
        except Exception as e:
            print("Error playing motion:", e)

    def handle_click():
        global click_flag
        if hiyori_obj is not None:
            motions = list(hiyori_obj.common.motions.keys())
            if motions:
                next_motion = motions[renpy.random.randint(0, len(motions) - 1)]
                play_motion(next_motion)
        click_flag = True

    def compute_pos_raw(value, room):
        if hasattr(absolute, "compute_raw"):
            return absolute.compute_raw(value, room)
        if isinstance(value, float):
            return value * room
        return value

    # Scaling and positioning logic from Ren'Py Live2D module
    def get_scaled_size(live_obj):
        zoom = live_obj.zoom
        sw, sh = live_obj.common.model.get_size()
        if zoom is None:
            top = compute_pos_raw(live_obj.top, sh)
            base = compute_pos_raw(live_obj.base, sh)
            size = max(base - top, 1.0)
            zoom = 1.0 * live_obj.height * renpy.config.screen_height / size
        else:
            size = sh
            top = 0
        return top, base, sw * zoom, size * zoom

    def handle_position(live_obj):
        top, base, sw, sh = get_scaled_size(live_obj)
        return [(0, (-top * base)), (sw, sh * 0.2)]

    def hiyori_update_func(live_obj, show_time):
        # Update eyes toward mouse / touch coordinates
        pos = handle_position(live_obj)
        x, y = renpy.get_mouse_pos()
        vec_x, vec_y = (x - xloc, -1 * (y - pos[1][1]))
        magnitude = math.sqrt(vec_x ** 2 + vec_y ** 2)
        if magnitude > 0:
            norm_x, norm_y = vec_x / magnitude, vec_y / magnitude
        else:
            norm_x, norm_y = 0.0, 0.0
        live_obj.blend_parameter("ParamEyeBallX", "Overwrite", norm_x)
        live_obj.blend_parameter("ParamEyeBallY", "Overwrite", norm_y)
        return 1.0 / 30.0

    # Live2D motion aliases mapping shorthand and idle to model filenames
    hiyori_aliases = {
        "idle": "hiyori_m01",
        "m01": "hiyori_m01",
        "m02": "hiyori_m02",
        "m03": "hiyori_m03",
        "m04": "hiyori_m04",
        "m05": "hiyori_m05",
        "m06": "hiyori_m06",
        "m07": "hiyori_m07",
        "m08": "hiyori_m08",
    }

    # Define Live2D model instance
    hiyori_obj = Live2D("Resources/hiyori_free", base=0.9, update_function=hiyori_update_func, loop=True, default_fade=0.0, aliases=hiyori_aliases)
    t, b, hiyori_w, hiyori_h = get_scaled_size(hiyori_obj)
    line = LineDisplayable([[(xloc - 10, hiyori_h * 0.2), (xloc + 10, hiyori_h * 0.2)]], color="#f00", width=2)

image hiyori = hiyori_obj

# Define Movie displayables for in-game video test
image sample_movie_widesample = Movie(play="video/widesample.webm", loop=True, size=(854, 480))
image sample_movie_writing = Movie(play="video/writing.webm", loop=True, size=(270, 480))

# Define game character
define h = Character("Hiyori", color="#ff70a6")

# Test store variables (default keyword registers them into Ren'Py save/cheat store)
default player_name = "Tomie"
default gold = 9999
default gems = 150
default affection = 75
default player_level = 5
default is_vip = True
default inventory = ["Health Potion", "Live2D Charm", "Mystic Key"]
default stat_str = 18
default stat_agi = 24
default stat_int = 30
default stats = {"str": 18, "agi": 24, "int": 30}
default current_motion = "idle"
default show_hud = True
default show_tracking_line = False

# Video player test state
default current_video_title = ""
default current_video_displayable = ""

# Shop & inventory variables
default potion_count = 3
default elixir_count = 1
default charm_count = 1
default key_count = 0

# Dice game & freezing cheat test variables
default dice_bet = 100
default player_dice = 0
default opponent_dice = 0
default dice_wins = 0
default dice_losses = 0
default dice_streak = 0
default lucky_modifier = 0

# Screen for optional eye debug vector and tapping Hiyori
screen displayLine():
    if show_tracking_line:
        add line
    # Interactive tap/click zone over Hiyori to trigger random motions
    button:
        xalign 0.5
        yalign 0.35
        xysize (360, 650)
        background None
        action Function(handle_click)

# Persistent Cheat & Variable Test Bench HUD (top-left)
screen cheat_debug_hud():
    zorder 100
    if show_hud:
        frame:
            xalign 0.02
            yalign 0.02
            background "#0f172acc"
            padding (16, 12)
            
            vbox:
                spacing 4
                text "{b}{color=#ff70a6}Live2D & Cheat Test Bench{/color}{/b}" size 15
                null height 2
                text "Player: {b}[player_name]{/b} (Lv.[player_level])" size 13
                text "Gold: {color=#ffd166}{b}[gold]{/b}{/color}  |  Gems: {color=#06d6a0}{b}[gems]{/b}{/color}" size 13
                text "Affection: {color=#ef476f}{b}[affection]/100{/b}{/color}" size 13
                text "STR: [stat_str]  |  AGI: [stat_agi]  |  INT: [stat_int]" size 12
                text "Potions: [potion_count]  |  Elixirs: [elixir_count]  |  Keys: [key_count]" size 11
                text "Bet: [dice_bet] G  |  Wins: [dice_wins]  |  Streak: [dice_streak]" size 11
                text "Motion: {color=#38bdf8}{b}[current_motion]{/b}{/color}" size 12

    # Floating HUD action pills in top-right
    hbox:
        xalign 0.98
        yalign 0.02
        spacing 6

        textbutton "(API Matrix)":
            text_size 12
            text_color "#ffffff"
            background "#2563ebcc"
            padding (10, 6)
            action Show("api_compatibility_inspector")

        textbutton ("Hide HUD" if show_hud else "Show HUD"):
            text_size 12
            text_color "#ffffff"
            background "#1e293bcc"
            padding (10, 6)
            action ToggleVariable("show_hud")

transform positioning:
    xpos int(xloc) - int(hiyori_w / 2)

label start:
    show screen displayLine
    show screen cheat_debug_hud
    show hiyori at positioning
    $ play_motion("idle")

    h "Hello! Welcome to the Live2D & Engine Test Bench!"

    # --- Test 1: Soft Keyboard IME Input ---
    $ input_name = renpy.input("Please enter your name (IME Text Input Test):", default=player_name, length=16)
    $ input_name = input_name.strip()
    if input_name:
        $ player_name = input_name

    h "Nice to meet you, [player_name]! Your input was committed successfully without any engine crashes!"

label main_menu_loop:
    menu:
        h "What would you like to test next?"

        "(API) Compatibility Matrix (Live Subsystem Audit)":
            show screen api_compatibility_inspector
            h "Opened the API Compatibility Matrix! Click Close or press Escape to return."
            jump main_menu_loop

        "(Shop) Item Merchant (Buy & Sell Test)":
            jump shop_menu

        "(Dice) High-Low Game (Freezing Cheat Test)":
            jump dice_game_menu

        "(Media) Audio & Video Player (MP3, WAV, WebM)":
            jump media_test_menu

        "(Input) Re-test Soft Keyboard (Android IME)":
            $ input_name = renpy.input("Type a new name:", default=player_name, length=20)
            $ input_name = input_name.strip()
            if input_name:
                $ player_name = input_name
            h "Your name is now set to [player_name]! Notice how the HUD in the top-left updated instantly."
            jump main_menu_loop

        "(Motion) Switch Live2D Motions (m01 - m08)":
            jump motion_selector_menu

        "(Cheats) Test Variables (+1000 Gold, +10 Affection)":
            $ gold += 1000
            $ affection += 10
            $ gems += 25
            h "Added +1000 Gold, +25 Gems, and +10 Affection!"
            h "Tip: You can also use GPlayer's in-game Cheat Engine menu to modify these variables directly, and the HUD will update in real time!"
            jump main_menu_loop

        "(Inspect) Detailed Cheat Variables State":
            h "Current variable states:\nPlayer: [player_name] (Level [player_level]) | VIP: [is_vip]\nGold: [gold] | Gems: [gems] | Affection: [affection]/100\nStats: STR=[stat_str], AGI=[stat_agi], INT=[stat_int]\nInventory: Potions=[potion_count], Elixirs=[elixir_count], Keys=[key_count]"
            jump main_menu_loop

        "(Debug) Toggle Eye-Tracking Indicator Line":
            $ show_tracking_line = not show_tracking_line
            if show_tracking_line:
                h "Eye-tracking indicator is now ON."
            else:
                h "Eye-tracking indicator is now OFF."
            jump main_menu_loop

label motion_selector_menu:
    menu:
        h "Select a Live2D motion to trigger on Hiyori:"

        "(Idle) Default Breathing Motion (m01 Loop)":
            $ play_motion("idle")
            h "Returned to default idle motion!"
            jump main_menu_loop

        "Motion 1 (Gentle Greeting)":
            $ play_motion("m01")
            h "Playing motion 01!"
            jump main_menu_loop

        "Motion 2 (Cheerful Nod)":
            $ play_motion("m02")
            h "Playing motion 02!"
            jump main_menu_loop

        "Motion 3 (Surprised Look)":
            $ play_motion("m03")
            h "Playing motion 03!"
            jump main_menu_loop

        "Motion 4 (Happy Smile)":
            $ play_motion("m04")
            h "Playing motion 04!"
            jump main_menu_loop

        "Motion 5 (Thinking / Pondering)":
            $ play_motion("m05")
            h "Playing motion 05!"
            jump main_menu_loop

        "Motion 6 (Shy / Blushing)":
            $ play_motion("m06")
            h "Playing motion 06!"
            jump main_menu_loop

        "Motion 7 (Energetic Wave)":
            $ play_motion("m07")
            h "Playing motion 07!"
            jump main_menu_loop

        "Motion 8 (Playful Wink)":
            $ play_motion("m08")
            h "Playing motion 08!"
            jump main_menu_loop

# Screen for embedded in-engine video player testing (Movie displayable)
screen video_player_modal():
    modal True
    zorder 200
    add "#000000dd"
    frame:
        xalign 0.5
        yalign 0.5
        background "#0f172acc"
        padding (24, 20)
        vbox:
            spacing 10
            xalign 0.5
            text "{b}(MOVIE TEST) In-Engine Video Displayable (Movie){/b}" size 17 color "#38bdf8" xalign 0.5
            text "[current_video_title]" size 13 color "#94a3b8" xalign 0.5
            null height 6
            add current_video_displayable xalign 0.5
            null height 10
            textbutton "Close Video Player":
                xalign 0.5
                background "#dc2626"
                hover_background "#b91c1c"
                padding (28, 10)
                text_size 15
                text_bold True
                text_color "#ffffff"
                text_hover_color "#ffffff"
                action Hide("video_player_modal")

# --- Audio & Video Media Test Suite ---
label media_test_menu:
    menu:
        h "Audio & Video Codec Test Arena!\nTest BGM music, sound effects, fullscreen cutscenes, and embedded Movie displayables."

        "(Music) Play BGM Music Track (MP3)":
            play music "audio/test.mp3" loop
            h "Playing audio/test.mp3 on the music channel! Notice how BGM loops seamlessly."
            jump media_test_menu

        "(Music) Stop BGM Playback":
            stop music fadeout 1.0
            h "Stopped BGM playback."
            jump media_test_menu

        "(Sound) Play Retro Sparkle SFX (WAV 16-bit PCM)":
            play sound "audio/magic-stars-retro-sparkle.wav"
            h "Played audio/magic-stars-retro-sparkle.wav on the sound channel!"
            jump media_test_menu

        "(Video) Play Widescreen (Embedded Movie Displayable 16:9)":
            $ current_video_title = "Widescreen Sample (1366x720 -> 854x480 VP9/WebM)"
            $ current_video_displayable = "sample_movie_widesample"
            show screen video_player_modal
            h "Showing embedded Movie displayable! Click Close Video Player when finished."
            jump media_test_menu

        "(Video) Play Widescreen Cutscene (Fullscreen Cutscene)":
            $ renpy.pause(0.2)
            $ renpy.movie_cutscene("video/widesample.webm")
            h "Widescreen video cutscene completed!"
            jump media_test_menu

        "(Video) Play Portrait Writing (Embedded Movie Displayable 9:16)":
            $ current_video_title = "Portrait Writing Sample (240x426 VP9/WebM)"
            $ current_video_displayable = "sample_movie_writing"
            show screen video_player_modal
            h "Showing embedded Movie displayable! Click Close Video Player when finished."
            jump media_test_menu

        "(Video) Play Portrait Writing Cutscene (Fullscreen Cutscene)":
            $ renpy.pause(0.2)
            $ renpy.movie_cutscene("video/writing.webm")
            h "Writing video cutscene completed!"
            jump media_test_menu

        "<< Back to Main Test Menu":
            jump main_menu_loop

# --- Shop (Buy & Sell) System ---
label shop_menu:
    menu:
        h "Welcome to the Item Shop!\nGold: [gold] G | Potions: [potion_count] | Elixirs: [elixir_count] | Keys: [key_count]"

        "(Buy) Purchase Items":
            jump shop_buy_menu

        "(Sell) Sell Items (Half Price Refund)":
            jump shop_sell_menu

        "<< Back to Main Menu":
            jump main_menu_loop

label shop_buy_menu:
    menu:
        h "Gold: [gold] G\nSelect an item to purchase:"

        "(Potion) Health Potion (50 Gold) - Owned: [potion_count]":
            if gold >= 50:
                $ gold -= 50
                $ potion_count += 1
                $ play_motion("m02")
                h "Bought 1x Health Potion! Remaining Gold: [gold] G."
            else:
                $ play_motion("m03")
                h "Not enough Gold! You need 50 G, but only have [gold] G."
            jump shop_buy_menu

        "(Elixir) Magic Elixir (150 Gold) - Owned: [elixir_count]":
            if gold >= 150:
                $ gold -= 150
                $ elixir_count += 1
                $ play_motion("m02")
                h "Bought 1x Magic Elixir! Remaining Gold: [gold] G."
            else:
                $ play_motion("m03")
                h "Not enough Gold! You need 150 G, but only have [gold] G."
            jump shop_buy_menu

        "(Charm) Live2D Charm (500 Gold) - Owned: [charm_count]":
            if gold >= 500:
                $ gold -= 500
                $ charm_count += 1
                $ play_motion("m04")
                h "Bought 1x Live2D Charm! Remaining Gold: [gold] G."
            else:
                $ play_motion("m03")
                h "Not enough Gold! You need 500 G, but only have [gold] G."
            jump shop_buy_menu

        "(Key) Mystic Key (1000 Gold) - Owned: [key_count]":
            if gold >= 1000:
                $ gold -= 1000
                $ key_count += 1
                $ play_motion("m07")
                h "Bought 1x Mystic Key! Remaining Gold: [gold] G."
            else:
                $ play_motion("m03")
                h "Not enough Gold! You need 1000 G, but only have [gold] G."
            jump shop_buy_menu

        "<< Back to Shop":
            jump shop_menu

label shop_sell_menu:
    menu:
        h "Gold: [gold] G\nSelect an item to sell for half refund:"

        "(Sell) Health Potion (+25 Gold) - Owned: [potion_count]":
            if potion_count > 0:
                $ potion_count -= 1
                $ gold += 25
                $ play_motion("m02")
                h "Sold 1x Health Potion for 25 Gold! Total Gold: [gold] G."
            else:
                $ play_motion("m05")
                h "You don't have any Health Potions to sell!"
            jump shop_sell_menu

        "(Sell) Magic Elixir (+75 Gold) - Owned: [elixir_count]":
            if elixir_count > 0:
                $ elixir_count -= 1
                $ gold += 75
                $ play_motion("m02")
                h "Sold 1x Magic Elixir for 75 Gold! Total Gold: [gold] G."
            else:
                $ play_motion("m05")
                h "You don't have any Magic Elixirs to sell!"
            jump shop_sell_menu

        "(Sell) Live2D Charm (+250 Gold) - Owned: [charm_count]":
            if charm_count > 0:
                $ charm_count -= 1
                $ gold += 250
                $ play_motion("m02")
                h "Sold 1x Live2D Charm for 250 Gold! Total Gold: [gold] G."
            else:
                $ play_motion("m05")
                h "You don't have any Live2D Charms to sell!"
            jump shop_sell_menu

        "(Sell) Mystic Key (+500 Gold) - Owned: [key_count]":
            if key_count > 0:
                $ key_count -= 1
                $ gold += 500
                $ play_motion("m02")
                h "Sold 1x Mystic Key for 500 Gold! Total Gold: [gold] G."
            else:
                $ play_motion("m05")
                h "You don't have any Mystic Keys to sell!"
            jump shop_sell_menu

        "<< Back to Shop":
            jump shop_menu

# --- High-Low Dice Game (Freezing Cheat Test) ---
label dice_game_menu:
    menu:
        h "High-Low Dice Arena!\nGold: [gold] G | Bet: [dice_bet] G\nScore: [dice_wins] Wins, [dice_losses] Losses (Streak: [dice_streak])"

        "(Roll) Roll Dice against Hiyori (Bet: [dice_bet] Gold)":
            jump dice_roll_logic

        "(Bet) Change Bet Amount":
            jump dice_bet_menu

        "(Help) Freezing Cheat Guide & Reset":
            h "Freezing Cheat Guide:\n1. Freeze 'gold' so losing never decreases your money!\n2. Freeze 'player_dice' or 'lucky_modifier' to 12+ to win every roll!\n3. Freeze 'dice_bet' to 1,000,000 for massive payouts!"
            menu:
                "Reset Dice Statistics":
                    $ dice_wins = 0
                    $ dice_losses = 0
                    $ dice_streak = 0
                    h "Dice stats reset to 0!"
                "Return to Dice Game":
                    pass
            jump dice_game_menu

        "<< Back to Main Menu":
            jump main_menu_loop

label dice_bet_menu:
    menu:
        h "Select a new bet amount (Current Bet: [dice_bet] Gold):"

        "Bet 50 Gold":
            $ dice_bet = 50
            h "Bet set to 50 Gold!"
            jump dice_game_menu

        "Bet 100 Gold":
            $ dice_bet = 100
            h "Bet set to 100 Gold!"
            jump dice_game_menu

        "Bet 500 Gold":
            $ dice_bet = 500
            h "Bet set to 500 Gold!"
            jump dice_game_menu

        "Bet 1,000 Gold":
            $ dice_bet = 1000
            h "Bet set to 1,000 Gold!"
            jump dice_game_menu

        "(Input) Enter Custom Bet (Soft Keyboard IME)":
            $ raw_bet = renpy.input("Enter custom bet amount (in Gold):", default=str(dice_bet), length=8)
            $ raw_bet = raw_bet.strip()
            python:
                try:
                    parsed_bet = int(raw_bet)
                    if parsed_bet > 0:
                        dice_bet = parsed_bet
                except ValueError:
                    pass
            h "Bet is now set to [dice_bet] Gold!"
            jump dice_game_menu

        "<< Cancel":
            jump dice_game_menu

label dice_roll_logic:
    if gold < dice_bet:
        $ play_motion("m03")
        h "You don't have enough Gold! Bet requires [dice_bet] G, but you only have [gold] G."
        jump dice_game_menu

    $ p_die1 = renpy.random.randint(1, 6)
    $ p_die2 = renpy.random.randint(1, 6)
    $ player_dice = p_die1 + p_die2 + lucky_modifier

    $ o_die1 = renpy.random.randint(1, 6)
    $ o_die2 = renpy.random.randint(1, 6)
    $ opponent_dice = o_die1 + o_die2

    h "Rolling dice...\nPlayer: [p_die1] + [p_die2] = [player_dice]!\nHiyori: [o_die1] + [o_die2] = [opponent_dice]!"

    if player_dice > opponent_dice:
        $ gold += dice_bet
        $ dice_wins += 1
        $ dice_streak += 1
        $ play_motion("m04")
        h "(WIN) You WIN! +[dice_bet] Gold! (Streak: [dice_streak])"
    elif player_dice < opponent_dice:
        $ gold -= dice_bet
        $ dice_losses += 1
        $ dice_streak = 0
        $ play_motion("m08")
        h "(LOST) You LOST! -[dice_bet] Gold. (Tip: Try freezing gold!)"
    else:
        $ play_motion("m02")
        h "(TIE) It's a TIE! Your [dice_bet] Gold bet was returned."

    jump dice_game_menu
