# level

!!! note "Work in progress"
    This page is being written. Content coming soon.

The `level` global provides access to the currently loaded map and its objects.

## Topics to cover

- `level.object_by_id(id)` — get any game object by its numeric ID
- `level.name()` — current map name (e.g. `"l01_escape"`, `"k00_marsh"`)
- `level.get_time_hours()` / `level.get_time_minutes()` — in-game clock
- Camera effects: `level.add_cam_effector(file, id, looped, cb)`, `level.remove_cam_effector(id)`
- Post-processing effects: `level.add_pp_effector(file, id, looped)`, `level.remove_pp_effector(id)`
- `level.present()` — whether a level is currently loaded
- Weather and environment queries
- `level.map_add_object_spot` / `level.map_remove_object_spot` — minimap markers
- Pathfinding helpers
- `level.iterate_online_objects(fn)` / `level.iterate_nearest` patterns
