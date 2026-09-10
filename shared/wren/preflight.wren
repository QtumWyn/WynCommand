class Preflight {
    static checkGit(project, gitClean) {
        System.print("Project: %(project)")
        if (gitClean) {
            System.print("The Git is clean.")
            return
        }

        System.print("The Git is dirty")
    }
}

var project = "DevDoctor"

Preflight.checkGit(project, true)