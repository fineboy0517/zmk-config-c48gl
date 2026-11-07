# Advanced DYA Studio build (experimental)

The existing working firmware on `main` is unchanged. This branch targets cormoran's experimental ZMK fork and custom RPC modules to support:
- USB/BLE DYA Studio keymap editing
- Runtime macros and combos; key input stream
- BLE profiles, OS detection, default layers per host
- Runtime settings, device info and watchdog

It preserves the C48GL 48-key Charlieplex scanner and JIS layout, and Studio unlock (LOWER + RAISE + left Space). This is a single-board keyboard without a trackball, encoder, or other input sensor. Their features are not enabled and cannot function without adding hardware.

**Status:** Requires CI compilation, feature checks and hardware testing. Do not flash firmware until the build is green. Keep stable main-branch UF2 for recovery. Firmware upgrade might require pairing again; never automatically erase Bluetooth bonds or flash storage.

See https://studio.dya.cormoran.works/developer-guide/ and https://github.com/cormoran/dya-studio.
