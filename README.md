# WynCommand

**WynCommand** is a programmable developer command surface built around the six dedicated macro keys on a Razer BlackWidow V4 X running on Kubuntu Linux.

Each physical macro key owns a specific development domain and is backed primarily by a different programming language. Modifier layers expand the six physical keys into **24 distinct command slots**.

The project is intentionally polyglot: part productivity tool, part programming-language laboratory, part systems-programming playground, and part excuse to make a keyboard far more powerful than it has any right to be. :3

---

## Key Layout

| Key | Primary Language | Domain |
| --- | --- | --- |
| **M1** | Python | Project navigation |
| **M2** | Bash | Linux / system utilities |
| **M3** | Java | Git tooling |
| **M4** | Zig | Build / test / run / debug |
| **M5** | Scala | Desktop utilities |
| **M6** | Elixir | Networking utilities |

WynCommand also has three shared specialist languages:

| Language | Role |
| --- | --- |
| **NASM / x86-64 Assembly** | Low-level helpers, hardware-specific work, optimized hot paths |
| **Wren** | Programmable configuration, workflows, and lightweight scripting |
| **Prolog** | Rules, diagnostics, policy evaluation, and reasoning |

These languages are shared across the project rather than belonging to a single macro key.

---

## Modifier Grammar

Each macro key follows the same conceptual modifier layout:

| Input | Purpose |
| --- | --- |
| **M#** | Primary action |
| **Shift + M#** | Secondary action |
| **Ctrl + M#** | Deeper / detailed action |
| **Alt + M#** | Alternate / tooling action |

This gives WynCommand:

```text
6 macro keys × 4 layers = 24 command slots
```

---

# Keyboard Input Stack

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

The keyboard releases physical modifier keys before emitting the macro-key event, so `keyd` is used to preserve modifier intent and translate the physical combinations into stable synthetic key combinations.

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

This gives KDE Plasma 24 independently bindable WynCommand actions.

The active input path is:

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

The tracked configuration lives at:

```text
config/blackwidow.conf
```

The active system configuration remains:

```text
/etc/keyd/blackwidow.conf
```

---

# M1: Projects

**Language:** Python

**Domain:** Project navigation and developer workspace management.

Planned command surface:

```text
M1          -> Open / focus project
Shift + M1  -> Search project
Ctrl + M1   -> Recent projects
Alt + M1    -> Project documentation
```

Potential executable:

```text
wyn-project
```

Potential interface:

```bash
wyn-project open
wyn-project search
wyn-project recent
wyn-project docs
```

M1 is intended to become the fast route into the projects WynCommand already knows about.

---

# M2: System

**Language:** Bash

**Domain:** Linux and system utilities.

Planned command surface:

```text
M2          -> Terminal
Shift + M2  -> SSH menu
Ctrl + M2   -> Services
Alt + M2    -> System / process information
```

Potential executable:

```text
wyn-system
```

Potential interface:

```bash
wyn-system terminal
wyn-system ssh
wyn-system services
wyn-system info
```

Bash is intentionally used here because Linux already exposes an enormous amount of useful system functionality through command-line tools, `/proc`, `/sys`, systemd, SSH, and standard Unix interfaces.

---

# M3: Git

**Language:** Java

**Domain:** Git repository inspection and tooling.

Potential executable:

```text
wyn-git
```

Conceptual macro layout:

```text
M3          -> Git status
Shift + M3  -> Git diff
Ctrl + M3   -> Git log
Alt + M3    -> Branch tools
```

Current work includes:

- Java project initialized
- Maven build working
- Git invocation through `ProcessBuilder`
- current branch detection
- Git porcelain status parsing
- separate staged and unstaged state
- conflict-state modeling
- structured models for repository and file status

Current Java components include concepts such as:

```text
GitClient
RepositoryStatus
FileStatus
FileChange
ChangeType
ConflictType
```

Future work includes:

```text
dedicated status parser
parser test suite
repository tree
diff viewer
branch tooling
GitHub account selection
three-way conflict management
full graphical Git cockpit
```

JGit remains a possible later addition where native Java repository access provides a real advantage over invoking Git directly.

---

# M4: Build

**Language:** Zig

**Domain:** Universal project build, test, run, and debug orchestration.

Executable:

```text
wyn-build
```

