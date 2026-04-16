# ini_file

`ini_file` is the Lua class for reading LTX config files at runtime. It is also the type of object returned by `game_ini()`, `system_ini()`, `obj:spawn_ini()`, and `create_ini_file()`.

LTX config reading is ubiquitous in mod code — anytime you want to look up a config value, check a section, or iterate a section's contents at runtime, you use an `ini_file`.

---

## Getting an ini_file object

| Source | How |
|--------|-----|
| Game configs (`configs/system.ltx` and all `#include`d files) | `system_ini()` |
| Game configs including AI-specific files | `game_ini()` |
| Any single file by VFS path | `create_ini_file("configs\\path\\to\\file.ltx")` |
| Spawn data embedded in an entity | `obj:spawn_ini()` |

```lua
-- Read from the global config tree
local ini = system_ini()
local value = ini:r_float("my_section", "my_key")

-- Read from a specific file
local custom_ini = create_ini_file("configs\\my_mod\\settings.ltx")

-- Read from a spawned entity's config
local spawn_ini = obj:spawn_ini()
if spawn_ini and spawn_ini:section_exist("story_object") then
    local sid = spawn_ini:r_string("story_object", "story_id")
end
```

---

## Checking structure

Before reading a value, it's good practice to verify the section and key exist — missing keys throw errors.

| Method | Description |
|--------|-------------|
| `ini:section_exist(section)` | `true` if the section `[section]` exists |
| `ini:line_exist(section, key)` | `true` if the key exists in the section |
| `ini:line_count(section)` | Number of key-value lines in the section |

```lua
local ini = system_ini()
if ini:section_exist("mutant_bloodsucker") then
    if ini:line_exist("mutant_bloodsucker", "health") then
        local hp = ini:r_float("mutant_bloodsucker", "health")
    end
end
```

---

## Reading values

| Method | Returns | Description |
|--------|---------|-------------|
| `ini:r_string(section, key)` | `string` | String value |
| `ini:r_string_wq(section, key)` | `string` | String value, preserving quotes |
| `ini:r_float(section, key)` | `number` | Float value |
| `ini:r_s32(section, key)` | `number` | Signed 32-bit integer |
| `ini:r_u32(section, key)` | `number` | Unsigned 32-bit integer |
| `ini:r_bool(section, key)` | `boolean` | Boolean value (`true`/`false` in ltx) |
| `ini:r_vector(section, key)` | `vector` | Three-float vector (`x, y, z` in ltx) |
| `ini:r_clsid(section, key)` | `number` | Class ID value |
| `ini:r_token(section, key, token_list)` | `number` | Token lookup against a token_list |

!!! warning "Always check before reading"
    Calling `r_string` on a key that doesn't exist throws a Lua error. Always use `line_exist` first unless you're certain the config is well-formed.

```lua
local ini = system_ini()
local section = "my_mod_settings"

local name   = ini:line_exist(section, "name")   and ini:r_string(section, "name")  or "default"
local count  = ini:line_exist(section, "count")  and ini:r_s32(section, "count")    or 0
local factor = ini:line_exist(section, "factor") and ini:r_float(section, "factor") or 1.0
local active = ini:line_exist(section, "active") and ini:r_bool(section, "active")  or false
```

---

## Iterating sections

`r_line` reads a line by index and writes the key and value into two variables. This is the only way to iterate all keys in a section without knowing their names in advance.

```lua
-- Signature: ini:r_line(section, index, key_out, value_out)
-- Returns nothing — key and value are passed by reference in C++, but in Lua
-- the returned key and value are the 1st and 2nd return values.

local ini = system_ini()
local section = "my_mod_items"
local n = ini:line_count(section)

for i = 0, n - 1 do
    local result, key, value = ini:r_line(section, i, "", "")
    printf("[my_mod] key=%s value=%s", tostring(key), tostring(value))
end
```

!!! note "r_line is 0-indexed"
    Indices run from `0` to `line_count(section) - 1`.

---

## Common patterns

### Read all items listed in a config section

A common LTX pattern is to list items one-per-line under a section:

```ltx
[my_mod_spawn_list]
item_1 = bandage
item_2 = medkit_army
item_3 = vodka
```

```lua
local ini = system_ini()
local section = "my_mod_spawn_list"
local items = {}

if ini:section_exist(section) then
    for i = 0, ini:line_count(section) - 1 do
        local _, key, value = ini:r_line(section, i, "", "")
        items[#items + 1] = value
    end
end
```

### Read a section that inherits from a base

LTX uses `[child] : parent` inheritance. `system_ini()` already flattens inheritance for you — when you read `r_string("child_section", "inherited_key")`, it walks the inheritance chain automatically.

### Check item config

```lua
local function get_item_weight(section)
    local ini = system_ini()
    if not ini:section_exist(section) then return 0 end
    if not ini:line_exist(section, "inv_weight") then return 0 end
    return ini:r_float(section, "inv_weight")
end

local weight = get_item_weight("bandage")
```

### Read spawn-time data

Objects in `.spawn` files or spawned via scripts can carry embedded LTX data accessible via `spawn_ini()`:

```lua
-- In a binder's reinit or net_spawn:
function MyBinder:net_spawn(data)
    local si = self.object:spawn_ini()
    if si and si:section_exist("logic") then
        self.custom_flag = si:r_bool("logic", "my_flag")
    end
    return true
end
```

---

## See also

- [Config Formats: LTX](../config-formats/ltx.md) — LTX syntax, sections, inheritance
- [Config Formats: DLTX](../config-formats/dltx.md) — modular config overrides
- [alife](alife.md) — server entity has its own `spawn_ini()`
