package dev.wyncommand.git;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class GitClient {
    private final File repository;

    public GitClient(File repository) {
        this.repository = repository;
    }

    // String... arguments is essentially String[]; the func can take a variable number of args
    private String runGit(String... arguments) throws Exception {
        String[] command = new String[arguments.length + 1];
        command[0] = "git";

        for (int i = 0; i < arguments.length; i++) {
            command[i + 1] = arguments[i];
        }

        ProcessBuilder builder = new ProcessBuilder(command);

        builder.directory(repository);
        builder.redirectErrorStream(true);

        Process process = builder.start();

        String output = new String(
                process.getInputStream().readAllBytes(),
                StandardCharsets.UTF_8
        );

        int exitCode = process.waitFor();

        if (exitCode != 0) {
            throw new RuntimeException(
                    "Git command failed with exit code "
                            + exitCode
                            + ": "
                            + output
            );
        }

        return output;
    }

    public String currentBranch() throws Exception {
        return runGit(
                "branch",
                "--show-current"
        ).trim();
    }

    public String status() throws Exception {
        return runGit(
                "status",
                "--porcelain"
        ).stripTrailing();
    }

    public List<FileChange> changes() throws Exception {
        List<FileChange> changes = new ArrayList<>();

        String output = status();

        if (output.isEmpty()) {
            return changes;
        }

        String[] lines = output.split("\n");

        for (String line : lines) {
            char indexCode = line.charAt(0);
            char workTreeCode = line.charAt(1);

            String path = line.substring(3);
            String statusCode = line.substring(0, 2);


            if (indexCode == '?' && workTreeCode == '?') {
                changes.add(
                        new FileChange(
                                path,
                                FileStatus.NONE,
                                FileStatus.UNTRACKED,
                                ConflictType.NONE
                        )
                );

                continue;
            }

            ConflictType conflictType = parseConflictType(statusCode);

            if (conflictType != ConflictType.NONE) {
                changes.add(
                        new FileChange(
                                path,
                                FileStatus.NONE,
                                FileStatus.NONE,
                                conflictType
                        )
                );

                continue;
            }

            FileStatus indexStatus = parseStatusCode(indexCode);

            FileStatus workTreeStatus = parseStatusCode(workTreeCode);

            changes.add(
                    new FileChange(
                            path,
                            indexStatus,
                            workTreeStatus,
                            ConflictType.NONE
                    )
            );
        }

        return changes;
    }

    public RepositoryStatus repositoryStatus() throws Exception {
        String branch = currentBranch();
        List<FileChange> changes = changes();

        return new RepositoryStatus(branch, changes);
    }


    private ConflictType parseConflictType(String statusCode) {
        return switch (statusCode) {
            case "DD" -> ConflictType.BOTH_DELETED;
            case "AU" -> ConflictType.ADDED_BY_US;
            case "UD" -> ConflictType.DELETED_BY_THEM;
            case "UA" -> ConflictType.ADDED_BY_THEM;
            case "DU" -> ConflictType.DELETED_BY_US;
            case "AA" -> ConflictType.BOTH_ADDED;
            case "UU" -> ConflictType.BOTH_MODIFIED;
            default -> ConflictType.NONE;
        };
    }
}