The four-action protocol is:

```text
M4          -> Test
Shift + M4  -> Build
Ctrl + M4   -> Run
Alt + M4    -> Debug
```

Equivalent conceptual interface:

```bash
wyn-build test
wyn-build build
wyn-build run
wyn-build debug
```

M4 is currently the most mature WynCommand suite and is considered **operational**.

## Project Picker

`wyn-build` provides a QML-based project picker with:

- registered project selection
- per-project action menu
- inline project creation
- native KDE directory chooser
- automatic language scanning
- editable detected-language list
- persistent project registration

The current wrapper exports:

```text
QT_QPA_PLATFORMTHEME=xdgdesktopportal
```

so the QML interface can invoke the native KDE folder chooser.

The project editor can recursively scan a project while ignoring common generated directories such as:

```text
.git
target
_build
deps
node_modules
zig-out
.zig-cache
.idea
.venv
venv
dist
```

---

## Language Detection

M4 recognizes the following language set:

```text
Zig
Elixir
Prolog
Wren
ASM
Rust
Java
Scala
Python
Shell
JavaScript
TypeScript
QML
HTML
CSS
C
C++
C#
F#
Lua
SQL
Kotlin
Swift
Go
PHP
Ruby
```

Recognition is separate from execution support.

This distinction is deliberate:

```text
language detection
        !=
build ecosystem detection
```

A project can therefore be correctly recognized without WynCommand pretending it knows how to build it.

Unsupported build ecosystems result in a **SAFE STOP** rather than an invented or dangerous command.

---

## Build Ecosystem Detection

M4 can distinguish build ecosystems using project metadata rather than assuming that one programming language always implies one build system.

Current or implemented ecosystem support includes:

```text
Cargo
cargo-leptos
Zig Build
Mix
Maven
Gradle
sbt
npm
.NET
CMake
Make
SwiftPM
Go modules
Python
Composer
Bundler / Rake
```

For example:

```text
Cargo.toml      -> Cargo / Rust
build.zig       -> Zig Build
mix.exs         -> Elixir / Mix
pom.xml         -> Java / Maven
build.gradle    -> Gradle
build.sbt       -> Scala / sbt
package.json    -> npm ecosystem
CMakeLists.txt  -> CMake
Makefile        -> Make
go.mod          -> Go modules
Package.swift   -> SwiftPM
```

Rust projects using Leptos receive separate detection rather than being treated as ordinary Cargo applications.

Leptos metadata such as:

```text
[package.metadata.leptos]
```

or workspace equivalents can select the `cargo leptos` workflow.

Example actions include:

```bash
cargo leptos test
cargo leptos build
cargo leptos watch
```

---

## Execution UI

Actual Test / Build / Run / Debug commands launch through Konsole.

Command execution includes a formatted WynCommand header containing information such as:

```text
project
project type
action
command
exit status
```

Successful execution ends with:

```text
✦ SUCCESS command completed :3
```

Because apparently merely compiling software was insufficiently theatrical.

Real command executions also receive the current ceremonial startup sequence:

```text
TRANS RIGHTS
ARE HUMAN
RIGHTS <3
```

rendered as large block lettering across the trans flag color sequence:

```text
blue
pink
white
pink
blue
```

followed by a large purple bat.

The banner is intentionally shown only when a real command is executed.

`SAFE STOP` does not display it, because WynCommand should never visually imply that a command ran when it deliberately refused to run one.

---

# M5: Desktop

**Language:** Scala

**Domain:** Desktop utilities and KDE integration.

Planned command surface:

```text
M5          -> Clipboard tools
Shift + M5  -> Screenshot
Ctrl + M5   -> Color picker
Alt + M5    -> Utility launcher
```

Potential executable:

```text
wyn-desktop
```

Potential interface:

```bash
wyn-desktop clipboard
wyn-desktop screenshot
wyn-desktop color
wyn-desktop launcher
```

Scala replaced the earlier F# plan.

This keeps another WynCommand suite inside the JVM ecosystem while providing a language with strong functional-programming capabilities and a very different style from M3's Java.

M5 is currently largely unimplemented.

---

# M6: Networking

**Language:** Elixir

**Domain:** Networking, remote hosts, diagnostics, concurrency, and network service inspection.

Project:

