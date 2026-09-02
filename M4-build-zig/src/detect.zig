const std = @import("std");
const project = @import("project.zig");

const ProjectType = project.ProjectType;

pub fn detectProjectType(
    path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !ProjectType {
    if (try markerExists(
        path,
        try project.markerFor(.rust),
        allocator,
        io
    )) {
        return .rust;
    }
    if (try markerExists(
        path,
        try project.markerFor(.zig),
        allocator,
        io
    )) {
        return .zig;
    }
    if (try markerExists(
        path,
        try project.markerFor(.python),
        allocator,
        io
    )) {
        return .python;
    }
    if (try markerExists(
        path,
        try project.markerFor(.java),
        allocator,
        io
    )) {
        return .java;
    }
    if (try markerExists(
        path,
        try project.markerFor(.node),
        allocator,
        io
    )) {
        return .node;
    }

    return error.UnknownProject;
}

fn markerExists(
    project_path: []const u8,
    marker: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !bool {
    const full_path = try std.Io.Dir.path.join(
        allocator,
        &.{project_path, marker},
    );
    defer allocator.free(full_path);

    std.Io.Dir.cwd().access(io, full_path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

test "detects DevDoctor as Zig" {
    const detected = try detectProjectType(
        "/home/qtummechanic/ZigProjects/DevDoctor",
        std.testing.allocator,
        std.testing.io,
    );

    try std.testing.expectEqual(
        ProjectType.zig,
        detected,
    );
}

test "detects Jnimbus-to-sheets as Rust" {
    const detected = try detectProjectType(
        "/home/qtummechanic/RustroverProjects/jnimbus-to-sheets",
        std.testing.allocator,
        std.testing.io,
    );

    try std.testing.expectEqual(
        ProjectType.rust,
        detected,
    );
}