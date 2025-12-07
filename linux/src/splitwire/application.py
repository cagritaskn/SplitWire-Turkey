"""
SplitWire-Turkey GTK4/Libadwaita Application.

Main application class that initializes the GUI and manages
the application lifecycle.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from typing import Optional
import sys
import os

from splitwire.core import (
    get_config_manager,
    init_language_manager,
    init_logger,
    get_logger,
)
from splitwire.ui.window import SplitWireWindow


class SplitWireApp(Adw.Application):
    """Main application class for SplitWire-Turkey."""

    def __init__(self):
        super().__init__(
            application_id='com.splitwire.turkey',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )

        self.window: Optional[SplitWireWindow] = None
        self._logger = None
        self._config = None

        # Set application name
        GLib.set_application_name("SplitWire-Turkey")
        GLib.set_prgname("splitwire")

        # Connect signals
        self.connect('activate', self.on_activate)
        self.connect('shutdown', self.on_shutdown)

        # Setup actions
        self._setup_actions()

    def _setup_actions(self):
        """Setup application actions."""
        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences)
        self.add_action(preferences_action)
        self.set_accels_for_action("app.preferences", ["<Control>comma"])

    def do_startup(self):
        """Called when the application starts."""
        Adw.Application.do_startup(self)

        # Initialize core systems
        self._init_core_systems()

        # Load CSS if available
        self._load_css()

    def _init_core_systems(self):
        """Initialize core systems (config, language, logging)."""
        try:
            # Initialize logger first
            self._logger = init_logger(
                name="splitwire",
                console_level="INFO",
                file_level="DEBUG"
            )
            self._logger.info("SplitWire-Turkey starting...")

            # Initialize config
            self._config = get_config_manager()
            config = self._config.load()
            self._logger.info(f"Config loaded: theme={config.theme}, language={config.language}")

            # Initialize language
            init_language_manager(language=config.language.value)
            self._logger.info(f"Language initialized: {config.language.value}")

            # Apply theme
            self._apply_theme(config.theme.value)

        except Exception as e:
            print(f"Error initializing core systems: {e}", file=sys.stderr)

    def _apply_theme(self, theme: str):
        """Apply the specified theme."""
        style_manager = Adw.StyleManager.get_default()

        if theme == "dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme == "light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:  # system
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def _load_css(self):
        """Load custom CSS styles."""
        css_provider = Gtk.CssProvider()

        # Custom CSS for the application
        css = b"""
        /* SplitWire-Turkey Custom Styles */

        /* Status indicators */
        .status-running {
            color: #4CAF50;
        }

        .status-stopped {
            color: #9E9E9E;
        }

        .status-error {
            color: #F44336;
        }

        /* Remove buttons */
        .destructive-action {
            background-color: #8B0000;
            color: white;
        }

        .destructive-action:hover {
            background-color: #b83737;
        }

        /* Logo container */
        .logo-container {
            padding: 16px;
        }

        /* Service status row */
        .service-status-row {
            padding: 8px 16px;
        }

        /* Page title */
        .page-title {
            font-size: 18px;
            font-weight: bold;
        }

        /* Action button */
        .action-button {
            min-height: 48px;
            min-width: 280px;
            font-weight: bold;
        }

        /* Toggle row */
        .toggle-row {
            padding: 8px 0;
        }

        /* Help button */
        .help-button {
            min-width: 32px;
            min-height: 32px;
            border-radius: 16px;
        }

        /* Preset editor */
        .preset-editor {
            font-family: monospace;
            min-height: 80px;
        }
        """

        css_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default() if hasattr(self, '_display') else Gtk.Widget.get_display(Gtk.Window()),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_activate(self, app):
        """Called when the application is activated."""
        if not self.window:
            self.window = SplitWireWindow(application=self)

        self.window.present()

        if self._logger:
            self._logger.info("Main window presented")

    def on_shutdown(self, app):
        """Called when the application is shutting down."""
        if self._logger:
            self._logger.info("SplitWire-Turkey shutting down...")

        # Save config
        if self._config:
            try:
                self._config.save()
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Error saving config: {e}")

    def on_quit(self, action, param):
        """Handle quit action."""
        self.quit()

    def on_about(self, action, param):
        """Show about dialog."""
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name="SplitWire-Turkey",
            application_icon="com.splitwire.turkey",
            developer_name="SplitWire Team",
            version="1.0.0",
            website="https://github.com/dogukanveziroglu/SplitWire-Turkey",
            issue_url="https://github.com/dogukanveziroglu/SplitWire-Turkey/issues",
            copyright="© 2024 SplitWire Team",
            license_type=Gtk.License.MIT_X11,
            developers=[
                "Dogukan Veziroglu",
            ],
            comments="Network restriction bypass tool for Linux.\n\n"
                     "Provides WireGuard VPN, Zapret DPI bypass, ByeDPI proxy, "
                     "and Discord repair tools."
        )
        about.present()

    def on_preferences(self, action, param):
        """Show preferences (navigate to settings page)."""
        if self.window:
            self.window.navigate_to_settings()

    def set_theme(self, theme: str):
        """Set the application theme."""
        self._apply_theme(theme)

        # Save to config
        if self._config:
            from splitwire.core import Theme
            config = self._config.load()
            config.theme = Theme(theme)
            self._config.save(config)

    def set_language(self, language: str):
        """Set the application language."""
        from splitwire.core import set_language, Language

        set_language(language)

        # Save to config
        if self._config:
            config = self._config.load()
            config.language = Language(language)
            self._config.save(config)

        # Refresh UI
        if self.window:
            self.window.refresh_translations()

    def show_notification(self, title: str, body: str, priority: Gio.NotificationPriority = Gio.NotificationPriority.NORMAL):
        """Show a desktop notification."""
        notification = Gio.Notification.new(title)
        notification.set_body(body)
        notification.set_priority(priority)
        self.send_notification(None, notification)

    def show_toast(self, message: str, timeout: int = 3):
        """Show a toast message in the main window."""
        if self.window:
            self.window.show_toast(message, timeout)


def main():
    """Main entry point for the application."""
    app = SplitWireApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
