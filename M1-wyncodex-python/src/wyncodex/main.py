import sys
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from wyncodex.repositories.language_repository import LanguageRepository
from wyncodex.repositories.category_repository import (
    CategoryRepository,
)
from wyncodex.repositories.package_repository import (
    PackageRepository,
)
from wyncodex.services.category_service import (
    CategoryService,
)
from wyncodex.services.package_service import (
    PackageService,
)
from wyncodex.repositories.entry_repository import (
    EntryRepository,
)

from wyncodex.services.entry_service import (
    EntryService,
)
from wyncodex.services.language_service import LanguageService
from wyncodex.ui.main_window import MainWindow
from wyncodex.ui.theme.stylesheet import apply_theme
from wyncodex.config import (
    APPLICATION_NAME,
    APPLICATION_VERSION,
    ORGANIZATION_NAME,
)
from wyncodex.database.connection import open_database
from wyncodex.database.migration_runner import run_migrations
from wyncodex.paths import AppPaths
from wyncodex.repositories.argument_repository import (
    ArgumentRepository,
)

from wyncodex.repositories.example_repository import (
    ExampleRepository,
)
from wyncodex.importers.json_importer import (
    JsonImportService,
)

from wyncodex.repositories.search_repository import (
    SearchRepository,
)

from wyncodex.services.search_service import (
    SearchService,
)

from wyncodex.services.starter_library_service import (
    StarterLibraryService,
)

def main() -> int:
    app = QApplication(sys.argv)

    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)

    apply_theme(app)

    paths = AppPaths.from_qt()

    print(f"WynCodex data directory: {paths.data_dir}")
    print(f"WynCodex database:       {paths.database_file}")

    connection = open_database(paths.database_file)

    try:
        run_migrations(connection)

        language_repository = LanguageRepository(connection)

        category_repository = CategoryRepository(connection)

        package_repository = PackageRepository(connection)

        entry_repository = EntryRepository(connection)
        argument_repository = ArgumentRepository(connection)

        example_repository = ExampleRepository(connection)

        search_repository = SearchRepository(connection)

        category_service = CategoryService(
            category_repository,
            language_repository,
        )

        package_service = PackageService(
            package_repository,
            category_repository,
        )

        entry_service = EntryService(
            entry_repository,
            category_repository,
            package_repository,
            argument_repository,
            example_repository,
        )

        language_service = LanguageService(language_repository)

        import_service = JsonImportService(
            connection,
            language_service,
            category_service,
            package_service,
            entry_service,
        )

        starter_library_service = (
            StarterLibraryService(
                connection,
                import_service,
            )
        )

        try:
            seed_result = (
                starter_library_service
                .seed_if_needed()
            )

        except Exception as error:
            QMessageBox.critical(
                None,
                "WynCodex Startup Failed",
                (
                    "WynCodex could not initialize "
                    "its starter library.\n\n"
                    f"{error}"
                ),
            )

            return 1

        search_service = SearchService(search_repository)

        if seed_result is not None:
            print(
                "Starter library initialized:"
            )

            print(
                f"  Languages: "
                f"{seed_result.languages_created}"
            )

            print(
                f"  Categories: "
                f"{seed_result.categories_created}"
            )

            print(
                f"  Packages: "
                f"{seed_result.packages_created}"
            )

            print(
                f"  Entries: "
                f"{seed_result.entries_created}"
            )

        window = MainWindow(
            language_service,
            category_service,
            package_service,
            entry_service,
            import_service,
            search_service,
        )

        window.show()

        return app.exec()
    finally:
        connection.close()