# Environment Setup

This page gets your development environment ready for Anomaly scripting. You'll need the game installed, a code editor configured to understand Anomaly's file types, and some familiarity with where things live on disk.

---

## 1. Install S.T.A.L.K.E.R. Anomaly

Anomaly is a free standalone mod — you don't need to own any S.T.A.L.K.E.R. game on Steam.

1. Download the latest release from [ModDB](https://www.moddb.com/mods/stalker-anomaly)
2. Extract to a directory with no spaces in the path (e.g. `C:\Games\Anomaly`) — the X-Ray engine has issues with spaces
3. Run `AnomalyLauncher.exe` once to configure graphics settings, then launch the game to verify it works

!!! warning "Installation path"
    Avoid `C:\Program Files\` and `C:\Program Files (x86)\`. Windows UAC restrictions on those folders will cause problems with file writes. Use a path like `C:\Games\Anomaly`.

---

## 2. Set Up VS Code

VS Code is the recommended editor. It has extensions for every file type you'll encounter.

### Install extensions

| Extension | ID | Purpose |
|-----------|-----|---------|
| **LTX Support** | `AziatkaVictor.ltx-support` | Syntax highlighting for `.ltx` config files |
| **Lua** | `keyring.Lua` | Lua language support for `.script` files |
| **Shader languages support** | `slevesque.shader` | HLSL syntax for shader files |
| **Audio Preview** | `sukumo28.wav-preview` | Preview `.ogg` sound files in-editor |

### Configure file associations

Anomaly uses non-standard extensions for standard formats. Add this to your VS Code `settings.json` (`Ctrl+Shift+P` → "Open User Settings JSON"):

```json
{
    "files.associations": {
        "*.script": "lua",
        "*.ltx": "ini",
        "*.s": "lua",
        "*.ps": "hlsl",
        "*.vs": "hlsl",
        "*.gs": "hlsl"
    }
}
```

This gives you Lua syntax highlighting and autocomplete in `.script` files and INI highlighting in `.ltx` files.

### Open the scripts folder as a workspace

For the best experience, open the `gamedata/scripts/` folder (from your Anomaly installation, after unpacking — see below) as a VS Code workspace. This lets the Lua language server resolve cross-file references.

---

## 3. Unpack the Base Game Scripts

Anomaly ships its game data as compressed archives in the `db/` folder. Before you can read the base scripts or configs, you need to unpack them.

1. In your Anomaly installation, navigate to the `tools/` folder
2. Run `db_unpacker.bat` — this unpacks scripts and configs only (fast, recommended for scripting work)
3. Alternatively run `db_unpacker_all.bat` to unpack everything including textures and sounds (slow, only needed for asset work)

Unpacked files appear in `_unpacked/` inside your Anomaly folder. You can browse these as reference — **don't edit them here**. Your mod files go in `gamedata/` (see [Gamedata Structure](gamedata-structure.md)).

!!! tip
    The GitHub repo `Tosox/STALKER-Anomaly-gamedata` contains the already-unpacked base game scripts and configs if you want to browse them without running the unpacker.

---

## 4. Understand the Game Log

The engine writes a log file to `appdata/logs/xray_<username>.log`. This is your primary debugging output — `printf` and `log` calls from scripts appear here.

During development, tail this file while the game runs:

=== "PowerShell"
    ```powershell
    Get-Content "C:\Games\Anomaly\appdata\logs\xray_yourname.log" -Wait -Tail 50
    ```

=== "Command Prompt"
    No built-in tail on cmd. Use a tool like [Baretail](https://www.baremetalsoft.com/baretail/) or open the file in VS Code (it auto-refreshes).

The in-game debug console (`~` key) also accepts console commands and shows recent log output.

---

## 5. Mod Management

For developing and testing addons, **Mod Organizer 2 (MO2)** with the Anomaly plugin is the standard setup in the community. It lets you enable/disable addons without touching the base game files.

However, for simple script development, you can also work directly:

1. Create a folder for your addon anywhere on your machine
2. Mirror the `gamedata/` structure inside it (e.g. `my_addon/gamedata/scripts/my_script.script`)
3. Copy your files into the game's `gamedata/` folder to test, remove them when done

Most modders graduate to MO2 quickly once they have more than one addon to manage.

---

## 6. Optional: Dev Tools

**stalker-anomaly-devtools** (by ChristopherCapito on GitHub) is a performance profiler and logger for scripts. Install it like any addon. Once active:

- Press `F11` in-game → DevTools → Profiler → Enable Profiling
- It tracks execution time per function across all scripts
- Export results as CSV or flamegraph for analysis

Useful once your mod is working and you want to make sure it isn't tanking FPS.

---

## Quick Reference: Key Paths

| Path | Contents |
|------|----------|
| `<anomaly>/gamedata/scripts/` | Lua scripts (`.script` files) |
| `<anomaly>/gamedata/configs/` | LTX and XML configuration |
| `<anomaly>/gamedata/configs/text/eng/` | English localization strings |
| `<anomaly>/gamedata/configs/ui/` | UI layout XML |
| `<anomaly>/appdata/logs/` | Game log output |
| `<anomaly>/appdata/savedgames/` | Save files |
| `<anomaly>/db/` | Packed archives (don't edit) |
| `<anomaly>/tools/` | Unpacker batch files |
