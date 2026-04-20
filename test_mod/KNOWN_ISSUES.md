# Extraction Mod - Known Issues

This file tracks currently known limitations/bugs in the extraction test mod.

## Save/Load Restrictions

- `load` typed directly in the in-game C++ console is not blocked during an active session.
- `load_last_save` typed directly in the in-game C++ console is not blocked during an active session.
- Direct C++ console loads bypass current Lua interception points; load prevention currently covers quickload input and ESC-menu load flow, but not raw console load commands.

## Safe-Zone Coverage

- Limansk (`l10_limansk`) zone coordinates are still unconfirmed.
- Late-game levels are not yet included in safe-zone config:
  - Pripyat
  - Red Forest
  - Dead City
