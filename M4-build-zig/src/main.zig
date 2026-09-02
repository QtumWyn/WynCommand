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
                , .{args[1]});

            return;
        }
    else
        null;

    const projects_path = try config.configPath(
        init.environ_map,
        allocator,
    );
    defer allocator.free(projects_path);

    const project_config = try config.loadProjects(
        projects_path,
        allocator,
        io,
    );
    defer project_config.deinit();

    const selected = try picker.pickProject(
        project_config.value.projects,
        qml_path,
        allocator,
        io,
    );

    const selected_project = selected orelse return;

    const selected_action: Action = if (requested_action) |requested|
        requested
    else
        (try picker.pickAction(
            qml_path,
            allocator,
            io,
        )) orelse return;

    const project_type = try detect.detectProjectType(
        selected_project.path,
        allocator,
        io,
    );

    try runner.runProject(
        selected_project,
        project_type,
        selected_action,
        allocator,
        io,
    );
}