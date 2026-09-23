import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import Qt.labs.folderlistmodel
import QtQuick.Dialogs

Controls.ApplicationWindow {
    id: root

    visible: true
    width: 780
    height: Math.min(720, Math.max(470, 274 + pickerModel.count * 92))
    minimumWidth: 660
    minimumHeight: 440
    title: "WynCommand"

    property color voidBlack: "#0b090e"
    property color cathedralBlack: "#121016"
    property color raisedBlack: "#19151d"
    property color hoverBlack: "#211a25"
    property color selectedBlack: "#241824"
    property color bone: "#eee8e2"
    property color ash: "#a89fac"
    property color dimAsh: "#746b78"
    property color iron: "#403846"
    property color brightIron: "#574b5d"
    property color wine: "#742b46"
    property color violet: "#8d6aa8"
    property color pastelPink: "#f5a9c8"
    property color pastelBlue: "#8ed8f8"
    property color softWhite: "#f5f3f5"

    property string heading: "WYNCOMMAND // BUILD"
    property string prompt: "Choose your invocation"
    property bool inlineActions: false
    property bool allowAddProject: false

    // Projects created inside the inline editor are emitted to Zig only
    // when the picker eventually exits. The pickerModel is updated
    // immediately so the new project can be used without reopening.
    property var pendingProjects: []
    property bool pendingProjectsEmitted: false

    // Inline project scanner state.
    property var scanQueue: []
    property var scanFound: ({})
    property var scanVisited: ({})
    property bool scanInProgress: false
    property int scannedDirectoryCount: 0
    property int maxScanDirectories: 2500

    // Keep this in the same order as the Zig decoder:
    // 0=test, 1=build, 2=run, 3=debug
    readonly property var actions: [
        { key: "test",  label: "Test",  detail: "SUMMON THE TEST SUITE", accent: pastelBlue },
        { key: "build", label: "Build", detail: "FORGE THE ARTIFACT", accent: violet },
        { key: "run",   label: "Run",   detail: "AWAKEN THE PROGRAM", accent: pastelPink },
        { key: "debug", label: "Debug", detail: "ENTER THE CATACOMBS", accent: wine }
    ]

    ListModel { id: pickerModel }

    function accentFor(key, index) {
        switch (key) {
            case "test": return root.pastelBlue
            case "build": return root.violet
            case "run": return root.pastelPink
            case "debug": return root.wine
            default: return index % 2 === 0 ? root.pastelBlue : root.pastelPink
        }
    }

    function looksLikePath(value) {
        return value.indexOf("/") !== -1 || value.indexOf("\\") !== -1
    }

    function indexLabel(index) {
        const value = index + 1
        return value < 10 ? "0" + value : String(value)
    }

    function invoke(index) {
        if (index < 0 || index >= pickerModel.count)
            return

        if (inlineActions) {
            openActionMenu(index)
        } else {
            root.finish(index + 1)
        }
    }

    function openActionMenu(projectIndex, sourceItem, localX, localY) {
        actionPopup.projectIndex = projectIndex
        optionList.currentIndex = projectIndex

        if (sourceItem !== undefined) {
            const point = sourceItem.mapToItem(root.contentItem,
                    localX === undefined ? sourceItem.width - 26 : localX,
                    localY === undefined ? sourceItem.height / 2 : localY)

            const wantedX = point.x + 12
            const wantedY = point.y - 22
            actionPopup.x = Math.min(root.width - actionPopup.width - 18,
                Math.max(18, wantedX))
            actionPopup.y = Math.min(root.height - actionPopup.height - 18,
                Math.max(60, wantedY))
        } else {
            actionPopup.x = root.width - actionPopup.width - 28
            actionPopup.y = Math.max(82, (root.height - actionPopup.height) / 2)
        }

        actionPopup.open()
        actionColumn.forceActiveFocus()
    }

    function chooseAction(actionIndex) {
        if (actionPopup.projectIndex < 0)
            return

        // Exit-code protocol used by picker.zig:
        // code = 1 + projectIndex * 4 + actionIndex
        root.finish(1 + actionPopup.projectIndex * actions.length + actionIndex)
    }


    readonly property var languageOrder: [
        "Zig", "Elixir", "Prolog", "Wren", "ASM", "Rust", "Java", "Scala",
        "Python", "Shell", "JavaScript", "TypeScript", "QML", "HTML", "CSS",
        "C", "C++", "C#", "F#", "Lua", "SQL", "Kotlin", "Swift", "Go",
        "PHP", "Ruby"
    ]

    function emitPendingProjects() {
        if (pendingProjectsEmitted)
            return

        pendingProjectsEmitted = true

        for (let i = 0; i < pendingProjects.length; ++i) {
            // qml6 writes console output to the child process' captured
            // output. Zig searches for this marker and persists the JSON.
            console.log("__WYN_ADD_PROJECT__" + JSON.stringify(pendingProjects[i]))
        }
    }

    function finish(code) {
        emitPendingProjects()
        Qt.exit(code)
    }

    function localPathFromUrl(urlValue) {
        let value = decodeURIComponent(urlValue.toString())

        if (value.startsWith("file://"))
            value = value.substring(7)

        return value
    }

    function localPathToUrl(path) {
        return "file://" + encodeURI(path)
    }

    function pathBaseName(path) {
        const normalized = path.replace(/\\/g, "/")
        const pieces = normalized.split("/").filter(function(piece) {
            return piece.length > 0
        })

        return pieces.length > 0 ? pieces[pieces.length - 1] : ""
    }

    function parseLanguages(text) {
        const raw = text.split(",")
        const result = []
        const seen = ({})

        for (let i = 0; i < raw.length; ++i) {
            const language = raw[i].trim()
            if (language.length === 0)
                continue

            const key = language.toLowerCase()
            if (seen[key])
                continue

            seen[key] = true
            result.push(language)
        }

        return result
    }

    function projectPathExists(path) {
        for (let i = 0; i < pickerModel.count; ++i) {
            if (pickerModel.get(i).key === path)
                return true
        }

        return false
    }

    function openProjectEditor() {
        actionPopup.close()

        projectNameField.text = ""
        projectPathField.text = ""
        languagesField.text = ""
        editorMessage.text = "Choose a platform. WynCommand will scan it automatically."
        editorMessage.color = root.dimAsh

        projectEditor.open()
        projectNameField.forceActiveFocus()
    }

    function saveProjectFromEditor() {
        const name = projectNameField.text.trim()
        const path = projectPathField.text.trim()
        const languages = parseLanguages(languagesField.text)

        if (name.length === 0) {
            editorMessage.text = "PROJECT NAME REQUIRED"
            editorMessage.color = root.pastelPink
            projectNameField.forceActiveFocus()
            return
        }

        if (path.length === 0) {
            editorMessage.text = "PROJECT DIRECTORY REQUIRED"
            editorMessage.color = root.pastelPink
            return
        }

        if (projectPathExists(path)) {
            editorMessage.text = "THAT DIRECTORY IS ALREADY REGISTERED"
            editorMessage.color = root.pastelPink
            return
        }

        if (languages.length === 0) {
            editorMessage.text = "ADD AT LEAST ONE LANGUAGE"
            editorMessage.color = root.pastelPink
            languagesField.forceActiveFocus()
            return
        }

        pickerModel.append({
            key: path,
            label: name,
            detail: languages.join(" • ")
        })

        pendingProjects = pendingProjects.concat([{
            name: name,
            path: path,
            languages: languages
        }])

        optionList.currentIndex = pickerModel.count - 1
        optionList.positionViewAtIndex(optionList.currentIndex, ListView.Contain)
        projectEditor.close()
        optionList.forceActiveFocus()
    }

    function shouldSkipDirectory(name) {
        switch (name) {
            case ".git":
            case "target":
            case "_build":
            case "deps":
            case "node_modules":
            case "zig-out":
            case ".zig-cache":
            case ".idea":
            case ".venv":
            case "venv":
            case "dist":
            case "build":
                return true
            default:
                return false
        }
    }

    function markLanguage(language) {
        scanFound[language] = true
    }

    function inspectScanFile(fileName) {
        const lower = fileName.toLowerCase()

        // Project markers. Keep these aligned with language_scan.zig.
        if (fileName === "build.zig") markLanguage("Zig")
        if (fileName === "mix.exs") markLanguage("Elixir")
        if (fileName === "Cargo.toml") markLanguage("Rust")
        if (fileName === "pom.xml") markLanguage("Java")
        if (fileName === "build.sbt") markLanguage("Scala")
        if (fileName === "pyproject.toml" ||
            fileName === "requirements.txt" ||
            fileName === "Pipfile" ||
            fileName === "setup.py") markLanguage("Python")
        if (fileName === "package.json") markLanguage("JavaScript")
        if (fileName === "tsconfig.json") markLanguage("TypeScript")
        if (fileName === "Package.swift") markLanguage("Swift")
        if (fileName === "go.mod") markLanguage("Go")
        if (fileName === "composer.json") markLanguage("PHP")
        if (fileName === "Gemfile" || fileName === "Rakefile") markLanguage("Ruby")
        if (fileName === "qmldir") markLanguage("QML")
        if (fileName === "pack.pl") markLanguage("Prolog")

        function endsWithAny(values) {
            for (let i = 0; i < values.length; ++i) {
                if (lower.endsWith(values[i]))
                    return true
            }
            return false
        }

        if (endsWithAny([".zig"])) markLanguage("Zig")
        if (endsWithAny([".ex", ".exs"])) markLanguage("Elixir")
        if (endsWithAny([".prolog", ".pl"])) markLanguage("Prolog")
        if (endsWithAny([".wren"])) markLanguage("Wren")
        if (endsWithAny([".asm", ".s"])) markLanguage("ASM")
        if (endsWithAny([".rs"])) markLanguage("Rust")
        if (endsWithAny([".java"])) markLanguage("Java")
        if (endsWithAny([".scala", ".sc"])) markLanguage("Scala")
        if (endsWithAny([".py", ".pyw"])) markLanguage("Python")
        if (endsWithAny([".sh", ".bash", ".zsh"])) markLanguage("Shell")
        if (endsWithAny([".js", ".jsx", ".mjs", ".cjs"])) markLanguage("JavaScript")
        if (endsWithAny([".ts", ".tsx", ".mts", ".cts"])) markLanguage("TypeScript")
        if (endsWithAny([".qml", ".qmlproject"])) markLanguage("QML")
        if (endsWithAny([".html", ".htm"])) markLanguage("HTML")
        if (endsWithAny([".css", ".scss", ".sass"])) markLanguage("CSS")
        if (endsWithAny([".c", ".h"])) markLanguage("C")
        if (endsWithAny([".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"])) markLanguage("C++")
        if (endsWithAny([".cs", ".csproj"])) markLanguage("C#")
        if (endsWithAny([".fs", ".fsx", ".fsproj"])) markLanguage("F#")
        if (endsWithAny([".lua"])) markLanguage("Lua")
        if (endsWithAny([".sql"])) markLanguage("SQL")
        if (endsWithAny([".kt", ".kts"])) markLanguage("Kotlin")
        if (endsWithAny([".swift"])) markLanguage("Swift")
        if (endsWithAny([".go"])) markLanguage("Go")
        if (endsWithAny([".php", ".phtml"])) markLanguage("PHP")
        if (endsWithAny([".rb", ".rake"])) markLanguage("Ruby")
    }

    function startProjectScan(path) {
        if (path.length === 0)
            return

        scanQueue = [path]
        scanFound = ({})
        scanVisited = ({})
        scannedDirectoryCount = 0
        scanInProgress = true

        editorMessage.text = "SCANNING PROJECT..."
        editorMessage.color = root.pastelBlue

        scanNextDirectory()
    }

    function scanNextDirectory() {
        if (!scanInProgress)
            return

        while (scanQueue.length > 0) {
            if (scannedDirectoryCount >= maxScanDirectories) {
                finishProjectScan(true)
                return
            }

            const nextPath = scanQueue.shift()

            if (scanVisited[nextPath])
                continue

            scanVisited[nextPath] = true
            scannedDirectoryCount += 1
            scanFolderModel.folder = localPathToUrl(nextPath)
            return
        }

        finishProjectScan(false)
    }

    function consumeCurrentScanFolder() {
        if (!scanInProgress)
            return

        for (let i = 0; i < scanFolderModel.count; ++i) {
            const name = scanFolderModel.get(i, "fileName")
            const path = scanFolderModel.get(i, "filePath")
            const isDirectory = scanFolderModel.get(i, "fileIsDir")

            if (isDirectory) {
                if (!shouldSkipDirectory(name))
                    scanQueue.push(path)
            } else {
                inspectScanFile(name)
            }
        }

        Qt.callLater(scanNextDirectory)
    }

    function finishProjectScan(truncated) {
        scanInProgress = false

        const detected = []
        for (let i = 0; i < languageOrder.length; ++i) {
            const language = languageOrder[i]
            if (scanFound[language])
                detected.push(language)
        }

        languagesField.text = detected.join(", ")

        if (detected.length === 0) {
            editorMessage.text = truncated
                ? "SCAN LIMIT REACHED • NO LANGUAGES DETECTED"
                : "NO LANGUAGES DETECTED • ENTER THEM MANUALLY"
            editorMessage.color = root.pastelPink
        } else {
            editorMessage.text = truncated
                ? "DETECTED " + detected.length + " LANGUAGES • SCAN LIMIT REACHED"
                : "DETECTED " + detected.length + (detected.length === 1 ? " LANGUAGE" : " LANGUAGES")
            editorMessage.color = root.pastelBlue
        }
    }

    function parseArguments() {
        const args = Application.arguments

        for (let i = 0; i < args.length; ++i) {
            const arg = args[i]

            if (arg.startsWith("--wyn-heading=")) {
                heading = arg.substring("--wyn-heading=".length)
                continue
            }

            if (arg.startsWith("--wyn-prompt=")) {
                prompt = arg.substring("--wyn-prompt=".length)
                continue
            }

            if (arg === "--wyn-inline-actions=true") {
                inlineActions = true
                continue
            }

            if (arg === "--wyn-add-project=true") {
                allowAddProject = true
                continue
            }

            if (arg.startsWith("--wyn-item=")) {
                const raw = arg.substring("--wyn-item=".length)
                const parts = raw.split("\t")

                pickerModel.append({
                    key: parts.length > 0 ? parts[0] : "",
                    label: parts.length > 1 ? parts[1] : "",
                    detail: parts.length > 2 ? parts[2] : ""
                })
            }
        }

        if (pickerModel.count > 0) {
            optionList.currentIndex = 0
            optionList.forceActiveFocus()
        }
    }

    Component.onCompleted: parseArguments()
    onClosing: root.emitPendingProjects()


    FolderListModel {
        id: scanFolderModel
        showDirs: true
        showFiles: true
        showDotAndDotDot: false
        showHidden: false
        showOnlyReadable: true

        onStatusChanged: {
            if (root.scanInProgress &&
                status === FolderListModel.Ready) {
                root.consumeCurrentScanFolder()
            }
        }
    }

    FolderDialog {
        id: projectFolderDialog

        title: "Choose a project platform"
        parentWindow: root

        currentFolder:
            "file:///home/qtummechanic"

        onAccepted: {
            const selectedPath =
                root.localPathFromUrl(selectedFolder)

            projectPathField.text =
                selectedPath

            if (projectNameField.text.trim().length === 0) {
                projectNameField.text =
                    root.pathBaseName(selectedPath)
            }

            root.startProjectScan(selectedPath)
        }
    }

    background: Rectangle {
        color: root.voidBlack
        border.width: 1
        border.color: root.iron
        radius: 10

        Rectangle {
            anchors.fill: parent
            anchors.margins: 10
            radius: 7
            color: "transparent"
            border.width: 1
            border.color: "#171219"
        }
    }

    Row {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 3

        Repeater {
            model: [root.pastelBlue, root.pastelPink, root.softWhite, root.pastelPink, root.pastelBlue]

            Rectangle {
                required property var modelData
                width: root.width / 5
                height: 3
                color: modelData
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 36
        anchors.rightMargin: 36
        anchors.topMargin: 28
        anchors.bottomMargin: 22
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 18

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                    text: root.heading
                    color: root.bone
                    font.family: "Cinzel"
                    font.pixelSize: 24
                    font.bold: true
                    font.letterSpacing: 2.2
                    Layout.fillWidth: true
                }

                Text {
                    text: root.inlineActions ? "Choose a project, then an action" : root.prompt
                    color: root.ash
                    font.family: "JetBrains Mono"
                    font.pixelSize: 12
                    font.letterSpacing: 0.3
                }
            }

            Rectangle {
                implicitWidth: headerStatus.implicitWidth + 22
                implicitHeight: 28
                radius: 14
                color: root.cathedralBlack
                border.width: 1
                border.color: root.brightIron

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 7

                    Rectangle {
                        Layout.preferredWidth: 6
                        Layout.preferredHeight: 6
                        radius: 3
                        color: pickerModel.count > 0 ? root.pastelBlue : root.wine
                    }

                    Text {
                        id: headerStatus
                        text: pickerModel.count + (pickerModel.count === 1 ? " TARGET" : " TARGETS")
                        color: root.ash
                        font.family: "JetBrains Mono"
                        font.pixelSize: 9
                        font.bold: true
                        font.letterSpacing: 1
                    }
                }
            }

            Text {
                text: "ᓚᘏᗢ  :3"
                color: root.pastelPink
                font.family: "JetBrains Mono"
                font.pixelSize: 15
                opacity: 0.82
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 9

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: root.iron
            }

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                width: 92
                height: 1
                color: root.wine

                Rectangle {
                    anchors.centerIn: parent
                    width: 18
                    height: 3
                    radius: 2
                    color: root.pastelPink
                    opacity: 0.75
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            visible: root.allowAddProject
            spacing: 10

            Item { Layout.fillWidth: true }

            Rectangle {
                id: addProjectButton
                Layout.preferredWidth: 178
                Layout.preferredHeight: 34
                radius: 7
                color: addProjectMouse.containsMouse ? root.hoverBlack : root.cathedralBlack
                border.width: 1
                border.color: addProjectMouse.containsMouse ? root.pastelBlue : root.brightIron

                Behavior on color { ColorAnimation { duration: 90 } }

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 8

                    Text {
                        text: "+"
                        color: root.pastelPink
                        font.family: "JetBrains Mono"
                        font.pixelSize: 17
                        font.bold: true
                    }

                    Text {
                        text: "ADD PROJECT"
                        color: root.bone
                        font.family: "JetBrains Mono"
                        font.pixelSize: 10
                        font.bold: true
                        font.letterSpacing: 1
                    }
                }

                MouseArea {
                    id: addProjectMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.openProjectEditor()
                }
            }
        }

        ListView {
            id: optionList
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 9
            clip: true
            focus: true
            keyNavigationWraps: true
            highlightMoveDuration: 90
            boundsBehavior: Flickable.StopAtBounds
            model: pickerModel

            Controls.ScrollBar.vertical: Controls.ScrollBar {
                policy: optionList.contentHeight > optionList.height
                    ? Controls.ScrollBar.AsNeeded
                    : Controls.ScrollBar.AlwaysOff
            }

            Keys.onReturnPressed: root.invoke(currentIndex)
            Keys.onEnterPressed: root.invoke(currentIndex)
            Keys.onEscapePressed: {
                if (actionPopup.opened)
                    actionPopup.close()
                else
                    root.finish(0)
            }

            Keys.onPressed: function(event) {
                if (root.allowAddProject &&
                    event.key === Qt.Key_N &&
                    (event.modifiers & Qt.ControlModifier)) {
                    root.openProjectEditor()
                    event.accepted = true
                    return
                }

                if (event.key >= Qt.Key_1 && event.key <= Qt.Key_9) {
                    const requestedIndex = event.key - Qt.Key_1
                    if (requestedIndex < pickerModel.count) {
                        optionList.currentIndex = requestedIndex
                        root.invoke(requestedIndex)
                        event.accepted = true
                    }
                }
            }

            delegate: Rectangle {
                id: card
                required property int index
                required property string key
                required property string label
                required property string detail

                readonly property color accent: root.accentFor(key, index)
                readonly property bool selected: ListView.isCurrentItem
                readonly property bool hasPath: root.looksLikePath(key)

                width: ListView.view.width
                height: hasPath ? 84 : 76
                radius: 7

                color: selected ? root.selectedBlack
                    : mouse.containsMouse ? root.hoverBlack
                        : root.raisedBlack
                border.width: selected ? 2 : 1
                border.color: selected ? accent
                    : mouse.containsMouse ? root.brightIron
                        : root.iron

                Behavior on color { ColorAnimation { duration: 110 } }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: selected ? 5 : 3
                    radius: 3
                    color: card.accent
                    opacity: selected ? 1.0 : 0.62
                    Behavior on width { NumberAnimation { duration: 100 } }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 17
                    anchors.rightMargin: 17
                    anchors.topMargin: 10
                    anchors.bottomMargin: 10
                    spacing: 13

                    Rectangle {
                        Layout.preferredWidth: 38
                        Layout.preferredHeight: 38
                        radius: 6
                        color: card.selected ? "#2a202c" : root.cathedralBlack
                        border.width: 1
                        border.color: card.selected ? card.accent : root.iron

                        Text {
                            anchors.centerIn: parent
                            text: root.indexLabel(card.index)
                            color: card.selected ? card.accent : root.dimAsh
                            font.family: "JetBrains Mono"
                            font.pixelSize: 11
                            font.bold: true
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3

                        Text {
                            text: card.label
                            color: root.bone
                            elide: Text.ElideRight
                            font.family: "JetBrains Mono"
                            font.pixelSize: 15
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        Text {
                            text: card.detail
                            visible: card.detail.length > 0
                            color: card.selected ? card.accent : root.pastelBlue
                            opacity: card.selected ? 0.9 : 0.68
                            elide: Text.ElideRight
                            font.family: "JetBrains Mono"
                            font.pixelSize: 10
                            font.letterSpacing: 0.8
                            Layout.fillWidth: true
                        }

                        Text {
                            text: card.key
                            visible: card.hasPath
                            color: root.dimAsh
                            elide: Text.ElideMiddle
                            font.family: "JetBrains Mono"
                            font.pixelSize: 9
                            Layout.fillWidth: true
                        }
                    }

                    ColumnLayout {
                        spacing: 2

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: root.inlineActions && card.selected ? "›" : card.selected ? "✦" : "◇"
                            color: card.selected ? card.accent : root.violet
                            font.pixelSize: 20
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: card.selected ? (root.inlineActions ? "ACTIONS" : "READY") : ""
                            color: card.accent
                            font.family: "JetBrains Mono"
                            font.pixelSize: 7
                            font.bold: true
                            font.letterSpacing: 0.8
                        }
                    }
                }

                MouseArea {
                    id: mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor

                    onEntered: optionList.currentIndex = card.index
                    onClicked: function(mouseEvent) {
                        optionList.currentIndex = card.index
                        if (root.inlineActions)
                            root.openActionMenu(card.index, card, mouseEvent.x, mouseEvent.y)
                        else
                            root.invoke(card.index)
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: root.iron
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            Text {
                Layout.fillWidth: true
                text: root.allowAddProject
                    ? "↑↓ navigate     ENTER actions     1–9 quick select     CTRL+N add     ESC vanish"
                    : root.inlineActions
                        ? "↑↓ navigate     ENTER actions     1–9 quick select     ESC vanish"
                        : "↑↓ navigate     ENTER invoke     1–9 quick invoke     ESC vanish"
                color: root.ash
                opacity: 0.68
                font.family: "JetBrains Mono"
                font.pixelSize: 9
            }

            Text {
                text: optionList.currentIndex >= 0
                    ? "NODE " + root.indexLabel(optionList.currentIndex)
                    : "IDLE"
                color: root.pastelPink
                opacity: 0.5
                font.family: "JetBrains Mono"
                font.pixelSize: 9
                font.letterSpacing: 1
            }
        }
    }


    Controls.Popup {
        id: projectEditor

        width: Math.min(620, root.width - 64)
        height: editorColumn.implicitHeight + 38
        x: Math.round((root.width - width) / 2)
        y: Math.round((root.height - height) / 2)
        modal: true
        dim: true
        focus: true
        closePolicy: Controls.Popup.CloseOnEscape | Controls.Popup.CloseOnPressOutside

        leftPadding: 26
        rightPadding: 20
        topPadding: 20
        bottomPadding: 18

        background: Rectangle {
            radius: 10
            color: root.cathedralBlack
            border.width: 1
            border.color: root.brightIron

            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 4
                radius: 2
                color: root.pastelPink
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 2
                color: root.pastelBlue
                opacity: 0.9
            }
        }

        contentItem: ColumnLayout {
            id: editorColumn
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "ADD PROJECT"
                        color: root.bone
                        font.family: "Cinzel"
                        font.pixelSize: 18
                        font.bold: true
                        font.letterSpacing: 1.6
                    }

                    Text {
                        text: "REGISTER A NEW WYNCOMMAND TARGET"
                        color: root.dimAsh
                        font.family: "JetBrains Mono"
                        font.pixelSize: 8
                        font.bold: true
                        font.letterSpacing: 1.1
                    }
                }

                Text {
                    text: "✦"
                    color: root.pastelPink
                    font.pixelSize: 18
                    opacity: 0.8
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: root.iron
            }

            Text {
                text: "PROJECT NAME"
                color: root.ash
                font.family: "JetBrains Mono"
                font.pixelSize: 8
                font.bold: true
                font.letterSpacing: 1
            }

            Controls.TextField {
                id: projectNameField
                Layout.fillWidth: true
                Layout.preferredHeight: 38
                placeholderText: "e.g. WynCommand M7"
                color: root.bone
                placeholderTextColor: root.dimAsh
                selectionColor: root.violet
                selectedTextColor: root.softWhite
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                leftPadding: 12
                rightPadding: 12

                background: Rectangle {
                    radius: 6
                    color: projectNameField.activeFocus ? root.hoverBlack : root.raisedBlack
                    border.width: 1
                    border.color: projectNameField.activeFocus ? root.pastelBlue : root.iron
                }
            }

            Text {
                text: "PROJECT DIRECTORY"
                color: root.ash
                font.family: "JetBrains Mono"
                font.pixelSize: 8
                font.bold: true
                font.letterSpacing: 1
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Controls.TextField {
                    id: projectPathField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 38
                    placeholderText: "/home/wyn/project"
                    color: root.bone
                    placeholderTextColor: root.dimAsh
                    selectionColor: root.violet
                    selectedTextColor: root.softWhite
                    font.family: "JetBrains Mono"
                    font.pixelSize: 10
                    leftPadding: 12
                    rightPadding: 12

                    background: Rectangle {
                        radius: 6
                        color: projectPathField.activeFocus ? root.hoverBlack : root.raisedBlack
                        border.width: 1
                        border.color: projectPathField.activeFocus ? root.pastelBlue : root.iron
                    }

                    onEditingFinished: {
                        const trimmed = text.trim()
                        if (trimmed.length > 0)
                            root.startProjectScan(trimmed)
                    }
                }

                Controls.Button {
                    id: browseButton
                    Layout.preferredWidth: 92
                    Layout.preferredHeight: 38

                    contentItem: Text {
                        text: "BROWSE"
                        color: root.bone
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.family: "JetBrains Mono"
                        font.pixelSize: 9
                        font.bold: true
                        font.letterSpacing: 0.8
                    }

                    background: Rectangle {
                        radius: 6
                        color: browseButton.hovered ? root.hoverBlack : root.raisedBlack
                        border.width: 1
                        border.color: browseButton.hovered ? root.pastelBlue : root.iron
                    }

                    onClicked: projectFolderDialog.open()
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: "LANGUAGES"
                    color: root.ash
                    font.family: "JetBrains Mono"
                    font.pixelSize: 8
                    font.bold: true
                    font.letterSpacing: 1
                }

                Item { Layout.fillWidth: true }

                Controls.Button {
                    id: rescanButton
                    enabled: projectPathField.text.trim().length > 0 && !root.scanInProgress
                    Layout.preferredWidth: 76
                    Layout.preferredHeight: 24

                    contentItem: Text {
                        text: root.scanInProgress ? "..." : "RESCAN"
                        color: rescanButton.enabled ? root.pastelBlue : root.dimAsh
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.family: "JetBrains Mono"
                        font.pixelSize: 8
                        font.bold: true
                    }

                    background: Rectangle {
                        radius: 5
                        color: "transparent"
                        border.width: 1
                        border.color: rescanButton.hovered && rescanButton.enabled
                            ? root.pastelBlue
                            : root.iron
                    }

                    onClicked: root.startProjectScan(projectPathField.text.trim())
                }
            }

            Controls.TextField {
                id: languagesField
                Layout.fillWidth: true
                Layout.preferredHeight: 38
                placeholderText: "Elixir, Prolog, Wren, ASM"
                color: root.bone
                placeholderTextColor: root.dimAsh
                selectionColor: root.violet
                selectedTextColor: root.softWhite
                font.family: "JetBrains Mono"
                font.pixelSize: 10
                leftPadding: 12
                rightPadding: 12

                background: Rectangle {
                    radius: 6
                    color: languagesField.activeFocus ? root.hoverBlack : root.raisedBlack
                    border.width: 1
                    border.color: languagesField.activeFocus ? root.pastelPink : root.iron
                }
            }

            Text {
                text: "Comma-separated. The scan is only a suggestion, so edit freely."
                color: root.dimAsh
                font.family: "JetBrains Mono"
                font.pixelSize: 8
                opacity: 0.78
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                radius: 6
                color: root.raisedBlack
                border.width: 1
                border.color: root.iron

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 11
                    anchors.rightMargin: 11
                    spacing: 8

                    Rectangle {
                        Layout.preferredWidth: 7
                        Layout.preferredHeight: 7
                        radius: 4
                        color: root.scanInProgress ? root.pastelPink : root.pastelBlue

                        SequentialAnimation on opacity {
                            running: root.scanInProgress
                            loops: Animation.Infinite
                            NumberAnimation { to: 0.25; duration: 420 }
                            NumberAnimation { to: 1.0; duration: 420 }
                        }
                    }

                    Text {
                        id: editorMessage
                        Layout.fillWidth: true
                        text: "Choose a platform. WynCommand will scan it automatically."
                        color: root.dimAsh
                        elide: Text.ElideRight
                        font.family: "JetBrains Mono"
                        font.pixelSize: 8
                        font.bold: true
                        font.letterSpacing: 0.5
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 9

                Item { Layout.fillWidth: true }

                Controls.Button {
                    id: cancelEditorButton
                    Layout.preferredWidth: 94
                    Layout.preferredHeight: 34

                    contentItem: Text {
                        text: "CANCEL"
                        color: root.ash
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.family: "JetBrains Mono"
                        font.pixelSize: 9
                        font.bold: true
                        font.letterSpacing: 0.8
                    }

                    background: Rectangle {
                        radius: 6
                        color: cancelEditorButton.hovered ? root.hoverBlack : root.raisedBlack
                        border.width: 1
                        border.color: cancelEditorButton.hovered ? root.brightIron : root.iron
                    }

                    onClicked: {
                        root.scanInProgress = false
                        projectEditor.close()
                        optionList.forceActiveFocus()
                    }
                }

                Controls.Button {
                    id: saveEditorButton
                    enabled: !root.scanInProgress
                    Layout.preferredWidth: 132
                    Layout.preferredHeight: 34

                    contentItem: Text {
                        text: "ADD PROJECT"
                        color: saveEditorButton.enabled ? root.bone : root.dimAsh
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.family: "JetBrains Mono"
                        font.pixelSize: 9
                        font.bold: true
                        font.letterSpacing: 0.8
                    }

                    background: Rectangle {
                        radius: 6
                        color: saveEditorButton.hovered && saveEditorButton.enabled
                            ? root.hoverBlack
                            : root.selectedBlack
                        border.width: 1
                        border.color: saveEditorButton.hovered && saveEditorButton.enabled
                            ? root.pastelPink
                            : root.violet
                    }

                    onClicked: root.saveProjectFromEditor()
                }
            }
        }
    }

    Controls.Popup {
        id: actionPopup
        property int projectIndex: -1

        width: 282
        height: actionColumn.implicitHeight + topPadding + bottomPadding
        leftPadding: 26
        rightPadding: 16
        topPadding: 18
        bottomPadding: 16
        modal: false
        focus: true
        closePolicy: Controls.Popup.CloseOnEscape | Controls.Popup.CloseOnPressOutside

        background: Rectangle {
            radius: 9
            color: root.cathedralBlack
            border.width: 1
            border.color: root.brightIron

            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 4
                radius: 2
                color: root.pastelPink
            }
        }

        contentItem: ColumnLayout {
            id: actionColumn
            spacing: 8
            focus: true

            Text {
                Layout.fillWidth: true
                text: actionPopup.projectIndex >= 0
                    ? pickerModel.get(actionPopup.projectIndex).label
                    : "PROJECT"
                color: root.bone
                elide: Text.ElideRight
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                font.bold: true
            }

            Text {
                text: "CHOOSE ACTION"
                color: root.dimAsh
                font.family: "JetBrains Mono"
                font.pixelSize: 8
                font.bold: true
                font.letterSpacing: 1.4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: root.iron
            }

            Repeater {
                model: root.actions

                delegate: Rectangle {
                    id: actionRow
                    required property int index
                    required property var modelData

                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    radius: 6
                    color: actionMouse.containsMouse ? root.hoverBlack : root.raisedBlack
                    border.width: 1
                    border.color: actionMouse.containsMouse ? modelData.accent : root.iron

                    Behavior on color { ColorAnimation { duration: 90 } }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 12
                        spacing: 11

                        Rectangle {
                            Layout.preferredWidth: 5
                            Layout.preferredHeight: 24
                            radius: 3
                            color: actionRow.modelData.accent
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Text {
                                text: actionRow.modelData.label
                                color: root.bone
                                font.family: "JetBrains Mono"
                                font.pixelSize: 12
                                font.bold: true
                            }

                            Text {
                                text: actionRow.modelData.detail
                                color: actionRow.modelData.accent
                                opacity: 0.66
                                font.family: "JetBrains Mono"
                                font.pixelSize: 7
                                font.letterSpacing: 0.7
                            }
                        }

                        Text {
                            text: "›"
                            color: actionMouse.containsMouse ? actionRow.modelData.accent : root.dimAsh
                            font.pixelSize: 17
                        }
                    }

                    MouseArea {
                        id: actionMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.chooseAction(actionRow.index)
                    }
                }
            }
        }
    }
}
