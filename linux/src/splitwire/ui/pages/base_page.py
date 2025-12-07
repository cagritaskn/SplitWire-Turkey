"""
Base page class for SplitWire-Turkey pages.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import Optional, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod

from splitwire.core import get_text, get_logger

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class BasePage(Gtk.Box):
    """Base class for all application pages."""

    def __init__(self, window: 'SplitWireWindow', **kwargs):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16,
            margin_start=16,
            margin_end=16,
            margin_top=16,
            margin_bottom=16,
            **kwargs
        )

        self._window = window
        self._logger = get_logger()
        self._is_busy = False

        # Build the page content
        self._build_ui()

    @abstractmethod
    def _build_ui(self):
        """Build the page UI. Must be implemented by subclasses."""
        pass

    def refresh(self):
        """Refresh page data. Override in subclasses if needed."""
        pass

    def refresh_translations(self):
        """Refresh translations. Override in subclasses if needed."""
        pass

    def show_toast(self, message: str, timeout: int = 3):
        """Show a toast notification."""
        if self._window:
            self._window.show_toast(message, timeout)

    def set_status(self, message: str):
        """Set status bar message."""
        if self._window:
            self._window.set_status(message)

    def set_busy(self, busy: bool):
        """Set busy state (for long operations)."""
        self._is_busy = busy
        self.set_sensitive(not busy)

    def run_async(self, func: Callable, callback: Optional[Callable] = None, *args):
        """Run a function asynchronously in a thread."""
        import threading

        def thread_func():
            try:
                result = func(*args)
                if callback:
                    GLib.idle_add(callback, result)
            except Exception as e:
                self._logger.error(f"Async operation failed: {e}")
                GLib.idle_add(self.show_toast, f"Hata: {e}")
            finally:
                GLib.idle_add(self.set_busy, False)

        self.set_busy(True)
        thread = threading.Thread(target=thread_func, daemon=True)
        thread.start()

    # Helper methods for creating common UI elements

    def create_action_button(
        self,
        label: str,
        callback: Callable,
        tooltip: Optional[str] = None,
        destructive: bool = False,
        suggested: bool = False,
        icon_name: Optional[str] = None,
    ) -> Gtk.Button:
        """Create a styled action button."""
        if icon_name:
            button = Gtk.Button(
                label=label,
                tooltip_text=tooltip,
            )
            button.set_icon_name(icon_name)
        else:
            button = Gtk.Button(
                label=label,
                tooltip_text=tooltip,
            )

        css_classes = ["action-button"]
        if destructive:
            css_classes.append("destructive-action")
        elif suggested:
            css_classes.append("suggested-action")

        button.set_css_classes(css_classes)
        button.connect("clicked", callback)
        return button

    def create_switch_row(
        self,
        title: str,
        subtitle: Optional[str] = None,
        active: bool = False,
        callback: Optional[Callable] = None,
    ) -> Adw.SwitchRow:
        """Create a switch row."""
        row = Adw.SwitchRow(
            title=title,
            active=active,
        )
        if subtitle:
            row.set_subtitle(subtitle)
        if callback:
            row.connect("notify::active", callback)
        return row

    def create_combo_row(
        self,
        title: str,
        items: list,
        selected: int = 0,
        callback: Optional[Callable] = None,
    ) -> Adw.ComboRow:
        """Create a combo box row."""
        model = Gtk.StringList.new(items)
        row = Adw.ComboRow(
            title=title,
            model=model,
            selected=selected,
        )
        if callback:
            row.connect("notify::selected", callback)
        return row

    def create_entry_row(
        self,
        title: str,
        text: str = "",
        placeholder: Optional[str] = None,
    ) -> Adw.EntryRow:
        """Create an entry row."""
        row = Adw.EntryRow(
            title=title,
            text=text,
        )
        if placeholder:
            row.set_input_purpose(Gtk.InputPurpose.FREE_FORM)
        return row

    def create_preferences_group(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Adw.PreferencesGroup:
        """Create a preferences group."""
        group = Adw.PreferencesGroup()
        if title:
            group.set_title(title)
        if description:
            group.set_description(description)
        return group

    def create_status_indicator(
        self,
        running: bool = False,
        label: Optional[str] = None,
    ) -> Gtk.Box:
        """Create a status indicator widget."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
        )

        # Status dot
        status_class = "status-running" if running else "status-stopped"
        dot = Gtk.Label(
            label="●",
            css_classes=[status_class],
        )
        box.append(dot)

        # Status label
        if label:
            status_label = Gtk.Label(label=label)
            box.append(status_label)

        return box

    def create_help_button(self, callback: Callable) -> Gtk.Button:
        """Create a help button."""
        button = Gtk.Button(
            label="?",
            css_classes=["circular", "help-button"],
            halign=Gtk.Align.END,
            valign=Gtk.Align.END,
            margin_end=8,
            margin_bottom=8,
        )
        button.connect("clicked", callback)
        return button
