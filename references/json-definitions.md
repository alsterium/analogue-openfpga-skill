# APF JSON definitions

Official source: [Core Definition Files](https://www.analogue.co/developer/docs/core-definition-files). Every definition uses the documented `APF_VER_1` magic value. Keep the outer object (`core`, `data`, `input`, `instance`, `interact`, `variants`, `video`, or `audio`) consistent with the file being authored.

## `core.json`

Source: [core.json](https://www.analogue.co/developer/docs/core-definition-files/core-json).

- `metadata.platform_ids`: supported platform shortnames; at most 4. An empty array makes the core standalone and changes asset/save placement.
- `metadata.shortname`: filesystem-facing short name, maximum 31 characters in the schema page.
- `metadata.description`: maximum 63 characters.
- `metadata.author`: maximum 31 characters.
- `metadata.url`: maximum 63 characters.
- `metadata.version`: maximum 31 characters; SemVer is encouraged.
- `metadata.date_release`: `YYYY-MM-DD`, maximum 10 characters. The Getting Started prose calls this `date_released` in one place; follow the current schema/template key `date_release` and verify a firmware-specific release against the live page.
- `framework.target_product`: must be `Analogue Pocket`.
- `framework.version_required`: minimum firmware version, for example `1.1`.
- `framework.sleep_supported`: whether save-state/sleep support is available.
- `framework.chip32_vm`: optional Chip32 filename in the core root; when present, Chip32 owns the load process.
- `framework.dock.supported`: documented value is `true`; `analog_output` is marked as upcoming.
- `framework.hardware.link_port`: whether the link port is used.
- `framework.hardware.cartridge_adapter`: bitfield controlling cartridge power, Play Cartridge, and strict/soft adapter checks; use the live page rather than guessing bit meanings.
- `cores`: at most 8 bitstreams. Each entry has an optional debug `name`, 16-bit `id`, and bit-reversed `filename`.

The official docs page currently renders `/` instead of `shortname` in its sample JSON. This is a documentation rendering/sample typo: the official [core-template `core.json`](https://raw.githubusercontent.com/open-fpga/core-template/main/core.json) uses `"shortname"`.

## `data.json`

Source: [data.json](https://www.analogue.co/developer/docs/core-definition-files/data-json). A core can define at most 32 slots.

| Field | Meaning and constraints |
| --- | --- |
| `magic` | Must be `APF_VER_1`. |
| `data_slots[].name` | UI name, max 15 characters. |
| `id` | 16-bit unsigned slot ID. |
| `required` | If true, a missing file opens the expected file browser; if false, a missing file is skipped. |
| `parameters` | Integer/hex bitmap described below. |
| `nonvolatile` | Load/unload the slot on core exit for save-like data. |
| `deferload` | Do not auto-load file data, but publish ID/size and allow Target commands to read/write it. |
| `secondary` | Ignore unless referenced by a selected variant/instance. |
| `filename` | Expected filename, max 31 characters. |
| `extensions` | Up to 4 extensions, each max 7 characters. |
| `size_exact` / `size_maximum` | Optional 32-bit unsigned size checks. |
| `address` | 32-bit unsigned load address. |

### `parameters` bitmap

| Bit | Set behavior |
| --- | --- |
| 0 | User-reloadable in the core UI. |
| 1 | Core-specific file, stored under the core folder rather than platform `common`. |
| 2 | Nonvolatile filename is cloned from slot 0 and given this slot's extension. |
| 3 | Read-only. |
| 4 | Treat the loaded JSON as an instance description. It must also be core-specific and is valid only in slot 0. |
| 5 | Initialize missing nonvolatile data with `0xFF` up to `size_maximum`. |
| 6 | Reset around loading: `[0010]` before the data sequence and `[0011]` after it. |
| 7 | Unload and fully restart the core before/after loading. |
| 8 | Same as bit 7 and also reload the FPGA bitstream. |
| 9 | Persist filenames chosen in the browser, overriding a definition/instance filename until Reset All to Defaults. |
| 25:24 | Index into `core.metadata.platform_ids` from which to resolve the file. |

The documented bitmap is an input to runtime behavior, not just metadata. If a slot is nonvolatile, the core can change the saved file size through the BRIDGE dataslot size table; Pocket flushes it on shutdown. With Chip32, bits 6–7 have special soft-restart semantics; read [data.json](https://www.analogue.co/developer/docs/core-definition-files/data-json) and [Chip32](https://www.analogue.co/developer/docs/chip32-vm) together.

## `input.json`

Source: [input.json](https://www.analogue.co/developer/docs/core-definition-files/input-json). The file describes the Controls menu and is currently read-only.

- Default path: `/Cores/AuthorName.CoreName/input.json`.
- Optional per-asset override: `/Presets/AuthorName.CoreName/Input/<path_to_slot0_asset>.json`.
- At most 4 controllers; each `type` must be `default`.
- At most 8 mappings per controller. Mapping IDs are 16-bit unsigned; names are max 19 characters.
- Supported keys: `pad_btn_a`, `pad_btn_b`, `pad_btn_x`, `pad_btn_y`, `pad_trig_l`, `pad_trig_r`, `pad_btn_start`, `pad_btn_select`.

## `<instance>.json`

Source: [instance JSON](https://www.analogue.co/developer/docs/core-definition-files/instance-json). The file lives where the selected asset would live. To make it selectable, slot 0 needs a `json` extension and the Instance JSON parameter bit.

- `data_path`: forward-slash asset path, max 255 characters.
- `core_select.id`: 16-bit bitstream ID; `select` chooses it instead of the first/only bitstream.
- `data_slots`: at most 32 entries; each ID is 16-bit and `filename` is an exact path/filename up to 255 characters. The docs say relative paths are not supported.
- `memory_writes`: at most 32 entries; each `address` and `data` is 32-bit unsigned.

## `interact.json`

Sources: [interact.json](https://www.analogue.co/developer/docs/core-definition-files/interact-json) and [Custom Interact UI](https://www.analogue.co/developer/docs/custom-interact-ui).

- The Core Settings menu supports `check`, `radio`, `slider_u32`, `list`, `action`, and `number_u32`.
- At most 16 `interact.json` UI entries are normally shown. If more than 4 reloadable data slots are also present, the combined menu is capped at 20 and additional entries may be dropped. A `list` can contain up to 16 options and is the most compact way to expose choices.
- Common fields: `name` (max 23), 16-bit `id` (unique for persistence), `type`, `enabled`, and 32-bit BRIDGE `address`.
- Read/modify/write is the default. `writeonly: true` avoids readback and is appropriate when the register cannot be read.
- `mask` preserves bits set to `1`; bits set to `0` may be changed by the element.
- `persist` saves the value across shutdown. Default and persistent files live under `/Cores/.../Interact` and `/Settings/.../Interact`; per-asset overrides use matching paths under `/Presets` and `/Settings`.
- Radio/check elements use `group`, `defaultval`, `value`, optional `value_off`, and optional `mask`.
- Sliders use `defaultval`, optional `mask`, and `graphical` (`signed`, `min`, `max`, `adjust_small`, `adjust_large`).
- Lists contain `{value, name}` options. Actions write `value` and may use `mask`.

## `variants.json`

Source: [variants.json](https://www.analogue.co/developer/docs/core-definition-files/variants-json). This is marked as an upcoming feature.

- Up to 8 variants; each has a max-15-character `name`, 16-bit `id`, optional core selection, data-slot overrides, and memory writes.
- The prose describes `core_select`, a data override array, and `memory_writes`; IDs are 16-bit and addresses/data are 32-bit.
- The current page contains naming inconsistencies between its headings/prose and sample (`data_override` versus `data_overridemagic`; `data_id`/`data_id_override` versus `data_id_to`/`data_id_from`). Do not copy those names blindly: inspect the live page and official template for the firmware/version being targeted.

## `video.json`

Source: [video.json](https://www.analogue.co/developer/docs/core-definition-files/video-json).

- At most 8 `scaler_modes`; width/height are active pixels, aspect is `aspect_w`/`aspect_h`, optional dock aspect can override it.
- `rotation` is `0`, `90`, `180`, or `270`. `mirror` uses bit 1 for left/right and bit 0 for up/down.
- At most 16 `display_modes`, each referring to a documented ID. `defaults.sharpness` ranges from soft `0` to maximum `3`.
- Use generic LCD modes for forward compatibility when possible. CRT Trinitron requires no horizontal pixel duplication; non-color LCD modes require grayscale output and a successful response to Host command `[00B8]`.
- The current table includes CRT `0x10`, generic/original GB/GBC/GBA modes (`0x20`–`0x42`), Game Gear (`0x51`–`0x52`), Neo Geo Pocket (`0x61`–`0x63`), TurboExpress/PC Engine LT (`0x71`–`0x72`), Lynx (`0x81`–`0x82`), Pinball Neon Matrix `0xE0`, and Vacuum Fluorescent `0xE1`. Verify the live table for newer firmware.

## `audio.json`

Source: [audio.json](https://www.analogue.co/developer/docs/core-definition-files/audio-json). It currently only documents `audio.magic: "APF_VER_1"` and is marked as an upcoming feature. Use [Bus Communication](https://www.analogue.co/developer/docs/bus-communication) for the current I2S electrical/timing requirements.
