const std = @import("std");
const action = @import("action.zig");
const config = @import("config.zig");
const detect = @import("detect.zig");
const picker = @import("picker.zig");
const runner = @import("runner.zig");

const Action = action.Action;

pub fn main(init: std.process.Init) !void {
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const io = init.io;
    const allocator = init.gpa;

    const qml_path = try config.uiPath(
        init.environ_map,
        allocator,
    );
    defer allocator.free(qml_path);

    const requested_action: ?Action = if (args.len >= 2)
        action.parseAction(args[1]) catch {
            std.debug.print(
                \\
                \\ Could not find selected action: {s}.
                \\ Accepted Actions:
                \\   test
                \\   build
                \\   run
                \\   debug
                \\
            ,
                .{args[1]},
            );

            return;
        }
    else
        null;

    const projects_path = try config.configPath(
        init.environ_map,
        allocator,
    );
    defer allocator.free(projects_path);

    // If the caller already supplied an action (for example
    // `wyn-build test`), preserve the fast path: choose only a project.
    if (requested_action) |requested| {
        const project_config = try config.loadProjects(
            projects_path,
            allocator,
            io,
        );
        defer project_config.deinit();

        const selected_project = (try picker.pickProject(
            project_config.value.projects,
            qml_path,
            allocator,
            io,
        )) orelse return;

        const project_profile = try detect.detectProject(
            selected_project.path,
            allocator,
            io,
        );

        try runner.runProject(
            selected_project,
            project_profile,
            requested,
            allocator,
            io,
        );

        return;
    }

    // Normal M4 flow: one QML session handles project selection,
    // inline actions, and the Add Project editor. New projects are
    // persisted when qml6 finally exits.
    var project_index: usize = undefined;
    var selected_action: Action = undefined;

    {
        const project_config = try config.loadProjects(
            projects_path,
            allocator,
            io,
        );
        defer project_config.deinit();

        const selection = (try picker.pickProjectAction(
            project_config.value.projects,
            projects_path,
            qml_path,
            allocator,
            io,
        )) orelse return;

        project_index = selection.project_index;
        selected_action = selection.selected_action;
    }

    // Reload because the user may have created one or more projects
    // while the picker remained open.
    const refreshed_config = try config.loadProjects(
        projects_path,
        allocator,
        io,
    );
    defer refreshed_config.deinit();

    if (project_index >= refreshed_config.value.projects.len) {
        return error.InvalidSelection;
    }

    const selected_project =
        refreshed_config.value.projects[project_index];

    const project_profile = try detect.detectProject(
        selected_project.path,
        allocator,
        io,
    );

    try runner.runProject(
        selected_project,
        project_profile,
        selected_action,
        allocator,
        io,
    );
}
