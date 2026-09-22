const std = @import("std");
const config = @import("config.zig");
const project = @import("project.zig");

const Project = project.Project;

const PendingProject = struct {
    name: []const u8,
    path: []const u8,
    languages: []const []const u8,
};

const record_prefix = "__WYN_ADD_PROJECT__";

fn persistBuffer(
    config_path: []const u8,
    buffer: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !usize {
    var persisted: usize = 0;
    var lines = std.mem.splitScalar(u8, buffer, '\n');

    while (lines.next()) |line| {
        const marker_index = std.mem.indexOf(
            u8,
            line,
            record_prefix,
        ) orelse continue;

        const json_start = marker_index + record_prefix.len;
        const json_text = std.mem.trim(
            u8,
            line[json_start..],
            " \t\r\n",
        );

        if (json_text.len == 0) continue;

        const parsed = try std.json.parseFromSlice(
            PendingProject,
            allocator,
            json_text,
            .{ .allocate = .alloc_always },
        );
        defer parsed.deinit();

        const pending = parsed.value;

        if (std.mem.trim(u8, pending.name, " \t\r\n").len == 0)
            continue;

        if (std.mem.trim(u8, pending.path, " \t\r\n").len == 0)
            continue;

        if (pending.languages.len == 0)
            continue;

        const new_project = Project{
            .name = pending.name,
            .path = pending.path,
            .languages = pending.languages,
        };

        config.appendProject(
            config_path,
            new_project,
            allocator,
            io,
        ) catch |err| switch (err) {
            // The QML editor already blocks duplicate paths. This also
            // makes the output protocol safely idempotent if a line is
            // ever duplicated by the QML runtime.
            error.ProjectAlreadyExists => continue,
            else => return err,
        };

        persisted += 1;
    }

    return persisted;
}

pub fn persistPickerAdditions(
    config_path: []const u8,
    stdout: []const u8,
    stderr: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !usize {
    const from_stdout = try persistBuffer(
        config_path,
        stdout,
        allocator,
        io,
    );

    const from_stderr = try persistBuffer(
        config_path,
        stderr,
        allocator,
        io,
    );

    return from_stdout + from_stderr;
}
