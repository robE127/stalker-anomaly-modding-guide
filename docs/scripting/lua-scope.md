# Lua Scope & Globals

Understanding scope in Lua is critical in Anomaly modding because **all scripts share a single global namespace**. A variable you accidentally declare as global in your mod is visible — and writable — by every other script in the game. This page explains how scoping works, what variables are visible from inside a function, and how to share state safely.

---

## Local vs global

In Lua, every variable is **global by default** unless you declare it with `local`.

```lua
-- Global: visible to every script in the game
enemy_count = 0

-- Local: visible only within this block
local enemy_count = 0
```

In Anomaly, all `.script` files are loaded into the same Lua state. Every global you create becomes part of the shared `_G` table. If two mods both declare a global called `enemy_count`, the second one to load silently overwrites the first.

**Always use `local` for everything in your mod.** The only exceptions are the specific entry-point functions the engine looks for by name: `on_game_start`, `on_game_end`, `on_game_load`, and `bind` (for object binders).

```lua
-- WRONG: pollutes the global namespace
function my_helper() end
data_table = {}

-- CORRECT
local function my_helper() end
local data_table = {}

-- These must be global so the engine can find them
function on_game_start() end
function on_game_end() end
```

---

## Module scope

A `.script` file in Anomaly is a Lua *module* — a chunk of code that executes once when the file is loaded. Variables declared with `local` at the top level of a file (outside any function) have **module scope**: they live for the entire session and are visible to every function defined in that same file.

```lua
-- my_mod.script

-- Module-level locals — created when the file loads, live until the game exits
local is_initialized = false
local tracked_ids = {}
local config = {
    range  = 50,
    damage = 0.5,
}

-- These functions can all read and write the module-level locals above
local function reset()
    is_initialized = false
    tracked_ids = {}
end

local function track(id)
    tracked_ids[id] = true
end

local function actor_on_first_update()
    if is_initialized then return end
    is_initialized = true
    -- config is readable here
    printf("[my_mod] range = %s", config.range)
end
```

Module-level locals are the correct place to keep your mod's persistent runtime state — counters, flags, caches, and configuration tables.

---

## Upvalues: what a function can see

When a function is defined, Lua records every `local` variable that is in scope at that point. These captured variables are called **upvalues**. The function can read and write them just like its own local variables.

```lua
local count = 0          -- upvalue for the functions below

local function increment()
    count = count + 1    -- writes the upvalue
end

local function get_count()
    return count         -- reads the upvalue
end

increment()
increment()
printf("%d", get_count())  -- prints 2
```

A function can access variables from any enclosing scope at the time it was **defined** — not just the immediate enclosing block:

```lua
local base_damage = 10.0

local function make_multiplier(factor)
    -- 'factor' is a parameter (local to make_multiplier)
    -- 'base_damage' is a module-level upvalue
    return function(target)
        -- This inner function captures both 'factor' AND 'base_damage'
        return base_damage * factor
    end
end

local double_damage = make_multiplier(2.0)
local triple_damage = make_multiplier(3.0)

printf("%f", double_damage())  -- 20.0
printf("%f", triple_damage())  -- 30.0
```

Each call to `make_multiplier` creates a new closure with its own copy of `factor`, but all closures share the same `base_damage` upvalue. If you write to `base_damage`, every closure sees the new value.

### Upvalue resolution order

Inside a function, Lua resolves a name by looking through scopes from innermost to outermost:

1. **Local variables declared inside the function** (most specific)
2. **Upvalues** — locals from all enclosing function scopes
3. **Module-level locals** — locals at the top of the file
4. **Globals** (`_G`) — the shared table for the entire Lua state (least specific)

```lua
local x = "module"   -- module-level local

local function outer()
    local x = "outer"   -- shadows the module-level x

    local function inner()
        local x = "inner"   -- shadows outer's x
        printf(x)           -- prints "inner"
    end

    inner()
    printf(x)   -- prints "outer"
end

outer()
printf(x)   -- prints "module"
```

If a variable isn't found at any local level, Lua falls back to `_G`. This is why forgetting `local` creates a global — the assignment silently writes into `_G`.

---

## Closures for encapsulation

Closures let you create private state that can't be accessed from outside the module:

