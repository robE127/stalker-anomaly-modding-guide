# Engine Internals

This page documents engine-level behaviour that affects how you write mods — object lifetimes, the online/offline system, save serialization, and engine limits.

!!! abstract "Advanced — skip on first read"
    This page covers implementation details of the X-Ray engine. You don't need to understand any of this to write most mods — come back here when you hit a specific problem (stale object references, save/load bugs, or unexplained spawn behaviour).

!!! info "Source: modded exes only"
    The information on this page is derived from the [xray-monolith](https://github.com/themrdemonized/xray-monolith) C++ source — the community **modded exes** maintained by themrdemonized. The vanilla Anomaly engine is closed-source and cannot be inspected. While the core architecture (online/offline switching, alife simulation, save format) originates from the original X-Ray engine and is likely similar in vanilla, specific implementation details — line counts, exact thresholds, Lua bridge callbacks, and modded-exes-specific features like the marshal `.scoc` save system — may differ. If you are targeting vanilla Anomaly without the modded exes, treat the details here as best-available approximations rather than guarantees.

---

## The two representations of every entity

Every entity in the game exists in two forms:

| | Server entity | Client object |
|--|--|--|
| C++ class | `CSE_ALifeDynamicObject` | `CGameObject` |
| Lua wrapper | `cse_alife_object` (from `alife_object(id)`) | `game_object` (from `level.object_by_id(id)`) |
| Always exists? | Yes, while registered with alife | Only while **online** |
| Contains | Position, section, spawn data, parent ID | Rendered model, physics, AI state |
| Used for | Offline simulation, spawning, save/load | Interaction, combat, callbacks |

The **server entity** is the permanent record. It exists from the moment the entity is created (at level load or via `alife():create()`) until it is released. The **client object** (`game_object`) is the in-world representation — it only exists while the entity is within render/simulation distance of the player.

When you call `alife_object(id)`, you get the server entity regardless of whether the object is online or offline. When you call `level.object_by_id(id)`, you get the client object — or `nil` if the entity is offline.

---

## Online and offline

The alife simulator manages a continuous cycle of bringing entities online (spawning their client objects) and taking them offline (destroying the client objects). This is how the engine handles a world with thousands of entities without rendering them all.

### Switch distance

The switch distance is configured in `alife.ltx`:

```ini
switch_distance = 750     ; meters
switch_factor   = 0.1     ; hysteresis factor
```

From these values, the engine computes two radii with a hysteresis gap to prevent objects from rapidly flickering on and off at the boundary:

| Radius | Formula | Default |
|--------|---------|---------|
| Online radius | `switch_distance * (1.0 - switch_factor)` | 675m |
| Offline radius | `switch_distance * (1.0 + switch_factor)` | 825m |

An offline entity switches online when the actor comes within the **online radius** (675m). An online entity switches offline when the actor moves beyond the **offline radius** (825m). The 150m gap means an entity at exactly 750m doesn't constantly switch states as the actor moves slightly back and forth.

### The switch process

**Going online** (`switch_online`):

1. The alife simulator detects the entity is within online radius
2. `CSE_ALifeDynamicObject::switch_online()` creates a `CGameObject` on the client
3. The object binder's `net_spawn()` fires
4. If the entity has saved `client_data` (from a previous save), it's fed back through `net_Load()` to restore the script binder state

**Going offline** (`switch_offline`):

1. The alife simulator detects the entity is beyond offline radius
2. The object binder's `net_destroy()` fires
3. The `CGameObject` is destroyed via a `GE_DESTROY` event
4. `client_data` is cleared (for most entity types — see [client_data lifecycle](#client_data-lifecycle) below)
5. Only the server entity remains

### Flags that control switching

Each server entity has flags that control whether it can go online or offline:

```lua
local se_obj = alife_object(id)

-- These are rarely modified directly, but useful for understanding behaviour
se_obj:can_switch_online()     -- can this entity go online?
se_obj:can_switch_offline()    -- can this entity go offline?
```

Entities with `can_switch_offline() == false` (like the actor) are always online once spawned. Entities with `can_switch_online() == false` remain permanently offline.

Items attached to a parent (e.g., items in an NPC's inventory, `ID_Parent ~= 65535`) are never independently switched — they follow their parent's online/offline state.

### Stale game_object references

When an entity goes offline, its `CGameObject` is destroyed. Any `game_object` reference you stored in a Lua variable becomes **stale**. Calling methods on a stale reference causes undefined behaviour or crashes.

```lua
-- WRONG: storing a game_object reference across frames
local my_npc = nil

local function npc_on_death_callback(victim, who)
    my_npc = victim  -- dangerous — victim may go offline later
end

local function actor_on_update()
    if my_npc then
        -- This may crash if my_npc went offline
        local pos = my_npc:position()
    end
end
```

**Safe pattern:** Store the object's **ID** instead, and look it up fresh each time:

```lua
local my_npc_id = nil

local function npc_on_death_callback(victim, who)
    my_npc_id = victim:id()  -- safe — IDs are stable
end

local function actor_on_update()
    if not my_npc_id then return end
    local npc = level.object_by_id(my_npc_id)
    if npc then
        -- npc is online and valid
        local pos = npc:position()
    end
end
```

The server entity (`alife_object(id)`) is always safe to access as long as the entity hasn't been released, but it provides a much smaller API than `game_object`.

---

## The alife simulator

`alife()` returns a `CALifeSimulator` — the singleton that manages all server entities. It inherits from several subsystems:

- **Switch manager** — handles online/offline transitions (described above)
- **Storage manager** — handles save/load to disk
- **Update manager** — ticks the offline AI simulation
- **Surge manager** — handles emission events

### Offline simulation

The alife simulator processes offline entities each frame. The processing budget is controlled by two parameters:

| Parameter | Default | Lua setter |
|-----------|---------|------------|
| Objects per update | 20 | `alife():set_objects_per_update(n)` |
| Process time | 900 microseconds | `alife():set_process_time(n)` |

Each tick, up to 20 offline entities have their `update()` called, which runs their offline AI (movement between smart terrains, combat resolution, etc.). Processing stops early if the time budget is exceeded.

The alife update runs on a **separate thread** when multithreaded alife is enabled (`mtALife` console variable), so be aware that alife state can change between frames.

### Spawning entities

`alife():create()` has different code paths depending on whether the parent is online:

- **Parent online** (e.g., giving an item to the player): Creates a temporary server entity, serializes it to a network packet, destroys the temp entity, then processes the packet through the full spawn pipeline. This ensures the client immediately sees the new object.
- **Parent offline** (e.g., adding loot to an offline NPC): Creates the server entity directly in the alife registry. No client object is created — it will appear when the parent comes online.
- **No parent** (world spawn): Creates the server entity at the given position. It will come online when the actor gets within switch distance.

This is why `alife_create_item("bandage", db.actor)` works immediately — the actor is always online, so the item appears in inventory right away.

---

## Save serialization

Anomaly has **two separate save systems** that work together.

### Engine save system (NET_Packet / client_data)

The engine's native save system uses binary network packets:

1. **On save:** The engine iterates all online `CGameObject`s, calls `net_Save()` on each, which writes native state plus the script binder's `save(packet)` data into a `NET_Packet`. This data is sent to the server and stored on the server entity as `client_data` (a raw byte vector).
2. **On disk write:** The alife storage manager serializes all server entities (including their `client_data`) into a compressed binary blob — the `.scop` file (Anomaly's save file format, stored in `appdata/savedgames/`).
3. **On load:** Server entities are deserialized from the `.scop` file. When an entity comes online, its `client_data` is fed back through `net_Load()` into the script binder's `load(packet)` method.

!!! warning "NET_Packet size limit"
    Each packet is limited to **16,384 bytes** (16 KB). This is the maximum amount of data any single object can save through the packet-based system. Exceeding this limit corrupts the save.

#### client_data lifecycle

An important subtlety: `client_data` is **cleared when an object goes offline** for most entity types. The `clear_client_data()` method runs during `switch_offline`, wiping the script binder's saved state. This means:

- Script binder data saved via `save(packet)` / `load(packet)` only survives **save-to-disk and reload** — not online/offline transitions during normal gameplay.
- Anomalous zones override this behaviour (`keep_saved_data_anyway()` returns `true`), so their binder state persists across online/offline switches.
- For most mods, this doesn't matter because the marshal-based `m_data` system (described below) is used instead.

### Marshal save system (m_data / .scoc file)

The Anomaly-specific save system, implemented in `alife_storage_manager.script`, exists specifically to overcome the limitations of the engine's native system:

1. A global Lua table `m_data` is maintained with two sub-tables:
    - `m_data.se_object` — persists even when entities are offline
    - `m_data.game_object` — purged when an entity is unregistered
2. **On save:** The `save_state` script callback fires, allowing all mods to write their data into `m_data`. The table is then serialized using the **marshal** library (Lua binary serialization) and written to a `.scoc` sidecar file alongside the `.scop` save file.
3. **On load:** The `.scoc` file is deserialized back into `m_data`, and the `load_state` script callback fires so mods can read their data back.

The C++ engine calls into Lua (`CALifeStorageManager_before_save` and `CALifeStorageManager_load`) at the right moments — this bridge is enabled by the `ENGINE_LUA_ALIFE_STORAGE_MANAGER_CALLBACKS` compile flag in the modded exes.

This is the system you use in most mods:

```lua
local function save_state(m_data)
    m_data.my_mod = {
        kill_count = my_kill_count,
        active = my_mod_active,
    }
end

local function load_state(m_data)
    local saved = m_data.my_mod or {}
    my_kill_count = saved.kill_count or 0
    my_mod_active = saved.active or false
end
```

See [Save & Load State](save-load.md) for the full pattern.

---

## Object IDs

Object IDs are unsigned 16-bit integers (`u16`), giving a range of `0` to `65534`. The value `65535` (`0xFFFF`) is reserved as the invalid/null ID.

| ID | Meaning |
|----|---------|
| `0` | The actor (always) |
| `1` – `65534` | All other entities |
| `65535` | Invalid / no parent / null |

The ID generator allocates IDs in blocks of 256. When all 65,534 IDs are exhausted, the engine asserts with `"Not enough IDs"`. In practice this limit is rarely hit, but mods that spawn large numbers of entities without releasing them can approach it.

An entity's ID is stable for its entire lifetime — it never changes. However, IDs **are reused** after an entity is released. Don't use an ID as a permanent identifier across save/load boundaries; use `story_id` for persistent references to specific entities.

---

## Engine limits reference

| Limit | Value | Notes |
|-------|-------|-------|
| Max simultaneous entities | 65,534 | Object IDs are `u16`; 65535 is reserved |
| NET_Packet size | 16,384 bytes | Per-object save data limit for packet system |
| Default switch distance | 750m | Online at 675m, offline at 825m (with hysteresis) |
| Offline entities per update | 20 | Configurable via `alife():set_objects_per_update()` |
| Alife process time per frame | 900 &mu;s | Configurable via `alife():set_process_time()` |
| `client_data` size field | `u16` | Max 65,535 bytes, but limited by NET_Packet (16 KB) |
