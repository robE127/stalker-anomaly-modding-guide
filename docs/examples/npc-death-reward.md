# Example: NPC Death Reward

A complete mod that gives the player a reward when they kill specific NPCs — money, items, or both. Demonstrates the death callback, identity checks, spawning loot, and preventing duplicate rewards.

---

## What this builds

- When the player kills an NPC matching certain criteria (faction, name, or any), give a reward
- Reward can be money, items, or a custom notification
- Rewards are only given once per NPC (tracked by object ID in save data)
- Configurable reward amounts via MCM

---

## Files

```
gamedata/
  scripts/
    my_death_reward.script
    my_death_reward_mcm.script
  configs/
    text/
      eng/
        ui_st_my_death_reward.xml
```

---

## my_death_reward_mcm.script

```lua
function on_mcm_load()
    return {
        id = "my_death_reward",
        sh = true,
        gr = {
            {
                id      = "banner",
                type    = "slide",
                text    = "ui_mcm_my_death_reward",
                link    = "ui_options_slider_player",
                size    = {512, 50},
                spacing = 20,
            },
            {
                id   = "enable",
                type = "check",
                val  = 1,
                def  = true,
                text = "ui_mcm_my_death_reward_enable",
            },
            {
                id   = "reward_money",
                type = "track",
                val  = 2,
                min  = 0,
                max  = 5000,
                step = 100,
                def  = 500,
                text = "ui_mcm_my_death_reward_money",
            },
        }
    }
end
```

---

## my_death_reward.script

```lua
-- ─────────────────────────────────────────────────────────────
-- Config
-- ─────────────────────────────────────────────────────────────

local defaults = {
    enable       = true,
    reward_money = 500,
}

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_death_reward/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

-- ─────────────────────────────────────────────────────────────
-- State
-- ─────────────────────────────────────────────────────────────

-- Track which NPC IDs we've already rewarded (prevents duplicates)
local rewarded = {}

-- ─────────────────────────────────────────────────────────────
-- Reward criteria
-- ─────────────────────────────────────────────────────────────

-- Return true if this NPC should give a reward when killed by the player
local function should_reward(victim)
    -- Example 1: specific named NPC
    -- if victim:name() == "zat_b33_stalker_hermit" then return true end

    -- Example 2: specific faction
    local community = victim:character_community()
    if community == "bandit" or community == "monolith" then
        return true
    end

    -- Example 3: any NPC killed by the player
    -- return true

    return false
end

-- ─────────────────────────────────────────────────────────────
-- Give the reward
-- ─────────────────────────────────────────────────────────────

local function give_reward(victim)
    local money = cfg("reward_money")
    if money > 0 then
        db.actor:give_money(money)
    end

    -- Also drop a bonus item at the victim's location
    alife_create_item("bandage", victim)

    -- Notify the player
    local msg = string.format(
        game.translate_string("my_death_reward_got_reward"),
        money
    )
    actor_menu.set_msg(1, msg, 4)
    news_manager.relocate_money(db.actor, "in", money)
end

-- ─────────────────────────────────────────────────────────────
-- Death callback
-- ─────────────────────────────────────────────────────────────

local function npc_on_death_callback(victim, who)
    -- Basic guards
    if not (victim and who) then return end
    if not cfg("enable") then return end

    -- Only reward for player kills
    -- The actor's id() returns 0 on the client side
    if who:id() ~= db.actor:id() then return end

    local victim_id = victim:id()

    -- Don't reward the same NPC twice (they can die only once, but be safe)
    if rewarded[victim_id] then return end

    -- Check criteria
    if not should_reward(victim) then return end

    rewarded[victim_id] = true
    give_reward(victim)
end

-- ─────────────────────────────────────────────────────────────
-- Save / load
-- ─────────────────────────────────────────────────────────────

local function save_state(m_data)
    m_data.my_death_reward = {
        rewarded = rewarded,
    }
end

local function load_state(m_data)
    local saved = m_data.my_death_reward or {}
    rewarded = saved.rewarded or {}
end

-- ─────────────────────────────────────────────────────────────
-- Lifecycle
-- ─────────────────────────────────────────────────────────────

function on_game_start()
    RegisterScriptCallback("npc_on_death_callback", npc_on_death_callback)
    RegisterScriptCallback("save_state",            save_state)
    RegisterScriptCallback("load_state",            load_state)
end

function on_game_end()
    UnregisterScriptCallback("npc_on_death_callback", npc_on_death_callback)
    UnregisterScriptCallback("save_state",            save_state)
    UnregisterScriptCallback("load_state",            load_state)
    rewarded = {}
end
```

---

## ui_st_my_death_reward.xml

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="ui_mcm_my_death_reward">
        <text>Death Reward Mod</text>
    </string>
    <string id="ui_mcm_my_death_reward_enable">
        <text>Enable kill rewards</text>
    </string>
    <string id="ui_mcm_my_death_reward_money">
        <text>Reward (roubles per kill)</text>
    </string>
    <string id="my_death_reward_got_reward">
        <text>Kill reward: +%d roubles.</text>
    </string>
</string_table>
```

---

## How it works

**Identifying the actor as killer.** `who:id()` returns the client-side ID. The player actor always has ID `0` on the client. Comparing against `db.actor:id()` is slightly more robust than hardcoding `0`.

**`victim:character_community()`.** Returns the full faction string (`"stalker"`, `"bandit"`, `"dolg"`, etc.). This is the right method for faction checks. `victim:community()` may return a shorter form.

**Spawning on the body.** `alife_create_item("bandage", victim)` creates the item at the victim's position. When the victim goes offline after death, the item remains on the ground. Do this _before_ the victim's client object is invalidated — during the callback is safe.

**Duplicate prevention.** `rewarded` is a table of already-rewarded NPC IDs, saved across sessions. An NPC can only die once, but having the guard is good practice, and it protects against edge cases in other mods that respawn NPCs.

**`news_manager.relocate_money`.** Shows a standard "+N roubles" news notification at the top of the screen — the same style as quest rewards.

---

## Variations

### Reward only named target NPCs

```lua
local TARGET_NPCS = {
    zat_b33_stalker_hermit = 1000,
    jup_b6_scientist_nuclear = 2000,
}

local function npc_on_death_callback(victim, who)
    if not (victim and who) then return end
    if who:id() ~= db.actor:id() then return end

    local reward = TARGET_NPCS[victim:name()]
    if not reward then return end

    db.actor:give_money(reward)
    actor_menu.set_msg(1, "Target eliminated. " .. reward .. " roubles.", 4)
end
```

### Reward based on victim's rank

```lua
local function npc_on_death_callback(victim, who)
    if not (victim and who) then return end
    if who:id() ~= db.actor:id() then return end
    if not IsStalker(victim) then return end

    local se_vic = alife_object(victim:id())
    if not se_vic then return end

    -- Higher-rank NPCs give more money
    local rank   = se_vic:rank and se_vic:rank() or 0
    local reward = 100 + rank * 50
    db.actor:give_money(reward)
end
```

### Give info portion on kill (quest trigger)

```lua
local function npc_on_death_callback(victim, who)
    if not (victim and who) then return end
    if who:id() ~= db.actor:id() then return end

    if victim:name() == "my_quest_target_npc" then
        db.actor:give_info_portion("my_mod_target_dead")
        news_manager.send_tip(db.actor, "my_mod_target_killed_tip", 0, nil, 6000)
    end
end
```
