package dev.wyncommand.git;

public record FileChange(
        String path,
        FileStatus indexStatus,
        FileStatus workTreeStatus,
        ConflictType conflictType
) {}
