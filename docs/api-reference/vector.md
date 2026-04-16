# vector

`vector` is the engine's 3D vector class, used for positions, directions, and velocities throughout the API. Every world position, bone position, and hit direction is a `vector`.

---

## Construction

```lua
-- Default constructor — creates (0, 0, 0)
local v = vector()

-- Set immediately
local pos = vector():set(10, 0, 5)

-- Copy from another vector
local copy = vector():set(other_vec)
```

Properties `x`, `y`, `z` are directly readable and writable:

```lua
local pos = db.actor:position()
printf("x=%.2f y=%.2f z=%.2f", pos.x, pos.y, pos.z)

-- Modify in place
pos.y = pos.y + 2.0
```

---

## Setting values

| Method | Description |
|--------|-------------|
| `v:set(x, y, z)` | Set all three components |
| `v:set(other)` | Copy from another vector |

---

## Arithmetic

All arithmetic methods modify the vector in place **and** return `self`, enabling chaining.

| Method | Description |
|--------|-------------|
| `v:add(n)` | Add scalar to all components |
| `v:add(other)` | Add component-wise |
| `v:add(a, b)` | Store `a + b` into `v` |
| `v:sub(n)` | Subtract scalar |
| `v:sub(other)` | Subtract component-wise |
| `v:sub(a, b)` | Store `a - b` into `v` |
| `v:mul(n)` | Multiply by scalar |
| `v:mul(other)` | Multiply component-wise |
| `v:mul(a, b)` | Store `a * b` into `v` |
| `v:div(n)` | Divide by scalar |
| `v:div(other)` | Divide component-wise |
| `v:div(a, b)` | Store `a / b` into `v` |
| `v:invert()` | Negate all components |
| `v:invert(other)` | Store `-other` into `v` |
| `v:abs(other)` | Store `abs(other)` into `v` |
| `v:mad(a, n)` | `v = v + a * n` |
| `v:mad(a, b, n)` | `v = a + b * n` |
| `v:mad(a, b)` | `v = a + b` (component-wise) |
| `v:mad(a, b, c)` | `v = a + b * c` (component-wise) |
| `v:average(other)` | `v = (v + other) / 2` |
| `v:average(a, b)` | `v = (a + b) / 2` |
| `v:lerp(a, b, t)` | Linear interpolate: `v = a + (b-a)*t` |
| `v:min(other)` | Component-wise minimum |
| `v:min(a, b)` | Store `min(a, b)` into `v` |
| `v:max(other)` | Component-wise maximum |
| `v:max(a, b)` | Store `max(a, b)` into `v` |
| `v:clamp(limit)` | Clamp components to `[-limit, limit]` |
| `v:inertion(other, t)` | Smooth approach to `other` by factor `t` |

---

## Length & normalisation

| Method | Description |
|--------|-------------|
| `v:magnitude()` | Euclidean length |
| `v:set_length(n)` | Scale to length `n` |
| `v:normalize()` | Normalise to unit length (modifies in place) |
| `v:normalize(other)` | Store normalised `other` into `v` |
| `v:normalize_safe()` | Normalise, or become `(0,0,0)` if zero-length |
| `v:normalize_safe(other)` | Safe-normalise `other` into `v` |

---

## Distance

| Method | Description |
|--------|-------------|
| `v:distance_to(other)` | 3D Euclidean distance |
| `v:distance_to_sqr(other)` | Squared distance (faster, no sqrt) |
| `v:distance_to_xz(other)` | 2D distance ignoring Y |
| `v:similar(other, epsilon)` | True if all components within `epsilon` |

```lua
local dist = db.actor:position():distance_to(npc:position())
if dist < 10 then
    printf("[my_mod] NPC is close")
end
```

---

## Dot & cross product

| Method | Description |
|--------|-------------|
| `v:dotproduct(other)` | Scalar dot product |
| `v:crossproduct(a, b)` | Store `a × b` into `v` |

```lua
-- Check if npc is roughly in front of actor (dot product with forward dir)
local actor_dir = db.actor:direction()
local to_npc = vector():sub(npc:position(), db.actor:position()):normalize_safe()
local fwd = vector():setHP(actor_dir, 0)  -- heading, 0 pitch
local dot = fwd:dotproduct(to_npc)        -- 1.0 = directly ahead, -1.0 = behind
```

---

## Direction helpers

| Method | Description |
|--------|-------------|
| `v:setHP(heading, pitch)` | Set from heading+pitch angles (radians) |
| `v:getH()` | Heading angle (radians) |
| `v:getP()` | Pitch angle (radians) |
| `v:align()` | Snap to nearest axis-aligned direction |
| `v:reflect(normal, incident)` | Reflection of `incident` around `normal` |
| `v:slide(n, normal)` | Slide along `normal` surface |

---

## Practical patterns

### Direction from A to B (normalised)

```lua
local function dir_to(from, to)
    return vector():sub(to, from):normalize_safe()
end

local dir = dir_to(db.actor:position(), npc:position())
```

### Offset a position upward

```lua
local above = vector():set(npc:position()):add(vector():set(0, 2, 0))
```

### Midpoint between two positions

```lua
local mid = vector():average(pos_a, pos_b)
```

### Spawn item near actor

```lua
local spawn_pos = vector():mad(db.actor:position(), vector():set(1, 0, 0), 2.0)
-- spawn_pos = actor_pos + forward * 2
```

---

## See also

- [game_object](game-object.md) — position, bone_position, etc. all return vectors
- [hit](hit.md) — `direction` property is a vector
- [level](level.md) — `vertex_position`, `vertex_id`, `spawn_phantom` take vectors
