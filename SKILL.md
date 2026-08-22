---
name: analogue-openfpga
description: Use when developing, reviewing, debugging, packaging, or documenting Analogue Pocket openFPGA cores, APF JSON definitions, BRIDGE/PAD/VIDEO/AUDIO interfaces, or Chip32 programs; not for general FPGA work unrelated to Analogue Pocket.
---

# Analogue Pocket openFPGA developer docs

Use this skill for work that targets Analogue Pocket's openFPGA Developer SDK and Analogue Platform Framework (APF). Treat the official Analogue documentation and the official core template as the source of truth; the bundled references are a compact snapshot captured on 2026-08-22 and are not a promise that the online beta documentation has stopped changing.

## Route the task

Read [docs-index.md](references/docs-index.md) first, then read only the relevant reference:

- Core JSON, asset loading, input, instance files, Interact UI, variants, or video: [json-definitions.md](references/json-definitions.md).
- BRIDGE/PAD/VIDEO/AUDIO, boot order, Host/Target commands, or Pocket hardware: [runtime-hardware.md](references/runtime-hardware.md).
- Chip32 assembly or custom loading: [chip32.md](references/chip32.md).
- Setup, Quartus/JTAG iteration, packaging, platform metadata, library images, palettes, or debug aids: [workflows.md](references/workflows.md).
- Exact field descriptions, opcode tables, or a version-specific behavior: follow the official page link in the reference and verify the live page when network access is available.

## Operating rules

1. Inspect the user's repository, existing JSON, HDL, and template version before proposing changes. Prefer the official [open-fpga/core-template](https://github.com/open-fpga/core-template) as the starting shape for a new core.
2. Keep JSON examples valid and preserve the documented root object and `magic: "APF_VER_1"`. Preserve documented limits, bitmaps, widths, paths, and endianness; do not silently turn an optional or upcoming feature into a requirement.
3. Keep the BRIDGE framework region `0xF8xxxxxx` reserved. Use the template HDL for exact top-level pin names and direction control, especially for cartridge, link, and memory interfaces.
4. Distinguish documented behavior from an inference. The docs contain beta/upcoming features and a few inconsistencies; call those out and link the exact page rather than inventing a compatibility rule. In particular, the `core.json` page's rendered sample shows `/` where the schema says `shortname`; use the official template's `shortname` key.
5. For current firmware behavior, display-mode IDs, command details, or changelog questions, prefer the live official page. If working offline, say that the answer is based on the bundled snapshot and identify the relevant page.
6. When implementing code, finish with a focused checklist: JSON syntax/schema and path checks; required baseline Host/Target handling; reset/heartbeat behavior; asset and nonvolatile-slot behavior; video/audio timing; and package layout/bitstream conversion as applicable.

The refresh helper is [scripts/crawl_docs.py](scripts/crawl_docs.py). It discovers the docs navigation, fetches official pages, and can write a local Markdown snapshot; use it only when a refreshed snapshot is needed.
