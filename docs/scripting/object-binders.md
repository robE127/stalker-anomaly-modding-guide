# Object Binders

An object binder is a Lua class that attaches to a specific `game_object` and receives lifecycle callbacks for that object alone — spawn, destroy, update, save, load. Where global callbacks let you react to events across all objects of a type, a binder lets you maintain **per-object state** with clean lifecycle boundaries.

The base game uses binders for the actor (`bind_stalker.script`), all NPCs and monsters (`bind_monster.script`), crows, helicopters, and more.

---

## When to use a binder vs a global callback

A binder is the **OOP approach**: each object gets its own class instance with private state and constructor/destructor semantics. A global callback is the **procedural approach**: one function handles all objects of a type, with a shared lookup table keyed by object ID.

Both patterns can solve many of the same problems — but **most mods don't need custom binders**. Global callbacks are simpler to write and handle the vast majority of use cases. There are three situations where the binder approach wins clearly:

### Situation 1 — You need per-object state that survives save/load

Suppose you want each stalker trader to have their own independent restock cooldown: after buying them out, that specific trader won't restock for an hour. The state belongs to the trader, not to the actor.

With a **global callback**, you'd maintain a table keyed by NPC ID, manually handle cleanup when NPCs go offline, and manually hook into `save_state`/`load_state` to persist the table:

```lua
-- Global callback approach
local restock_timers = {}  -- keyed by NPC alife ID

local function npc_on_update(npc)
    local id = npc:id()
    if restock_timers[id] then
        restock_timers[id] = restock_timers[id] - 1
    end
end

local function save_state(m_data)
    m_data.my_mod = { restock_timers = restock_timers }
end

local function load_state(m_data)
    restock_timers = (m_data.my_mod or {}).restock_timers or {}
end

local function on_game_start()
    RegisterScriptCallback("npc_on_update", npc_on_update)
    RegisterScriptCallback("save_state",    save_state)
    RegisterScriptCallback("load_state",    load_state)
end
```

This works, but `restock_timers` accumulates entries for every NPC ever encountered, you need to remember to prune it, and the global `npc_on_update` runs for every NPC in the zone every frame — even the ones that don't need a restock check.

With a **binder**, each trader instance owns its timer. The binder is created when the NPC comes online and destroyed when it goes offline — no manual cleanup:

```lua
-- Binder approach (per-NPC instance)
function trader_binder:__init(obj) super(obj)
    self.restock_timer = 0
end

function trader_binder:update(delta)
    object_binder.update(self, delta)
    if self.restock_timer > 0 then
        self.restock_timer = self.restock_timer - delta
    end
end

function trader_binder:save_state(m_data)
    local state = alife_storage_manager.get_game_object_state(self.object, true)
    state.restock_timer = self.restock_timer
end

function trader_binder:load_state()
    local state = alife_storage_manager.get_game_object_state(self.object)
    self.restock_timer = state and state.restock_timer or 0
end
```

No global table, no cleanup, no running on the wrong NPCs.

### Situation 2 — You need per-frame `update()` on specific objects only

Global callbacks like `npc_on_update` fire for **every** online NPC every frame. If you only care about 3 specific entities, you're still running the check for every NPC in the zone.

A binder's `update()` only runs for the objects you've attached a binder to. If you're adding a custom device, a trap, or any entity type you control, a binder is the only way to get a per-frame update hook without paying for a global scan.

### Situation 3 — You're creating an entirely new entity type

This is the clearest case. If you're adding a new type of interactive object — a placeable sensor, a drone, a custom container — it has no existing binder. You need a binder to give it:

- `net_spawn` / `net_destroy` lifecycle
- Per-frame `update()`
- Save/load via `save_state` / `load_state`
- Per-object callbacks (`callback.hit`, `callback.use_object`, etc.)

There is no alternative here — you must write a binder.

---

!!! warning "Don't replace the existing binders"
    The base game registers binders for all NPCs (`bind_monster.script`), the actor (`bind_stalker.script`), and other entity types. If your `bind()` function replaces the one in those scripts, AI will break — the base binder sets up pathfinding, combat logic, and dozens of other systems.

    **In practice: extend via global callbacks, not by replacing binders.** Writing a custom binder is primarily for new entity types you've added yourself. For modifying existing NPC behaviour, use `RegisterScriptCallback` with the NPC lifecycle callbacks instead.

---

## Class declaration

Binders inherit from `object_binder`, a C++ base class provided by the engine:

```lua
class "my_binder" (object_binder)

function my_binder:__init(obj) super(obj)
    -- obj is the game_object this binder is attached to
    -- self.object is available from here onward
    self.my_timer = 0
end
```

`super(obj)` must be called to initialise the base class. `self.object` is set by the base class constructor and is available in every lifecycle method.

---

## Lifecycle methods

The engine calls these methods in order as an object moves through its lifecycle.

### `__init(obj)` — construction

Called once when the binder instance is created. `self.object` is already set by `super(obj)`. Use this for one-time variable initialisation.

```lua
function my_binder:__init(obj) super(obj)
    self.state = "idle"
    self.timer = 0
end
```

---

### `reinit()` — re-initialisation

Called after `__init` and also after level reloads. This is where you set up `db.storage`, register object-specific callbacks, and attach engine callbacks.

```lua
function my_binder:reinit()
    object_binder.reinit(self)                  -- always call this first
    db.storage[self.object:id()] = {}
    self.st = db.storage[self.object:id()]

    self.object:set_callback(callback.hit,   self.on_hit,   self)
    self.object:set_callback(callback.death, self.on_death, self)
end
```

---

### `net_spawn(se_abstract)` — object comes online

