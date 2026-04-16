# hit

The `hit` class represents a damage event applied to a game object. Create one, set its properties, then call `obj:hit(h)` to deal damage.

---

## Construction

```lua
local h = hit()          -- new hit, all zeroes
local h2 = hit(other_h)  -- copy constructor
```

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `h.type` | `number` | Hit type constant (see below) |
| `h.power` | `number` | Damage magnitude (0–1+, relative to max health) |
| `h.direction` | `vector` | Direction the hit comes from (normalised) |
| `h.draftsman` | `game_object` | Who is credited with the hit (affects death credit, callbacks) |
| `h.impulse` | `number` | Physics impulse applied to the ragdoll |

---

## Hit type constants

| Constant | Meaning |
|----------|---------|
| `hit.burn` | Fire / heat damage |
| `hit.shock` | Electrical shock |
| `hit.chemical_burn` | Chemical burn |
| `hit.radiation` | Radiation damage |
| `hit.telepatic` | Psy damage |
| `hit.wound` | Gunshot / bullet wound |
| `hit.strike` | Blunt strike / melee |
| `hit.explosion` | Explosion damage |
| `hit.fire_wound` | Fire wound (burning wound) |
| `hit.light_burn` | Light burn / singeing |
| `hit.dummy` | No actual damage type (for physics-only hits) |

---

## Applying a hit

```lua
obj:hit(h)
```

The `draftsman` determines who is credited. If you want an NPC to appear to take self-damage (e.g. from a trap), set `draftsman` to the NPC itself. If you want the actor to receive kill credit, set it to `db.actor`.

---

## Targeting a specific bone

By default the hit is applied to the whole object. To specify a bone:

```lua
h:bone("bip01_head")
```

---

## Examples

### Damage the actor

```lua
local function zap_actor(amount)
    local h = hit()
    h.type      = hit.shock
    h.power     = amount
    h.direction = vector():set(0, -1, 0)
    h.draftsman = db.actor
    h.impulse   = 0
    db.actor:hit(h)
end
```

### Kill an NPC via script

```lua
local function script_kill(npc)
    local h = hit()
    h.type      = hit.wound
    h.power     = 1.0
    h.direction = vector():set(0, -1, 0)
    h.draftsman = db.actor
    h.impulse   = 0
    npc:hit(h)
end
```

### Apply psy damage

```lua
local function psy_blast(amount)
    local h = hit()
    h.type      = hit.telepatic
    h.power     = amount
    h.direction = vector():set(0, -1, 0)
    h.draftsman = db.actor
    h.impulse   = 0
    db.actor:hit(h)
end
```

---

## Notes

- `power` is relative to the target's max health — `1.0` removes all health.  
  Armour and resistances modify the effective damage further.
- Setting `impulse` to a non-zero value will knock a ragdoll physically. Keep it at `0` if you want clean kills without a physics fling.
- `draftsman` must be a valid live `game_object`. Passing `nil` can crash.

---

## See also

- [game_object](game-object.md) — `obj:hit(h)` call
- [Callbacks Reference](../callbacks-reference/index.md) — `entity_on_hit` callback receives a hit's properties
