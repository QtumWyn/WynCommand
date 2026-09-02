const std = @import("std");

pub const Action = enum {
    test_project,
    build,
    run,
    debug,
};

pub const ActionError = error{
    UnknownAction,
    MissingAction,
};

pub fn actionLabel(selected_action: Action) []const u8 {
    return switch (selected_action) {
        .test_project => "Test",
        .build => "Build",
        .run => "Run",
        .debug => "Debug",
    };
}

pub fn parseAction(argument: []const u8) ActionError!Action {
    if (std.mem.eql(u8, argument, "test")) {
        return .test_project;
    }
    if (std.mem.eql(u8, argument, "build")) {
        return .build;
    }
    if (std.mem.eql(u8, argument, "run")) {
        return .run;
    }
    if (std.mem.eql(u8, argument, "debug")) {
        return .debug;
    }
    return error.UnknownAction;
}

test "parseAction returns test_project for test" {
    const action = try parseAction("test");

    try std.testing.expectEqual(Action.test_project, action);
}

test "parseAction returns build for build" {
    const action = try parseAction("build");

    try std.testing.expectEqual(Action.build, action);
}

test "parseAction returns run for run" {
    const action = try parseAction("run");

    try std.testing.expectEqual(Action.run, action);
}

test "parseAction returns debug for debug" {
    const action = try parseAction("debug");

    try std.testing.expectEqual(Action.debug, action);
}

test "parseAction returns error for unknown action" {
    try std.testing.expectError(
        error.UnknownAction,
        parseAction("run this thang girlllll"),
    );
}