Called when the object transitions from offline (alife simulation) to online (loaded near the player). This is the right place to add the object to databases and finish AI setup.

**Must return `true` on success.** Returning `false` rejects the spawn.

```lua
function my_binder:net_spawn(se_abstract)
    if not object_binder.net_spawn(self, se_abstract) then
        return false
    end
    db.add_obj(self.object)
    -- object is fully online and db.storage entry exists
    return true
end
```

---

### `update(delta)` — per-frame

Called every frame while the object is online. `delta` is the elapsed time in milliseconds since the last call. Keep this fast — it runs every frame for every online object with a binder.

```lua
function my_binder:update(delta)
    object_binder.update(self, delta)   -- always call this first

    if not self.object:alive() then return end

    self.timer = self.timer + delta
    if self.timer > 5000 then           -- every 5 seconds
        self.timer = 0
        -- do something periodic
    end
end
```

---

### `net_destroy()` — object goes offline

Called when the object leaves the online zone or is permanently removed. Clean up callbacks and db.storage here. Call `object_binder.net_destroy(self)` **last** — after this call `self.object` is no longer valid.

```lua
function my_binder:net_destroy()
    self.object:set_callback(callback.hit,   nil)
    self.object:set_callback(callback.death, nil)

    db.del_obj(self.object)

    object_binder.net_destroy(self)     -- must be last
end
```

---

### `net_save_relevant()` — should this object be saved?

Return `true` to include this object's state in the save file. Return `false` for transient objects whose state doesn't need to survive a reload. Most binders return `true`.

```lua
function my_binder:net_save_relevant()
    return true
end
```

---

### `save_state(m_data)` and `load_state()` — saving and restoring state

Modern Anomaly uses marshal serialisation (`USE_MARSHAL = true`). Override these to persist your binder's data across saves.

```lua
function my_binder:save_state(m_data)
    local state = alife_storage_manager.get_game_object_state(self.object, true)
    state.my_mod = {
        timer = self.timer,
        custom_flag = self.st.custom_flag,
    }
end

function my_binder:load_state()
    local state = alife_storage_manager.get_game_object_state(self.object)
    if not (state and state.my_mod) then return end

    self.timer = state.my_mod.timer or 0
    self.st.custom_flag = state.my_mod.custom_flag
end
```

!!! note "save/load vs save_state/load_state"
    The `save(packet)` / `load(reader)` methods use legacy binary packet serialisation and are called when `USE_MARSHAL = false`. Anomaly 1.5.2 uses the marshal path (`USE_MARSHAL = true`), so `save_state` / `load_state` are what you override in practice. You only need `save` / `load` for compatibility with older code paths.

---

## Object-specific engine callbacks

Inside `reinit()` you can attach callbacks to `self.object` using `set_callback`. These fire on that object only, unlike the global `RegisterScriptCallback` which fires for all objects:

```lua
-- Available callback types (from the callback.* enum)
self.object:set_callback(callback.hit,                    self.on_hit,    self)
self.object:set_callback(callback.death,                  self.on_death,  self)
self.object:set_callback(callback.patrol_path_in_point,   self.on_waypoint, self)
self.object:set_callback(callback.sound,                  self.on_sound,  self)
self.object:set_callback(callback.use_object,             self.on_use,    self)

-- Clear a callback in net_destroy
self.object:set_callback(callback.hit, nil)
```

The third argument (`self`) is passed as the first argument to the handler, making them proper methods.

---

## Complete example — tracking an NPC that's been talked to

```lua
-- my_mod_binder.script

class "my_npc_binder" (object_binder)

function my_npc_binder:__init(obj) super(obj)
    self.greeted = false
end

function my_npc_binder:reinit()
    object_binder.reinit(self)
    db.storage[self.object:id()] = {}
    self.st = db.storage[self.object:id()]
end

function my_npc_binder:net_spawn(se_abstract)
    if not object_binder.net_spawn(self, se_abstract) then return false end
    db.add_obj(self.object)
    return true
end

function my_npc_binder:net_destroy()
    db.del_obj(self.object)
    object_binder.net_destroy(self)
end

function my_npc_binder:net_save_relevant()
    return true
end

function my_npc_binder:save_state(m_data)
    local state = alife_storage_manager.get_game_object_state(self.object, true)
    state.my_npc_binder = { greeted = self.greeted }
end

function my_npc_binder:load_state()
    local state = alife_storage_manager.get_game_object_state(self.object)
    if state and state.my_npc_binder then
        self.greeted = state.my_npc_binder.greeted or false
    end
end

function my_npc_binder:update(delta)
    object_binder.update(self, delta)
end

-- Attach the binder to all stalker NPCs
function bind(obj)
    obj:bind_object(my_npc_binder(obj))
end
```

---

## How binders are registered with the engine

The engine associates binder classes with entity types in `class_registrator.script`:

```lua
cs_register(object_factory, "CAI_Stalker", "se_stalker.se_stalker", "AI_STL_S", "script_stalker")
cs_register(object_factory, "CActor",      "se_actor.se_actor",     "S_ACTOR",  "script_actor")
```

When an entity of a given type comes online, the engine calls the `bind(obj)` function in the script registered for that class. That function creates the binder and attaches it:

```lua
-- bind_monster.script
function bind(obj)
    obj:bind_object(generic_object_binder(obj))
end
```

You won't need to modify `class_registrator.script` unless you're creating a completely new entity type.

---

## See also

- [What is a game_object?](game-object.md) — `self.object` explained
- [What is db.storage?](db-storage.md) — the storage table binders populate
- [The Callback System](callbacks.md) — global callbacks vs per-object binder callbacks
- [Save & Load State](save-load.md) — the global save/load system binders integrate with
