const std = @import("std");

pub const ProjectType = enum {
    rust,
    zig,
    python,
    java,
    fsharp,
    node,
};

pub const ProjectConfig = struct {
    projects: []const Project,
};

pub const Project = struct {
    name: []const u8,
    path: []const u8,
    languages: []const []const u8
};

pub const DetectionError = error {
    UnknownProject
};

pub fn projectTypeLabel(project_type: ProjectType) []const u8 {
    return switch (project_type) {
        .rust => "Rust",
        .zig => "Zig",
        .python => "Python",
        .java => "Java",
        .fsharp => "F#",
        .node => "Node",
    };
}

pub fn markerFor(project_type: ProjectType) DetectionError![]const u8 {
    return switch (project_type) {
        .rust => "Cargo.toml",
        .zig => "build.zig",
        .python => "pyproject.toml",
        .java => "pom.xml",
        .node => "package.json",
        .fsharp => error.UnknownProject,
    };
}

test "markerFor returns build.zig for Zig" {
    const project = try markerFor(.zig);

    try std.testing.expectEqualStrings("build.zig", project);
}

test "markerFor returns pyproject.toml for Python" {
    const project = try markerFor(.python);

    try std.testing.expectEqualStrings("pyproject.toml", project);
}

test "markerFor returns pom.xml for Java" {
    const project = try markerFor(.java);

    try std.testing.expectEqualStrings("pom.xml", project);
}

test "markerFor returns package.json for Node" {
    const project = try markerFor(.node);

    try std.testing.expectEqualStrings("package.json", project);
}

test "markerFor returns Cargo.toml for Rust" {
    const project = try markerFor(.rust);

    try std.testing.expectEqualStrings("Cargo.toml", project);
}

test "markerFor returns UnknownProject for unknown project type" {
    try std.testing.expectError(
        error.UnknownProject,
        markerFor(.fsharp)
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