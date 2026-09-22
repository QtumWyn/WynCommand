const std = @import("std");
const project = @import("project.zig");
const project_add = @import("project_add.zig");
const action = @import("action.zig");

const Project = project.Project;
const Action = action.Action;

const PickerItem = struct {
    key: []const u8,
    label: []const u8,
    detail: []const u8,
};

pub const ProjectActionSelection = struct {
    project_index: usize,
    selected_action: Action,
};

pub const PickerError = error{
    InvalidSelection,
    PickerFailed,
    TooManyProjects,
};

fn runPicker(
    qml_path: []const u8,
    heading: []const u8,
    prompt: []const u8,
    items: []const PickerItem,
    inline_actions: bool,
    allow_add_project: bool,
    config_path: ?[]const u8,
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

    if (inline_actions) {
        try argv.append(
            allocator,
            "--wyn-inline-actions=true",
        );
    }

    if (allow_add_project) {
        try argv.append(
            allocator,
            "--wyn-add-project=true",
        );
    }

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
        .{ .argv = argv.items },
    );

    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    var added_project_count: usize = 0;

    if (config_path) |path| {
        added_project_count = try project_add.persistPickerAdditions(
            path,
            result.stdout,
            result.stderr,
            allocator,
            io,
        );
    }

    return switch (result.term) {
        .exited => |code| {
            if (code == 0) {
                return null;
            }

            const selected_index: usize = @intCast(code - 1);
            const project_count = items.len + added_project_count;
            const selection_count = if (inline_actions)
                project_count * 4
            else
                project_count;

            if (selected_index >= selection_count) {
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
        false,
        false,
        null,
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
        false,
        false,
        null,
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

pub fn pickProjectAction(
    projects: []const Project,
    config_path: []const u8,
    qml_path: []const u8,
    allocator: std.mem.Allocator,
    io: std.Io,
) !?ProjectActionSelection {
    const actions = [_]Action{
        .test_project,
        .build,
        .run,
        .debug,
    };

    // The current QML protocol returns the project/action pair in an
    // 8-bit process exit status: 1 + project_index * 4 + action_index.
    if (projects.len > 63) {
        return error.TooManyProjects;
    }

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

    const encoded_selection = try runPicker(
        qml_path,
        "WYNCOMMAND // BUILD",
        "Choose a project, then an action",
        items.items,
        true,
        true,
        config_path,
        allocator,
        io,
    );

    if (encoded_selection) |encoded| {
        const project_index = encoded / actions.len;
        const action_index = encoded % actions.len;

        if (action_index >= actions.len) {
            return error.InvalidSelection;
        }

        return .{
            .project_index = project_index,
            .selected_action = actions[action_index],
        };
    }

    return null;
}
