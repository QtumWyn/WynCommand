const std = @import("std");
const action = @import("action.zig");
const project = @import("project.zig");

const Project = project.Project;
const Action = action.Action;
const BuildSystem = project.BuildSystem;
const ProjectProfile = project.ProjectProfile;

pub const RunnerError = error{
    UnsupportedProjectType,
    UnsupportedAction,
};

pub fn commandFor(
    build_system: BuildSystem,
    selected_action: Action,
) RunnerError![]const []const u8 {
    return switch (build_system) {
        .cargo => switch (selected_action) {
            .test_project => &.{ "cargo", "test" },
            .build => &.{ "cargo", "build" },
            .run => &.{ "cargo", "run" },
            .debug => error.UnsupportedAction,
        },

        .cargo_leptos => switch (selected_action) {
            .test_project => &.{ "cargo", "leptos", "test" },
            .build => &.{ "cargo", "leptos", "build" },
            // `watch` is the cargo-leptos development/run path and includes
            // server/client rebuilds plus browser live reload.
            .run => &.{ "cargo", "leptos", "watch" },
            .debug => error.UnsupportedAction,
        },

        .zig => switch (selected_action) {
            .test_project => &.{ "zig", "build", "test" },
            .build => &.{ "zig", "build" },
            .run => &.{ "zig", "build", "run" },
            .debug => error.UnsupportedAction,
        },

        .mix => switch (selected_action) {
            .test_project => &.{ "mix", "test" },
            .build => &.{ "mix", "compile" },
            .run => &.{ "mix", "run" },
            .debug => &.{ "iex", "-S", "mix" },
        },

        .maven => switch (selected_action) {
            .test_project => &.{ "mvn", "test" },
            .build => &.{ "mvn", "package" },
            // Maven has no universal run/debug goal without knowing which
            // plugin/application model the project uses.
            .run, .debug => error.UnsupportedAction,
        },

        .gradle_wrapper => switch (selected_action) {
            .test_project => &.{ "./gradlew", "test" },
            .build => &.{ "./gradlew", "build" },
            .run => &.{ "./gradlew", "run" },
            .debug => error.UnsupportedAction,
        },

        .gradle => switch (selected_action) {
            .test_project => &.{ "gradle", "test" },
            .build => &.{ "gradle", "build" },
            .run => &.{ "gradle", "run" },
            .debug => error.UnsupportedAction,
        },

        .sbt => switch (selected_action) {
            .test_project => &.{ "sbt", "test" },
            .build => &.{ "sbt", "compile" },
            .run => &.{ "sbt", "run" },
            .debug => error.UnsupportedAction,
        },

        .npm => switch (selected_action) {
            .test_project => &.{ "npm", "test" },
            .build => &.{ "npm", "run", "build" },
            .run => &.{ "npm", "start" },
            .debug => error.UnsupportedAction,
        },

        .dotnet => switch (selected_action) {
            .test_project => &.{ "dotnet", "test" },
            .build => &.{ "dotnet", "build" },
            .run => &.{ "dotnet", "run" },
            .debug => error.UnsupportedAction,
        },

        .cmake => switch (selected_action) {
            // Do not silently configure into an arbitrary platform or guess
            // an executable target. These assume the conventional ./build
            // tree already exists.
            .test_project => &.{ "ctest", "--test-dir", "build" },
            .build => &.{ "cmake", "--build", "build" },
            .run, .debug => error.UnsupportedAction,
        },

        .make => switch (selected_action) {
            .build => &.{ "make" },
            // `test`, `run`, and `debug` are not mandatory Make targets.
            .test_project, .run, .debug => error.UnsupportedAction,
        },

        .swiftpm => switch (selected_action) {
            .test_project => &.{ "swift", "test" },
            .build => &.{ "swift", "build" },
            .run => &.{ "swift", "run" },
            .debug => error.UnsupportedAction,
        },

        .go => switch (selected_action) {
            .test_project => &.{ "go", "test", "./..." },
            .build => &.{ "go", "build", "./..." },
            .run => &.{ "go", "run", "." },
            .debug => error.UnsupportedAction,
        },

        .python => switch (selected_action) {
            .test_project => &.{ "python3", "-m", "pytest" },
            .build => &.{ "python3", "-m", "compileall", "." },
            // Python projects have no universal executable module.
            .run, .debug => error.UnsupportedAction,
        },

        .composer => switch (selected_action) {
            // Composer scripts are project-defined; these commands are safe
            // and fail clearly when the corresponding script is absent.
            .test_project => &.{ "composer", "test" },
            .build => &.{ "composer", "build" },
            .run, .debug => error.UnsupportedAction,
        },

        .bundler => switch (selected_action) {
            .test_project => &.{ "bundle", "exec", "rake", "test" },
            .build => &.{ "bundle", "exec", "rake", "build" },
            .run, .debug => error.UnsupportedAction,
        },

        .none => error.UnsupportedProjectType,
    };
}

