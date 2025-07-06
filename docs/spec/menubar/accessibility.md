# Menu Bar Application Specification: Accessibility



## VoiceOver Support

class AccessibleMenu:
    """Ensure menu items are accessible."""
    
    def create_menu_item(self, title: str, action=None):
        """Create accessible menu item."""
        item = rumps.MenuItem(title)
        
        # Add accessibility description
        if hasattr(item, '_menuitem'):
            item._menuitem.setAccessibilityDescription_(
                f"Network stats menu item: {title}"
            )
        
        return item

```python
class AccessibleMenu:
    """Ensure menu items are accessible."""
    
    def create_menu_item(self, title: str, action=None):
        """Create accessible menu item."""
        item = rumps.MenuItem(title)
        
        # Add accessibility description
        if hasattr(item, '_menuitem'):
            item._menuitem.setAccessibilityDescription_(
                f"Network stats menu item: {title}"
            )
        
        return item

```
