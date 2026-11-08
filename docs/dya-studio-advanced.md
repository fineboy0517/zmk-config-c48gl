# Advanced DYA Studio build (experimental)

The existing working firmware on `main` is unchanged. This branch targets cormoran's experimental ZMK fork and custom RPC modules to support:
- USB/BLE DYA Studio keymap editing
- Runtime macros and combos; key input stream
- BLE profiles, OS detection, default layers per host
- Runtime settings, device info and watchdog

It preserves the C48GL 48-key Charlieplex scanner and JIS layout, and Studio unlock (LOWER + RAISE + left Space). This is a single-board keyboard without a trackball, encoder, or other input sensor. Their features are not enabled and cannot function without adding hardware.

## Studio unlock fix

This branch binds `&studio_unlock` directly at ADJUST key 41 (zero-based,
bottom row, sixth key from the left). The previous `#if CONFIG_ZMK_STUDIO`
selected `&none` during devicetree preprocessing even though the final
Kconfig enabled Studio. DYA builds always enable Studio; this keymap is
intended for that configuration. `scripts/verify_config.py` checks the
direct binding and its position before Actions builds the firmware.

For installation, use `c48gl-nice_nano_v2-dya.uf2` from the `firmware` artifact
of a successful Actions run for this branch. The older files committed under
`firmware/` belong to the stable main build and do not include this fix.

After flashing, connect to DYA Studio and hold LOWER + RAISE, then press left
Space. LOWER is the bottom-row key between left Alt and Muhenkan; RAISE is
between Henkan and left arrow. Left Space is immediately left of the other
Space. Release all three keys afterwards.

**Status:** CI must pass compilation and UF2 checks; real hardware validation
is still required for input, Studio USB/BLE RPC, settings and power use. Keep
the stable main-branch UF2 for recovery. Stored Studio keymaps can override
the compiled defaults after a firmware update. If the old no-op binding
persists, restore the keymap defaults through Studio when accessible; do not
automatically erase all flash settings or Bluetooth bonds.

See https://studio.dya.cormoran.works/developer-guide/ and https://github.com/cormoran/dya-studio.
