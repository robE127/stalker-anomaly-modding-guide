# CTime

`CTime` is the engine's in-game time class. The most common way to get one is `game.get_game_time()`, which returns a `CTime` representing the current in-game date and time.

---

## Getting a CTime

```lua
-- Current in-game time
local t = game.get_game_time()

-- Copy of another CTime
local t2 = CTime(t)

-- New empty CTime (zeroed)
local t3 = CTime()
```

---

## Reading date and time

### Extracting components with `t:get()`

```lua
local t = game.get_game_time()
local Y, Mo, D, H, Mi, S, Ms = t:get(0, 0, 0, 0, 0, 0, 0)
-- Y=2012, Mo=4, D=14, H=21, Mi=33, S=7, Ms=0 (for example)
```

The C++ binding uses output-by-reference parameters, but in Lua `get` works by **return value** — capture the seven return values as shown above. The arguments themselves are ignored; passing zeros is the idiomatic pattern (used throughout the base game in `utils_data.CTime_to_table`).

### Setting components

```lua
-- Set full date + time
t:set(year, month, day, hours, minutes, seconds, milliseconds)

-- Set only H:M:S:ms
t:setHMS(hours, minutes, seconds)
t:setHMSms(hours, minutes, seconds, milliseconds)
```

---

## Formatting

| Method | Returns | Description |
|--------|---------|-------------|
| `t:timeToString(format)` | `string` | Time as formatted string |
| `t:dateToString(format)` | `string` | Date as formatted string |

Format constants:

| Constant | Value | Output example |
|----------|-------|----------------|
| `CTime.TimeToHours` | 0 | `"14"` |
| `CTime.TimeToMinutes` | 1 | `"14:35"` |
| `CTime.TimeToSeconds` | 2 | `"14:35:22"` |
| `CTime.TimeToMilisecs` | 3 | `"14:35:22.500"` |
| `CTime.DateToDay` | 0 | `"12"` |
| `CTime.DateToMonth` | 1 | `"April 12"` |
| `CTime.DateToYear` | 2 | `"April 12, 2012"` |

```lua
local t = game.get_game_time()
printf("Time: %s", t:timeToString(CTime.TimeToMinutes))   -- "14:35"
printf("Date: %s", t:dateToString(CTime.DateToYear))      -- "April 12, 2012"
```

---

## Arithmetic

`CTime` supports standard comparison operators (`==`, `<`, `<=`, `>`, `>=`) and addition/subtraction.

| Method | Description |
|--------|-------------|
| `t:add(other)` | Add another `CTime` to this one in place |
| `t:sub(other)` | Subtract another `CTime` in place |
| `t:diffSec(other)` | Absolute difference in **seconds** between two CTimes |

```lua
local now = game.get_game_time()
local last = ...  -- stored earlier

local elapsed_sec = now:diffSec(last)
if elapsed_sec > 3600 then
    printf("[my_mod] More than one game hour has passed")
end
```

---

## Common patterns

### Get current hour as a number

```lua
local t = game.get_game_time()
local _, _, _, hours, minutes = t:get(0, 0, 0, 0, 0, 0, 0)
-- hours: 0-23
```

### Check if daytime (6:00–21:00)

```lua
local function is_daytime()
    local t = game.get_game_time()
    local _, _, _, h = t:get(0, 0, 0, 0, 0, 0, 0)
    return h >= 6 and h < 21
end
```

### Format a combined date and time string

`timeToString` and `dateToString` each cover part of the picture. When you need a single string with both date and time (for a log line, a PDA marker label, etc.), use `get` and `string.format`:

```lua
local t = game.get_game_time()
local Y, Mo, D, H, Mi = t:get(0, 0, 0, 0, 0, 0, 0)
local label = string.format("Death: %02d.%02d.%04d %02d:%02d", D, Mo, Y, H, Mi)
-- e.g. "Death: 14.04.2012 21:33"
```

---

### Store a timestamp and check elapsed time later

```lua
local my_mod = {}

function my_mod.on_game_start()
    RegisterScriptCallback("actor_on_update", my_mod.on_update)
end

local start_time = nil

function my_mod.on_update()
    if not start_time then
        start_time = game.get_game_time()
    end

    local now = game.get_game_time()
    if now:diffSec(start_time) > 600 then  -- 10 minutes game time
        printf("[my_mod] 10 minutes have passed")
        start_time = now
    end
end
```

---

## See also

- [game](game.md) — `game.get_game_time()`, `game.time()` (real-ms timer)
- [level](level.md) — `level.get_time_hours()`, `level.get_time_minutes()`, `level.change_game_time()`
