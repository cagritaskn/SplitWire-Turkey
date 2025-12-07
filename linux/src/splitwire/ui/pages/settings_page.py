"""
Settings Page for SplitWire-Turkey.

Provides application settings and about information.
Equivalent to Windows "Ayarlar" tab.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio
from typing import TYPE_CHECKING
import subprocess
import os

from splitwire.core import get_text, get_config, Language, Theme
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class SettingsPage(BasePage):
    """Application settings page."""

    def __init__(self, window: 'SplitWireWindow'):
        super().__init__(window)

    def _build_ui(self):
        """Build the settings page UI."""
        # Appearance group
        appearance_group = self.create_preferences_group(
            title=get_text("settings", "appearance") or "Görünüm"
        )
        self.append(appearance_group)

        # Language selector
        languages = [
            ("tr", "Türkçe", "🇹🇷"),
            ("en", "English", "🇬🇧"),
            ("ru", "Русский", "🇷🇺"),
            ("es", "Español", "🇪🇸"),
        ]

        lang_row = Adw.ComboRow(
            title=get_text("settings", "language") or "Dil",
            subtitle=get_text("settings", "language_subtitle") or "Uygulama dilini seçin",
        )

        # Create model with language names
        lang_model = Gtk.StringList.new([f"{flag} {name}" for code, name, flag in languages])
        lang_row.set_model(lang_model)

        # Set current language
        config = get_config()
        current_lang = config.language.value if config else "tr"
        for i, (code, name, flag) in enumerate(languages):
            if code == current_lang:
                lang_row.set_selected(i)
                break

        lang_row.connect("notify::selected", self._on_language_changed)
        lang_row.set_data("languages", languages)
        self._lang_row = lang_row
        appearance_group.add(lang_row)

        # Theme selector
        themes = [
            ("system", get_text("settings", "theme_system") or "Sistem"),
            ("light", get_text("settings", "theme_light") or "Açık"),
            ("dark", get_text("settings", "theme_dark") or "Koyu"),
        ]

        theme_row = Adw.ComboRow(
            title=get_text("settings", "theme") or "Tema",
            subtitle=get_text("settings", "theme_subtitle") or "Uygulama temasını seçin",
        )

        theme_model = Gtk.StringList.new([name for code, name in themes])
        theme_row.set_model(theme_model)

        # Set current theme
        current_theme = config.theme.value if config else "system"
        for i, (code, name) in enumerate(themes):
            if code == current_theme:
                theme_row.set_selected(i)
                break

        theme_row.connect("notify::selected", self._on_theme_changed)
        theme_row.set_data("themes", themes)
        self._theme_row = theme_row
        appearance_group.add(theme_row)

        # DNS Settings group
        dns_group = self.create_preferences_group(
            title=get_text("settings", "dns") or "DNS Ayarları"
        )
        self.append(dns_group)

        # DNS preset selector
        dns_presets = [
            "Google (8.8.8.8)",
            "Cloudflare (1.1.1.1)",
            "Quad9 (9.9.9.9)",
            "AdGuard (94.140.14.14)",
            "OpenDNS (208.67.222.222)",
        ]

        self._dns_row = self.create_combo_row(
            title=get_text("settings", "dns_server") or "DNS Sunucusu",
            items=dns_presets,
            selected=1,  # Default: Cloudflare
            callback=self._on_dns_changed,
        )
        dns_group.add(self._dns_row)

        # DoH mode switch
        self._switch_doh = self.create_switch_row(
            title=get_text("settings", "doh_enabled") or "DNS over HTTPS (DoH)",
            subtitle=get_text("settings", "doh_subtitle") or "Şifrelenmiş DNS sorguları kullan",
            active=True,
            callback=self._on_doh_changed,
        )
        dns_group.add(self._switch_doh)

        # About group
        about_group = self.create_preferences_group(
            title=get_text("settings", "about") or "Hakkında"
        )
        self.append(about_group)

        # Version row
        version_row = Adw.ActionRow(
            title=get_text("settings", "version") or "Sürüm",
            subtitle="1.0.0",
        )
        about_group.add(version_row)

        # GitHub row
        github_row = Adw.ActionRow(
            title="GitHub",
            subtitle="github.com/dogukanveziroglu/SplitWire-Turkey",
            activatable=True,
        )
        github_row.add_suffix(Gtk.Image.new_from_icon_name("external-link-symbolic"))
        github_row.connect("activated", self._on_github_clicked)
        about_group.add(github_row)

        # Support row (Patreon)
        support_row = Adw.ActionRow(
            title=get_text("settings", "support") or "Destek",
            subtitle="patreon.com/splitwire",
            activatable=True,
        )
        support_row.add_suffix(Gtk.Image.new_from_icon_name("external-link-symbolic"))
        support_row.connect("activated", self._on_support_clicked)
        about_group.add(support_row)

        # Logs group
        logs_group = self.create_preferences_group(
            title=get_text("settings", "logs") or "Loglar"
        )
        self.append(logs_group)

        # Open logs row
        logs_row = Adw.ActionRow(
            title=get_text("settings", "open_logs") or "Logs Klasörünü Aç",
            subtitle=get_text("settings", "logs_subtitle") or "Uygulama loglarını görüntüle",
            activatable=True,
        )
        logs_row.add_suffix(Gtk.Image.new_from_icon_name("folder-symbolic"))
        logs_row.connect("activated", self._on_open_logs)
        about_group.add(logs_row)

        # Check updates row
        updates_row = Adw.ActionRow(
            title=get_text("settings", "check_updates") or "Güncellemeleri Kontrol Et",
            subtitle=get_text("settings", "updates_subtitle") or "Yeni sürüm kontrolü yap",
            activatable=True,
        )
        updates_row.add_suffix(Gtk.Image.new_from_icon_name("software-update-available-symbolic"))
        updates_row.connect("activated", self._on_check_updates)
        about_group.add(updates_row)

    def refresh_translations(self):
        """Refresh UI translations."""
        # Update theme names
        themes = [
            ("system", get_text("settings", "theme_system") or "Sistem"),
            ("light", get_text("settings", "theme_light") or "Açık"),
            ("dark", get_text("settings", "theme_dark") or "Koyu"),
        ]
        theme_model = Gtk.StringList.new([name for code, name in themes])
        self._theme_row.set_model(theme_model)
        self._theme_row.set_data("themes", themes)

    # Event handlers

    def _on_language_changed(self, row, param):
        """Handle language selection change."""
        selected = row.get_selected()
        languages = row.get_data("languages")

        if selected < len(languages):
            code, name, flag = languages[selected]
            app = self._window.get_application()
            if app:
                app.set_language(code)
                self.show_toast(f"Dil değiştirildi: {name}")

    def _on_theme_changed(self, row, param):
        """Handle theme selection change."""
        selected = row.get_selected()
        themes = row.get_data("themes")

        if selected < len(themes):
            code, name = themes[selected]
            app = self._window.get_application()
            if app:
                app.set_theme(code)
                self.show_toast(f"Tema değiştirildi: {name}")

    def _on_dns_changed(self, row, param):
        """Handle DNS selection change."""
        selected = row.get_selected()
        self._logger.info(f"DNS changed to index: {selected}")
        # DNS will be applied when a service is installed

    def _on_doh_changed(self, row, param):
        """Handle DoH switch change."""
        active = row.get_active()
        self._logger.info(f"DoH enabled: {active}")

    def _on_github_clicked(self, row):
        """Handle GitHub row click."""
        self._open_url("https://github.com/dogukanveziroglu/SplitWire-Turkey")

    def _on_support_clicked(self, row):
        """Handle support row click."""
        self._open_url("https://patreon.com/splitwire")

    def _on_open_logs(self, row):
        """Handle open logs click."""
        logs_dir = os.path.expanduser("~/.cache/splitwire/logs")
        os.makedirs(logs_dir, exist_ok=True)
        self._open_url(f"file://{logs_dir}")

    def _on_check_updates(self, row):
        """Handle check updates click."""
        self.set_status("Güncellemeler kontrol ediliyor...")

        def do_check():
            import httpx

            try:
                response = httpx.get(
                    "https://api.github.com/repos/dogukanveziroglu/SplitWire-Turkey/releases/latest",
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("tag_name", "unknown")
            except Exception as e:
                self._logger.error(f"Update check failed: {e}")
            return None

        def on_complete(result):
            self.set_status("")
            if result:
                current = "v1.0.0"
                if result != current:
                    self.show_toast(f"Yeni sürüm mevcut: {result}")
                    # Optionally open release page
                    self._open_url(f"https://github.com/dogukanveziroglu/SplitWire-Turkey/releases/tag/{result}")
                else:
                    self.show_toast("En güncel sürümü kullanıyorsunuz")
            else:
                self.show_toast("Güncelleme kontrolü başarısız")

        self.run_async(do_check, on_complete)

    def _open_url(self, url: str):
        """Open a URL in the default browser."""
        try:
            Gio.AppInfo.launch_default_for_uri(url, None)
        except Exception as e:
            self._logger.error(f"Error opening URL: {e}")
            # Fallback to xdg-open
            try:
                subprocess.Popen(["xdg-open", url])
            except Exception:
                self.show_toast(f"URL açılamadı: {url}")
