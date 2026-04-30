import pytest
from sync_mail.tui.app import SyncMailApp
from sync_mail.tui.screens.menu import MenuScreen
from sync_mail.tui.screens.connection import ConnectionScreen
from sync_mail.tui.screens.dry_run import DryRunScreen

@pytest.mark.asyncio
async def test_dry_run_screen_navigation():
    """Smoke test to ensure DryRunScreen can be pushed and renders widgets."""
    app = SyncMailApp()
    app.config_status = "VALID"
    
    async with app.run_test() as pilot:
        await pilot.pause()
        # Click the Dry Run button (ID: btn-dry-run)
        await pilot.click("#btn-dry-run")
        await pilot.pause()
        
        assert isinstance(app.screen, DryRunScreen)
        # Verify main components
        assert app.screen.query_one("#select-mapping") is not None
        assert app.screen.query_one("#input-sample-limit") is not None
        assert app.screen.query_one("#anomaly-table") is not None
        assert app.screen.query_one("#recommendation-panel") is not None

@pytest.mark.asyncio
async def test_app_initialization_invalid_config():
    """
    Smoke test to ensure the TUI app can be initialized and mounted
    when config is missing/invalid, landing on ConnectionScreen.
    """
    app = SyncMailApp()
    app.config_status = "MISSING_FILE"
    
    async with app.run_test() as pilot:
        assert app._running
        await pilot.pause()
        
        # Verify that we are on the ConnectionScreen
        assert isinstance(app.screen, ConnectionScreen)
        assert app.screen.query_one("#connection-form-container") is not None

@pytest.mark.asyncio
async def test_app_initialization_valid_config():
    """
    Smoke test to ensure the TUI app can be initialized and mounted
    when config is valid, landing on MenuScreen.
    """
    app = SyncMailApp()
    app.config_status = "VALID"
    
    async with app.run_test() as pilot:
        assert app._running
        await pilot.pause()
        
        # Verify that we are on the MenuScreen
        assert isinstance(app.screen, MenuScreen)
        assert app.screen.query_one("#title") is not None

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_app_initialization_invalid_config())
    asyncio.run(test_app_initialization_valid_config())