```text
M6-networking-elixir/
```

M6 replaced the former Rust Observatory concept inside WynCommand.

The Observatory and endpoint-observability work has since become the separate **WynObserve** project, allowing WynCommand's M6 slot to focus specifically on networking.

The final mapping of the four physical M6 modifier layers is still evolving.

---

## Current M6 Architecture

The Elixir application currently includes concepts such as:

```text
WynCommand.Networking
WynCommand.Networking.Application

Networking.Host
Networking.Result

Checks.Ping
Checks.Port
Checks.Runner
```

The networking facade can perform checks against a host and normalize the results into structured data.

Current functionality includes:

```text
ICMP / ping checks
TCP port checks
structured success / failure results
multiple checks through a Runner
BEAM concurrency using Task.async_stream/3
```

Current diagnostic probes include common TCP ports such as:

```text
22
80
443
```

The application is built as a Mix / OTP project.

---

## Planned M6 Expansion

Near-term networking work includes:

```text
local listening-port discovery
local process ownership
Linux-specific platform inspection
Windows-specific platform inspection
DNS checks
SSH integration
Tailscale integration
remote-host tooling
monitoring / supervision
network diagnostic workflows
```

Remote port checking and local port/process inspection remain separate concepts.

For example:

```text
Checks.Port
```

asks:

> Can I reach this TCP port on that host?

while future modules such as:

```text
Local.Ports
Local.Processes
Platform.Linux
Platform.Windows
```

will answer:

> What is listening on this machine, and which process owns it?

Elixir is particularly useful here because the BEAM provides lightweight processes, supervision, concurrency, and failure isolation without requiring WynCommand to grow its own miniature scheduling system.

---

# Shared Languages

WynCommand is organized around six primary suite languages, but several problems naturally cross suite boundaries.

Shared helpers live under:

```text
shared/
├── asm/
├── prolog/
│   └── diagnostics.prolog
└── wren/
    └── preflight.wren
```

These languages should have genuine architectural jobs rather than being inserted solely for novelty.

Learning them is part of the project.

Making them justify their continued residence is also part of the project.

---

## Wren

Wren serves as WynCommand's lightweight embedded scripting and configuration language.

Good uses include:

```text
workflow definitions
user-configurable preflight sequences
project-specific behavior
diagnostic profiles
command orchestration
small programmable policies
```

Example conceptual workflow:

```text
network check
    ->
Wren profile selects probes
    ->
Elixir performs probes
    ->
normalized results
```

Wren should describe behavior rather than replace components better handled by the suite's primary language.

---

## Prolog

Prolog serves as the shared reasoning and rule layer.

Potential uses include:

```text
diagnostic reasoning
policy enforcement
dependency rules
project classification
network failure interpretation
safety rules
configuration validation
```

For M6, a future flow might look like:

```text
Elixir collects networking facts
        |
        v
normalized facts
        |
        v
Prolog diagnostic rules
        |
        v
likely explanation / recommended inspection path
```

Example reasoning concepts:

```text
host reachable
port 22 closed
port 443 open
DNS failed
Tailscale reachable
service unavailable
```

Prolog can reason over those facts without turning the Elixir codebase into a growing forest of nested conditional statements.

---

## NASM / x86-64 Assembly

Assembly is welcome in WynCommand, but it must earn its place.

Good reasons to use NASM include:

- CPU feature detection
- cycle-accurate timing
- SIMD / AVX optimization
- byte scanning
- specialized binary parsing
- packet manipulation
- checksum routines
- byte-order operations
- hardware-specific operations
- FFI experiments
- genuinely hot paths discovered through profiling

For M6 specifically, potential future assembly helpers include tightly scoped low-level packet, checksum, binary, or byte-order work.

Assembly helpers should generally remain isolated behind a clean interface rather than contaminating the architecture around them.

Where practical, retain a high-level reference implementation for:

```text
correctness testing
portability
benchmarking
regression detection
```

The preferred optimization workflow remains:

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

In other words:

```text
hehe optimize :3
```

is an acceptable commit message only if the benchmark supports the allegation.

---

# Repository Structure

Current high-level layout:

