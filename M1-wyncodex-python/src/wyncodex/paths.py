from dataclasses import dataclass
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QStandardPaths

@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    database_file: Path

    @classmethod
    def from_qt(cls) -> "AppPaths":
        app = QCoreApplication.instance()

        if app is None:
            raise RuntimeError(
                "AppPaths.from_qt() requires an active Qt application."
            )

        if not app.organizationName() or not app.applicationName():
            raise RuntimeError(
                "Qt organization and application names must be configured "
                "before resolving application paths."
            )

        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )

        if not location:
            raise RuntimeError(
                "Qt could not determine an application data directory."
            )

        data_dir = Path(location)
        data_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            data_dir=data_dir,
            database_file=data_dir / "wyncodex.db",
        )