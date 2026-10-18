# live2drenpytestapp

A comprehensive Ren'Py + Live2D Cubism test application designed to validate engine capabilities, rendering fidelity, mobile input stability, and in-game variable cheat modification in GPlayer and Ren'Py 8.x.

---

## 🎮 Features & Test Suites

- **🎭 Live2D Cubism Rendering & Eye Tracking**:
  - Implements Cubism model rendering (`Resources/hiyori_free`).
  - Dynamic eye-tracking update function following mouse/touch coordinates at 30 FPS.
  - Interactive motion triggers (`m01` through `m08`) and tap-to-animate functionality.
- **⌨️ Android Soft Keyboard (IME) Input Test**:
  - Validates `renpy.input` soft keyboard stability, avoiding `UnsatisfiedLinkError` or `commitText` crashes across SDL2 and Android IME implementations.
- **🔍 Real-Time API Compatibility Matrix**:
  - Live engine audit inspecting active subsystems: Cubism C exports (v4 vs v5), GL2 renderer, GLSL shaders, audio/video playback, mobile APIs, and Python architecture.
  - Visual color-coded matrix displaying `{color=#10b981}AVAILABLE{/color}` (green) vs `{color=#ef4444}MISSING{/color}` (red) across engine runtimes.
- **🏪 Item Shop (Buy & Sell Test)**:
  - Interactive item economy with purchases and 50% refunds (Health Potions, Magic Elixirs, Live2D Charms, Mystic Keys).
  - Perfect for testing integer quantity search and variable freezing in Cheat Engine.
- **🎲 High-Low Dice Arena (Freezing Cheat Test)**:
  - Roll 2d6 against Hiyori with customizable bets (presets or custom text input).
  - Win/Loss tracking, win streak counter, and reactive Live2D animations.
  - Test targets: freeze `gold` to prevent loss, freeze `player_dice` to 12+ for guaranteed wins, or freeze `dice_bet` for massive payouts.
- **📋 Branching Choice Menus (`menu:`)**:
  - Multi-level interactive menus testing touch responsiveness, rollback, and state persistence.
- **💰 Real-Time Cheat Engine Test Bench**:
  - Exposes typed game variables (`int`, `str`, `dict`, `list`, `bool`) in Ren'Py's store (`gold`, `gems`, `affection`, `player_level`, `stats`, `inventory`, item counts, dice stats).
  - Persistent, stylish on-screen HUD (top-left) that displays variables in real time.
  - Changes made via in-game cheat engines immediately reflect on the HUD overlay!

---

## 🚀 Getting Started

### Running in Ren'Py
Open this folder in Ren'Py 8.x (8.3.x, 8.4.x, 8.5.x, or 8.6.x) and launch the project directly.

### Running on Android in GPlayer
1. Place this project folder or its `.zip` archive into your game directory.
2. Launch via GPlayer with a Ren'Py 8.x runtime.
3. Use the top speed-dial or overlay menu to test the Cheat Engine, FPS overlay, and gamepad controls.

---

## 📄 License
MIT License. Model assets courtesy of Live2D Free Material (Hiyori).
