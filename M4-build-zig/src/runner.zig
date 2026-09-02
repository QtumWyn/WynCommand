const std = @import("std");
const action = @import("action.zig");
const project = @import("project.zig");

const Project = project.Project;
const Action = action.Action;
const ProjectType = project.ProjectType;

pub const RunnerError = error{
    UnsupportedProjectType,
    UnsupportedAction,
};

pub fn commandFor(
    project_type: ProjectType,
    selected_action: Action,
) RunnerError![]const []const u8 {
    return switch (project_type) {
        .zig => switch (selected_action) {
            .test_project => &.{ "zig", "build", "test" },
            .build => &.{ "zig", "build" },
            .run => &.{ "zig", "build", "run" },
            .debug => error.UnsupportedAction,
        },

        .rust => switch (selected_action) {
            .test_project => &.{ "cargo", "test" },
            .build => &.{ "cargo", "build" },
            .run => &.{ "cargo", "run" },
            .debug => error.UnsupportedAction,
        },

        else => error.UnsupportedProjectType,
    };
}

pub fn runProject(
    selected_project: Project,
    project_type: ProjectType,
    selected_action: Action,
    allocator: std.mem.Allocator,
    io: std.Io,
) !void {
    const command = try commandFor(
        project_type,
        selected_action,
    );
    const command_text = try std.mem.join(
        allocator,
        " ",
        command,
    );
    defer allocator.free(command_text);

    const shell_script =
        \\project="$1"
        \\ptype="$2"
        \\action="$3"
        \\command_text="$4"
        \\shift 4
        \\
        \\printf '\033[38;2;245;169;200m'
        \\printf '╔═ WYNCOMMAND // EXECUTION ═════════════════════════════╗\n'
        \\printf '\033[0m'
        \\printf '║ \033[38;2;142;216;248mProject\033[0m  %s\n' "$project"
        \\printf '║ \033[38;2;245;169;200mType\033[0m     %s\n' "$ptype"
        \\printf '║ \033[38;2;142;216;248mAction\033[0m   %s\n' "$action"
        \\printf '║ \033[38;2;245;169;200mCommand\033[0m  %s\n' "$command_text"
        \\printf '\033[38;2;141;106;168m'
        \\printf '╚═══════════════════════════════════════════════════════╝\n'
        \\printf '\033[0m\n'
        \\
        \\"$@"
        \\status=$?
        \\
        \\printf '\n'
        \\
        \\if [ "$status" -eq 0 ]; then
        \\    printf '\033[38;2;142;216;248m✦ SUCCESS\033[0m  command completed :3\n'
        \\else
        \\    printf '\033[38;2;245;169;200m✦ FAILURE\033[0m  exit code %s\n' "$status"
        \\fi
        \\
        \\exit "$status"
    ;

    var argv: std.ArrayList([]const u8) = .empty;
    defer argv.deinit(allocator);

    try argv.append(allocator, "konsole");
    try argv.append(allocator, "--hold");

    try argv.append(allocator, "--workdir");
    try argv.append(allocator, selected_project.path);

    try argv.append(allocator, "-e");

    try argv.append(allocator, "bash");
    try argv.append(allocator, "-lc");
    try argv.append(allocator, shell_script);

    // bash uses this as $0
    try argv.append(allocator, "wyncommand");

    // These become $1 through $4
    try argv.append(allocator, selected_project.name);
    try argv.append(allocator, project.projectTypeLabel(project_type));
    try argv.append(allocator, action.actionLabel(selected_action));
    try argv.append(allocator, command_text);

    // Remaining arguments become "$@"
    for (command) |part| {
        try argv.append(allocator, part);
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
}