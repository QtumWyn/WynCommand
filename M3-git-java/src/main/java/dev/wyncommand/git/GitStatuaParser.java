package dev.wyncommand.git;

public class GitStatuaParser {
    private FileStatus parseStatusCode(char code) {
        return switch (code) {
            case ' ' -> FileStatus.NONE;
            case 'M' -> FileStatus.MODIFIED;
            case 'A' -> FileStatus.ADDED;
            case 'D' -> FileStatus.DELETED;

            default -> throw new IllegalArgumentException(
                    "Unknown Git status code: [" + code + "]"
            );
        };
    }

    public FileChange parseLine(String line) {
        // orchestration here
    }

    private ConflictType parseConflictType(String statusCode) {
        // existing switch
    }
}
