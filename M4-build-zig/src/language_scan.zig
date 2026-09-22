const std = @import("std");
const project = @import("project.zig");

pub const ScanError = error{
    ScanFailed,
};

const Language = project.Language;

fn mark(found: *[@typeInfo(Language).@"enum".fields.len]bool, language: Language) void {
    found[@intFromEnum(language)] = true;
}

fn inspectPath(
    found: *[@typeInfo(Language).@"enum".fields.len]bool,
    file_path: []const u8,
) void {
    const basename = std.Io.Dir.path.basename(file_path);

    // Project markers catch languages even when a tiny project contains
    // little or no source yet.
    if (std.mem.eql(u8, basename, "build.zig")) mark(found, .zig);
    if (std.mem.eql(u8, basename, "mix.exs")) mark(found, .elixir);
    if (std.mem.eql(u8, basename, "Cargo.toml")) mark(found, .rust);
    if (std.mem.eql(u8, basename, "pom.xml")) mark(found, .java);
    if (std.mem.eql(u8, basename, "build.sbt")) mark(found, .scala);

    if (std.mem.eql(u8, basename, "pyproject.toml") or
        std.mem.eql(u8, basename, "requirements.txt") or
        std.mem.eql(u8, basename, "Pipfile") or
        std.mem.eql(u8, basename, "setup.py"))
    {
        mark(found, .python);
    }

    if (std.mem.eql(u8, basename, "package.json")) mark(found, .javascript);
    if (std.mem.eql(u8, basename, "tsconfig.json")) mark(found, .typescript);
    if (std.mem.eql(u8, basename, "Package.swift")) mark(found, .swift);
    if (std.mem.eql(u8, basename, "go.mod")) mark(found, .go);
    if (std.mem.eql(u8, basename, "composer.json")) mark(found, .php);
    if (std.mem.eql(u8, basename, "Gemfile") or
        std.mem.eql(u8, basename, "Rakefile"))
    {
        mark(found, .ruby);
    }

    if (std.mem.eql(u8, basename, "qmldir")) mark(found, .qml);
    if (std.mem.eql(u8, basename, "pack.pl")) mark(found, .prolog);

    const ext = std.Io.Dir.path.extension(basename);

    if (std.mem.eql(u8, ext, ".zig")) return mark(found, .zig);
    if (std.mem.eql(u8, ext, ".ex") or std.mem.eql(u8, ext, ".exs")) return mark(found, .elixir);
    if (std.mem.eql(u8, ext, ".prolog") or std.mem.eql(u8, ext, ".pl")) return mark(found, .prolog);
    if (std.mem.eql(u8, ext, ".wren")) return mark(found, .wren);
    if (std.mem.eql(u8, ext, ".asm") or std.mem.eql(u8, ext, ".s") or std.mem.eql(u8, ext, ".S")) return mark(found, .assembly);
    if (std.mem.eql(u8, ext, ".rs")) return mark(found, .rust);
    if (std.mem.eql(u8, ext, ".java")) return mark(found, .java);
    if (std.mem.eql(u8, ext, ".scala") or std.mem.eql(u8, ext, ".sc")) return mark(found, .scala);
    if (std.mem.eql(u8, ext, ".py") or std.mem.eql(u8, ext, ".pyw")) return mark(found, .python);
    if (std.mem.eql(u8, ext, ".sh") or std.mem.eql(u8, ext, ".bash") or std.mem.eql(u8, ext, ".zsh")) return mark(found, .shell);
    if (std.mem.eql(u8, ext, ".js") or std.mem.eql(u8, ext, ".jsx") or std.mem.eql(u8, ext, ".mjs") or std.mem.eql(u8, ext, ".cjs")) return mark(found, .javascript);
    if (std.mem.eql(u8, ext, ".ts") or std.mem.eql(u8, ext, ".tsx") or std.mem.eql(u8, ext, ".mts") or std.mem.eql(u8, ext, ".cts")) return mark(found, .typescript);
    if (std.mem.eql(u8, ext, ".qml") or std.mem.eql(u8, ext, ".qmlproject")) return mark(found, .qml);
    if (std.mem.eql(u8, ext, ".html") or std.mem.eql(u8, ext, ".htm")) return mark(found, .html);
    if (std.mem.eql(u8, ext, ".css") or std.mem.eql(u8, ext, ".scss") or std.mem.eql(u8, ext, ".sass")) return mark(found, .css);
    if (std.mem.eql(u8, ext, ".c")) return mark(found, .c);
    if (std.mem.eql(u8, ext, ".h")) return mark(found, .c);
    if (std.mem.eql(u8, ext, ".cpp") or std.mem.eql(u8, ext, ".cc") or std.mem.eql(u8, ext, ".cxx") or std.mem.eql(u8, ext, ".hpp") or std.mem.eql(u8, ext, ".hh") or std.mem.eql(u8, ext, ".hxx")) return mark(found, .cpp);
    if (std.mem.eql(u8, ext, ".cs") or std.mem.eql(u8, ext, ".csproj")) return mark(found, .csharp);
    if (std.mem.eql(u8, ext, ".fs") or std.mem.eql(u8, ext, ".fsx") or std.mem.eql(u8, ext, ".fsproj")) return mark(found, .fsharp);
    if (std.mem.eql(u8, ext, ".lua")) return mark(found, .lua);
    if (std.mem.eql(u8, ext, ".sql")) return mark(found, .sql);
    if (std.mem.eql(u8, ext, ".kt") or std.mem.eql(u8, ext, ".kts")) return mark(found, .kotlin);
    if (std.mem.eql(u8, ext, ".swift")) return mark(found, .swift);
    if (std.mem.eql(u8, ext, ".go")) return mark(found, .go);
    if (std.mem.eql(u8, ext, ".php") or std.mem.eql(u8, ext, ".phtml")) return mark(found, .php);
    if (std.mem.eql(u8, ext, ".rb") or std.mem.eql(u8, ext, ".rake")) return mark(found, .ruby);
}

