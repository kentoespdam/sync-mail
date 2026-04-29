from sync_mail.tui.app import SyncMailApp
from sync_mail.tui.screens.menu import MenuScreen
from sync_mail.tui.screens.introspect import IntrospectScreen
from sync_mail.tui.screens.migrate import MigrateScreen
from sync_mail.tui.screens.inspect import InspectScreen
from sync_mail.tui.widgets.progress import MigrationProgress
from sync_mail.tui.widgets.log_panel import LogPanel

def test_imports():
    app = SyncMailApp()
    print("TUI imports successful.")

if __name__ == "__main__":
    test_imports()
