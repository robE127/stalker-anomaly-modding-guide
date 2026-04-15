# Your First Mod

This walkthrough creates a complete, working addon from scratch. By the end you'll have a mod that logs a message on game load and prints to the screen when you press a key — simple enough to understand fully, real enough to show every concept you'll use in every mod you write.

---

## What we're building

An addon called `hello_anomaly` that:

1. Prints `"Hello Anomaly!"` to the game log when a save is loaded
2. Displays a HUD notification when you press `F6`

---

## Why gamedata/ is your workspace

Unlike many game engines, Anomaly has no separate "project" or "workspace" folder concept. The engine loads all game assets directly from `gamedata/` and its subfolders — scripts, configs, meshes, textures, sounds, shaders, and more all live under this single tree. There is no build step, no compilation, and no packaging required during development.

When you install a mod (manually or via MO2), its `gamedata/` folder is **merged** into the game's `gamedata/`. A file at `gamedata/scripts/my_mod.script` in your mod lands alongside base game scripts. A file at `gamedata/meshes/actors/stalker/my_model.ogf` replaces or adds to the base game meshes. A file at `gamedata/textures/ui/my_icon.dds` adds a new texture. The engine treats your files identically to its own.

This means the folder structure of your mod always mirrors the game's `gamedata/` layout — whatever you're modding:

```
my_mod/
└── gamedata/
    ├── scripts/        ← Lua code
    ├── configs/        ← LTX and XML config changes
    ├── meshes/         ← 3D models
    ├── textures/       ← DDS textures
    ├── sounds/         ← Audio files
    └── shaders/        ← Renderer shaders
```

**MO2 maps each enabled mod's `gamedata/` into a virtual file system**, so your files appear at the right paths without ever touching the real installation directory. This is why MO2's mod folder structure mirrors the game's `gamedata/` layout exactly — it's the same layout by design.

The practical implication: you develop directly against the `gamedata/` structure, then ship the same folder as your release package.

---

## Step 1: Create the addon folder structure

Create this folder layout anywhere on your machine (outside the game folder):

```
hello_anomaly/
└── gamedata/
    └── scripts/
        └── hello_anomaly.script
```

---

## Step 2: Write the script

Create `hello_anomaly.script` with this content:

```lua
-- hello_anomaly.script
-- A minimal addon that logs a message and responds to a keypress.

-- DIK_keys is an engine-provided table of DirectInput key constants.
-- DIK_F6 = the F6 key.
local MY_KEY = DIK_keys.DIK_F6

-- This function fires every time the player loads a save.
local function on_game_load()
    printf("Hello Anomaly! Game loaded.")
end

-- This function fires every time a key is pressed.
-- 'key' is a number matching a DIK_keys constant.
local function on_key_press(key)
    if key == MY_KEY then
        actor_menu.set_msg(1, "Hello Anomaly!", 3)  -- Show HUD message for 3 seconds
    end
end

-- on_game_start() is called automatically by the engine for every script
-- that defines it. This is where you register your callbacks.
function on_game_start()
    RegisterScriptCallback("on_game_load", on_game_load)
    RegisterScriptCallback("on_key_press", on_key_press)
end
```

---

## Step 3: Install it

Copy your `gamedata/` folder into the Anomaly installation directory so it merges with the existing `gamedata/`:

```
C:\Games\Anomaly\
└── gamedata/
    └── scripts/
        ├── _g.script          (base game, already here)
        ├── axr_main.script    (base game, already here)
        └── hello_anomaly.script  ← your new file
```

!!! tip "Using MO2"
    If you're using Mod Organizer 2, create a new mod entry, place your `gamedata/` folder inside it, and activate it. MO2 will merge it automatically.

---

## Step 4: Test it

1. Launch Anomaly
2. Load a save (or start a new game)
3. Check the log file at `appdata/logs/xray_<yourname>.log` — you should see:
   ```
   Hello Anomaly! Game loaded.
   ```
4. Press `F6` in-game — a message should appear in the top-left of the HUD

---

## What just happened

Let's walk through exactly what the engine did:

**At startup**, the engine scans `gamedata/scripts/` and loads every `.script` file. For each one that has an `on_game_start()` function, it calls that function. Your `on_game_start()` ran and registered two callbacks.

**When a save loaded**, the engine fired the `on_game_load` callback. The engine looked up every function registered under that name and called them all — including your `on_game_load`.

**When you pressed F6**, the engine fired `on_key_press` with the key code as an argument. Your function checked if the code matched `DIK_F6`, and if so displayed the message.

This pattern — register in `on_game_start`, act in the callback — is the foundation of every Anomaly mod.

---

## Common first mistakes

**Wrong file extension**  
The file must be `.script`, not `.lua`. The Lua language server in VS Code will still work with it if you set the file association correctly.

**Typo in callback name**  
`RegisterScriptCallback("on_Game_Load", ...)` silently does nothing — the name is case-sensitive. If your callback isn't firing, double-check the spelling.

**Accessing `db.actor` too early**  
If you try to use `db.actor` inside `on_game_load`, it may be `nil`. The actor isn't guaranteed to exist until `actor_on_first_update` fires. See [Script Lifecycle](../scripting/script-lifecycle.md).

**No feedback on syntax errors**  
Lua syntax errors in your script will prevent the whole file from loading, usually with a message in the log like `LUA error: ...hello_anomaly.script:10: ...`. Always check the log when something doesn't work.

---

## Next steps

This addon does something, but it's not structured for a real mod yet. The [Scripting](../scripting/index.md) section covers:

- How to properly clean up callbacks when the game ends
- Persisting data across saves
- The full callback system and what's available
