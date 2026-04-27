# Callback Logger

A development tool that registers a handler for every known script callback and logs each one as it fires. Install it, load a save, and watch the log while doing things in-game to learn exactly when each callback fires and what arguments it provides.

All log lines are prefixed with `[CBL]` and include a wall-clock timestamp so they are easy to filter and correlate with in-game actions.

---

## What this covers

- Registering many callbacks without hitting LuaJIT's 60-upvalue limit
- Throttling high-frequency callbacks so the log stays readable
- `flush()` for real-time log output
- MCM integration for enabling/disabling without touching scripts
- Which callbacks fire in large bursts during A-Life simulation, and why

---

## Files

```
gamedata/
  scripts/
    callback_logger.script
    callback_logger_mcm.script
  configs/text/eng/
    ui_st_callback_logger.xml
```

---

## The 60-upvalue limit

A naive approach registers every callback as a separate named local and captures them all in `on_game_start`:

```lua
local function on_game_load() log("on_game_load") end
local function save_state()   log("save_state") end
-- ... 100+ more ...

function on_game_start()
    RegisterScriptCallback("on_game_load", on_game_load)
    RegisterScriptCallback("save_state",   save_state)
    -- ...
end
```

This fails at runtime with:

```
function at line N has more than 60 upvalues
```

LuaJIT limits each function to 60 captured upvalues. `on_game_start` would be capturing every handler local — far exceeding that limit.

The fix: store handlers in a table. `on_game_start` captures only the table itself (one upvalue) and iterates it:

```lua
local handlers = {
    on_game_load = function() log("on_game_load") end,
    save_state   = function() log("save_state") end,
    -- ...
}

function on_game_start()
    for name, fn in pairs(handlers) do
        RegisterScriptCallback(name, fn)
    end
end

function on_game_end()
    for name, fn in pairs(handlers) do
        UnregisterScriptCallback(name, fn)
    end
end
```

The function references stored in the table are stable — the same reference used to register is used to unregister, which is the requirement for `UnregisterScriptCallback` to work correctly.

---

## Throttling high-frequency callbacks

Some callbacks fire every simulation tick or in large bursts. Two categories need throttling to keep the log useful:

**Per-tick** — fire every frame while active:

| Callback | Why noisy |
|----------|-----------|
| `actor_on_update` | Every frame while the actor is alive |
| `npc_on_update`, `monster_on_update` | Every frame per online NPC/monster |
| `squad_on_update`, `smart_terrain_on_update` | Every simulation tick |
| `on_key_hold`, `on_before_key_hold` | Every frame while a key is held |
| `actor_on_foot_step`, `actor_on_footstep` | Every footstep sound |

**Burst on load** — fire hundreds or thousands of times as A-Life initialises:

| Callback | Why noisy |
|----------|-----------|
| `squad_on_add_npc`, `squad_on_enter_smart`, etc. | Fires for every squad during A-Life init |
| `se_stalker_on_spawn` | Every stalker in the simulation on load |
| `on_try_respawn` | Smart terrains evaluate respawn continuously |
| `server_entity_on_register/unregister` | Every A-Life entity on load |
| `on_enemy_eval`, `npc_on_eval_danger`, `npc_on_choose_weapon`, `npc_shot_dispersion`, `npc_on_hear_callback` | Constant during combat |

The throttle uses `time_global()` (milliseconds) and a per-callback last-fire table:

```lua
local THROTTLE_SECONDS = 10   -- one constant controls all throttled callbacks

local throttle_last = {}
local function log_throttled(name, ...)
    local now = time_global()
    if now - (throttle_last[name] or 0) < THROTTLE_SECONDS * 1000 then return end
    throttle_last[name] = now
    log(name, ...)
end
```

Some callbacks are commented out entirely even from the throttled table — the source includes comments explaining each one.

---

## Real-time output

By default, `printf` output accumulates in a memory buffer and only appears in the log file when the process exits. `flush()` forces the buffer to disk after each write:

```lua
printf("[CBL] %s %s", os.date("%H:%M:%S"), name)
flush()
```

See [Debugging & Logging](../scripting/debugging.md) for more on `flush()` and the log buffer.

---

## Script loading limitation

No `[CBL]` output appears until you load or start a game. Mod scripts are not loaded at application startup — a script only loads when it is first referenced by another loaded script, or when the engine calls `on_game_start()` at game session start.

Getting a mod script to run at main-menu time requires being explicitly referenced from a startup script. In practice the only candidate is `ui_main_menu.script`, which is owned by MCM. Editing it risks breakage on MCM updates, so this logger accepts the limitation: `main_menu_on_*` callbacks will only fire when the menu is opened from within a running game session, not at application open.