pub fn runProject(
    selected_project: Project,
    profile: ProjectProfile,
    selected_action: Action,
    allocator: std.mem.Allocator,
    io: std.Io,
) !void {
    const command = commandFor(
        profile.build_system,
        selected_action,
    ) catch |err| switch (err) {
        error.UnsupportedProjectType, error.UnsupportedAction => return showUnsupported(
            selected_project,
            profile,
            selected_action,
            allocator,
            io,
        ),
    };

    const command_text = try std.mem.join(
        allocator,
        " ",
        command,
    );
    defer allocator.free(command_text);

    const shell_script =
        \\printf '\033[2J\033[H'
        \\printf '\033[1m'
        \\printf '\033[38;2;91;206;250m█████ ████   ███  █   █  ████     ████  █████  ████ █   █ █████  ████ \n'
        \\printf '\033[38;2;245;169;184m  █   █   █ █   █ ██  █ █         █   █   █   █     █   █   █   █     \n'
        \\printf '\033[38;2;255;255;255m  █   ████  █████ █ █ █  ███      ████    █   █ ███ █████   █    ███  \n'
        \\printf '\033[38;2;245;169;184m  █   █  █  █   █ █  ██     █     █  █    █   █   █ █   █   █       █ \n'
        \\printf '\033[38;2;91;206;250m  █   █   █ █   █ █   █ ████      █   █ █████  ███  █   █   █   ████  \n'
        \\printf '\n'
        \\printf '\033[38;2;91;206;250m ███  ████  █████     █   █ █   █ █   █  ███  █   █\n'
        \\printf '\033[38;2;245;169;184m█   █ █   █ █         █   █ █   █ ██ ██ █   █ ██  █\n'
        \\printf '\033[38;2;255;255;255m█████ ████  ████      █████ █   █ █ █ █ █████ █ █ █\n'
        \\printf '\033[38;2;245;169;184m█   █ █  █  █         █   █ █   █ █   █ █   █ █  ██\n'
        \\printf '\033[38;2;91;206;250m█   █ █   █ █████     █   █  ███  █   █ █   █ █   █\n'
        \\printf '\n'
        \\printf '\033[38;2;91;206;250m████  █████  ████ █   █ █████  ████        ██ ████\n'
        \\printf '\033[38;2;245;169;184m█   █   █   █     █   █   █   █           █       █\n'
        \\printf '\033[38;2;255;255;255m████    █   █ ███ █████   █    ███       █     ███\n'
        \\printf '\033[38;2;245;169;184m█  █    █   █   █ █   █   █       █       █       █\n'
        \\printf '\033[38;2;91;206;250m█   █ █████  ███  █   █   █   ████         ██ ████\n'
        \\printf '\033[0m\n'
        \\printf '\033[38;2;177;140;255m'
        \\printf '                                   _.-~~~~-._                                   \n'
        \\printf '             _..---.._          .~          ~.          _..---.._               \n'
        \\printf '        _.-~~         ~-._     /              \     _.-~         ~~-._          \n'
        \\printf '      ./                  ~-._/                \_.-~                  \.        \n'
        \\printf '     /       _.._            /      /\  /\      \            _.._       \       \n'
        \\printf '    /_____.-~    ~-.___     /______/  \/  \______\     ___.-~    ~-._____\      \n'
        \\printf '                       \___/                  \___/                        \n'
        \\printf '                          \      .----.      /                             \n'
        \\printf '                           \____/  /\  \____/                              \n'
        \\printf '                                \/  \/                                    \n'
        \\printf '                                 \__/                                     \n'
        \\printf '\033[0m\n'
        \\project="$1"
        \\ptype="$2"
        \\tool="$3"
        \\action="$4"
        \\command_text="$5"
        \\shift 5
        \\
        \\printf '\033[38;2;245;169;200m'
        \\printf '╔═ WYNCOMMAND // EXECUTION ═════════════════════════════╗\n'
        \\printf '\033[0m'
        \\printf '║ \033[38;2;142;216;248mProject\033[0m  %s\n' "$project"
        \\printf '║ \033[38;2;245;169;200mType\033[0m     %s\n' "$ptype"
        \\printf '║ \033[38;2;142;216;248mTool\033[0m     %s\n' "$tool"
        \\printf '║ \033[38;2;245;169;200mAction\033[0m   %s\n' "$action"
        \\printf '║ \033[38;2;142;216;248mCommand\033[0m  %s\n' "$command_text"
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

    // These become $1 through $5
    try argv.append(allocator, selected_project.name);
    try argv.append(allocator, project.profileLabel(profile));
    try argv.append(allocator, project.buildSystemLabel(profile.build_system));
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

fn showUnsupported(
    selected_project: Project,
    profile: ProjectProfile,
    selected_action: Action,
    allocator: std.mem.Allocator,
    io: std.Io,
) !void {
    const shell_script =
        \\printf '\033[38;2;245;169;200m'
        \\printf '╔═ WYNCOMMAND // SAFE STOP ═════════════════════════════╗\n'
        \\printf '\033[0m'
        \\printf '║ \033[38;2;142;216;248mProject\033[0m  %s\n' "$1"
        \\printf '║ \033[38;2;245;169;200mType\033[0m     %s\n' "$2"
        \\printf '║ \033[38;2;142;216;248mTool\033[0m     %s\n' "$3"
        \\printf '║ \033[38;2;245;169;200mAction\033[0m   %s\n' "$4"
        \\printf '\033[38;2;141;106;168m'
        \\printf '╚═══════════════════════════════════════════════════════╝\n'
        \\printf '\033[0m\n'
        \\printf 'No safe universal command exists for this project/action yet.\n'
        \\printf 'WynCommand deliberately did not guess an entrypoint, target, database,\n'
        \\printf 'assembler format, linker setup, or framework command.\n\n'
        \\printf '\033[38;2;142;216;248m✦ NOTHING EXECUTED\033[0m\n'
    ;

    const argv = [_][]const u8{
        "konsole",
        "--hold",
        "--workdir",
        selected_project.path,
        "-e",
        "bash",
        "-lc",
        shell_script,
        "wyncommand",
        selected_project.name,
        project.profileLabel(profile),
        project.buildSystemLabel(profile.build_system),
        action.actionLabel(selected_action),
    };

    const result = try std.process.run(
        allocator,
        io,
        .{ .argv = &argv },
    );

    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);
}

test "Elixir test action uses mix test" {
    const command = try commandFor(
        .mix,
        .test_project,
    );

    try std.testing.expectEqual(@as(usize, 2), command.len);
    try std.testing.expectEqualStrings("mix", command[0]);
    try std.testing.expectEqualStrings("test", command[1]);
}

test "Leptos run action uses cargo leptos watch" {
    const command = try commandFor(
        .cargo_leptos,
        .run,
    );

    try std.testing.expectEqual(@as(usize, 3), command.len);
    try std.testing.expectEqualStrings("cargo", command[0]);
    try std.testing.expectEqualStrings("leptos", command[1]);
    try std.testing.expectEqualStrings("watch", command[2]);
}

test "Go test action covers all packages" {
    const command = try commandFor(
        .go,
        .test_project,
    );

    try std.testing.expectEqualStrings("go", command[0]);
    try std.testing.expectEqualStrings("test", command[1]);
    try std.testing.expectEqualStrings("./...", command[2]);
}

test "source-only project refuses to guess a command" {
    try std.testing.expectError(
        error.UnsupportedProjectType,
        commandFor(.none, .run),
    );
}
