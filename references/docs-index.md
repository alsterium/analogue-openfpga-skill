# Analogue openFPGA documentation index

Snapshot date: 2026-08-22. The canonical entry point is [Analogue Developer Docs](https://www.analogue.co/developer/docs/), which redirects to [Overview](https://www.analogue.co/developer/docs/overview). The site labels the SDK as beta and marks some features as upcoming, so use the live page for a firmware-specific answer.

## Choose a page family

| Question or task | Start here | Then consult |
| --- | --- | --- |
| What is a core, how do I start, or where do files go? | [Overview](https://www.analogue.co/developer/docs/overview), [Getting Started](https://www.analogue.co/developer/docs/getting-started) | [SD folder structure](https://www.analogue.co/developer/docs/directories-and-sd-folder-structure), [Packaging](https://www.analogue.co/developer/docs/packaging-a-core) |
| JSON schema or asset loading | [Core Definition Files](https://www.analogue.co/developer/docs/core-definition-files) | The individual JSON pages below |
| Core-to-Pocket communication or boot failure | [Bus Communication](https://www.analogue.co/developer/docs/bus-communication), [Core Boot Process](https://www.analogue.co/developer/docs/core-boot-process) | [Host/Target Commands](https://www.analogue.co/developer/docs/host-target-commands), [Debugging Aids](https://www.analogue.co/developer/docs/debugging-aids) |
| Custom asset loader or file inspection | [Chip32 VM](https://www.analogue.co/developer/docs/chip32-vm) | Chip32 initialization, file-process, special, and opcode pages |
| Pocket I/O, memory, cartridge, or link port | [External Hardware](https://www.analogue.co/developer/docs/external-hardware) | The template's `core_top.v` for exact pins and directions |
| UI, display, platform, or image assets | [Custom Interact UI](https://www.analogue.co/developer/docs/custom-interact-ui), [Platform Metadata](https://www.analogue.co/developer/docs/platform-metadata) | [video.json](https://www.analogue.co/developer/docs/core-definition-files/video-json), [Library](https://www.analogue.co/developer/docs/library), [Custom Palettes](https://www.analogue.co/developer/docs/custom-palettes) |
| Release or firmware compatibility | [Packaging a Core](https://www.analogue.co/developer/docs/packaging-a-core) | [2.3 changelog](https://www.analogue.co/developer/docs/changelog/2-3), then the relevant older changelog |

## Page inventory

### Orientation and filesystem

- [Overview](https://www.analogue.co/developer/docs/overview)
- [Getting Started](https://www.analogue.co/developer/docs/getting-started)
- [Directories and SD Folder Structure](https://www.analogue.co/developer/docs/directories-and-sd-folder-structure)

### Core definition files

- [Core Definition Files](https://www.analogue.co/developer/docs/core-definition-files)
- [audio.json](https://www.analogue.co/developer/docs/core-definition-files/audio-json)
- [core.json](https://www.analogue.co/developer/docs/core-definition-files/core-json)
- [data.json](https://www.analogue.co/developer/docs/core-definition-files/data-json)
- [input.json](https://www.analogue.co/developer/docs/core-definition-files/input-json)
- [<instance>.json](https://www.analogue.co/developer/docs/core-definition-files/instance-json)
- [interact.json](https://www.analogue.co/developer/docs/core-definition-files/interact-json)
- [variants.json](https://www.analogue.co/developer/docs/core-definition-files/variants-json)
- [video.json](https://www.analogue.co/developer/docs/core-definition-files/video-json)

### Runtime and hardware

- [Bus Communication](https://www.analogue.co/developer/docs/bus-communication)
- [External Hardware](https://www.analogue.co/developer/docs/external-hardware)
- [Host/Target Commands](https://www.analogue.co/developer/docs/host-target-commands)
- [Core Boot Process](https://www.analogue.co/developer/docs/core-boot-process)

### Chip32 VM

- [Chip32 VM overview](https://www.analogue.co/developer/docs/chip32-vm)
- [Initialization](https://www.analogue.co/developer/docs/chip32-vm/initialization-of-the-chip32-vm)
- [ALU](https://www.analogue.co/developer/docs/chip32-vm/alu)
- [ALU Logic](https://www.analogue.co/developer/docs/chip32-vm/alu-logic)
- [Shift](https://www.analogue.co/developer/docs/chip32-vm/shift)
- [Load and Store](https://www.analogue.co/developer/docs/chip32-vm/load-and-store)
- [Jump and Flow Control](https://www.analogue.co/developer/docs/chip32-vm/jump-and-flow-control)
- [File Process](https://www.analogue.co/developer/docs/chip32-vm/file-process)
- [Special](https://www.analogue.co/developer/docs/chip32-vm/special)
- [Debugging](https://www.analogue.co/developer/docs/chip32-vm/debugging)
- [Opcode Mnemonic](https://www.analogue.co/developer/docs/chip32-vm/opcode-mnemonic)

### UI, metadata, distribution, and tools

- [Custom Interact UI](https://www.analogue.co/developer/docs/custom-interact-ui)
- [Platform Metadata](https://www.analogue.co/developer/docs/platform-metadata)
- [Packaging a Core](https://www.analogue.co/developer/docs/packaging-a-core)
- [Library](https://www.analogue.co/developer/docs/library)
- [Custom Palettes](https://www.analogue.co/developer/docs/custom-palettes)
- [Debugging Aids](https://www.analogue.co/developer/docs/debugging-aids)

### Changelogs

The current sidebar includes [2.3](https://www.analogue.co/developer/docs/changelog/2-3), [2.1](https://www.analogue.co/developer/docs/changelog/2-1), [2.0](https://www.analogue.co/developer/docs/changelog/2-0), [1.2](https://www.analogue.co/developer/docs/changelog/1-2), [1.1](https://www.analogue.co/developer/docs/changelog/1-1), and earlier beta pages. The 2.3 page records framework version 2.3, additional original display modes, Vacuum Fluorescent, and a fix to `[0192 Open new file]` updating dataslot size fields.

## Official implementation reference

Analogue's Getting Started page links to [open-fpga/core-template](https://github.com/open-fpga/core-template). It contains the JSON files, starter FPGA source, build output, and `core_top.v` pin/interface definitions. Use it to resolve sample-code details that are not fully specified in the prose docs.
