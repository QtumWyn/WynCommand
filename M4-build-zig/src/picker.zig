const std = @import("std");
const project = @import("project.zig");
const config = @import("config.zig");
const action = @import("action.zig");

const Project = project.Project;
const Action = action.Action;

const PickerItem = struct {
    key: []const u8,
    label: []const u8,
    detail: []const u8,
};

pub const PickerError = error{
    InvalidSelection,
    PickerFailed,
};

fn runPicker(
    qml_path: []const u8,
    heading: []const u8,
    prompt: []const u8,
    items: []const PickerItem,
    allocator: std.mem.Allocator,
    io: std.Io,
) !?usize {
    var argv: std.ArrayList([]const u8) = .empty;
    defer argv.deinit(allocator);

    var owned_args: std.ArrayList([]u8) = .empty;

    defer {
        for (owned_args.items) |arg| {
            allocator.free(arg);
        }

        owned_args.deinit(allocator);
    }

    try argv.append(allocator, "qml6");
    try argv.append(allocator, qml_path);
    try argv.append(allocator, "--");

    {
        const heading_arg = try std.fmt.allocPrint(
            allocator,
            "--wyn-heading={s}",
            .{heading},
        );
        errdefer allocator.free(heading_arg);

        try argv.append(allocator, heading_arg);
        try owned_args.append(allocator, heading_arg);
    }

    {
        const prompt_arg = try std.fmt.allocPrint(
            allocator,
            "--wyn-prompt={s}",
            .{prompt},
        );
        errdefer allocator.free(prompt_arg);

        try argv.append(allocator, prompt_arg);
        try owned_args.append(allocator, prompt_arg);
    }

    for (items) |item| {
        const arg = try std.fmt.allocPrint(
            allocator,
            "--wyn-item={s}\t{s}\t{s}",
            .{
                item.key,
                item.label,
                item.detail,
            },
        );
        errdefer allocator.free(arg);

        try argv.append(allocator, arg);
        try owned_args.append(allocator, arg);
    }

    const result = try std.process.run(
        allocator,
        io,
        .{
            .argv = argv.items,
        },
    );

    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    return switch (result.term) {
        .exited => |code| {
            if (code == 0) {
                return null;
            }

            const selected_index: usize = @intCast(code - 1);

            if (selected_index >= items.len) {
                return error.InvalidSelection;
            }

            return selected_index;
        },

        else => error.PickerFailed,
    };
}

pub fn pickProject(
    projects: []const Project,
    qml_path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !?Project {
    var items: std.ArrayList(PickerItem) = .empty;
    defer items.deinit(allocator);

    var owned_details: std.ArrayList([]u8) = .empty;

    defer {
        for (owned_details.items) |detail| {
            allocator.free(detail);
        }

        owned_details.deinit(allocator);
    }

    for (projects) |proj| {
        const language_text = try std.mem.join(
            allocator,
            " • ",
            proj.languages,
        );
        errdefer allocator.free(language_text);

        try items.append(
            allocator,
            .{
                .key = proj.path,
                .label = proj.name,
                .detail = language_text,
            },
        );

        try owned_details.append(
            allocator,
            language_text,
        );
    }

    const selected_index = try runPicker(
        qml_path,
        "WYNCOMMAND // BUILD",
        "Choose a project",
        items.items,
        allocator,
        io,
    );

    if (selected_index) |index| {
        return projects[index];
    }

    return null;
}

pub fn pickAction(
    qml_path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !?Action {
    const items = [_]PickerItem{
        .{
            .key = "test",
            .label = "Test",
            .detail = "SUMMON THE TEST SUITE",
        },
        .{
            .key = "build",
            .label = "Build",
            .detail = "FORGE THE ARTIFACT",
        },
        .{
            .key = "run",
            .label = "Run",
            .detail = "AWAKEN THE PROGRAM",
        },
        .{
            .key = "debug",
            .label = "Debug",
            .detail = "ENTER THE CATACOMBS",
        },
    };

    const selected_index = try runPicker(
        qml_path,
        "WYNCOMMAND // BUILD",
        "Choose an action  :3",
        &items,
        allocator,
        io,
    );

    if (selected_index) |index| {
        return try action.parseAction(
            items[index].key,
        );
    }

    return null;
}

test "captures child process stdout" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    const result = try std.process.run(
        allocator,
        io,
        .{
            .argv = &.{
                "kdialog",
                "--title",
                "WynCommand",
                "--menu",
                "Select Project",

                "devdoctor",
                "DevDoctor — Zig, Lua",

                "aplus360",
                "APlus360_Flask — React, Flask",
            },
        },
    );

    const selected = std.mem.trim(
        u8,
        result.stdout,
        " \t\r\n",
    );

    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqualStrings(
        "devdoctor",
        selected,
    );
}

test "pickProject returns selected project path" {
    const parsed = try config.loadProjects(
        "config/projects.json",
        std.testing.allocator,
        std.testing.io,
    );
    defer parsed.deinit();

    const selected = try pickProject(
        parsed.value.projects,
        std.testing.allocator,
        std.testing.io,
    );
    defer if (selected) |path| {
        std.testing.allocator.free(path);
    };

    if (selected) |path| {
        std.debug.print("Selected: {s}\n", .{path});
    }
}