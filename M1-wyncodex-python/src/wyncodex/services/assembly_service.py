"""Assembly targets are views over existing entries and tags, not new languages."""
from dataclasses import dataclass
import sqlite3

@dataclass(frozen=True)
class AssemblyTrack:
    id: int
    slug: str
    name: str
    description: str
    syntax_hint: str

TRACKS = (
    AssemblyTrack(0, "all", "All Assembly", "Every entry, including new or unclassified notes. NASM remains searchable.", "text"),
    AssemblyTrack(1, "x86-64", "Shared x86-64 core", "ISA: x86-64 · 64-bit · OS/ABI independent · NASM syntax. Shared by Linux and Windows tracks.", "nasm"),
    AssemblyTrack(2, "linux-x64", "x86-64 · Linux", "ISA: x86-64 · Linux · System V AMD64 functions / Linux syscall ABI · NASM / ELF64.", "nasm"),
    AssemblyTrack(3, "windows-x64", "x86-64 · Windows", "ISA: x86-64 · Windows x64 ABI · NASM / COFF. Includes shared instruction fundamentals.", "nasm"),
    AssemblyTrack(4, "x86-32", "x86-32", "ISA: IA-32 · 32-bit · Linux i386 starter / NASM ELF32. Distinct from Windows x64 and x86-64.", "nasm"),
    AssemblyTrack(5, "cortex-m4", "ARM · Cortex-M4 Thumb", "ISA: Armv7E-M · 32-bit Thumb · STM32F401 context · bare metal / AAPCS32 · GNU unified syntax.", "gas"),
    AssemblyTrack(6, "aarch64", "ARM · AArch64", "ISA: A64 · 64-bit · AAPCS64 integer functions / ELF · GNU syntax. Not Cortex-M Thumb.", "gas"),
    AssemblyTrack(7, "rv32", "RISC-V · RV32", "ISA: RV32I (extensions explicit) · ILP32 integer ABI · GNU syntax. Environment defines system services.", "gas"),
    AssemblyTrack(8, "rv64", "RISC-V · RV64", "ISA: RV64I (extensions explicit) · LP64 integer ABI · GNU syntax. XLEN and load widths matter.", "gas"),
)
TRACK_BY_ID = {track.id: track for track in TRACKS}

class AssemblyService:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def language_id(self):
        row = self._connection.execute("SELECT id FROM languages WHERE slug='nasm'").fetchone()
        return row[0] if row else None

    def entry_ids(self, track_id):
        language_id = self.language_id()
        if track_id in (None, 0):
            return {r[0] for r in self._connection.execute("SELECT id FROM entries WHERE language_id=?", (language_id,))}
        track = TRACK_BY_ID[track_id]
        slugs = ["assembly-track-" + track.slug]
        if track.slug in ("linux-x64", "windows-x64"):
            slugs.append("assembly-track-x86-64")
        marks = ",".join("?" for _ in slugs)
        return {r[0] for r in self._connection.execute(f"""SELECT DISTINCT e.id FROM entries e
            JOIN entry_tags et ON et.entry_id=e.id JOIN tags t ON t.id=et.tag_id
            WHERE e.language_id=? AND t.slug IN ({marks})""", (language_id, *slugs))}

    def filter_entries(self, entries, track_id):
        allowed = self.entry_ids(track_id)
        return [entry for entry in entries if entry.id in allowed]

    def category_ids(self, track_id):
        allowed = self.entry_ids(track_id)
        return {r[1] for r in self._connection.execute("SELECT id,category_id FROM entries WHERE language_id=?", (self.language_id(),)) if r[0] in allowed}

    def syntax_hint(self, entry_id):
        slugs = {r[0] for r in self._connection.execute("SELECT t.slug FROM tags t JOIN entry_tags et ON et.tag_id=t.id WHERE et.entry_id=?", (entry_id,))}
        if "assembly-assembler-nasm" in slugs:
            return "nasm"
        if "assembly-assembler-gas" in slugs:
            return "gas"
        return "text"
