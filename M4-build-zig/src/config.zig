const std = @import("std");
const project = @import("project.zig");

const ProjectConfig = project.ProjectConfig;
const Project = project.Project;

pub const ConfigError = error{
    MissingConfigDirectory,
    ProjectAlreadyExists,
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

pub fn appendProject(
    path: []const u8,
    new_project: Project,
    allocator: std.mem.Allocator,
    io: std.Io,
) !void {
    const parsed = try loadProjects(
        path,
        allocator,
        io,
    );
    defer parsed.deinit();

    for (parsed.value.projects) |existing| {
        if (std.mem.eql(
            u8,
            existing.path,
            new_project.path,
        )) {
            return error.ProjectAlreadyExists;
        }
    }

    const projects = try allocator.alloc(
        Project,
        parsed.value.projects.len + 1,
    );
    defer allocator.free(projects);

    @memcpy(
        projects[0..parsed.value.projects.len],
        parsed.value.projects,
    );

    projects[projects.len - 1] = new_project;

    const updated = ProjectConfig{
        .projects = projects,
    };

    var output: std.Io.Writer.Allocating =
        .init(allocator);
    defer output.deinit();

    try std.json.Stringify.value(
        updated,
        .{
            .whitespace = .indent_2,
        },
        &output.writer,
    );

    try std.Io.Dir.cwd().writeFile(
        io,
        .{
            .sub_path = path,
            .data = output.written(),
        },
    );
}

test "loadProjects loads project config" {
    const parsed = try loadProjects(
        "testdata/projects.json",
        std.testing.allocator,
        std.testing.io,
    );
    defer parsed.deinit();

    const projects = parsed.value.projects;

    try std.testing.expectEqual(
        @as(usize, 1),
        projects.len,
    );

    try std.testing.expectEqualStrings(
        "TestProject",
        projects[0].name,
    );

    try std.testing.expectEqualStrings(
        "/tmp/test-project",
        projects[0].path,
    );

    try std.testing.expectEqual(
        @as(usize, 2),
        projects[0].languages.len,
    );

    try std.testing.expectEqualStrings(
        "Zig",
        projects[0].languages[0],
    );

    try std.testing.expectEqualStrings(
        "Elixir",
        projects[0].languages[1],
    );
}
