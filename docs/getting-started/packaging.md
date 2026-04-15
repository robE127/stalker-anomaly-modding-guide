# Packaging & Publishing Your Mod

Once your mod works locally, packaging it correctly ensures other players can install it without issues — whether they're using Mod Organizer 2, installing manually, or using a modpack manager.

---

## The golden rule: mirror gamedata/

Every Anomaly mod package, regardless of complexity, follows the same structural rule: **files are placed at the same relative path they need to land in the game's `gamedata/` folder.**

```
my_mod/
└── gamedata/
    ├── scripts/
    │   └── my_mod.script
    ├── configs/
    │   └── items/weapons/
    │       └── mod_my_weapon.ltx
    └── textures/
        └── ui/
            └── my_mod_icon.dds
```

A player installs by merging this `gamedata/` folder into their Anomaly installation. MO2 does this automatically via its virtual filesystem — it reads the `gamedata/` folder from each enabled mod and presents a merged view to the game.

---

## Simple mods — no installer needed

For most mods, a flat `gamedata/` folder is all you need. MO2 will recognise it automatically.

```
my_mod_v1.0/
├── gamedata/          ← MO2 detects this and maps it correctly
│   └── scripts/
│       └── my_mod.script
└── README.md
```

**To install via MO2:** drop the folder (or a zip of it) onto MO2's mod list panel, or use "Install a new mod from archive." MO2 detects the `gamedata/` root automatically.

**To install manually:** copy `gamedata/` into the Anomaly installation directory.

!!! tip "Always include a README"
    Even a short README with installation requirements, load order notes, and a description of what the mod does saves you from a flood of support questions.

---

## MO2 compatibility checklist

MO2 compatibility requires only one thing: the `gamedata/` folder must be at the **root level** of your archive. If your archive has an extra wrapper folder:

```
❌  my_mod_v1.0.zip
    └── my_mod_v1.0/          ← extra wrapper
        └── gamedata/
            └── scripts/

✓   my_mod_v1.0.zip
    └── gamedata/             ← gamedata at root
        └── scripts/
```

If MO2 shows a "No game data on top level" warning during install, you have a wrapper folder. Either fix the archive or use MO2's folder remapping in the install dialog.

---

## BAIN-compatible structure

BAIN (the Wrye Bash Installer) uses **numbered sub-packages**. Each sub-package is a numbered folder containing a `gamedata/` root. The numbering serves two purposes: it lets players select which sub-packages to install, and it defines install order — **files from higher-numbered folders overwrite files from lower-numbered ones** when paths conflict.

```
my_mod_v1.0/
├── 00 Core/
│   └── gamedata/
│       └── scripts/
│           └── my_mod.script
├── 01 Optional HD Textures/
│   └── gamedata/
│       └── textures/
│           └── ...
└── 02 AVO Patch/
    └── gamedata/
        └── configs/
            └── ...            ← overwrites matching files from 00 and 01
```

- Folder `00` is the required base — put your core files here
- Subsequent folders are patches or optional components — they overwrite any conflicting files from lower-numbered folders
- Players select which numbered folders to install; unselected folders are skipped entirely
- MO2 handles this format natively — it prompts for sub-package selection during install

---

## FOMOD — optional components with a UI installer

FOMOD is the standard for mods with multiple optional components. It provides a graphical installer inside MO2 where the player makes choices, and FOMOD copies the right files based on their selections.

