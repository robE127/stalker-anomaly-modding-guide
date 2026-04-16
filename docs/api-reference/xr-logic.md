# xr_logic

`xr_logic` is a Lua script module (not an engine global) that provides the condition list evaluator and NPC behavior scheme system. It's the engine under the NPC scripting layer — understanding it unlocks how Anomaly's AI and quest logic actually works.

---

## What is a condition list?

A **condlist** is a mini-language embedded in `.ltx` config field values. It encodes branching logic as a string that the script system evaluates at runtime.

**Basic syntax:**

```
result_section
result_section, fallback_section
{conditions} result_section
{conditions} result_section %effects%, fallback_section
```

The evaluator reads left to right, stopping at the first clause whose conditions all pass. It returns that clause's section name and applies any effects.

**Condition operators inside `{}`:**

| Operator | Meaning |
|----------|---------|
| `+info_id` | Actor has this info portion |
| `-info_id` | Actor does NOT have this info portion |
| `=func_name` | `xr_conditions.func_name(actor, npc, nil)` returns true |
| `=func_name(p1:p2)` | Same, with parameters passed as a table |
| `!func_name` | The function returns false |
| `~50` | 50% random chance |

**Effect operators inside `%`:**

| Operator | Meaning |
|----------|---------|
| `+info_id` | Give actor this info portion |
| `-info_id` | Remove info portion from actor |
| `=func_name` | Call `xr_effects.func_name(actor, npc, nil)` |
| `=func_name(p1:p2)` | Same, with parameters |

**Examples from base game configs:**

```ltx
; Simple: always returns "walker"
active = walker

; Two branches: if flag given, use walker@bandit, otherwise walker
on_info = {+zat_b5_actor_with_bandits} walker@bandit, walker

; Multiple conditions: dist <= 6 AND actor visible → switch to walker@fight
on_actor_dist_le = 6 | walker@fight

; Condition with function and params, plus effect
combat_ignore_cond = {=check_enemy_name(zat_b5_dealer)} true, {=fighting_dist_ge(30)} true

; Effect only — no result, just fire side-effects
on_death = {=some_condition} %=inc_counter(stalker_death)%
```

---

## Parsing a condlist

Before you can evaluate a condlist, you must parse the raw string. The result is a table that can be evaluated repeatedly.

```lua
-- xr_logic.parse_condlist(obj, section_name, field_name, raw_string)
-- Returns a compiled condlist table (cached — safe to call repeatedly with the same string)
local condlist = xr_logic.parse_condlist(npc, "my_section", "my_field", raw_string)
```

The `obj`, section, and field arguments are only used for error-reporting — they don't affect parsing.

---

## Evaluating a condlist

```lua
-- xr_logic.pick_section_from_condlist(actor, npc, condlist)
-- Returns the section name string of the first matching clause, or nil
local result = xr_logic.pick_section_from_condlist(db.actor, npc, condlist)

if result == "true" then
    -- all conditions met, effects applied
elseif result == "false" or result == nil then
    -- conditions not met
end
```

When the function runs:
1. It iterates through each clause in the compiled condlist
2. For each clause it checks all conditions (info portions + function calls)
3. The first clause with all conditions satisfied: applies effects and returns the section name
4. If no clause matches, returns `nil`

---

## Reading condlists from config

### Read a plain condlist field

```lua
-- Reads and parses a condlist from an INI file field
local cl = xr_logic.cfg_get_condlist(ini, section, "active", npc)
-- cl is {name = "active", condlist = <compiled table>} or nil
```

### Read a number+condlist field

```lua
-- For fields like: on_actor_dist_le = 6 | walk_away
local entry = xr_logic.cfg_get_number_and_condlist(ini, section, "on_actor_dist_le", npc)
-- entry.v1 = 6 (the number)
-- entry.condlist = <compiled condlist for "walk_away">
```

### Read a string+condlist field

```lua
-- For fields like: on_signal = arrived | next_section
local entry = xr_logic.cfg_get_string_and_condlist(ini, section, "on_signal", npc)
-- entry.v1 = "arrived"
-- entry.condlist = <compiled condlist>
```

---

## Adding custom conditions and effects

