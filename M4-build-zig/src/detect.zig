const std = @import("std");
const project = @import("project.zig");
const language_scan = @import("language_scan.zig");

const BuildSystem = project.BuildSystem;
const Language = project.Language;
const ProjectProfile = project.ProjectProfile;
const ProjectType = project.ProjectType;

pub fn detectProject(
    path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !ProjectProfile {
    // Framework-specific checks must happen before the generic language
    // marker. A Leptos project is still Rust, but its correct dev/build
    // entrypoint is cargo-leptos rather than ordinary `cargo run`.
    if (try markerExists(path, "Cargo.toml", allocator, io)) {
        if (try isCargoLeptosProject(path, allocator, io)) {
            return .{
                .language = .rust,
                .build_system = .cargo_leptos,
            };
        }

        return .{
            .language = .rust,
            .build_system = .cargo,
        };
    }

    if (try markerExists(path, "build.zig", allocator, io)) {
        return .{ .language = .zig, .build_system = .zig };
    }

    if (try markerExists(path, "mix.exs", allocator, io)) {
        return .{ .language = .elixir, .build_system = .mix };
    }

    if (try markerExists(path, "pom.xml", allocator, io)) {
        return .{ .language = .java, .build_system = .maven };
    }

    if (try markerExists(path, "build.sbt", allocator, io)) {
        return .{ .language = .scala, .build_system = .sbt };
    }

    if (try markerExists(path, "Package.swift", allocator, io)) {
        return .{ .language = .swift, .build_system = .swiftpm };
    }

    if (try markerExists(path, "go.mod", allocator, io)) {
        return .{ .language = .go, .build_system = .go };
    }

    if ((try markerExists(path, "pyproject.toml", allocator, io)) or
        (try markerExists(path, "requirements.txt", allocator, io)) or
        (try markerExists(path, "Pipfile", allocator, io)))
    {
        return .{ .language = .python, .build_system = .python };
    }

    if (try markerExists(path, "tsconfig.json", allocator, io)) {
        const build_system: BuildSystem =
            if (try markerExists(path, "package.json", allocator, io))
                .npm
            else
                .none;

        return .{
            .language = .typescript,
            .build_system = build_system,
        };
    }

    if (try markerExists(path, "package.json", allocator, io)) {
        return .{
            .language = .javascript,
            .build_system = .npm,
        };
    }

    if (try markerExists(path, "composer.json", allocator, io)) {
        return .{ .language = .php, .build_system = .composer };
    }

    if (try markerExists(path, "Gemfile", allocator, io)) {
        return .{ .language = .ruby, .build_system = .bundler };
    }

    const languages = try language_scan.scanLanguages(
        path,
        allocator,
        io,
    );
    defer allocator.free(languages);

    if (languages.len == 0) {
        return error.UnknownProject;
    }

    const has_gradle_wrapper =
        try markerExists(path, "gradlew", allocator, io);

    const has_gradle =
        has_gradle_wrapper or
        (try markerExists(path, "build.gradle", allocator, io)) or
        (try markerExists(path, "build.gradle.kts", allocator, io));

    const gradle_system: BuildSystem =
        if (has_gradle_wrapper) .gradle_wrapper else .gradle;

    if (containsLanguage(languages, .kotlin) and has_gradle) {
        return .{ .language = .kotlin, .build_system = gradle_system };
    }

    if (containsLanguage(languages, .java) and has_gradle) {
        return .{ .language = .java, .build_system = gradle_system };
    }

    if (containsLanguage(languages, .scala) and has_gradle) {
        return .{ .language = .scala, .build_system = gradle_system };
    }

    if (containsLanguage(languages, .csharp)) {
        const has_project =
            (try matchingRootFileExists(path, "*.csproj", allocator, io)) or
            (try matchingRootFileExists(path, "*.sln", allocator, io)) or
            (try matchingRootFileExists(path, "*.slnx", allocator, io));

        return .{
            .language = .csharp,
            .build_system = if (has_project) .dotnet else .none,
        };
    }

    if (containsLanguage(languages, .fsharp)) {
        const has_project =
            (try matchingRootFileExists(path, "*.fsproj", allocator, io)) or
            (try matchingRootFileExists(path, "*.sln", allocator, io)) or
            (try matchingRootFileExists(path, "*.slnx", allocator, io));

        return .{
            .language = .fsharp,
            .build_system = if (has_project) .dotnet else .none,
        };
    }

    if (containsLanguage(languages, .cpp)) {
        if (try markerExists(path, "CMakeLists.txt", allocator, io)) {
            return .{ .language = .cpp, .build_system = .cmake };
        }

        if (try markerExists(path, "Makefile", allocator, io)) {
            return .{ .language = .cpp, .build_system = .make };
        }

        return .{ .language = .cpp, .build_system = .none };
    }

    if (containsLanguage(languages, .c)) {
        if (try markerExists(path, "CMakeLists.txt", allocator, io)) {
            return .{ .language = .c, .build_system = .cmake };
        }

        if (try markerExists(path, "Makefile", allocator, io)) {
            return .{ .language = .c, .build_system = .make };
        }

        return .{ .language = .c, .build_system = .none };
    }

    // For source-only/script projects, recognition and execution are kept
    // separate. We can identify the language without guessing an entrypoint,
    // database, assembler format, linker target, or framework.
    for (project.all_languages) |language| {
        if (containsLanguage(languages, language)) {
            return .{
                .language = language,
                .build_system = .none,
            };
        }
    }

    return error.UnknownProject;
}

// Compatibility helper for callers/tests that only care about the primary
// language. New execution code should use detectProject() so it also gets
// the build-system/framework information.
pub fn detectProjectType(
    path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !ProjectType {
    const profile = try detectProject(path, allocator, io);
    return profile.language;
}

fn containsLanguage(
    languages: []const []const u8,
    wanted: Language,
) bool {
    const wanted_label = project.languageLabel(wanted);

    for (languages) |language| {
        if (std.mem.eql(u8, language, wanted_label)) {
            return true;
        }
    }

    return false;
}

fn markerExists(
    project_path: []const u8,
    marker: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !bool {
    const full_path = try std.Io.Dir.path.join(
        allocator,
        &.{ project_path, marker },
    );
    defer allocator.free(full_path);

    std.Io.Dir.cwd().access(io, full_path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };

    return true;
}

fn matchingRootFileExists(
    project_path: []const u8,
    pattern: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !bool {
    const argv = [_][]const u8{
        "find",
        project_path,
        "-maxdepth",
        "1",
        "-type",
        "f",
        "-name",
        pattern,
        "-print",
        "-quit",
    };

    const result = try std.process.run(
        allocator,
        io,
        .{ .argv = &argv },
    );
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    return switch (result.term) {
        .exited => |code| code == 0 and
            std.mem.trim(u8, result.stdout, " \t\r\n").len > 0,
        else => false,
    };
}

fn isCargoLeptosProject(
    project_path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !bool {
    const cargo_path = try std.Io.Dir.path.join(
        allocator,
        &.{ project_path, "Cargo.toml" },
    );
    defer allocator.free(cargo_path);

    const contents = std.Io.Dir.cwd().readFileAlloc(
        io,
        cargo_path,
        allocator,
        .limited(1024 * 1024),
    ) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    defer allocator.free(contents);

    // cargo-leptos' supported configuration is declared through Cargo
    // metadata. Deliberately do not classify a crate as cargo-leptos merely
    // because it depends on `leptos`; libraries can use Leptos without being
    // runnable cargo-leptos applications.
    return std.mem.indexOf(
        u8,
        contents,
        "[package.metadata.leptos]",
    ) != null or
        std.mem.indexOf(
            u8,
            contents,
            "[[workspace.metadata.leptos]]",
        ) != null or
        std.mem.indexOf(
            u8,
            contents,
            "[workspace.metadata.leptos]",
        ) != null;
}

test "containsLanguage matches canonical labels" {
    const languages = [_][]const u8{
        "Rust",
        "HTML",
        "CSS",
    };

    try std.testing.expect(containsLanguage(&languages, .rust));
    try std.testing.expect(containsLanguage(&languages, .html));
    try std.testing.expect(!containsLanguage(&languages, .go));
}
