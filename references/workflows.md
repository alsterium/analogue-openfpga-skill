# Development, packaging, and debugging workflows

Official sources: [Getting Started](https://www.analogue.co/developer/docs/getting-started), [Directories and SD Folder Structure](https://www.analogue.co/developer/docs/directories-and-sd-folder-structure), [Packaging a Core](https://www.analogue.co/developer/docs/packaging-a-core), [Platform Metadata](https://www.analogue.co/developer/docs/platform-metadata), [Library](https://www.analogue.co/developer/docs/library), [Custom Palettes](https://www.analogue.co/developer/docs/custom-palettes), and [Debugging Aids](https://www.analogue.co/developer/docs/debugging-aids).

## Start from the official template

The documented baseline is [open-fpga/core-template](https://github.com/open-fpga/core-template). It supplies the JSON files, starter FPGA source, `core_top.v`, and a sample bitstream. The Docs list Intel Quartus Lite with Cyclone V support, an Intel-approved USB/Ethernet Blaster, Pocket, and a FAT32/exFAT microSD card as the development setup. Pocket Developer Edition exposes a removable JTAG door; otherwise use the documented T-6 access procedure and ESD care.

Inspect and edit the template JSON first, then compile with Quartus. The SD core folder follows `/Cores/AuthorName.CoreName/`. Platform-common assets use `/Assets/<platform>/common/`; core-specific assets use `/Assets/<platform>/AuthorName.CoreName/`; platformless assets use `/Assets/_none/AuthorName.CoreName/`. Nonvolatile files go under the matching `/Saves/` tree. The Assets and Saves trees should mirror each other.

For fast iteration, copy JSON/assets/bitstream outputs to the SD card or use USB Link Mode. USB Link Mode is convenient but slow (under 1 MB/s in the Getting Started page), so use JTAG for bitstream reloads and avoid large transfers. A JTAG bitstream reload causes Pocket to repeat the load process with the same starting conditions.

## Package a release

1. Copy the core's JSON and binary files into the matching `/Cores/AuthorName.CoreName` tree.
2. Ensure `core.json` metadata has the release version and date. SemVer is recommended; the schema page calls the date key `date_release`.
3. Convert the Quartus raw `.rbf` to `.rbf_r` by reversing the bit order within every byte. Do not reverse byte order or alter file length.
4. Add platform metadata/assets when the core declares a platform.
5. Zip a snapshot of the SD tree. The archive must not add arbitrary base folders beyond Pocket's own base folders.
6. Name the archive `<AuthorName>.<CoreName>_<Version>_<ReleaseDate>.zip`, for example `Analogue.PDP-1_1.0_2022-07-30.zip`.

For a project not created from the template, the Packaging page says to set Quartus output to `output_files`, enable Raw Binary File (`.rbf`), and enable compressed bitstreams. The package uses the reversed RBF; the SOF is for JTAG/debugging and is not the packaged format.

## Platform metadata and images

If `core.metadata.platform_ids` names a platform, add `/Platforms/<platform_shortname>.json`. Platform shortnames are lowercase `a-z`, `0-9`, and `_`, max 15 characters, and cannot begin with `_`. The JSON fields are `category`, `name`, `manufacturer`, and integer `year`, with 31-character limits on the strings. Optional platform art goes in `/Platforms/_images/<platform_shortname>.bin`.

The [Library](https://www.analogue.co/developer/docs/library) page describes per-platform image files under `/System/Library/Images/<platform>/`. A single asset's lowercase CRC32 becomes the filename; multiple assets are concatenated in the documented recursive alphabetical order before CRC32. The image header is 8 bytes, followed by rotated 90° anti-clockwise pixel data. The documented current format is RGB 32-bit with BGRA byte order and opaque alpha.

For GB custom palettes, the [Custom Palettes](https://www.analogue.co/developer/docs/custom-palettes) page documents 56-byte `.pal` files under `/Assets/gb/common/palettes`: 48 bytes of four RGB colors for each of BG, OBJ0, OBJ1, and Window, one LCD-off RGB color, then footer bytes `0x81` + ASCII `APGB`. This feature is for OS 2.0+ and GB-targeting cartridges/cores.

## Debug on Pocket

The Developer menu provides:

- Builds: installed-core list; a missing platform JSON or invalid platform shortname can make a core appear here but not in the openFPGA menu.
- USB SD Access: useful for small files; the Debugging Aids page reports about 700 KB/s and recommends avoiding large files.
- Statistics: power (Developer units), temperature, video sync rate/status.
- Pause Core Boot and Pause Load Data: arm SignalTap or inspect setup; neither applies when Chip32 is running.
- Asset Load Detail, Debug Logging (`/System/Logs/`), and Chip32 Exec Log. Exec Log can greatly slow long programs.

Use the [Core Boot Process](https://www.analogue.co/developer/docs/core-boot-process) sequence when diagnosing a hang: first distinguish bitstream/heartbeat, setup/status, cartridge notification, dataslot transfer, `Ready to run`, persistent Interact writes, and reset exit. Keep a minimal package and template bitstream as a control case.
