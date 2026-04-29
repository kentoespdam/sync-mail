import pytest
from sync_mail.tui.app import SyncMailApp
from sync_mail.tui.screens.menu import MenuScreen

@pytest.mark.asyncio
async def test_app_initialization():
    """
    Smoke test to ensure the TUI app can be initialized and mounted
    without CSS parsing errors or other bootstrap failures.
    """
    app = SyncMailApp()
    # run_test is an async context manager that runs the app in headless mode.
    # If there are CSS errors, it should raise an exception during the setup.
    async with app.run_test() as pilot:
        # Check if the app is actually running
        assert app._running
        
        # Pause to allow the initial mount and screen push to complete
        await pilot.pause()
        
        # Verify that we are on the MenuScreen
        assert isinstance(app.screen, MenuScreen)
        
        # Verify title is present in the menu
        assert app.screen.query_one("#title") is not None

if __name__ == "__main__":
    # Allow running this script directly for manual verification
    import asyncio
    asyncio.run(test_app_initialization())
