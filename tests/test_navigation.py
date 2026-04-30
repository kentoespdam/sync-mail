import pytest
from sync_mail.tui.app import SyncMailApp
from sync_mail.tui.screens.menu import MenuScreen
from sync_mail.tui.screens.connection import ConnectionScreen
from sync_mail.tui.screens.introspect import IntrospectScreen
from textual.widgets import Input

@pytest.mark.asyncio
async def test_back_navigation_with_b_key():
    """Test that typing 'B' and pressing Enter goes back to the previous screen."""
    app = SyncMailApp()
    app.config_status = "VALID"
    
    async with app.run_test() as pilot:
        # 1. Start at Menu
        assert isinstance(app.screen, MenuScreen)
        
        # 2. Go to Introspect
        await pilot.click("#btn-introspect")
        await pilot.pause()
        assert isinstance(app.screen, IntrospectScreen)
        
        # 3. Type 'B' in an input and press Enter
        await pilot.press("tab") # Focus first input
        await pilot.press("b", "enter")
        await pilot.pause()
        
        # 4. Should be back at Menu
        assert isinstance(app.screen, MenuScreen)
        assert len(app.nav_history) == 1
        assert app.nav_history[0]["screen"] == "menu"

@pytest.mark.asyncio
async def test_state_retention_on_back():
    """Test that input data is retained when navigating back and forth."""
    app = SyncMailApp()
    app.config_status = "VALID"
    
    async with app.run_test() as pilot:
        # 1. Go to Introspect
        await pilot.click("#btn-introspect")
        await pilot.pause()
        
        # 2. Fill some data
        input_source = app.screen.query_one("#source-dsn", Input)
        input_source.value = "test_dsn"
        
        # 3. Go to another step (not implemented as a separate screen yet, but we can push menu again for test)
        # Actually, let's just go back to Menu and then back to Introspect
        # But wait, the snapshot is saved when PUSHING.
        # So we need to push SOMETHING from Introspect to save Introspect's state.
        # Or, we can modify push_screen_with_snapshot to also save when popping?
        # My current implementation saves when PUSHING.
        
        # Wait, if I am at Introspect and I go BACK, the Introspect state is discarded from history.
        # But the state of the screen I am GOING BACK TO should be restored.
        
        # Let's test going forward then back.
        # Step 1: Menu -> Connection. Snapshot Menu (empty). History: [Menu, Connection]
        # Step 2: Fill Connection. History: [Menu, Connection]
        # Step 3: Go to Introspect. Snapshot Connection. History: [Menu, Connection(data), Introspect]
        # Step 4: Go Back. Pop Introspect. Load Connection(data).
        
        app.push_screen_with_snapshot("connection")
        await pilot.pause()
        assert isinstance(app.screen, ConnectionScreen)
        
        # Fill connection
        app.screen.query_one("#src-host", Input).value = "host-123"
        
        # Go to Introspect
        app.push_screen_with_snapshot("introspect")
        await pilot.pause()
        assert isinstance(app.screen, IntrospectScreen)
        
        # Go Back using 'B'
        await pilot.press("tab", "b", "enter")
        await pilot.pause()
        
        # Should be back at Connection with host-123
        assert isinstance(app.screen, ConnectionScreen)
        assert app.screen.query_one("#src-host", Input).value == "host-123"

@pytest.mark.asyncio
async def test_menu_root_protection():
    """Test that the Menu screen cannot be popped from the navigation history."""
    app = SyncMailApp()
    app.config_status = "VALID"
    
    async with app.run_test() as pilot:
        assert isinstance(app.screen, MenuScreen)
        assert len(app.nav_history) == 1
        
        # Attempt to pop
        app.pop_screen_with_snapshot()
        await pilot.pause()
        
        # Still at Menu
        assert isinstance(app.screen, MenuScreen)
        assert len(app.nav_history) == 1
