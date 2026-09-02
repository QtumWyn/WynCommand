import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts

Controls.ApplicationWindow {
    id: root

    visible: true

    width: 720
    height: Math.min(
        680,
        Math.max(440, 245 + pickerModel.count * 86)
    )

    minimumWidth: 620
    minimumHeight: 420

    title: "WynCommand"

    // Gothic core
    property color voidBlack: "#0b090e"
    property color cathedralBlack: "#121016"
    property color raisedBlack: "#19151d"
    property color hoverBlack: "#211a25"

    property color bone: "#eee8e2"
    property color ash: "#a89fac"
    property color iron: "#403846"

    // Gothic accents
    property color wine: "#742b46"
    property color violet: "#8d6aa8"

    // Tiny trans-girl shimmer :3
    property color pastelPink: "#f5a9c8"
    property color pastelBlue: "#8ed8f8"
    property color softWhite: "#f5f3f5"

    property string heading: "WYNCOMMAND // BUILD"
    property string prompt: "Choose your invocation"

    ListModel {
        id: pickerModel
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

    background: Rectangle {
        color: root.voidBlack

        border.width: 1
        border.color: root.iron
        radius: 8
    }

    // Tiny trans stripe along the top.
    Row {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        height: 3

        Rectangle {
            width: parent.width / 5
            height: parent.height
            color: root.pastelBlue
        }

        Rectangle {
            width: parent.width / 5
            height: parent.height
            color: root.pastelPink
        }

        Rectangle {
            width: parent.width / 5
            height: parent.height
            color: root.softWhite
        }

        Rectangle {
            width: parent.width / 5
            height: parent.height
            color: root.pastelPink
        }

        Rectangle {
            width: parent.width / 5
            height: parent.height
            color: root.pastelBlue
        }
    }

    ColumnLayout {
        anchors.fill: parent

        anchors.leftMargin: 34
        anchors.rightMargin: 34
        anchors.topMargin: 28
        anchors.bottomMargin: 22

        spacing: 12

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3

                Text {
                    text: root.heading

                    color: root.bone

                    font.family: "Cinzel"
                    font.pixelSize: 24
                    font.bold: true
                    font.letterSpacing: 2

                    Layout.fillWidth: true
                }

                Text {
                    text: root.prompt

                    color: root.ash

                    font.family: "JetBrains Mono"
                    font.pixelSize: 13
                }
            }

            // A tiny familiar watches over the build system.
            Text {
                text: "ᓚᘏᗢ  :3"

                color: root.pastelPink

                font.family: "JetBrains Mono"
                font.pixelSize: 15

                opacity: 0.8
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 7

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

                width: 70
                height: 1

                color: root.wine
            }
        }

        ListView {
            id: optionList

            Layout.fillWidth: true
            Layout.fillHeight: true

            spacing: 8

            clip: true
            focus: true

            model: pickerModel

            Controls.ScrollBar.vertical: Controls.ScrollBar {}

            Keys.onReturnPressed: {
                if (currentIndex >= 0) {
                    Qt.exit(currentIndex + 1)
                }
            }

            Keys.onEnterPressed: {
                if (currentIndex >= 0) {
                    Qt.exit(currentIndex + 1)
                }
            }

            Keys.onEscapePressed: {
                Qt.exit(0)
            }

            delegate: Rectangle {
                id: card

                required property int index
                required property string key
                required property string label
                required property string detail

                width: ListView.view.width
                height: 72

                radius: 5

                color: ListView.isCurrentItem
                    ? "#211723"
                    : mouse.containsMouse
                        ? root.hoverBlack
                        : root.raisedBlack

                border.width: ListView.isCurrentItem ? 2 : 1

                border.color: ListView.isCurrentItem
                    ? root.pastelPink
                    : mouse.containsMouse
                        ? root.wine
                        : root.iron

                Behavior on color {
                    ColorAnimation {
                        duration: 100
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom

                    width: 4

                    radius: 2

                    color: card.ListView.isCurrentItem
                        ? root.pastelBlue
                        : root.wine
                }

                RowLayout {
                    anchors.fill: parent

                    anchors.leftMargin: 20
                    anchors.rightMargin: 18
                    anchors.topMargin: 10
                    anchors.bottomMargin: 10

                    ColumnLayout {
                        Layout.fillWidth: true

                        spacing: 3

                        Text {
                            text: card.label

                            color: root.bone

                            font.family: "JetBrains Mono"
                            font.pixelSize: 16
                            font.bold: true
                        }

                        Text {
                            text: card.detail

                            visible: card.detail.length > 0

                            color: root.pastelBlue

                            opacity: 0.72

                            font.family: "JetBrains Mono"
                            font.pixelSize: 11
                            font.letterSpacing: 1
                        }
                    }

                    Text {
                        text: card.ListView.isCurrentItem
                            ? "✦"
                            : "◇"

                        color: card.ListView.isCurrentItem
                            ? root.pastelPink
                            : root.violet

                        font.pixelSize: 19
                    }
                }

                MouseArea {
                    id: mouse

                    anchors.fill: parent

                    hoverEnabled: true

                    onEntered: {
                        optionList.currentIndex = card.index
                    }

                    onClicked: {
                        Qt.exit(card.index + 1)
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

            Text {
                text: "↑ ↓  choose     ENTER  invoke     ESC  vanish"

                color: root.ash
                opacity: 0.65

                font.family: "JetBrains Mono"
                font.pixelSize: 10

                Layout.fillWidth: true
            }

            Text {
                text: "nya.exe"

                color: root.pastelPink
                opacity: 0.48

                font.family: "JetBrains Mono"
                font.pixelSize: 9
            }
        }
    }
}