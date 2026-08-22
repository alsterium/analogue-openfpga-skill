# Runtime, buses, and Pocket hardware

Official sources: [Bus Communication](https://www.analogue.co/developer/docs/bus-communication), [Host/Target Commands](https://www.analogue.co/developer/docs/host-target-commands), [Core Boot Process](https://www.analogue.co/developer/docs/core-boot-process), and [External Hardware](https://www.analogue.co/developer/docs/external-hardware).

## Buses

| Bus | Role | Important constraints |
| --- | --- | --- |
| BRIDGE | Framework/Pocket is controller; core is peripheral. | 32-bit address/read/write space. Reserve `0xF8xxxxxx` for APF. Reads/writes are relatively slow (a few MB/s), and the APF adapter buffers reads. |
| PAD | Framework/Pocket is peripheral; core is controller. | Up to 4 controllers. The type nibble determines built-in pad, digital/analog dock controller, keyboard, or mouse. The heartbeat also tells APF that the core is alive. |
| VIDEO | Core produces digital video. | RGB 24-bit; 16×16 to 800×720; approximately 47–61 Hz; pixel clock about 1–50 MHz. Use the documented VS/HS/DE/SKIP timing and scaler-slot endline feature. |
| AUDIO | Core produces I2S-compatible stereo. | Signed 16-bit, exactly 48 kHz; MCLK 12.288 MHz. LRCK is low for left and high for right; each channel has 16 active and 16 spacer bits. |

### BRIDGE

The framework presents a 32-bit wide memory-mapped adapter. The template's top-level signals are `bridge_endian_little`, `bridge_addr`, `bridge_rd`, `bridge_rd_data`, `bridge_wr`, and `bridge_wr_data`. A core may use any other address range for its own devices, but the `0xF8xxxxxx` range is reserved for framework communication. All cores must implement the baseline Host/Target commands needed for boot.

### PAD input words

The `key` register uses bits 0–15 for d-pad, face buttons, triggers, select, and start; bits 31:28 carry the controller type and bits 28:16 are unused. `joy` packs four 8-bit analog axes, and `trigger` packs two 8-bit analog triggers. Only interpret analog/keyboard/mouse fields after checking the type nibble.

Type values documented by the current page:

- `0x0`: nothing connected
- `0x1`: Pocket built-in buttons (Player 1 only)
- `0x2`: docked controller without analog
- `0x3`: docked controller with analog
- `0x4`: docked keyboard
- `0x5`: docked mouse
- `0x7`–`0xF`: reserved

Keyboard and mouse data reuse the PAD registers and are report-oriented; do not parse them as joystick data without checking the type.

## Host/Target command protocol

The command BRAM base is `0xF8000000`. There are two command/status channels:

- Host (Pocket → core): status at offset `0x00`, parameter pointer `0x04`, response pointer `0x08`.
- Target (core → Pocket): status at offset `0x1000`, parameter pointer `0x1004`, response pointer `0x1008`.

The status handshake has three stages. The issuer writes a command marker plus a 16-bit command word (`CM`/`cm`); the receiver changes it to busy (`BU`/`bu`), then completes with result (`OK`/`ok`) and a 16-bit result code. Parameter and response buffers are pointed to by the corresponding registers.

The dataslot ID/size table occupies `0x2000`–`0x20FF`: 32 entries × 8 bytes, with a 16-bit slot ID and a 32-bit size. The core may update the size for nonvolatile files. Build date/time/ID are exposed at `0x2380`–`0x238B`.

### Common Host commands

| ID | Meaning | Use |
| --- | --- | --- |
| `0x0000` | Request Status | Report `0x01` booting, `0x02` setup, `0x03` idle, or `0x04` running. |
| `0x0010` / `0x0011` | Reset Enter / Reset Exit | Stop or start core execution. |
| `0x0080` | Dataslot request read | Prepare Pocket to read a nonvolatile slot. |
| `0x0082` | Dataslot request write | Prepare a slot load/write, with 48-bit expected size split across parameters. |
| `0x008A` | Dataslot update | Notify a changed/deferred slot, especially with `deferload`. |
| `0x008F` | Dataslot access all complete | End the standard load sequence. |
| `0x0090` | Real-time Clock Data | One boot-time timestamp command. |
| `0x00A0` / `0x00A4` | Savestate start/query and load/query | Negotiate and then poll save-state operations. |
| `0x00B0` / `0x00B1` / `0x00B2` | OS menu, cartridge adapter, and dock notifications | Optional compatibility notifications. |
| `0x00B8` | Display Mode | Bits 15:8 carry mode ID; bit 0 requests grayscale. For the non-color LCD modes the core must output grayscale and respond `16'h444D`. |

### Common Target commands

| ID | Meaning | Important parameters |
| --- | --- | --- |
| `0x0140` | Ready to run | Sent after all required setup and data operations. |
| `0x0152` | Debug Event Log | 32-bit event ID. |
| `0x0180` / `0x0181` | Dataslot read / 48-bit read | Slot ID, slot offset, BRIDGE destination, length. |
| `0x0184` / `0x0185` | Dataslot write / 48-bit write | Slot ID, slot offset, BRIDGE source, length. |
| `0x0188` | Dataslot flush | Slot ID. |
| `0x0190` | Get filename | Slot ID and pointer to a 256-byte path struct. |
| `0x0192` | Open new file | Slot ID and pointer to path/flags/desired-size struct. Only Assets/Saves paths in supported platforms are allowed. |

Use [Host/Target Commands](https://www.analogue.co/developer/docs/host-target-commands) for exact parameter layout and result codes. `deferload` slots are the intended path for large files and target-side reads/writes.

## Boot flow

The [boot process](https://www.analogue.co/developer/docs/core-boot-process) describes this order:

1. Pocket loads the bitstream; the core starts clocks/FSMs and reports `booting`.
2. After the initial wait, Pocket polls `0x0000` until the core reports `setup`.
3. Pocket informs the core about a detected cartridge adapter with `0x00B1`.
4. Pocket applies variant and instance memory writes, then loads data slots in order.
5. The core may request additional slot operations; Pocket ends the normal sequence with `0x008F` and sends RTC data with `0x0090`.
6. The core sends Target `0x0140` and enters `idle`.
7. Pocket writes persistent Interact registers, enables cartridge power if needed, sends `0x0011`, and the core enters `running`.
8. On shutdown, Pocket enters reset, saves persistent values, flushes nonvolatile data using the size table, and resets the FPGA.

The core must continuously produce the heartbeat after the bitstream starts. Losing it makes Pocket terminate and reload the core from the same initial state.

## External hardware safety

The [External Hardware](https://www.analogue.co/developer/docs/external-hardware) page gives electrical details; use the template HDL for exact pins and initialization.

- User-visible RAM includes two PSRAM chips (four dies, 16 MB total per chip), 128K×16 asynchronous SRAM (256 KB), and 32M×16 SDRAM (64 MB). PSRAM die enables must never be asserted simultaneously; the highest word of each die has a configuration-register access hazard.
- Cartridge voltage is hardware-selected (3.3 V or 5 V), power is controlled by `core.json`, and level-translator direction must be configured correctly. Keep unused pins at template defaults; a bad configuration while cartridge power is on can damage or corrupt an inserted cartridge.
- Link-port power is on the cartridge-bus rail.
- IR transmit must use PWM pulses below 100% duty cycle; disable the receiver when unused and allow AGC time to settle when enabling it.