pub fn scanLanguages(
    project_path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) ![]const []const u8 {
    // M4 is currently a KDE/Linux macro, so using `find` here keeps the
    // recursive scan tiny and lets Zig focus on classification. We prune
    // dependency/build directories before find descends into them.
    const argv = [_][]const u8{
        "find",
        project_path,
        "(",
        "-name",
        ".git",
        "-o",
        "-name",
        "target",
        "-o",
        "-name",
        "_build",
        "-o",
        "-name",
        "deps",
        "-o",
        "-name",
        "node_modules",
        "-o",
        "-name",
        "zig-out",
        "-o",
        "-name",
        ".zig-cache",
        "-o",
        "-name",
        ".idea",
        "-o",
        "-name",
        ".venv",
        "-o",
        "-name",
        "venv",
        "-o",
        "-name",
        "dist",
        "-o",
        "-name",
        "build",
        ")",
        "-prune",
        "-o",
        "-type",
        "f",
        "-print0",
    };

    const result = try std.process.run(
        allocator,
        io,
        .{ .argv = &argv },
    );
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| if (code != 0) return error.ScanFailed,
        else => return error.ScanFailed,
    }

    const language_count = @typeInfo(Language).@"enum".fields.len;
    var found = [_]bool{false} ** language_count;

    var paths = std.mem.splitScalar(u8, result.stdout, 0);
    while (paths.next()) |file_path| {
        if (file_path.len == 0) continue;
        inspectPath(&found, file_path);
    }

    var languages: std.ArrayList([]const u8) = .empty;
    errdefer languages.deinit(allocator);

    for (project.all_languages) |language| {
        if (found[@intFromEnum(language)]) {
            try languages.append(
                allocator,
                project.languageLabel(language),
            );
        }
    }

    return try languages.toOwnedSlice(allocator);
}

test "detects languages from file names" {
    const language_count = @typeInfo(Language).@"enum".fields.len;
    var found = [_]bool{false} ** language_count;

    inspectPath(&found, "/tmp/project/lib/app.ex");
    inspectPath(&found, "/tmp/project/scripts/check.prolog");
    inspectPath(&found, "/tmp/project/ui/picker.qml");
    inspectPath(&found, "/tmp/project/App.csproj");
    inspectPath(&found, "/tmp/project/Package.swift");

    try std.testing.expect(found[@intFromEnum(Language.elixir)]);
    try std.testing.expect(found[@intFromEnum(Language.prolog)]);
    try std.testing.expect(found[@intFromEnum(Language.qml)]);
    try std.testing.expect(found[@intFromEnum(Language.csharp)]);
    try std.testing.expect(found[@intFromEnum(Language.swift)]);
    try std.testing.expect(!found[@intFromEnum(Language.rust)]);
}
