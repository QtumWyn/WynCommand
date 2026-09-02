package dev.wyncommand.git;

public enum ConflictType {
    NONE,
    BOTH_MODIFIED,
    BOTH_ADDED,
    BOTH_DELETED,
    ADDED_BY_US,
    ADDED_BY_THEM,
    DELETED_BY_US,
    DELETED_BY_THEM
}