---

## MCM integration

A companion `_mcm.script` registers a single enable/disable toggle. MCM discovers any file with an `on_mcm_load()` function automatically:

```lua
function on_mcm_load()
    return {
        id = "callback_logger",
        sh = true,
        gr = {
            { id = "enabled", type = "check", val = 1, def = true,
              text = "ui_mcm_callback_logger_enabled" },
        }
    }
end
```

The main script checks the setting before every log call:

```lua
local function is_enabled()
    return ui_mcm and ui_mcm.get("callback_logger/enabled") ~= false
end
```

The `~= false` guard means the logger defaults to on if MCM is not installed or the value has not been saved yet.

---

## Complete source

=== "callback_logger.script"

    ```lua
    -- callback_logger.script
    -- Logs every known script callback so you can watch the log and learn when they fire.
    -- High-frequency callbacks are throttled: at most one message per THROTTLE_SECONDS.
    --
    -- Usage: install this script, load a save, open console log or debug output.
    -- All messages are prefixed with [CBL] for easy grep/filter.
    --
    -- LIMITATION: no [CBL] output appears until you load or start a game. This script is only
    -- loaded by the engine when on_game_start is called, which happens at game session start.
    -- Scripts load at application open only if another startup script explicitly references them.
    -- The only startup script we could hook is ui_main_menu.script (shipped by MCM), and editing
    -- that risks breakage on MCM updates. The main_menu_on_* and early on_xml_read callbacks
    -- therefore cannot be captured by this logger.

    local THROTTLE_SECONDS = 10

    local function is_enabled()
        return ui_mcm and ui_mcm.get("callback_logger/enabled") ~= false
    end

    local function log(name, ...)
        if not is_enabled() then return end
        local args = {...}
        local parts = {}
        for i, v in ipairs(args) do
            local ok, s = pcall(function()
                if type(v) == "userdata" then
                    if v.name then return tostring(v:name())
                    elseif v.id then return "id="..tostring(v:id())
                    else return tostring(v) end
                end
                return tostring(v)
            end)
            parts[i] = ok and s or "<?>"
        end
        local suffix = #parts > 0 and (" | "..table.concat(parts, ", ")) or ""
        printf("[CBL] %s %s%s", os.date("%H:%M:%S"), name, suffix)
        flush()
    end

    local throttle_last = {}
    local function log_throttled(name, ...)
        local now = time_global()
        if now - (throttle_last[name] or 0) < THROTTLE_SECONDS * 1000 then return end
        throttle_last[name] = now
        log(name, ...)
    end

    -- handlers: fire every time
    local handlers = {
        -- Core game flow
        on_game_load                        = function()            log("on_game_load") end,
        save_state                          = function()            log("save_state") end,
        load_state                          = function()            log("load_state") end,
        actor_on_init                       = function()            log("actor_on_init") end,
        actor_on_reinit                     = function()            log("actor_on_reinit") end,
        actor_on_first_update               = function()            log("actor_on_first_update") end,
        actor_on_net_destroy                = function()            log("actor_on_net_destroy") end,
        on_before_level_changing            = function()            log("on_before_level_changing") end,
        on_level_changing                   = function()            log("on_level_changing") end,
        -- on_pstor_save_all fires once per online object on every save — generates hundreds of lines.
        -- Uncomment to debug per-object persistent storage save behaviour.
        -- on_pstor_save_all                = function(go)          log("on_pstor_save_all", go) end,
        on_pstor_load_all                   = function(go)          log("on_pstor_load_all", go) end,
        se_actor_on_STATE_Write             = function()            log("se_actor_on_STATE_Write") end,
        se_actor_on_STATE_Read              = function()            log("se_actor_on_STATE_Read") end,
        fill_start_position                 = function()            log("fill_start_position") end,
        -- Input
        on_key_press                        = function(key)         log("on_key_press", key) end,
        on_key_release                      = function(key)         log("on_key_release", key) end,
        on_before_key_press                 = function(key)         log("on_before_key_press", key) end,
        on_before_key_release               = function(key)         log("on_before_key_release", key) end,
        on_console_execute                  = function(cmd)         log("on_console_execute", cmd) end,
        on_option_change                    = function()            log("on_option_change") end,
        on_localization_change              = function()            log("on_localization_change") end,
        on_screen_resolution_changed        = function()            log("on_screen_resolution_changed") end,
        on_before_save_input                = function()            log("on_before_save_input") end,
        on_before_load_input                = function(key)         log("on_before_load_input", key) end,
        -- Inventory & items
        actor_on_item_take                  = function(obj)         log("actor_on_item_take", obj) end,
        actor_on_item_take_from_box         = function(box, item)   log("actor_on_item_take_from_box", item) end,
        actor_on_item_put_in_box            = function(item)        log("actor_on_item_put_in_box", item) end,
        actor_on_item_drop                  = function(obj)         log("actor_on_item_drop", obj) end,
        actor_on_item_use                   = function(obj, sec)    log("actor_on_item_use", obj, sec) end,
        actor_on_item_before_use            = function(obj)         log("actor_on_item_before_use", obj) end,
        actor_on_item_before_pickup         = function(obj)         log("actor_on_item_before_pickup", obj) end,
        actor_item_to_belt                  = function(obj)         log("actor_item_to_belt", obj) end,
        actor_item_to_ruck                  = function(obj)         log("actor_item_to_ruck", obj) end,
        actor_item_to_slot                  = function(obj)         log("actor_item_to_slot", obj) end,
        actor_on_trade                      = function(obj, sell, cost) log("actor_on_trade", obj, sell, cost) end,
        -- Combat & damage
        actor_on_before_hit                 = function(s, bone)     log("actor_on_before_hit", bone) end,
        actor_on_hit_callback               = function(obj, amt)    log("actor_on_hit_callback", amt) end,
        actor_on_before_death               = function(who_id)      log("actor_on_before_death", who_id) end,
        actor_on_feeling_anomaly            = function(anomaly)     log("actor_on_feeling_anomaly", anomaly) end,
        -- Weapons
        actor_on_weapon_fired               = function(obj, wpn)    log("actor_on_weapon_fired", wpn) end,
        actor_on_weapon_before_fire         = function()            log("actor_on_weapon_before_fire") end,
        actor_on_weapon_jammed              = function(wpn)         log("actor_on_weapon_jammed", wpn) end,
        actor_on_weapon_no_ammo             = function(wpn)         log("actor_on_weapon_no_ammo", wpn) end,
        actor_on_weapon_reload              = function(wpn)         log("actor_on_weapon_reload", wpn) end,
        actor_on_weapon_lower               = function(wpn)         log("actor_on_weapon_lower", wpn) end,
        actor_on_weapon_raise               = function(wpn)         log("actor_on_weapon_raise", wpn) end,
        actor_on_weapon_zoom_in             = function(wpn)         log("actor_on_weapon_zoom_in", wpn) end,
        actor_on_weapon_zoom_out            = function(wpn)         log("actor_on_weapon_zoom_out", wpn) end,
        actor_on_before_throwable_select    = function()            log("actor_on_before_throwable_select") end,
        actor_on_hud_animation_play         = function(anm, obj)    log("actor_on_hud_animation_play", obj) end,
        actor_on_hud_animation_end          = function(obj, name)   log("actor_on_hud_animation_end", obj, name) end,
        actor_on_hud_animation_mark         = function(mark, name)  log("actor_on_hud_animation_mark", mark, name) end,
        -- Movement & interaction
        actor_on_sleep                      = function(hours)       log("actor_on_sleep", hours) end,
        actor_on_jump                       = function()            log("actor_on_jump") end,
        actor_on_land                       = function(spd)         log("actor_on_land", spd) end,
        actor_on_movement_changed           = function(mtype)       log("actor_on_movement_changed", mtype) end,
        -- actor_on_interaction fires continuously while the player faces usable objects — very noisy.
        -- Uncomment to debug interaction triggers.
        -- actor_on_interaction             = function(itype, obj, sec) log("actor_on_interaction", itype, sec) end,
        actor_on_attach_vehicle             = function(v)           log("actor_on_attach_vehicle", v) end,
        actor_on_detach_vehicle             = function(v)           log("actor_on_detach_vehicle", v) end,
        actor_on_use_vehicle                = function(v)           log("actor_on_use_vehicle", v) end,
        actor_on_leave_dialog               = function(id)          log("actor_on_leave_dialog", id) end,
        actor_on_stash_create               = function()            log("actor_on_stash_create") end,
        actor_on_stash_remove               = function()            log("actor_on_stash_remove") end,
        actor_on_frequency_change           = function(old, new)    log("actor_on_frequency_change", old, new) end,
        actor_on_achievement_earned         = function(id, name)    log("actor_on_achievement_earned", id, name) end,
        actor_on_info_callback              = function(obj, info_id) log("actor_on_info_callback", info_id) end,
        -- NPCs
        npc_on_death_callback               = function(victim, who) log("npc_on_death_callback", victim, who) end,
        npc_on_before_hit                   = function(npc)         log("npc_on_before_hit", npc) end,
        npc_on_hit_callback                 = function(npc, amt)    log("npc_on_hit_callback", npc, amt) end,
        npc_on_net_spawn                    = function(npc)         log("npc_on_net_spawn", npc) end,
        npc_on_net_destroy                  = function(npc)         log("npc_on_net_destroy", npc) end,
        npc_on_use                          = function(npc)         log("npc_on_use", npc) end,
        npc_on_item_take                    = function(npc, item)   log("npc_on_item_take", npc, item) end,
        npc_on_item_take_from_box           = function(npc, item)   log("npc_on_item_take_from_box", npc, item) end,
        npc_on_item_drop                    = function(npc, item)   log("npc_on_item_drop", npc, item) end,
        npc_on_fighting_actor               = function(npc)         log("npc_on_fighting_actor", npc) end,
        npc_on_weapon_strapped              = function(npc, wpn)    log("npc_on_weapon_strapped", npc) end,
        npc_on_weapon_unstrapped            = function(npc, wpn)    log("npc_on_weapon_unstrapped", npc) end,
        npc_on_weapon_drop                  = function(npc, wpn)    log("npc_on_weapon_drop", npc) end,
        npc_on_get_all_from_corpse          = function(npc)         log("npc_on_get_all_from_corpse", npc) end,
        -- se_stalker_on_spawn fires for every stalker in the A-Life simulation on load — thousands of lines.
        -- Uncomment to debug server-side stalker spawn events.
        -- se_stalker_on_spawn              = function()            log("se_stalker_on_spawn") end,
        -- Monsters
        monster_on_death_callback           = function(victim)      log("monster_on_death_callback", victim) end,
        monster_on_before_hit               = function(monster)     log("monster_on_before_hit", monster) end,
        monster_on_hit_callback             = function(monster, amt) log("monster_on_hit_callback", monster, amt) end,
        monster_on_net_spawn                = function(monster)     log("monster_on_net_spawn", monster) end,
        monster_on_net_destroy              = function(monster)     log("monster_on_net_destroy", monster) end,
        monster_on_actor_use_callback       = function(monster)     log("monster_on_actor_use_callback", monster) end,
        monster_on_loot_init                = function(monster)     log("monster_on_loot_init", monster) end,
        burer_on_before_weapon_drop         = function(burer)       log("burer_on_before_weapon_drop", burer) end,
        anomaly_on_before_activate          = function(anomaly)     log("anomaly_on_before_activate", anomaly) end,
        -- Squads & simulation
        -- The callbacks below fire for every squad during A-Life simulation — hundreds to thousands of
        -- lines on load. Uncomment individually to debug specific squad/simulation behaviour.
        -- squad_on_npc_creation            = function()            log("squad_on_npc_creation") end,
        squad_on_npc_death                  = function()            log("squad_on_npc_death") end,
        -- squad_on_add_npc                 = function(sq, npc, sec) log("squad_on_add_npc", sec) end,
        -- squad_on_enter_smart             = function()            log("squad_on_enter_smart") end,
        -- squad_on_leave_smart             = function()            log("squad_on_leave_smart") end,
        -- squad_on_first_update            = function()            log("squad_on_first_update") end,
        -- squad_on_after_game_vertex_change = function()           log("squad_on_after_game_vertex_change") end,
        -- squad_on_after_level_change      = function(sq, old, new) log("squad_on_after_level_change", old, new) end,
        -- on_try_respawn                   = function()            log("on_try_respawn") end,
        -- UI & inventory screens
        GUI_on_show                         = function(name)        log("GUI_on_show", name) end,
        GUI_on_hide                         = function(name)        log("GUI_on_hide", name) end,
        ActorMenu_on_mode_changed           = function(old, new)    log("ActorMenu_on_mode_changed", old, new) end,
        ActorMenu_on_before_init_mode       = function(mode)        log("ActorMenu_on_before_init_mode", mode) end,
        ActorMenu_on_item_drag_drop         = function(item)        log("ActorMenu_on_item_drag_drop", item) end,
        ActorMenu_on_item_focus_receive     = function(item)        log("ActorMenu_on_item_focus_receive", item) end,
        ActorMenu_on_item_focus_lost        = function(item)        log("ActorMenu_on_item_focus_lost", item) end,
        ActorMenu_on_item_before_move       = function(fl, mode, item) log("ActorMenu_on_item_before_move", item) end,
        ActorMenu_on_item_after_move        = function(mode, item)  log("ActorMenu_on_item_after_move", item) end,
        ActorMenu_on_trade_started          = function()            log("ActorMenu_on_trade_started") end,
        ActorMenu_on_trade_closed           = function()            log("ActorMenu_on_trade_closed") end,
        map_spot_menu_add_property          = function(w, id, sec)  log("map_spot_menu_add_property", sec) end,
        map_spot_menu_property_clicked      = function(w, id, sec)  log("map_spot_menu_property_clicked", sec) end,
        -- Main menu (fires when opened mid-game; not at app start — see top-of-file note)
        main_menu_on_init                   = function()            log("main_menu_on_init") end,
        main_menu_on_quit                   = function()            log("main_menu_on_quit") end,
        main_menu_on_keyboard               = function(key)         log("main_menu_on_keyboard", key) end,
        -- Physics, vehicles & misc
        physic_object_on_hit_callback       = function(obj, amt)    log("physic_object_on_hit_callback", obj, amt) end,
        physic_object_on_use_callback       = function(obj)         log("physic_object_on_use_callback", obj) end,
        heli_on_hit_callback                = function(heli, amt)   log("heli_on_hit_callback", amt) end,
        vehicle_on_death_callback           = function(id)          log("vehicle_on_death_callback", id) end,
        on_before_surge                     = function()            log("on_before_surge") end,
        on_before_psi_storm                 = function()            log("on_before_psi_storm") end,
        bullet_on_hit                       = function(sec, obj)    log("bullet_on_hit", sec) end,
        on_get_item_cost                    = function()            log("on_get_item_cost") end,
    }

    -- throttled_handlers: at most one log per THROTTLE_SECONDS
    local throttled_handlers = {
        actor_on_update             = function()    log_throttled("actor_on_update") end,
        on_key_hold                 = function(key) log_throttled("on_key_hold", key) end,
        on_before_key_hold          = function(key) log_throttled("on_before_key_hold", key) end,
        actor_on_foot_step          = function()    log_throttled("actor_on_foot_step") end,
        actor_on_footstep           = function(s)   log_throttled("actor_on_footstep", s) end,
        npc_on_update               = function(npc) log_throttled("npc_on_update", npc) end,
        monster_on_update           = function(m)   log_throttled("monster_on_update", m) end,
        squad_on_update             = function()    log_throttled("squad_on_update") end,
        smart_terrain_on_update     = function()    log_throttled("smart_terrain_on_update") end,
        -- high-volume even outside per-tick loops
        on_xml_read                 = function(p)           log_throttled("on_xml_read", p) end,
        server_entity_on_register   = function(o, t)        log_throttled("server_entity_on_register", t) end,
        server_entity_on_unregister = function(o, t)        log_throttled("server_entity_on_unregister", t) end,
        on_enemy_eval               = function(npc, enemy)  log_throttled("on_enemy_eval", npc, enemy) end,
        npc_on_eval_danger          = function(npc)         log_throttled("npc_on_eval_danger", npc) end,
        npc_on_choose_weapon        = function(npc)         log_throttled("npc_on_choose_weapon", npc) end,
        npc_shot_dispersion         = function(npc)         log_throttled("npc_shot_dispersion", npc) end,
        npc_on_hear_callback        = function(npc, who)    log_throttled("npc_on_hear_callback", npc, who) end,
    }

    function on_game_start()
        for name, fn in pairs(handlers) do
            RegisterScriptCallback(name, fn)
        end
        for name, fn in pairs(throttled_handlers) do
            RegisterScriptCallback(name, fn)
        end
    end

    function on_game_end()
        for name, fn in pairs(handlers) do
            UnregisterScriptCallback(name, fn)
        end
        for name, fn in pairs(throttled_handlers) do
            UnregisterScriptCallback(name, fn)
        end
    end
    ```

=== "callback_logger_mcm.script"

    ```lua
    -- callback_logger_mcm.script
    -- MCM registration for Callback Logger.

    function on_mcm_load()
        return {
            id = "callback_logger",
            sh = true,
            gr = {
                {
                    id      = "enabled",
                    type    = "check",
                    val     = 1,
                    def     = true,
                    text    = "ui_mcm_callback_logger_enabled",
                },
            }
        }
    end
    ```

=== "ui_st_callback_logger.xml"

    ```xml
    <?xml version="1.0" encoding="windows-1251"?>
    <string_table>
        <string id="ui_mcm_menu_callback_logger">
            <text>Callback Logger</text>
        </string>
        <string id="ui_mcm_callback_logger_enabled">
            <text>Enable callback logging</text>
        </string>
    </string_table>
    ```
