# sound_object

`sound_object` is the engine class for scripted sound playback — playing sounds at world positions, attaching them to objects, and controlling looping sounds.

---

## Construction

```lua
-- Load a sound file (no extension, relative to sounds/)
local snd = sound_object("anomaly\\electra_idle")

-- Load with explicit sound type
local snd2 = sound_object("interface\\inv_slot_pick_up", sound_object.s2d)
```

Sound paths are relative to `gamedata/sounds/` and have **no file extension** (the engine appends `.ogg` or finds the right format automatically).

---

## Constants

| Constant | Description |
|----------|-------------|
| `sound_object.s3d` | 3D positional sound (default) |
| `sound_object.s2d` | 2D non-positional (UI sounds, music) |
| `sound_object.looped` | Loop flag — combine with `play` delay parameter |

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `snd.volume` | `number` | Playback volume (0–1) |
| `snd.frequency` | `number` | Pitch multiplier (1.0 = normal) |
| `snd.min_distance` | `number` | Distance at which sound is at full volume |
| `snd.max_distance` | `number` | Distance beyond which sound is inaudible |

---

## Playback methods

| Method | Description |
|--------|-------------|
| `snd:play(obj)` | Play at `obj`'s current position (follows the object) |
| `snd:play(obj, delay)` | Play after `delay` seconds |
| `snd:play(obj, delay, flags)` | Play with flags (e.g. `sound_object.looped`) |
| `snd:play_at_pos(obj, pos)` | Play at world position `pos` |
| `snd:play_at_pos(obj, pos, delay)` | Play at position with delay |
| `snd:play_at_pos(obj, pos, delay, flags)` | Play at position with flags |
| `snd:play_no_feedback(obj, flags, delay, pos, freq, vol)` | Play without feedback to game systems |
| `snd:stop()` | Stop immediately |
| `snd:stop_deffered()` | Stop after current loop completes |
| `snd:playing()` | `true` if currently playing |
| `snd:length()` | Duration in seconds |
| `snd:get_position()` | Current world position |
| `snd:set_position(pos)` | Move to new world position |
| `snd:attach_tail(path)` | Append another sound file to play after this one |

---

## Examples

### One-shot sound at actor

```lua
local snd = sound_object("interface\\inv_slot_pick_up")
snd:play(db.actor)
```

### Looping positional sound at world position

```lua
local my_snd = sound_object("ambient\\campfire")
my_snd.volume = 0.5
my_snd.min_distance = 1.0
my_snd.max_distance = 20.0
my_snd:play_at_pos(db.actor, some_vector, 0, sound_object.looped)

-- Stop it later
my_snd:stop()
```

### Sound attached to an NPC

```lua
-- Attaches to the NPC and moves with them
local npc_snd = sound_object("monsters\\bloodsucker\\idle_1")
npc_snd:play(npc_obj, 0, sound_object.looped)
```

### 2D UI sound

```lua
local ui_snd = sound_object("interface\\inv_slot_pick_up", sound_object.s2d)
ui_snd:play(db.actor)
```

---

## Notes

- The `obj` argument to `play` / `play_at_pos` is used for game feedback (combat detection, AI hearing). For non-diegetic sounds (UI, music) pass `db.actor` and use `sound_object.s2d`.
- `sound_object` instances are garbage-collected by Lua but the engine may continue playing the sound until `stop()` is called. Hold a reference while the sound is in use.
- Use `game_object:add_sound` / `game_object:play_sound` for NPC AI-managed sounds. `sound_object` is for fully script-driven sounds.

---

## See also

- [game_object](game-object.md) — `add_sound`, `play_sound`, `external_sound_start`
- [snd_type constants](index.md#snd_type) — sound category bitmask constants
