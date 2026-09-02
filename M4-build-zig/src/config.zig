const std = @import("std");
const project = @import("project.zig");

const ProjectConfig = project.ProjectConfig;

pub const ConfigError = error{
    MissingConfigDirectory,
};

pub fn configPath(
    environ: *const std.process.Environ.Map,
    allocator: std.mem.Allocator,
) (ConfigError || std.mem.Allocator.Error)![]u8 {
    if (environ.get("XDG_CONFIG_HOME")) |xdg_config_home| {
        return std.Io.Dir.path.join(
            allocator,
            &.{
                xdg_config_home,
                "wyncommand",
                "projects.json",
            },
        );
    }

    if (environ.get("HOME")) |home| {
        return std.Io.Dir.path.join(
            allocator,
            &.{
                home,
                ".config",
                "wyncommand",
                "projects.json",
            },
        );
    }

    return error.MissingConfigDirectory;
}

pub fn uiPath(
    environ: *const std.process.Environ.Map,
    allocator: std.mem.Allocator,
) ![]u8 {
    if (environ.get("XDG_DATA_HOME")) |xdg_data_home| {
        return std.Io.Dir.path.join(
            allocator,
            &.{
                xdg_data_home,
                "wyncommand",
                "picker.qml",
            },
        );
    }

    if (environ.get("HOME")) |home| {
        return std.Io.Dir.path.join(
            allocator,
            &.{
                home,
                ".local",
                "share",
                "wyncommand",
                "picker.qml",
            },
        );
    }

    return error.MissingDataDirectory;
}

pub fn loadProjects(
    path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !std.json.Parsed(ProjectConfig) {
    const contents = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
    defer allocator.free(contents);

    const parsed = try std.json.parseFromSlice(
        ProjectConfig,
        allocator,
        contents,
        .{
            .allocate = .alloc_always,
        },
    );

    return parsed;
}

test "loadProjects loads project config" {
    const parsed = try loadProjects(
        "config/projects.json",
        std.testing.allocator,
        std.testing.io,
    );
    defer parsed.deinit();

    const projects = parsed.value.projects;

    try std.testing.expect(projects.len > 0);
    try std.testing.expectEqualStrings(
        "APlus360_Flask",
        projects[0].name,
    );
}