```text
WynCommand/
├── M1-projects-python/
├── M2-system-bash/
├── M3-git-java/
├── M4-build-zig/
│   ├── build.zig
│   ├── src/
│   │   ├── action.zig
│   │   ├── config.zig
│   │   ├── detect.zig
│   │   ├── main.zig
│   │   ├── picker.zig
│   │   ├── project.zig
│   │   ├── runner.zig
│   │   └── tests.zig
│   └── ui/
│       └── picker.qml
├── M5-desktop-scala/
├── M6-networking-elixir/
│   ├── lib/
│   │   └── wyn_command/
│   │       ├── networking.ex
│   │       └── networking/
│   │           ├── application.ex
│   │           ├── host.ex
│   │           ├── result.ex
│   │           └── checks/
│   │               ├── ping.ex
│   │               ├── port.ex
│   │               └── runner.ex
│   ├── test/
│   └── mix.exs
├── shared/
│   ├── asm/
│   ├── prolog/
│   │   └── diagnostics.prolog
│   └── wren/
│       └── preflight.wren
├── config/
│   └── blackwidow.conf
└── README.md
```

Each suite follows the normal conventions of its own ecosystem rather than forcing six unrelated languages into one artificial project structure.

That is part of the experiment.

---

# WynCommand vs WynObserve

WynCommand and WynObserve are now separate projects.

## WynCommand

A local developer command surface driven by the keyboard:

```text
projects
system utilities
Git
build tooling
desktop utilities
networking
```

## WynObserve

A separate endpoint observability and remote-diagnostics platform.

WynObserve owns concepts such as:

```text
endpoint telemetry
machine observability
incident timelines
remote diagnostics
self-healing
remote actions
machine dashboards
fleet monitoring
```

Keeping the projects separate prevents M6 from becoming an entire observability platform hiding inside one increasingly alarmed keyboard button.

---

# Design Principles

## Real tools, not exercises

Each suite should eventually become something worth using.

The purpose of using many languages is not merely to produce six different versions of:

```text
print("hello world")
```

Each language should encounter problems appropriate to its ecosystem.

---

## Polyglot by design

WynCommand deliberately compares different programming models:

```text
Python  -> scripting and automation
Bash    -> Unix composition
Java    -> object-oriented JVM tooling
Zig     -> explicit systems programming
Scala   -> functional / JVM programming
Elixir  -> concurrency and fault-tolerant orchestration
Wren    -> embedded scripting
Prolog  -> logical reasoning
NASM    -> machine-level programming
```

The resulting architecture should use those strengths rather than flattening every language into the same style.

---

## Safe automation

WynCommand should know when it does not know something.

Recognizing a project is not permission to invent a build command.

Detecting an unsupported environment should produce a clear result such as:

```text
SAFE STOP
```

instead of guessing.

Automation is useful only when its behavior remains understandable.

---

## Measure before optimizing

Low-level optimization should be evidence-driven.

The project encourages experimentation with Zig, native interfaces, assembly, SIMD, binary formats, and operating-system internals, but optimization begins with measurement rather than aesthetic suspicion of high-level code.

---

## Shared helpers must earn their place

NASM, Wren, and Prolog are deliberately available across the repository.

Whenever a suite reaches a problem that genuinely benefits from:

```text
low-level machine code
embedded scripting
logical inference
```

a shared helper is encouraged.

The point is to learn these languages by giving them real responsibilities.

No language gets free rent.

---

# Goals

WynCommand exists to:

- make common development actions physically accessible
- reduce repeated terminal and IDE navigation
- create reusable developer tooling rather than disposable exercises
- provide practical projects for learning multiple programming languages
- compare how different ecosystems solve similar problems
- explore concurrency, systems programming, scripting, logic programming, and assembly
- build safe automation rather than opaque automation
- provide legitimate opportunities for profiling and optimization
- integrate deeply with Linux, KDE, and developer tooling
- develop small utilities into a coherent command platform
- create shared NASM, Wren, and Prolog components where they genuinely belong
- slowly turn six innocent macro keys into an unreasonable amount of infrastructure

---

# Status

## Keyboard Infrastructure

- [x] OpenRazer support for BlackWidow V4 X
- [x] M1-M6 exposed as F13-F18
- [x] F13-F24 configured as normal function keys in KDE
- [x] `keyd` installed and managing keyboard
- [x] Shift macro layer
- [x] Ctrl macro layer
- [x] Alt macro layer
- [x] 24 unique shortcut slots available
- [x] tracked `config/blackwidow.conf`

