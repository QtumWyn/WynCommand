package dev.wyncommand.git;

import java.util.List;

public record RepositoryStatus(
        String branch,
        List<FileChange> changes
) {
    public RepositoryStatus {
        changes = List.copyOf(changes);
    }
}
