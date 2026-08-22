# Chip32 VM

Official sources: [Chip32 overview](https://www.analogue.co/developer/docs/chip32-vm), [Initialization](https://www.analogue.co/developer/docs/chip32-vm/initialization-of-the-chip32-vm), [File Process](https://www.analogue.co/developer/docs/chip32-vm/file-process), [Special](https://www.analogue.co/developer/docs/chip32-vm/special), and [Opcode Mnemonic](https://www.analogue.co/developer/docs/chip32-vm/opcode-mnemonic).

## When to use it

Chip32 replaces APF's normal load process. Use it only when the core needs logic such as inspecting file headers, choosing among bitstreams, selecting/loading files conditionally, handling external triggers, or writing special initialization registers. A normal core should let APF load `data.json` slots directly.

When `core.framework.chip32_vm` names a program in the core root, that program must load the bitstream and all required data slots itself, then return control to APF.

## Execution model

- 32-bit CPU with 16 registers and a stack; combined program/data address space is 8 KiB (up to 2,000 instructions in the overview).
- Instructions are 16-bit aligned. An odd number of direct bytes before opcodes can misalign later instructions; this is a documented erratum.
- `R0` receives the selected JSON/data-slot ID. On a cold boot it is the ID of slot index 0. `R1`–`R15` start at zero on first boot and retain values across a core reset, so they can remember what was already loaded.
- Boot vector `0x0000` is the error vector; `0x0002` contains the start address vector. RAM outside the loaded program may be random after a VM restart and must not hold persistent state.
- The VM can read/write the FPGA address space through BRIDGE and has custom I/O for loading and host communication.

The minimal load program is conceptually:

1. `CORE` the required bitstream (normally ID 0).
2. `LOADF` for each applicable data slot, or use the file/process instructions for conditional loading.
3. `HOST 0x4002` to tell APF that dataslot access is complete and normal core bring-up may continue.

When a user reloads a slot marked User-reloadable, Chip32 is called again with the selected slot ID in `R0`; the saved register state is available. The program must decide what to load and still call `HOST 0x4002` when ready.

## Instruction families

Use the linked subpages for exact encodings and operand forms:

- [ALU](https://www.analogue.co/developer/docs/chip32-vm/alu): add, subtract, compare, multiply, divide, carry flag.
- [ALU Logic](https://www.analogue.co/developer/docs/chip32-vm/alu-logic): AND/OR/XOR/BIT, CRC.
- [Shift](https://www.analogue.co/developer/docs/chip32-vm/shift): ASL, LSR, ROL, ROR with immediate/register counts and carry behavior.
- [Load and Store](https://www.analogue.co/developer/docs/chip32-vm/load-and-store): immediate/register moves, byte/word/long memory access, stack, and PMP access.
- [Jump and Flow Control](https://www.analogue.co/developer/docs/chip32-vm/jump-and-flow-control): conditional branches/calls/returns and flag conditions.
- [File Process](https://www.analogue.co/developer/docs/chip32-vm/file-process): `LOADF`, open/close/seek/read/copy, file metadata, and file-size/offset/address adjustment.
- [Special](https://www.analogue.co/developer/docs/chip32-vm/special): core selection, Host commands, slot queries, and other VM I/O.
- [Debugging](https://www.analogue.co/developer/docs/chip32-vm/debugging): `PRINTF`, `HEX`, and `DEC` output.
- [Opcode Mnemonic](https://www.analogue.co/developer/docs/chip32-vm/opcode-mnemonic): complete opcode/encoding table; consult it instead of inferring binary encodings from mnemonic names.

The ALU exposes Z (result is zero) and C (carry/borrow/overflow) flags. Division by zero is an execution error. The documented stack is 32-bit and 16 words deep; overflow/underflow are errors.

## Debugging and safety

Enable Debug Logging and, when needed, Chip32 Exec Log in Pocket's Developer menu. `PRINTF` uses a null-terminated string and a 40-character buffer; long or missing-terminator strings can obscure the real failure. If execution hangs, holding B cancels Chip32. Keep VM code deterministic, avoid relying on uninitialized RAM, and always make the successful APF handoff reachable.