`xr_logic` exposes two global tables where you can register your own functions:

```lua
-- Register a custom condition
-- Called as: =my_mod_player_is_rich in a condlist
xr_conditions.my_mod_player_is_rich = function(actor, npc, params)
    return actor:money() >= 10000
end

-- Register a custom effect
-- Called as: %=my_mod_reward_player% in a condlist
xr_effects.my_mod_reward_player = function(actor, npc, params)
    actor:give_money(1000)
    actor:give_info_portion("my_mod_rewarded")
end
```

Once registered, these can be used in any `.ltx` config that is evaluated through `xr_logic`:

```ltx
; In a dialog condition
on_info = {=my_mod_player_is_rich} rich_dialog %=my_mod_reward_player%, poor_dialog
```

Parameters are passed as a colon-separated string and arrive in `params` as a table:

```lua
-- Called as: =my_mod_check(25:100)
xr_conditions.my_mod_check = function(actor, npc, params)
    local min = tonumber(params[1])  -- 25
    local max = tonumber(params[2])  -- 100
    return actor:money() >= min and actor:money() <= max
end
```

---

## State machine: switching sections

`xr_logic` drives NPC behavior by switching between named sections in `.ltx` config. Each section defines a behavior scheme (`walker`, `combat`, `patrol`, etc.) plus switch conditions.

```lua
-- Force an NPC to switch to a new behavior section
xr_logic.switch_to_section(npc, st.ini, "new_section_name")

-- Internally called each update to check all on_* conditions
xr_logic.try_switch_to_another_section(npc, st, db.actor)
```

The common `on_*` switch trigger fields are:

| Field | Trigger |
|-------|---------|
| `on_info` | Info portion state changes |
| `on_actor_dist_le = N \| section` | Actor within N metres |
| `on_actor_dist_ge = N \| section` | Actor beyond N metres |
| `on_timer = N \| section` | N milliseconds elapsed |
| `on_signal = sig \| section` | Named signal fired |
| `on_actor_in_zone = zone \| section` | Actor enters named zone |
| `on_first_update` | Fires once on first update |

---

## Scripted creature control

For creatures (mutants), `xr_logic` provides take/release of script control:

```lua
-- Take script control (enables Lua-driven actions)
xr_logic.mob_capture(creature_obj, true)

-- Release back to engine AI
xr_logic.mob_release(creature_obj)

-- Check if currently captured
if xr_logic.mob_captured(creature_obj) then ... end
```

---

## Practical patterns

### Evaluate a hardcoded condlist string

```lua
local raw = "{+my_mod_quest_done} complete, in_progress"
local condlist = xr_logic.parse_condlist(nil, "", "", raw)
local result = xr_logic.pick_section_from_condlist(db.actor, nil, condlist)
-- result == "complete" if the actor has "my_mod_quest_done"
-- result == "in_progress" otherwise
```

### Custom condition that reads a save variable

```lua
-- In your mod's init (at top level or in on_game_start)
xr_conditions.my_mod_has_seen_stalker = function(actor, npc, params)
    return my_mod_data.seen_stalker == true
end
```

### Custom effect that grants items

```lua
xr_effects.my_mod_give_quest_reward = function(actor, npc, params)
    local count = tonumber(params and params[1]) or 1
    for i = 1, count do
        alife_create_item("bandage", actor)
    end
    actor:give_info_portion("my_mod_rewarded")
end
```

---

## When you'll use xr_logic

Most mod scripts don't need to call `xr_logic` directly. It's most relevant when:

- **Writing NPC behavior scripts** — if you create a custom behavior scheme, you drive it via xr_logic
- **Adding condlist conditions or effects** — register into `xr_conditions` / `xr_effects`
- **Reading condlist values from config** — when your mod's `.ltx` fields need condlist support
- **Evaluating condlist strings dynamically** — when you want to check complex game state expressed as condlist syntax

For simple checks (has info portion, has item, etc.) it's always cleaner to check directly in Lua rather than going through the condlist evaluator.

---

## See also

- [Glossary: condition list](../reference/glossary.md#condition-list) — definition and syntax summary
- [Systems: NPCs & Factions](../systems/npcs.md) — how condlists drive NPC behavior schemes
