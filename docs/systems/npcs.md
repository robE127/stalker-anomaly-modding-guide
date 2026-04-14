# NPCs & Factions

This page covers working with NPCs, mutants, squads, and the faction relation system from script.

---

## NPC vs mutant

Anomaly has two broad categories of AI entities:

| | Stalkers / humanoid NPCs | Mutants / creatures |
|--|--|--|
| Class | `CAI_Stalker` | Various monster classes |
| Check | `IsStalker(obj)` | `IsMonster(obj)` |
| Death callback | `npc_on_death_callback` | `monster_on_death_callback` |
| Faction | Yes (`.community()`) | No |
| Dialog | Yes | No |
| Squad | Usually | Rarely (some creature packs) |

---

## Death callbacks

The two most common NPC callbacks. Both follow the same pattern.

### npc_on_death_callback

Fires when any humanoid NPC dies.

```lua
local function npc_on_death_callback(victim, who)
    -- victim and who are game_object references
    -- who can be nil (killed by environment / anomaly)
    if not (victim and who) then return end

    local victim_name = victim:name()
    local killer_name = who:name()
    printf("[my_mod] %s killed by %s", victim_name, killer_name)

    -- Check if player was the killer
    if who:id() == 0 then   -- actor always has id 0 on the client
        on_player_killed_npc(victim)
    end
end

function on_game_start()
    RegisterScriptCallback("npc_on_death_callback", npc_on_death_callback)
end

function on_game_end()
    UnregisterScriptCallback("npc_on_death_callback", npc_on_death_callback)
end
```

### monster_on_death_callback

Same signature, fires for mutants.

```lua
local function monster_on_death_callback(victim, who)
    if not (victim and who) then return end
    -- same pattern as npc_on_death_callback
end
```

---

## Modifying incoming hits

`npc_on_before_hit` fires before damage is applied to an NPC. You can read the hit, modify it, or cancel it entirely.

```lua
local function npc_on_before_hit(npc, hit, bone_id, flags)
    -- hit.draftsman  = source game_object (who fired the shot)
    -- hit.type       = hit type (hit.wound, hit.explosion, etc.)
    -- hit.power      = damage amount
    -- bone_id        = bone that was hit

    -- Example: cancel all damage from the actor to a specific NPC
    if hit.draftsman and hit.draftsman:id() == 0 then
        if npc:name() == "my_protected_npc" then
            flags.ret_value = false   -- block the hit
        end
    end

    -- Example: halve all damage to NPCs from explosions
    if hit.type == hit.explosion then
        hit.power = hit.power * 0.5
    end
end

function on_game_start()
    RegisterScriptCallback("npc_on_before_hit", npc_on_before_hit)
end
```

The equivalent `actor_on_before_hit` fires when the player is hit.

---

## NPC game_object methods

When you have an NPC as a `game_object` (from a callback or `db.storage`), the common methods:

```lua
-- Identity
npc:id()                    -- numeric ID
npc:name()                  -- internal name (unique per NPC)
npc:character_name()        -- display name (for PDA/dialog)
npc:section()               -- config section
npc:community()             -- faction string, e.g. "stalker", "bandit", "dolg"

-- Status
npc:alive()                 -- true if alive
npc:health                  -- property (0.0–1.0)
npc:position()              -- vector3
npc:game_vertex_id()
npc:level_vertex_id()

-- Sight
npc:see(obj)                -- can NPC see this object?

-- Info portions
npc:give_info_portion(id)
npc:has_info(id)
npc:disable_info_portion(id)

-- Relations
npc:relation(other)         -- game_object.enemy / .neutral / .friend
npc:sympathy()              -- 0.0–1.0
npc:set_sympathy(v)
npc:force_set_goodwill(value, target)
```

---

## db.storage — per-NPC Lua state

`db.storage` is a table keyed by object ID that holds each online NPC's Lua-side state. It's written by the NPC binder when the NPC enters the world, and cleared when it leaves.

```lua
-- Get the game_object for any online NPC by ID
local npc = db.storage[id] and db.storage[id].object

if npc and npc:alive() then
    local pos = npc:position()
end
```

Key fields inside `db.storage[id]`:

| Field | Description |
|-------|-------------|
| `.object` | The NPC's `game_object` |
| `.active_section` | Current behavior section (e.g. `"walker@idle"`) |
| `.state_mgr` | State machine manager instance |
| `.move_mgr` | Movement manager instance |
| `.squad_id` | Squad ID (may not always be present) |

!!! note
    `db.storage[id]` only exists while the NPC is **online** (within spawn distance). For offline NPCs, use `alife_object(id)` to get the server-side entity.

---