!!! tip "FOMOD Creation Tool"
    Rather than writing `ModuleConfig.xml` by hand, use the community **[FOMOD Creation Tool](https://www.nexusmods.com/fallout4/mods/6821)** — a GUI editor for building FOMOD installers. Despite being hosted in the Fallout 4 section of Nexus, it's a general-purpose tool used across many games including Anomaly. Western-Goods was built with it.

A FOMOD package needs two files in a `fomod/` folder at the root:

```
my_mod_v1.0/
├── fomod/
│   ├── info.xml           ← mod metadata
│   └── ModuleConfig.xml   ← installer definition
├── src/
│   ├── core/
│   │   └── gamedata/
│   ├── optional_a/
│   │   └── gamedata/
│   └── optional_b/
│       └── gamedata/
└── README.md
```

### info.xml

Metadata shown in the installer header:

```xml
<fomod>
    <Name>My Mod</Name>
    <Author>YourName</Author>
    <Version>1.0.0</Version>
    <Description>A short description of your mod.</Description>
    <Website>https://www.moddb.com/mods/my-mod</Website>
</fomod>
```

### ModuleConfig.xml — basic structure

```xml
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">

    <moduleName>My Mod</moduleName>

    <installSteps order="Explicit">
        <installStep name="Choose Components">
            <optionalFileGroups order="Explicit">

                <!-- Required core files — always installed -->
                <group name="Core" type="SelectAll">
                    <plugins order="Explicit">
                        <plugin name="Core Files">
                            <description>Required base files.</description>
                            <files>
                                <folder source="src\core\gamedata"
                                        destination="gamedata"
                                        priority="0" />
                            </files>
                            <typeDescriptor><type name="Required"/></typeDescriptor>
                        </plugin>
                    </plugins>
                </group>

                <!-- Optional add-ons — player picks any -->
                <group name="Optional Components" type="SelectAny">
                    <plugins order="Explicit">
                        <plugin name="Optional A">
                            <description>Adds optional feature A.</description>
                            <files>
                                <folder source="src\optional_a\gamedata"
                                        destination="gamedata"
                                        priority="0" />
                            </files>
                            <typeDescriptor><type name="Optional"/></typeDescriptor>
                        </plugin>
                        <plugin name="Optional B">
                            <description>Adds optional feature B.</description>
                            <files>
                                <folder source="src\optional_b\gamedata"
                                        destination="gamedata"
                                        priority="0" />
                            </files>
                            <typeDescriptor><type name="Optional"/></typeDescriptor>
                        </plugin>
                    </plugins>
                </group>

            </optionalFileGroups>
        </installStep>
    </installSteps>

</config>
```

Key points:
- `source` paths are relative to the archive root
- `destination` is always `gamedata` for Anomaly mods
- `priority` controls which files win when two components provide the same file — higher wins
- Group types: `SelectAll` (all required), `SelectAny` (player picks any), `SelectExactlyOne` (radio buttons)

---

## What to include in your release

| File | Required | Notes |
|------|----------|-------|
| `gamedata/` (or `src/` + `fomod/`) | Yes | The actual mod files |
| `README.md` | Strongly recommended | Description, requirements, install instructions, known issues |
| `CHANGELOG.md` | Recommended for ongoing mods | Version history |
| `LICENSE.md` | Recommended | CC BY-NC-SA 4.0 is common in the Anomaly community |

**Do not include:**
- `meta.ini` — MO2 generates this itself on install; shipping it causes version conflicts
- `.git/` folder — exclude this when zipping; it adds hundreds of MB
- The game's own files — only ship your additions and overrides

---

## Testing your package before publishing

Publishing a broken mod reflects poorly and generates support requests. The investment in thorough testing before release is almost always worth it.

### Step 1 — Test the package itself

Before testing gameplay, verify the package installs correctly.

1. **Build your release archive** from the folder — don't zip your development folder directly. Create a clean copy containing only the files meant for release (no `.git/`, no dev notes, no temp files).
2. **Install from the archive via MO2** as if you were a first-time user. Does MO2 detect `gamedata/` at the root without a "No game data on top level" warning?
3. If you have a FOMOD, step through every combination of options and confirm each one installs without errors.
4. **Disable then re-enable** the mod in MO2 and relaunch — the game must work cleanly in both states.

### Step 2 — Test on a clean profile

Your personal MO2 profile likely has dozens of other mods that may be filling gaps or masking conflicts in your mod. Create a **separate MO2 profile** with only:

- Vanilla Anomaly (no other addons)
- Your mod

Test the specific feature your mod adds in this minimal environment. If something breaks here that worked on your main profile, another mod was covering for a bug in yours.

### Step 3 — Read the log after every launch

The log at `appdata/logs/xray_x64.log` is your first line of diagnosis. After each test launch, search it for:

```
!              — any line starting with ! is a warning or error
LUA ERROR      — Lua script errors
SCRIPT ERROR   — engine-level script failures
[error]        — engine errors of any kind
```

A clean launch should have no `!` lines from your mod's files. Pay particular attention to:

- **LTX merge conflicts** — if two files define the same section/key, one silently wins. The log may show which.
- **Missing files** — textures, sounds, or meshes referenced in configs that don't exist produce log warnings and visual glitches.
- **Script registration errors** — `![axr_main callback_set] callback X doesn't exist` means a typo in a callback name.

### Step 4 — Test save/load cycle

Many mod bugs only appear after saving and reloading. For any mod that stores state:

1. Trigger the mod's feature (fire a callback, pick up an item, kill an NPC, etc.)
2. Save the game
3. Quit to main menu completely
4. Load the save
5. Verify the mod's state was correctly restored — flags, timers, counters

Also test **loading an existing save that predates your mod**. Players will do this. If your mod assumes state that was set during a new game and doesn't handle a missing save entry gracefully, it will crash on old saves.

### Step 5 — Test new game and existing save

Test both:

- **New game** — does your mod work correctly from the very start?
- **Save from before the mod was installed** — load it with your mod active. Nil-check your `load_state` defensively; assume nothing was saved.

### Step 6 — Stress test the feature

Don't just test the happy path. Deliberately try to break your mod:

- Trigger the feature multiple times in quick succession
- Trigger it at unusual game states (mid-combat, while in a menu, while trading)
- Die and respawn while the mod's feature is active
- Fast-travel or change levels while the mod has active state
- Quit without saving while the mod is mid-operation, then reload

### Step 7 — Test with common mods

Your mod will be installed alongside others. At minimum, test with the most popular base mods your audience is likely to use — check for file conflicts in MO2 (any red/yellow conflict indicators in the mod list) and verify both mods still work correctly when loaded together.

If your mod patches a file that another popular mod also patches (via DLTX/DXML), test that both patches apply without one silently overwriting the other.

### Step 8 — Performance check

If your mod registers `actor_on_update` or any other per-frame callback, verify it isn't tanking FPS. Run the game with your mod active and check the framerate in a busy area. The **stalker-anomaly-devtools** profiler (see [Environment Setup](environment-setup.md)) can show you your mod's per-frame execution time.

A well-written `actor_on_update` should take under a millisecond. If yours is doing expensive work every frame — iterating large tables, calling `level.iterate_nearest`, reading INI files — add a timer so it only runs every N seconds instead of every tick.

---

## Where to publish

- **[ModDB](https://www.moddb.com/games/stalker-anomaly)** — The primary Anomaly mod hosting site. Most players look here first.
- **[Nexus Mods](https://www.nexusmods.com/stalkeranomaly)** — Larger general modding audience; integrates directly with MO2's download manager.
- **GitHub** — Good for open-source mods where you want version control and issue tracking. Link to your ModDB/Nexus page from the README.

Most authors publish on ModDB or Nexus as the primary release and use GitHub for source and issue tracking.

---

## See also

- [Gamedata Structure](gamedata-structure.md) — the full `gamedata/` folder layout
- [Your First Mod](first-mod.md) — the `gamedata/` workspace concept
- [DLTX (LTX Patching)](../config-formats/dltx.md) — mod-compatible config changes
- [DXML (XML Patching)](../config-formats/dxml.md) — mod-compatible XML changes
