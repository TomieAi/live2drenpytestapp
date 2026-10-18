# api_inspector.rpy - Comprehensive Ren'Py, Live2D & Android Native API Compatibility Matrix
# Inspects active engine subsystems, Cubism C symbols, JNI methods, Cython extensions, and shims.

init -1 python:
    import sys
    import os
    import ctypes

    def audit_engine_apis():
        """Run comprehensive runtime inspection across all Ren'Py, Live2D & Android subsystems."""
        results = []

        def add_check(category, name, ok, details):
            results.append({
                "category": category,
                "name": name,
                "ok": bool(ok),
                "details": str(details)
            })

        # =========================================================================
        # 1. Live2D Cubism Native C Library & Symbols
        # =========================================================================
        cubism_dll = None
        cdll = None
        for cand in ["Live2DCubismCore.dll", "libLive2DCubismCore.so", "libLive2DCubismCore.dylib"]:
            p = os.path.abspath(cand)
            if os.path.exists(p):
                cubism_dll = p
                break
            exe_cand = os.path.join(os.path.dirname(sys.executable), cand)
            if os.path.exists(exe_cand):
                cubism_dll = exe_cand
                break

        if cubism_dll:
            try:
                cdll = ctypes.CDLL(cubism_dll)
            except Exception as e:
                cdll = None

        add_check(
            "Live2D C Symbols",
            "Live2DCubismCore Native Library",
            cdll is not None,
            ("Loaded: " + os.path.basename(cubism_dll)) if cdll else "DLL/SO not found in search path"
        )

        # Inspect all key Cubism C functions
        c_symbols = [
            ("csmGetVersion", "Core semver query API"),
            ("csmGetLatestMocVersion", "Latest supported .moc3 format version"),
            ("csmGetRenderOrders", "Cubism 5 API: Render orders (Ren'Py 8.5.0+)"),
            ("csmGetDrawableRenderOrders", "Cubism 4 API: Draw orders (Ren'Py 7.4.0 - 8.4.1)"),
            ("csmInitializeModelInPlace", "Model memory buffer initialization"),
            ("csmReviveMocInPlace", "MOC parser & memory resurrection"),
            ("csmUpdateModel", "Dynamic physics & parameter solver"),
            ("csmReadCanvasInfo", "Canvas pixel bounds & origin coordinates"),
            ("csmGetParameterCount", "Parameter reflection count API"),
            ("csmGetDrawableCount", "Mesh drawable part count API"),
        ]

        for sym, desc in c_symbols:
            has_sym = hasattr(cdll, sym) if cdll else False
            if sym == "csmGetVersion" and has_sym:
                val = hex(cdll.csmGetVersion())
                detail = "Exported (Version Code: {}) - {}".format(val, desc)
            else:
                detail = ("Exported: " + desc) if has_sym else ("Missing symbol - " + desc)
            add_check("Live2D C Symbols", sym, has_sym, detail)

        # =========================================================================
        # 2. Native Cython C-Extensions (.so / .pyd)
        # =========================================================================
        cython_modules = [
            ("_renpy", "Core Cython C engine accelerator"),
            ("renpy.style", "High-performance style calculator"),
            ("renpy.gl2.gl2draw", "Hardware OpenGL/GLES renderer extension"),
            ("renpy.gl2.live2dmodel", "Live2D Cython C++ bridge extension"),
        ]

        for mod_name, desc in cython_modules:
            try:
                __import__(mod_name)
                found = True
            except Exception:
                found = False
            detail = ("Available ({})".format(desc)) if found else ("MISSING binary (.so/.pyd) - " + desc)
            add_check("Cython C-Extensions", mod_name, found, detail)

        # =========================================================================
        # 3. Android JNI & SDL2 Bridge
        # =========================================================================
        is_android = (
            getattr(renpy, "android", False) or
            getattr(renpy, "mobile", False) or
            "ANDROID_ARGUMENT" in os.environ or
            "ANDROID_PRIVATE" in os.environ
        )

        if is_android:
            try:
                from jnius import autoclass
                SDLActivity = autoclass("org.libsdl.app.SDLActivity")
                jni_checks = [
                    ("nativeGenerateScancodeForUnichar", "Soft keyboard scancode JNI (SDL 2.0.9+; missing in 7.3.2/2.0.8)"),
                    ("nativeCommitText", "IME text input commit bridge (Soft keyboard typing)"),
                    ("nativeSetScreenResolution", "Screen resolution & display scaling bridge"),
                    ("onNativeResize", "Window surface resize handler"),
                ]
                for jni_name, jni_desc in jni_checks:
                    has_jni = hasattr(SDLActivity, jni_name)
                    detail = ("JNI exported: " + jni_desc) if has_jni else ("MISSING in librenpython.so: " + jni_desc)
                    add_check("Android JNI & SDL2", "SDLActivity." + jni_name, has_jni, detail)
            except Exception as e:
                add_check("Android JNI & SDL2", "PyJNIus Reflection", False, "Could not reflect Android SDLActivity: " + str(e))
        else:
            add_check(
                "Android JNI & SDL2",
                "Android JNI Bridge (SDLActivity)",
                False,
                "Inactive in Desktop PC mode (Active when launched on Android test device)"
            )

        # =========================================================================
        # 4. Cross-Version Engine Shims (Forward & Backward Compatibility)
        # =========================================================================
        shims = [
            ("im.Cache.get_renders", hasattr(renpy.display.im.Cache, "get_renders"), "Polyfill for 7.4.x games on 7.4.11+ runtimes (mark_sweep)"),
            ("config.gl2_modify_window_flags", hasattr(renpy.config, "gl2_modify_window_flags"), "Polyfill for 7.4.x games on 7.5+ runtimes"),
            ("config.crop_relative_default", hasattr(renpy.config, "crop_relative_default"), "Polyfill for 7.4.x games on 7.5+ runtimes"),
            ("config.always_shown_screens", hasattr(renpy.config, "always_shown_screens"), "Screen manager polyfill for 7.4.x on 7.5+ runtimes"),
            ("Displayable._offer_size", hasattr(renpy.display.core.Displayable, "_offer_size"), "Layout engine property for 7.4.x on 7.5+ runtimes"),
            ("Displayable._box_skip", hasattr(renpy.display.core.Displayable, "_box_skip"), "Box layout property for 7.4.x on 7.5+ runtimes"),
            ("Displayable.delay", hasattr(renpy.display.core.Displayable, "delay"), "Transition timing property for 7.4.x on 7.5+ runtimes"),
        ]

        for s_name, s_ok, s_desc in shims:
            detail = ("Present: " + s_desc) if s_ok else ("MISSING: Needs shim in shims/renpy/main.py (" + s_desc + ")")
            add_check("Engine Shims", s_name, s_ok, detail)

        # =========================================================================
        # 5. Graphics & GL2 Shaders
        # =========================================================================
        is_gl2 = getattr(renpy.config, "gl2", False)
        add_check(
            "Graphics & GL2",
            "GL2 Model-Based Renderer",
            is_gl2,
            "Enabled (Hardware accelerated 3D/GL2 pipeline)" if is_gl2 else "Disabled (Legacy GL1 software pipeline)"
        )

        has_shader = hasattr(renpy, "register_shader") and callable(renpy.register_shader)
        add_check(
            "Graphics & GL2",
            "Custom GLSL Shader System (register_shader)",
            has_shader,
            "register_shader API functional" if has_shader else "register_shader not found in renpy"
        )

        has_matrix = hasattr(renpy.display, "matrix") or hasattr(renpy.display.transform, "Matrix")
        add_check(
            "Graphics & GL2",
            "3D Matrix Transform Engine",
            has_matrix,
            "Matrix / Transform3D class available" if has_matrix else "Matrix transforms not supported"
        )

        has_mark_sweep = hasattr(renpy.display.render, "mark_sweep")
        add_check(
            "Graphics & GL2",
            "Render Cache Mark-Sweep (mark_sweep)",
            has_mark_sweep,
            "Present (Ren'Py 7.4.11+ / 8.x garbage eviction)" if has_mark_sweep else "Missing (Older 7.4.x layout)"
        )

        # =========================================================================
        # 6. Audio, Video & Mobile Subsystems
        # =========================================================================
        has_audio = hasattr(renpy, "music") and hasattr(renpy.music, "play")
        add_check(
            "Audio & Video",
            "Ren'Py Audio Subsystem (renpy.music)",
            has_audio,
            "Audio playback engine functional" if has_audio else "Audio subsystem missing"
        )

        has_movie = hasattr(renpy, "Movie")
        add_check(
            "Audio & Video",
            "Movie Displayable (renpy.Movie)",
            has_movie,
            "Video playback displayable available" if has_movie else "Movie class missing"
        )

        hw_vid = getattr(renpy.config, "hw_video", False)
        add_check(
            "Audio & Video",
            "Hardware Accelerated Video (hw_video)",
            hw_vid,
            "Hardware decoding enabled" if hw_vid else "Software fallback / disabled"
        )

        # Asset codec samples
        mp3_ok = renpy.loadable("audio/test.mp3") if hasattr(renpy, "loadable") else os.path.exists("game/audio/test.mp3")
        add_check(
            "Audio & Video",
            "MP3 Music Asset (audio/test.mp3)",
            mp3_ok,
            "Asset loadable: Ready for BGM music playback" if mp3_ok else "Asset missing: audio/test.mp3 not found"
        )

        wav_ok = renpy.loadable("audio/magic-stars-retro-sparkle.wav") if hasattr(renpy, "loadable") else os.path.exists("game/audio/magic-stars-retro-sparkle.wav")
        add_check(
            "Audio & Video",
            "WAV Sound FX Asset (sparkle.wav)",
            wav_ok,
            "Asset loadable: Ready for SFX sound playback" if wav_ok else "Asset missing: audio/magic-stars-retro-sparkle.wav not found"
        )

        mp4_ok = renpy.loadable("video/writing.mp4") if hasattr(renpy, "loadable") else os.path.exists("game/video/writing.mp4")
        add_check(
            "Audio & Video",
            "MP4 Movie Video Asset (video/writing.mp4)",
            mp4_ok,
            "Asset loadable: Ready for video cutscene playback" if mp4_ok else "Asset missing: video/writing.mp4 not found"
        )

        has_input = hasattr(renpy, "input")
        add_check(
            "Audio & Video",
            "Soft Keyboard / Text Input (renpy.input)",
            has_input,
            "IME text input prompt ready" if has_input else "renpy.input missing"
        )

        has_touch = hasattr(renpy.display, "touch")
        add_check(
            "Audio & Video",
            "Touch Interaction Subsystem",
            has_touch,
            "Touch event dispatching active" if has_touch else "Touch subsystem missing"
        )

        # =========================================================================
        # 7. Python Engine Architecture
        # =========================================================================
        py_major = sys.version_info[0]
        py_ver_str = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
        add_check(
            "Core Architecture",
            "Python 3.x Modern Runtime",
            py_major >= 3,
            ("Active: Python {} (Ren'Py 8.x modern runtime)".format(py_ver_str)) if py_major >= 3 else "Python 2.7 legacy runtime"
        )

        add_check(
            "Core Architecture",
            "Python 2.7 Compatibility Mode",
            py_major == 2,
            "Active: Python 2.7 (Ren'Py 7.x runtime)" if py_major == 2 else ("Inactive (Running on Python {}.x)".format(py_major))
        )

        renpy_ver = renpy.version if hasattr(renpy, "version") else "Unknown"
        add_check(
            "Core Architecture",
            "Ren'Py Engine Semver",
            True,
            str(renpy_ver)
        )

        return results

