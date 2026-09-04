# WynCommand

**WynCommand** is a programmable developer command surface built around the six dedicated macro keys on a Razer BlackWidow V4 X running on Kubuntu Linux.

Each physical macro key owns a specific development domain and is backed by a different programming language. Modifier layers expand the six physical keys into **24 distinct commands**.

The project is intentionally polyglot: part productivity tool, part programming-language laboratory, and part excuse to make a keyboard far more powerful than it has any right to be. :3

---

## Key Layout

| Key | Language | Domain |
| --- | --- | --- |
| **M1** | Python | Project navigation |
| **M2** | Bash | Linux / system utilities |
| **M3** | Java | Git tooling |
| **M4** | Zig | Build / test / run / debug |
| **M5** | Scala | Desktop utilities |
| **M6** | Rust | Developer dashboard |

NASM/x86-64 assembly may be integrated into any suite where it provides a legitimate low-level capability, measurable performance improvement, hardware-specific feature, or useful learning opportunity.

---

## Modifier Grammar

Each macro key follows the same conceptual modifier layout:

| Input | Purpose |
| --- | --- |
| **M#** | Primary action |
| **Shift + M#** | Secondary action |
| **Ctrl + M#** | Deeper / detailed action |
| **Alt + M#** | Alternate / tooling action |

This gives WynCommand a total of:

```text
6 macro keys × 4 layers = 24 commands
```

---

## Linux Key Mapping

OpenRazer exposes the BlackWidow V4 X macro keys as:

```text
M1 -> F13
M2 -> F14
M3 -> F15
M4 -> F16
M5 -> F17
M6 -> F18
```

The keyboard releases modifier keys before emitting the macro-key event, so `keyd` is used to preserve modifier intent and translate the physical combinations into stable synthetic keys.

Current mapping:

| Physical Input | Linux / KDE Input |
| --- | --- |
| M1-M6 | F13-F18 |
| Shift + M1-M6 | F19-F24 |
| Ctrl + M1-M6 | Ctrl+F19-F24 |
| Alt + M1-M6 | Alt+F19-F24 |

Example:

```text
M1          -> F13
Shift + M1  -> F19
Ctrl + M1   -> Ctrl+F19
Alt + M1    -> Alt+F19
```

This lets KDE bind each WynCommand action independently.

---

## Planned Commands

### M1 - Projects - Python

```text
M1          -> Open / focus project
Shift + M1  -> Search project
Ctrl + M1   -> Recent projects
Alt + M1    -> Project documentation
```

Possible executable:

```text
wyn-project
```

Example interface:

```bash
wyn-project open
wyn-project search
wyn-project recent
wyn-project docs
```

---

### M2 - System - Bash

```text
M2          -> Terminal
Shift + M2  -> SSH menu
Ctrl + M2   -> Services
Alt + M2    -> System / process information
```

Possible executable:

```text
wyn-system
```

Example interface:

```bash
wyn-system terminal
wyn-system ssh
wyn-system services
wyn-system info
```

---

### M3 - Git - Java

```text
M3          -> Git status
Shift + M3  -> Git diff
Ctrl + M3   -> Git log
Alt + M3    -> Branch tools
```

Possible executable:

```text
wyn-git
```

Example interface:

```bash
wyn-git status
wyn-git diff
wyn-git log
wyn-git branches
```

The first version may use Java's `ProcessBuilder` to invoke Git directly. A later version may use JGit for native repository inspection and manipulation.

---

### M4 - Build - Zig

```text
M4          -> Test
Shift + M4  -> Build
Ctrl + M4   -> Run
Alt + M4    -> Debug
```

Possible executable:

```text
wyn-build
```

Example interface:

```bash
wyn-build test
wyn-build build
wyn-build run
wyn-build debug
```

The suite should eventually detect the current project type automatically.

Possible project markers:

```text
Cargo.toml      -> Rust
build.zig       -> Zig
pyproject.toml  -> Python
pom.xml         -> Java
*.fsproj        -> F#
package.json    -> Node / frontend project
```

---