## Repository

- [x] WynCommand repository created
- [x] polyglot top-level project structure
- [x] shared project registry
- [x] `shared/asm`
- [x] `shared/wren`
- [x] `shared/prolog`
- [x] M5 migrated from F# plan to Scala
- [x] M6 migrated from Rust Observatory to Elixir networking
- [x] WynObserve separated into its own project

## M1: Projects / Python

- [ ] Build initial project-navigation suite
- [ ] integrate shared project registry
- [ ] project open / focus
- [ ] project search
- [ ] recent projects
- [ ] documentation launcher

## M2: System / Bash

- [ ] Build initial system suite
- [ ] terminal launcher
- [ ] SSH menu
- [ ] service tooling
- [ ] system / process information

## M3: Git / Java

- [x] Java project initialized
- [x] Maven build working
- [x] Git commands through `ProcessBuilder`
- [x] branch detection
- [x] porcelain status parsing
- [x] staged / unstaged state representation
- [x] conflict model started
- [ ] parser extraction and comprehensive tests
- [ ] repository tree
- [ ] diff viewer
- [ ] branch tools
- [ ] GitHub account selector
- [ ] conflict manager
- [ ] graphical Git cockpit

## M4: Build / Zig

- [x] Zig project initialized
- [x] project registry integration
- [x] QML project picker
- [x] action picker
- [x] native KDE directory chooser
- [x] inline project editor
- [x] automatic project language scan
- [x] 26-language recognition
- [x] language detection separated from build-system detection
- [x] multiple build ecosystems supported
- [x] Rust / Cargo support
- [x] Leptos-aware Rust support
- [x] Zig Build support
- [x] Elixir / Mix support
- [x] Maven / Gradle support
- [x] Scala / sbt support
- [x] npm support
- [x] Test action
- [x] Build action
- [x] Run action
- [x] Debug framework
- [x] Konsole execution
- [x] SAFE STOP behavior
- [x] KDE M4 binding
- [x] real project execution tested
- [x] ceremonial trans-rights execution banner
- [x] enormous purple bat
- [x] M4 considered operational

## M5: Desktop / Scala

- [x] language changed from F# to Scala
- [ ] initialize Scala implementation
- [ ] clipboard tools
- [ ] screenshot tools
- [ ] color picker
- [ ] utility launcher

## M6: Networking / Elixir

- [x] Mix / OTP project initialized
- [x] project compiles
- [x] ExUnit baseline working
- [x] Host model
- [x] Result model
- [x] Ping check
- [x] TCP port check
- [x] check Runner
- [x] concurrent checks with `Task.async_stream/3`
- [ ] local port discovery
- [ ] process ownership inspection
- [ ] Linux platform adapter
- [ ] Windows platform adapter
- [ ] DNS diagnostics
- [ ] SSH integration
- [ ] Tailscale integration
- [ ] remote host tooling
- [ ] monitoring / supervision
- [ ] finalize four M6 physical macro actions

## Shared Helpers

- [x] Wren shared directory
- [x] Prolog shared directory
- [x] NASM shared directory
- [x] initial Wren preflight script
- [x] initial Prolog diagnostics knowledge base
- [ ] integrate Wren workflow configuration into active suites
- [ ] integrate Prolog diagnostic reasoning into active suites
- [ ] identify first justified NASM helper
- [ ] benchmark any assembly implementation against a high-level reference

---

# Current Development Focus

The keyboard plumbing is complete.

M4 has graduated from prototype to useful tool.

M3 has working Git foundations.

M6 is actively being developed as an Elixir networking suite, with concurrency and network checks forming the current foundation.

The next broad phase is:

```text
deepen M6 networking
        +
continue M3 Git tooling
        +
begin M1 / M2 / M5
        +
introduce shared Wren / Prolog / NASM helpers
where they naturally earn a job
```

The long-term target remains delightfully unreasonable:

```text
six keys
six primary languages
twenty-four commands
three shared specialist languages
one keyboard with far too much responsibility
```

---

# License

TBD.

---

> Six keys. Six primary languages. Twenty-four commands. NASM, Wren, and Prolog lurking in `shared/`. One increasingly overqualified keyboard.