default api_filter_category = "All"
default api_audit_data = []

# --- Material 3 Style API Inspector Dialog Screen ---
screen api_compatibility_inspector():
    modal True
    zorder 200

    # Dim background overlay
    add "#000000bb"

    # Refresh audit data on screen open
    on "show" action SetVariable("api_audit_data", audit_engine_apis())

    python:
        if not api_audit_data:
            api_audit_data = audit_engine_apis()
        total_count = len(api_audit_data)
        ok_count = sum(1 for item in api_audit_data if item["ok"])
        missing_count = total_count - ok_count
        status_tabs = [("All", "All ({})".format(total_count)), ("Missing Only", u"✘ Missing Only ({})".format(missing_count)), ("Ready Only", u"✔ Ready Only ({})".format(ok_count))]
        subsystem_categories = ["Live2D C Symbols", "Cython C-Extensions", "Android JNI & SDL2", "Engine Shims", "Graphics & GL2", "Audio & Video", "Core Architecture"]
        
        if api_filter_category == "Missing Only":
            filtered_items = [i for i in api_audit_data if not i["ok"]]
        elif api_filter_category == "Ready Only":
            filtered_items = [i for i in api_audit_data if i["ok"]]
        elif api_filter_category == "All":
            filtered_items = api_audit_data
        else:
            filtered_items = [i for i in api_audit_data if i["category"] == api_filter_category]

    frame:
        xalign 0.5
        yalign 0.5
        xsize 960
        ysize 640
        background "#0f172ae6"
        padding (24, 18)

        vbox:
            spacing 8

            # Top Header Row
            hbox:
                spacing 14
                xfill True

                # Title & Subtitle
                vbox:
                    spacing 2
                    text "{b}{color=#38bdf8}(API MATRIX) Ren'Py, Live2D & Android Subsystems{/color}{/b}" size 20
                    text "Early Diagnostic Auditor: Green = Ready | Red = Missing (Needs JNI / Native Shim)" size 11 color "#94a3b8"

                # Metric Summary Chips (Clickable Filters!) & Close Button
                hbox:
                    xalign 1.0
                    spacing 8

                    button:
                        background ("#10b981" if api_filter_category == "Ready Only" else "#10b98133")
                        padding (10, 4)
                        action SetVariable("api_filter_category", "Ready Only")
                        text ("✔ " + str(ok_count) + " Ready") size 12 color ("#ffffff" if api_filter_category == "Ready Only" else "#10b981") bold True substitute False

                    button:
                        background ("#ef4444" if api_filter_category == "Missing Only" else "#ef444433")
                        padding (10, 4)
                        action SetVariable("api_filter_category", "Missing Only")
                        text ("✘ " + str(missing_count) + " Missing") size 12 color ("#ffffff" if api_filter_category == "Missing Only" else "#ef4444") bold True substitute False

                    textbutton "✕ Close":
                        background "#334155"
                        padding (12, 4)
                        text_color "#ffffff"
                        text_size 12
                        action Hide("api_compatibility_inspector")

            # Row 1: Status Filter Tabs (Quick Filter)
            hbox:
                spacing 6
                text "Status:" size 11 color "#94a3b8" yalign 0.5
                for tab_key, tab_label in status_tabs:
                    $ is_sel = (api_filter_category == tab_key)
                    $ btn_bg = "#ef4444" if (tab_key == "Missing Only" and is_sel) else ("#10b981" if (tab_key == "Ready Only" and is_sel) else ("#2563eb" if is_sel else ("#7f1d1d44" if tab_key == "Missing Only" else "#1e293b")))
                    textbutton tab_label:
                        text_size 10
                        padding (8, 4)
                        text_color ("#ffffff" if is_sel else ("#f87171" if tab_key == "Missing Only" else "#94a3b8"))
                        background btn_bg
                        action SetVariable("api_filter_category", tab_key)

            # Row 2: Subsystem Category Tabs
            hbox:
                spacing 5
                text "Subsystem:" size 11 color "#94a3b8" yalign 0.5
                for cat in subsystem_categories:
                    $ is_sel = (api_filter_category == cat)
                    textbutton cat:
                        text_size 10
                        padding (7, 4)
                        text_color ("#ffffff" if is_sel else "#94a3b8")
                        background ("#2563eb" if is_sel else "#1e293b")
                        action SetVariable("api_filter_category", cat)

            null height 2

            # Scrollable API Audit Viewport
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                ysize 440

                vbox:
                    spacing 6
                    xfill True

                    if not filtered_items:
                        frame:
                            xfill True
                            padding (24, 40)
                            background "#1e293b33"
                            text "No APIs match this filter! All items in this category are fully functional." size 13 color "#10b981" xalign 0.5

                    for item in filtered_items:
                        frame:
                            xfill True
                            padding (12, 8)
                            background ("#064e3b33" if item["ok"] else "#7f1d1d33")

                            hbox:
                                spacing 12
                                yalign 0.5

                                # Status Icon
                                text ("✔" if item["ok"] else "✘") size 16 yalign 0.5 bold True color ("#10b981" if item["ok"] else "#ef4444") substitute False

                                # Name & Details
                                vbox:
                                    spacing 2
                                    hbox:
                                        spacing 8
                                        text item["name"] size 12 bold True color ("#ffffff" if item["ok"] else "#fca5a5") substitute False
                                        text ("• " + item["category"]) size 10 color "#64748b" yalign 0.5 substitute False
                                    text item["details"] size 10 color ("#94a3b8" if item["ok"] else "#f87171") substitute False

                                # Right status badge
                                frame:
                                    xalign 1.0
                                    yalign 0.5
                                    background ("#10b981" if item["ok"] else "#ef4444")
                                    padding (8, 3)
                                    text ("AVAILABLE" if item["ok"] else "MISSING") size 9 color "#ffffff" bold True substitute False
