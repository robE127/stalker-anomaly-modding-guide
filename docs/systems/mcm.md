# Mod Configuration Menu (MCM)

!!! note "Work in progress"
    This page is being written. Content coming soon.

MCM (Mod Configuration Menu) is a community-standard system that gives mods a settings UI accessible from the main menu and in-game ESC menu. It appears in 121 `on_option_change` callbacks and 323 `ui_mcm.get` calls across the analyzed repos — virtually every feature mod uses it.

## Topics to cover

- What MCM is and where it comes from (it's a mod itself, bundled with GAMMA and most modpacks)
- Checking for MCM availability (graceful fallback when MCM isn't installed)
- Registering your mod's options: the `mcm_options` table format
- Option types: checkbox, slider, list, key bind, input
- Reading values at runtime: `ui_mcm.get("mod_id/key")`
- The `on_option_change` callback — fired when the user saves MCM settings
- Full MCM registration pattern:

```lua
-- my_mod_mcm.script
function on_mcm_load()
    local op = {
        id = "my_mod",
        sh = true,
        gr = {
            { id = "title", type = "slide", text = "My Mod Settings", size = {512, 50} },
            { id = "enable", type = "check", val = 1, def = true },
            { id = "intensity", type = "track", val = 2, min = 0, max = 1, step = 0.05, def = 0.5 },
        }
    }
    return op
end
```

- Key naming conventions to avoid collisions with other mods
- Default values and how they're used when MCM isn't present
