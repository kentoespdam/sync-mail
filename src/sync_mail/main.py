import sys

def main():
    """
    Main entry point for the sync-mail CLI application.
    Launches the Textual TUI.
    """
    from sync_mail.observability import configure_logging
    configure_logging()
    
    try:
        from sync_mail.config import resolve_connection_config
        from sync_mail.tui.app import SyncMailApp
        
        # Resolve connection config (YAML or Interactive)
        connection_config = resolve_connection_config()
        
        app = SyncMailApp()
        # We can store the config in the app instance if needed
        app.connection_config = connection_config
        app.run()
        sys.exit(0)
    except ImportError:
        print("Error: TUI application not found. Please ensure it is defined in src/sync_mail/tui/app.py.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