### M5 - Desktop - F#

```text
M5          -> Clipboard tools
Shift + M5  -> Screenshot
Ctrl + M5   -> Color picker
Alt + M5    -> Utility launcher
```

Possible executable:

```text
wyn-desktop
```

Example interface:

```bash
wyn-desktop clipboard
wyn-desktop screenshot
wyn-desktop color
wyn-desktop launcher
```

This suite can use .NET APIs where appropriate and orchestrate KDE/Linux utilities where that is the cleaner solution.

---

### M6 - Dashboard - Rust

```text
M6          -> Project health
Shift + M6  -> DevDoctor
Ctrl + M6   -> Logs
Alt + M6    -> Full developer dashboard
```

Possible executable:

```text
wyn-dashboard
```

Potential dashboard checks:

```text
Git state
Tests
PostgreSQL
Listening ports
Local services
Backend health
Docker / containers
Cloud connectivity
Build status
```

---

## Project Structure

Suggested repository layout:

```text
WynCommand/
├── M1-projects-python/
├── M2-system-bash/
├── M3-git-java/
├── M4-build-zig/
├── M5-desktop-fsharp/
├── M6-dashboard-rust/
├── asm/
├── config/
│   └── blackwidow.conf
└── README.md
```

Each suite should use the normal project structure and conventions of its language rather than forcing all six languages into one artificial layout.

---

## Assembly Philosophy

Assembly is welcome in WynCommand, but it must earn its place.

Good reasons to add NASM include:

- CPU feature detection
- cycle-accurate timing
- SIMD / AVX optimization
- byte scanning
- specialized parsing
- hardware-specific operations
- FFI experiments
- genuinely hot paths identified through profiling

The preferred optimization workflow is:

```text
measure
  ->
profile
  ->
understand the bottleneck
  ->
improve algorithm / data layout
  ->
inspect compiler output
  ->
benchmark
  ->
write assembly if it can actually win
  ->
benchmark again
```

Where practical, retain a high-level reference implementation for correctness testing, portability, and benchmarking.

In other words:

```text
hehe optimize :3
```

is an acceptable commit message only if the benchmark supports the allegation.

---

## Keyboard Stack

The current Linux input path is:

```text
Razer BlackWidow V4 X
        |
        v
OpenRazer
        |
        v
evdev
        |
        v
keyd
        |
        v
keyd virtual keyboard
        |
        v
KDE Plasma / Wayland
        |
        v
WynCommand
```

`keyd` is necessary because the BlackWidow V4 X releases physical modifiers before emitting F13-F18. One-shot modifier layers allow WynCommand to preserve the intended combination.

A tracked copy of the active keyd configuration should live at:

```text
config/blackwidow.conf
```

The active system configuration remains:

```text
/etc/keyd/blackwidow.conf
```

---

## Goals

WynCommand exists to:

- make common development actions physically accessible
- reduce repeated terminal / IDE navigation
- provide a practical project for learning multiple languages
- compare how different ecosystems solve similar CLI and automation problems
- create reusable developer tooling rather than disposable exercises
- provide legitimate places to practice systems programming and assembly
- slowly turn six innocent macro keys into an unreasonable amount of infrastructure

---

## Status

**Current phase:** keyboard input plumbing complete.

Working:

- [x] OpenRazer support for BlackWidow V4 X
- [x] M1-M6 exposed as F13-F18
- [x] F13-F24 configured as normal function keys in KDE
- [x] keyd installed and managing the keyboard
- [x] Shift macro layer
- [x] Ctrl macro layer
- [x] Alt macro layer
- [x] 24 unique shortcut slots available

Next:

- [ ] Create repository structure
- [ ] Add tracked `blackwidow.conf`
- [ ] Build M4 Zig `wyn-build test`
- [ ] Bind first real WynCommand action in KDE
- [ ] Expand each language suite incrementally
- [ ] Add assembly only when WynASM senses weakness

---

## License

TBD.

---

> Six keys. Six languages. Twenty-four commands. One increasingly suspicious `asm/` directory.
