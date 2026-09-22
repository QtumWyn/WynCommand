const std = @import("std");

pub const Language = enum(u8) {
    zig,
    elixir,
    prolog,
    wren,
    assembly,
    rust,
    java,
    scala,
    python,
    shell,
    javascript,
    typescript,
    qml,
    html,
    css,
    c,
    cpp,
    csharp,
    fsharp,
    lua,
    sql,
    kotlin,
    swift,
    go,
    php,
    ruby,
};

// Kept as an alias so the rest of WynCommand can continue using the
// "ProjectType" name while the enum itself now represents the project's
// primary language rather than its build tool.
pub const ProjectType = Language;

pub const all_languages = [_]Language{
    .zig,
    .elixir,
    .prolog,
    .wren,
    .assembly,
    .rust,
    .java,
    .scala,
    .python,
    .shell,
    .javascript,
    .typescript,
    .qml,
    .html,
    .css,
    .c,
    .cpp,
    .csharp,
    .fsharp,
    .lua,
    .sql,
    .kotlin,
    .swift,
    .go,
    .php,
    .ruby,
};

pub const BuildSystem = enum {
    none,
    cargo,
    cargo_leptos,
    zig,
    mix,
    maven,
    gradle_wrapper,
    gradle,
    sbt,
    npm,
    dotnet,
    cmake,
    make,
    swiftpm,
    go,
    python,
    composer,
    bundler,
};

pub const ProjectProfile = struct {
    language: Language,
    build_system: BuildSystem,
};

pub const ProjectConfig = struct {
    projects: []const Project,
};

pub const Project = struct {
    name: []const u8,
    path: []const u8,
    languages: []const []const u8,
};

pub const DetectionError = error{UnknownProject};

pub fn languageLabel(language: Language) []const u8 {
    return switch (language) {
        .zig => "Zig",
        .elixir => "Elixir",
        .prolog => "Prolog",
        .wren => "Wren",
        .assembly => "ASM",
        .rust => "Rust",
        .java => "Java",
        .scala => "Scala",
        .python => "Python",
        .shell => "Shell",
        .javascript => "JavaScript",
        .typescript => "TypeScript",
        .qml => "QML",
        .html => "HTML",
        .css => "CSS",
        .c => "C",
        .cpp => "C++",
        .csharp => "C#",
        .fsharp => "F#",
        .lua => "Lua",
        .sql => "SQL",
        .kotlin => "Kotlin",
        .swift => "Swift",
        .go => "Go",
        .php => "PHP",
        .ruby => "Ruby",
    };
}

pub fn projectTypeLabel(project_type: ProjectType) []const u8 {
    return languageLabel(project_type);
}

pub fn buildSystemLabel(build_system: BuildSystem) []const u8 {
    return switch (build_system) {
        .none => "No safe default",
        .cargo => "Cargo",
        .cargo_leptos => "cargo-leptos",
        .zig => "Zig Build",
        .mix => "Mix",
        .maven => "Maven",
        .gradle_wrapper => "Gradle Wrapper",
        .gradle => "Gradle",
        .sbt => "sbt",
        .npm => "npm",
        .dotnet => ".NET",
        .cmake => "CMake",
        .make => "Make",
        .swiftpm => "SwiftPM",
        .go => "Go",
        .python => "Python",
        .composer => "Composer",
        .bundler => "Bundler/Rake",
    };
}

pub fn profileLabel(profile: ProjectProfile) []const u8 {
    return if (profile.build_system == .cargo_leptos)
        "Rust / Leptos"
    else
        languageLabel(profile.language);
}

// High-confidence root markers only. Languages whose project format is
// ambiguous (C/C++, Kotlin, QML, etc.) are resolved by detect.zig using
// the source scan plus build-system markers.
pub fn markerFor(project_type: ProjectType) DetectionError![]const u8 {
    return switch (project_type) {
        .rust => "Cargo.toml",
        .zig => "build.zig",
        .elixir => "mix.exs",
        .python => "pyproject.toml",
        .java => "pom.xml",
        .scala => "build.sbt",
        .javascript => "package.json",
        .typescript => "tsconfig.json",
        .swift => "Package.swift",
        .go => "go.mod",
        .php => "composer.json",
        .ruby => "Gemfile",
        else => error.UnknownProject,
    };
}

test "all languages have stable labels" {
    try std.testing.expectEqualStrings("Zig", languageLabel(.zig));
    try std.testing.expectEqualStrings("Prolog", languageLabel(.prolog));
    try std.testing.expectEqualStrings("C++", languageLabel(.cpp));
    try std.testing.expectEqualStrings("F#", languageLabel(.fsharp));
    try std.testing.expectEqualStrings("Ruby", languageLabel(.ruby));
}

test "markerFor returns Cargo.toml for Rust" {
    try std.testing.expectEqualStrings(
        "Cargo.toml",
        try markerFor(.rust),
    );
}

test "markerFor returns package.json for JavaScript" {
    try std.testing.expectEqualStrings(
        "package.json",
        try markerFor(.javascript),
    );
}

test "markerFor rejects source-only project types" {
    try std.testing.expectError(
        error.UnknownProject,
        markerFor(.assembly),
    );
}

test "Can parse json and build associated ProjectConfig and Project structs" {
    const json =
        \\{
        \\  "projects": [
        \\    {
        \\      "name": "TestProject",
        \\      "path": "/tmp/test",
        \\      "languages": ["Zig", "Lua"]
        \\    }
        \\  ]
        \\}
    ;

    const parsed = try std.json.parseFromSlice(
        ProjectConfig,
        std.testing.allocator,
        json,
        .{},
    );
    defer parsed.deinit();

    const projects = parsed.value.projects;

    try std.testing.expectEqual(@as(usize, 1), projects.len);
    try std.testing.expectEqualStrings("TestProject", projects[0].name);
    try std.testing.expectEqualStrings("/tmp/test", projects[0].path);

    try std.testing.expectEqual(@as(usize, 2), projects[0].languages.len);
    try std.testing.expectEqualStrings("Zig", projects[0].languages[0]);
    try std.testing.expectEqualStrings("Lua", projects[0].languages[1]);
}