## Factions and relations

### Reading relations

```lua
local relation = game_relations.get_npcs_relation(npc1, npc2)
-- returns: game_object.friend, game_object.neutral, or game_object.enemy

if relation == game_object.enemy then
    -- hostile
end
```

### Setting relations

```lua
game_relations.set_npcs_relation(npc, db.actor, game_relations.FRIENDS)
-- game_relations.FRIENDS  =  1000
-- game_relations.NEUTRALS =     0
-- game_relations.ENEMIES  = -1000

-- Set NPC sympathy (0.0 = hate, 1.0 = love)
game_relations.set_npc_sympathy(npc, 0.8)
```

### Community/faction goodwill

```lua
-- Actor's goodwill with a faction (-10000 to 10000)
local goodwill = db.actor:community_goodwill("dolg")
db.actor:set_community_goodwill("dolg", 1000)

-- NPC's faction community (short name)
local faction = npc:community()  -- "stalker", "bandit", "dolg", "freedom", etc.
```

---

## Squads

Squads are the server-side grouping of NPCs. They have their own `se_abstract` object accessible via `alife_object(squad_id)`.

### Getting an NPC's squad

```lua
local function get_squad(npc_or_se_obj)
    return get_object_squad(npc_or_se_obj)  -- helper from _g.script
end

-- Or manually from the server entity
local se_npc = alife_object(npc:id())
if se_npc and se_npc.group_id ~= 65535 then
    local squad = alife_object(se_npc.group_id)
    -- use squad
end
```

### Iterating squad members

```lua
local squad = get_object_squad(npc)
if squad then
    for member in squad:squad_members() do
        -- member.id is the NPC's ID
        local member_obj = db.storage[member.id] and db.storage[member.id].object
        if member_obj and member_obj:alive() then
            printf("squad member: %s", member_obj:name())
        end
    end

    local leader_id = squad:commander_id()
    local count     = squad:npc_count()
end
```

---

## Dialog system

Dialog conditions and actions are plain Lua functions called from dialog XML. The XML references them by `script_text` function name.

### Condition function (precondition)

Returns `true` to show a dialog option, `false` to hide it.

```lua
-- In dialogs.script or your own script file (must be a global function)
function my_mod_can_give_quest(first_speaker, second_speaker)
    -- first_speaker = NPC, second_speaker = actor (db.actor)
    return not db.actor:has_info("my_mod_quest_given")
        and first_speaker:community() == "stalker"
end
```

### Action function (dialog result)

Called when the player selects a dialog option. No return value.

```lua
function my_mod_give_quest(first_speaker, second_speaker)
    db.actor:give_info_portion("my_mod_quest_given")
    alife_create_item("my_quest_document", db.actor)
    news_manager.send_tip(db.actor, "my_mod_quest_start_tip", 0, first_speaker, 7000)
end
```

### Registering in dialog XML

```xml
<dialog id="my_mod_quest_dialog">
    <phrase_list>
        <phrase id="0">
            <text>my_mod_dialog_ask</text>
            <next>1</next>
        </phrase>
        <phrase id="1">
            <text>my_mod_dialog_response</text>
            <precondition>my_mod_can_give_quest</precondition>
            <action>my_mod_give_quest</action>
        </phrase>
    </phrase_list>
</dialog>
```

---

## Common patterns

### Give loot when an NPC dies

```lua
local function npc_on_death_callback(victim, who)
    if not victim then return end
    if victim:name() ~= "my_special_npc" then return end

    -- Spawn items on their body (will appear when looting)
    alife_create_item("my_special_document", victim)
    alife_create_item("bandage", victim)
end
```

### Check if the player killed an NPC

```lua
local function npc_on_death_callback(victim, who)
    if not (victim and who) then return end
    if who:id() ~= db.actor:id() then return end  -- actor's client id is 0, but use :id() for clarity

    -- Player made the kill
    my_data.player_kills = (my_data.player_kills or 0) + 1
end
```

### Find all online NPCs of a faction

```lua
local function get_online_faction_npcs(faction)
    local result = {}
    for id, data in pairs(db.storage) do
        local obj = data.object
        if obj and obj:alive() and IsStalker(obj) and obj:community() == faction then
            result[#result + 1] = obj
        end
    end
    return result
end
```

### Make all nearby NPCs friendly

```lua
local function pacify_nearby(radius)
    level.iterate_nearest(db.actor:position(), radius, function(obj)
        if IsStalker(obj) and obj:alive() then
            game_relations.set_npc_sympathy(obj, 1.0)
            game_relations.set_npcs_relation(obj, db.actor, game_relations.FRIENDS)
        end
    end)
end
```