```lua
-- Counter with private state — nothing outside this file can touch 'n'
local n = 0

function my_mod.increment() n = n + 1 end
function my_mod.get()       return n  end
```

The base game uses this pattern extensively. For example, `xr_sound.script` keeps its sound cache in a module-level local:

```lua
local sound_object_by_path = {}

function get_safe_sound_object(path)
    if sound_object_by_path[path] == nil then
        sound_object_by_path[path] = sound_object(path)
    end
    return sound_object_by_path[path]
end
```

`sound_object_by_path` is invisible outside `xr_sound.script` but shared across every call to `get_safe_sound_object`.

---

## `this` — referring to your own script

Inside any script, `this` is a special reference to the script's own module table. You use it to call your own exported functions when you need an explicit module reference:

```lua
-- xr_sound.script (from base game)
function set_actor_sound(sound)
    actor_sound.theme = sound
    this.set_actor_sound_factor(1)   -- call another function in this same script
end
```

You won't need `this` often — calling functions by name directly (`my_function()`) works fine within the same file. `this` becomes useful when passing a reference to the current module as an argument.

---

## Accessing other scripts

Every script file is loaded as a global table named after the file (without the `.script` extension). To call a function from another script:

```lua
-- Call a function from utils_item.script
local weapon_name = utils_item.get_weapon_name(weapon_obj)

-- Call a function from game_relations.script
local relation = game_relations.get_npcs_relation(npc1, npc2)
```

The base game's `_g.script` is special — it runs before all other scripts and its functions are placed directly into `_G`, so you call them without a prefix:

```lua
-- These are defined in _g.script and available everywhere without a prefix
RegisterScriptCallback("on_game_load", handler)
IsWeapon(obj)
alife_create("medkit", pos)
```

---

## Sharing state between scripts

If two of your own scripts need to share state, the cleanest approach is a dedicated state module:

```lua
-- my_mod_state.script
-- No local — this table is intentionally global so other scripts can access it
my_mod = my_mod or {}
my_mod.player_kills = 0
my_mod.active = false
```

```lua
-- my_mod_combat.script
local function npc_on_death_callback(victim, who)
    if who:id() == db.actor:id() then
        my_mod.player_kills = my_mod.player_kills + 1
    end
end
```

```lua
-- my_mod_ui.script
local function actor_on_update()
    if my_mod.active then
        -- show kill count using my_mod.player_kills
    end
end
```

The `my_mod = my_mod or {}` pattern is important — if the scripts load in an order where `my_mod_state.script` hasn't run yet, the `or {}` ensures the table exists before the first write.

!!! warning "One shared table, one namespace"
    Use a single table named after your mod (`my_mod`) for all cross-script state. This limits global pollution to a single name. Spreading state across multiple bare globals (`my_mod_kills`, `my_mod_active`, `my_mod_config`) clutters `_G` and increases the chance of collision with other mods.

---

## Common mistakes

### Forgetting `local` on a loop variable

```lua
-- WRONG: 'i' becomes a global
for i = 1, 10 do
    printf(i)
end

-- Correct: Lua 'for' loop variables are always local — this is fine
for i = 1, 10 do   -- 'i' is local to the loop
    printf(i)
end

-- WRONG: 'v' becomes a global inside a manual while loop
v = 1
while v <= 10 do
    v = v + 1
end
```

### Forgetting `local` on a helper function

```lua
-- WRONG: my_helper is now a global visible to all scripts
function my_helper(x)
    return x * 2
end

-- Correct
local function my_helper(x)
    return x * 2
end
```

### Mutating a shared upvalue from a callback

Module-level locals persist across callbacks. This is useful for state, but can cause bugs if a callback modifies something you assumed was reset each call:

```lua
local results = {}   -- shared across all calls!

local function actor_on_update()
    -- WRONG: results accumulates across every frame
    results[#results + 1] = get_something()
end

-- Correct: declare inside the function, or clear it at the start
local function actor_on_update()
    local results = {}   -- fresh each call
    results[#results + 1] = get_something()
end
```

---

## See also

- [Script Lifecycle](script-lifecycle.md) — when module-level code runs vs `on_game_start`
- [The Callback System](callbacks.md) — why anonymous callbacks can't be unregistered (closure mechanics)
- [Debugging & Logging](debugging.md) — how to diagnose global namespace collisions
