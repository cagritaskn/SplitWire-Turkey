"""
SplitWire-Turkey Main Window.

The main application window with navigation and all pages.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf
from typing import Optional, Dict, Callable
import os

from splitwire.core import get_text, get_logger


class SplitWireWindow(Adw.ApplicationWindow):
    """Main window for SplitWire-Turkey application."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._logger = get_logger()
        self._pages: Dict[str, Gtk.Widget] = {}
        self._current_page: Optional[str] = None

        # Setup window properties
        self.set_title("SplitWire-Turkey")
        self.set_default_size(640, 700)
        self.set_size_request(600, 640)

        # Build UI
        self._build_ui()

        # Load initial page
        GLib.idle_add(self._on_page_selected, "main")

    def _build_ui(self):
        """Build the main UI structure."""
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header bar with window controls
        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(Gtk.Label(label="SplitWire-Turkey"))
        main_box.append(header_bar)

        # Toast overlay for notifications
        self._toast_overlay = Adw.ToastOverlay()
        main_box.append(self._toast_overlay)

        # Content box inside toast overlay
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        self._toast_overlay.set_child(content_box)

        # Header with logo
        self._build_header(content_box)

        # Navigation tabs
        self._build_navigation(content_box)

        # Content stack
        self._build_content_stack(content_box)

        # Status bar
        self._build_status_bar(content_box)

    def _build_header(self, parent: Gtk.Box):
        """Build the header with logo and controls."""
        header_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            css_classes=["card"],
            margin_start=16,
            margin_end=16,
            margin_top=8,
            margin_bottom=8,
        )
        parent.append(header_box)

        # Top row with theme toggle
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.append(top_row)

        # Spacer
        top_row.append(Gtk.Box(hexpand=True))

        # Theme toggle
        self._theme_toggle = Gtk.Switch(
            valign=Gtk.Align.CENTER,
            tooltip_text=get_text("settings", "theme"),
        )
        # Set initial state based on current theme
        self._init_theme_toggle()
        # Use notify::active instead of state-set for reliable toggle handling
        self._theme_toggle.connect("notify::active", self._on_theme_toggled)
        
        theme_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            margin_end=8,
            margin_top=8,
        )
        theme_icon = Gtk.Image.new_from_icon_name("weather-clear-night-symbolic")
        theme_box.append(theme_icon)
        theme_box.append(self._theme_toggle)
        top_row.append(theme_box)

        # Logo
        logo_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            spacing=4,
        )
        header_box.append(logo_box)

        # Logo image (placeholder - use icon)
        logo_image = Gtk.Image.new_from_icon_name("network-vpn-symbolic")
        logo_image.set_pixel_size(64)
        logo_box.append(logo_image)

        # Title
        title_label = Gtk.Label(
            label="SplitWire-Turkey",
            css_classes=["title-1"],
        )
        logo_box.append(title_label)

        # Subtitle
        subtitle_label = Gtk.Label(
            label="Linux Edition",
            css_classes=["dim-label"],
        )
        logo_box.append(subtitle_label)

        # Control buttons row
        controls_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=8,
            margin_top=12,
            margin_bottom=8,
        )
        header_box.append(controls_box)

        # Info button
        info_btn = Gtk.Button(
            icon_name="help-about-symbolic",
            tooltip_text=get_text("main", "about"),
            css_classes=["circular"],
        )
        info_btn.connect("clicked", self._on_about_clicked)
        controls_box.append(info_btn)

        # Language selector
        self._lang_button = Gtk.MenuButton(
            icon_name="preferences-desktop-locale-symbolic",
            tooltip_text=get_text("settings", "language"),
            css_classes=["circular"],
        )
        self._build_language_menu()
        controls_box.append(self._lang_button)

    def _build_language_menu(self):
        """Build the language selection menu."""
        menu = Gio.Menu()
        menu.append("Türkçe", "win.set-language::tr")
        menu.append("English", "win.set-language::en")
        menu.append("Русский", "win.set-language::ru")
        menu.append("Español", "win.set-language::es")

        self._lang_button.set_menu_model(menu)

        # Setup action
        action = Gio.SimpleAction.new("set-language", GLib.VariantType.new("s"))
        action.connect("activate", self._on_language_selected)
        self.add_action(action)

    def _build_navigation(self, parent: Gtk.Box):
        """Build the navigation tabs."""
        # ViewSwitcher for navigation
        self._view_switcher = Adw.ViewSwitcher(
            policy=Adw.ViewSwitcherPolicy.WIDE,
            margin_start=16,
            margin_end=16,
        )
        parent.append(self._view_switcher)

    def _build_content_stack(self, parent: Gtk.Box):
        """Build the content stack for pages."""
        # Scrolled window for content
        scrolled = Gtk.ScrolledWindow(
            vexpand=True,
            hscrollbar_policy=Gtk.PolicyType.NEVER,
        )
        parent.append(scrolled)

        # View stack
        self._stack = Adw.ViewStack()
        scrolled.set_child(self._stack)

        # Connect view switcher to stack
        self._view_switcher.set_stack(self._stack)

        # Add pages
        self._add_pages()

    def _add_pages(self):
        """Add all pages to the stack."""
        # Import pages here to avoid circular imports
        from splitwire.ui.pages.main_page import MainPage
        from splitwire.ui.pages.byedpi_page import ByeDPIPage
        from splitwire.ui.pages.zapret_page import ZapretPage
        from splitwire.ui.pages.goodbyedpi_page import GoodbyeDPIPage
        from splitwire.ui.pages.repair_page import RepairPage
        from splitwire.ui.pages.advanced_page import AdvancedPage
        from splitwire.ui.pages.settings_page import SettingsPage

        # Main page (WireGuard)
        main_page = MainPage(window=self)
        self._stack.add_titled_with_icon(
            main_page,
            "main",
            get_text("tabs", "main") or "Ana Sayfa",
            "go-home-symbolic"
        )
        self._pages["main"] = main_page

        # ByeDPI page
        byedpi_page = ByeDPIPage(window=self)
        self._stack.add_titled_with_icon(
            byedpi_page,
            "byedpi",
            "ByeDPI",
            "network-transmit-receive-symbolic"
        )
        self._pages["byedpi"] = byedpi_page

        # Zapret page
        zapret_page = ZapretPage(window=self)
        self._stack.add_titled_with_icon(
            zapret_page,
            "zapret",
            "Zapret",
            "security-high-symbolic"
        )
        self._pages["zapret"] = zapret_page

        # GoodbyeDPI page (uses Zapret nfqws on Linux)
        goodbyedpi_page = GoodbyeDPIPage(window=self)
        self._stack.add_titled_with_icon(
            goodbyedpi_page,
            "goodbyedpi",
            "GoodbyeDPI",
            "security-medium-symbolic"
        )
        self._pages["goodbyedpi"] = goodbyedpi_page

        # Repair page (Discord)
        repair_page = RepairPage(window=self)
        self._stack.add_titled_with_icon(
            repair_page,
            "repair",
            get_text("tabs", "repair") or "Onarım",
            "applications-games-symbolic"
        )
        self._pages["repair"] = repair_page

        # Advanced page
        advanced_page = AdvancedPage(window=self)
        self._stack.add_titled_with_icon(
            advanced_page,
            "advanced",
            get_text("tabs", "advanced") or "Gelişmiş",
            "applications-system-symbolic"
        )
        self._pages["advanced"] = advanced_page

        # Settings page
        settings_page = SettingsPage(window=self)
        self._stack.add_titled_with_icon(
            settings_page,
            "settings",
            get_text("tabs", "settings") or "Ayarlar",
            "preferences-system-symbolic"
        )
        self._pages["settings"] = settings_page

    def _build_status_bar(self, parent: Gtk.Box):
        """Build the status bar at the bottom."""
        status_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            css_classes=["toolbar"],
            margin_start=16,
            margin_end=16,
            margin_bottom=8,
        )
        parent.append(status_bar)

        # Status label
        self._status_label = Gtk.Label(
            label="",
            css_classes=["dim-label"],
            hexpand=True,
            halign=Gtk.Align.START,
        )
        status_bar.append(self._status_label)

        # Version label
        version_label = Gtk.Label(
            label="v1.0.0",
            css_classes=["dim-label"],
        )
        status_bar.append(version_label)

    def _on_page_selected(self, page_name: str):
        """Handle page selection."""
        self._current_page = page_name
        self._stack.set_visible_child_name(page_name)

        # Refresh page if it has a refresh method
        page = self._pages.get(page_name)
        if page and hasattr(page, 'refresh'):
            page.refresh()

    def _init_theme_toggle(self):
        """Initialize theme toggle state from config."""
        from splitwire.core import get_config_manager
        try:
            config = get_config_manager().load()
            # Switch ON = dark mode
            is_dark = config.theme == "dark"
            self._theme_toggle.set_active(is_dark)
        except Exception:
            pass

    def _on_theme_toggled(self, switch: Gtk.Switch, pspec) -> None:
        """Handle theme toggle."""
        app = self.get_application()
        if app:
            is_active = switch.get_active()
            theme = "dark" if is_active else "light"
            app.set_theme(theme)

    def _on_language_selected(self, action, param):
        """Handle language selection."""
        language = param.get_string()
        app = self.get_application()
        if app:
            app.set_language(language)

    def _on_about_clicked(self, button):
        """Handle about button click."""
        app = self.get_application()
        if app:
            app.on_about(None, None)

    def navigate_to_settings(self):
        """Navigate to settings page."""
        self._stack.set_visible_child_name("settings")

    def refresh_translations(self):
        """Refresh all UI translations."""
        # Refresh each page
        for page in self._pages.values():
            if hasattr(page, 'refresh_translations'):
                page.refresh_translations()

        # Update window title
        self.set_title("SplitWire-Turkey")

    def show_toast(self, message: str, timeout: int = 3):
        """Show a toast notification."""
        toast = Adw.Toast(
            title=message,
            timeout=timeout,
        )
        self._toast_overlay.add_toast(toast)

    def set_status(self, message: str):
        """Set the status bar message."""
        self._status_label.set_label(message)

    def get_page(self, name: str) -> Optional[Gtk.Widget]:
        """Get a page by name."""
        return self._pages.get(name)
