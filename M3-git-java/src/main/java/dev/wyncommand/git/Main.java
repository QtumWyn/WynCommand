package dev.wyncommand.git;

import java.io.File;
import java.util.List;

public class Main {
     public static void main(String[] args) throws Exception {
        System.out.println("WynCommand // Git :3");

        GitClient git = new GitClient(
                new File("/home/qtummechanic/ZigProjects/DevDoctor")
        );

        RepositoryStatus status = git.repositoryStatus();
        System.out.println("Branch: " + status.branch());

        for (FileChange change : status.changes()) {
           System.out.println(change);
        }
    }
}