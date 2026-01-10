"""
Main Page (WireGuard/WireSock) for SplitWire-Turkey.

Provides WireGuard VPN setup with split tunneling support.
Equivalent to Windows "Ana Sayfa" tab.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import Optional, List, TYPE_CHECKING
from pathlib import Path

from splitwire.core import get_text, get_config, save_config
from splitwire.services import (
    get_wireguard_service,
    get_split_tunnel_service,
    get_dns_service,
    ServiceStatus,
    KNOWN_APPS,
    BROWSER_APPS,
)
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class MainPage(BasePage):
    """WireGuard/WireSock setup page."""

    def __init__(self, window: 'SplitWireWindow'):
        self._wg_service = get_wireguard_service()
        self._st_service = get_split_tunnel_service()
        self._dns_service = get_dns_service()
        # Load custom apps from config
        config = get_config()
        self._custom_apps: List[str] = list(config.wireguard.custom_apps or [])
        # Track which known apps are enabled (all enabled by default)
        self._enabled_apps: dict[str, bool] = {app_id: True for app_id in KNOWN_APPS.keys()}
        super().__init__(window)

    def _build_ui(self):
        """Build the main page UI."""
        # Status indicator
        self._status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=8,
            margin_bottom=8,
        )
        self.append(self._status_box)
        # Note: _update_status_indicator() called at end of _build_ui after buttons exist

        # Main buttons group
        buttons_group = self.create_preferences_group(
            title=get_text("main", "setup") or "Kurulum"
        )
        self.append(buttons_group)

        # Standard setup button
        self._btn_standard = self.create_action_button(
            label=get_text("main", "standard_setup") or "Standart Kurulum",
            callback=self._on_standard_setup,
            tooltip=get_text("tooltips", "standard_install") or "WireGuard/WGCF ile standart kurulum",
            suggested=True,
        )
        buttons_group.add(self._btn_standard)

        # Alternative setup button
        self._btn_alternative = self.create_action_button(
            label=get_text("main", "alternative_setup") or "Alternatif Kurulum",
            callback=self._on_alternative_setup,
            tooltip=get_text("tooltips", "alternative_install") or "Alternatif WireGuard kurulumu",
        )
        buttons_group.add(self._btn_alternative)

        # Disconnect button (initially hidden)
        self._btn_disconnect = self.create_action_button(
            label=get_text("buttons", "disconnect") or "Bağlantıyı Kes",
            callback=self._on_disconnect,
            tooltip=get_text("tooltips", "wireguard_disconnect") or "VPN bağlantısını kes",
            destructive=True,
        )
        self._btn_disconnect.set_visible(False)
        buttons_group.add(self._btn_disconnect)

        # Options group
        options_group = self.create_preferences_group(
            title=get_text("main", "options") or "Seçenekler"
        )
        self.append(options_group)

        # Browser tunneling switch
        self._switch_browser = self.create_switch_row(
            title=get_text("main", "browser_tunneling") or "Tarayıcılar için de tünelleme yap",
            subtitle=get_text("tooltips", "browser_tunneling") or "Chrome, Firefox, Edge vb. tarayıcıları dahil et",
            active=False,
            callback=self._on_browser_tunneling_changed,
        )
        options_group.add(self._switch_browser)

        # Refresh timer switch
        self._switch_refresh = self.create_switch_row(
            title=get_text("main", "refresh_timer") or "WireSock yineleyici kur",
            subtitle=get_text("tooltips", "wiresock_repeater") or "Bağlantıyı periyodik olarak yenile (30 dakika)",
            active=False,
            callback=self._on_refresh_timer_changed,
        )
        options_group.add(self._switch_refresh)

        # Advanced settings expander
        self._advanced_expander = Adw.ExpanderRow(
            title=get_text("main", "folder_customization") or "Klasör listesini özelleştir",
            subtitle=get_text("tooltips", "folder_customization") or "Tünelleme yapılacak uygulamaları özelleştir",
        )
        options_group.add(self._advanced_expander)

        # App list inside expander
        self._build_app_list()

        # Custom buttons row
        custom_buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
            margin_top=8,
            margin_bottom=8,
        )
        self._advanced_expander.add_row(Adw.ActionRow(child=custom_buttons_box))

        # Add folder button
        self._btn_add_folder = Gtk.Button(
            label=get_text("main", "add_folder") or "Klasör Ekle",
            tooltip_text=get_text("tooltips", "add_folder") or "Özel uygulama klasörü ekle",
        )
        self._btn_add_folder.connect("clicked", self._on_add_folder)
        custom_buttons_box.append(self._btn_add_folder)

        # Clear list button
        self._btn_clear = Gtk.Button(
            label=get_text("main", "clear_list") or "Listeyi Temizle",
            tooltip_text=get_text("tooltips", "clear_list") or "Özel listeyi temizle",
        )
        self._btn_clear.connect("clicked", self._on_clear_list)
        custom_buttons_box.append(self._btn_clear)

        # Advanced buttons row
        advanced_buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
            margin_top=8,
        )
        self._advanced_expander.add_row(Adw.ActionRow(child=advanced_buttons_box))

        # Custom setup button
        self._btn_custom = Gtk.Button(
            label=get_text("main", "custom_setup") or "Özel Kurulum",
            tooltip_text=get_text("tooltips", "custom_install") or "Özel listeyle kurulum yap",
        )
        self._btn_custom.connect("clicked", self._on_custom_setup)
        advanced_buttons_box.append(self._btn_custom)

        # Generate config button
        self._btn_generate = Gtk.Button(
            label=get_text("main", "generate_config") or "Özel Config Oluştur",
            tooltip_text=get_text("tooltips", "generate_config") or "Özel WireGuard config dosyası oluştur",
        )
        self._btn_generate.connect("clicked", self._on_generate_config)
        advanced_buttons_box.append(self._btn_generate)

        # Remove service button
        remove_box = Gtk.Box(
            halign=Gtk.Align.CENTER,
            margin_top=16,
        )
        self.append(remove_box)

        self._btn_remove = self.create_action_button(
            label=get_text("main", "remove_service") or "Hizmeti Kaldır",
            callback=self._on_remove_service,
            destructive=True,
        )
        remove_box.append(self._btn_remove)

        # Help button
        help_box = Gtk.Box(
            halign=Gtk.Align.END,
            valign=Gtk.Align.END,
            vexpand=True,
        )
        self.append(help_box)
        help_btn = self.create_help_button(self._on_help)
        help_box.append(help_btn)

        # Load saved settings
        self._load_settings()

        # Update status indicator now that all buttons exist
        self._update_status_indicator()

    def _build_app_list(self):
        """Build the app selection list inside the expander."""
        # Known apps section - KNOWN_APPS is {app_id: [paths...]}
        for app_id, paths in KNOWN_APPS.items():
            # Get first existing path as subtitle
            subtitle = ""
            for path in paths:
                if Path(path).exists():
                    subtitle = path
                    break
            if not subtitle and paths:
                subtitle = paths[0]

            # Format app name nicely
            display_name = app_id.replace("-", " ").replace("_", " ").title()

            row = Adw.ActionRow(
                title=display_name,
                subtitle=subtitle,
            )

            # Check button - use set_name to store app_id (GTK4 compatible)
            check = Gtk.CheckButton(
                active=True,
                valign=Gtk.Align.CENTER,
            )
            check.set_name(app_id)  # Store app_id in widget name
            check.connect("toggled", self._on_app_toggled)
            row.add_prefix(check)

            self._advanced_expander.add_row(row)

    def _update_status_indicator(self):
        """Update the status indicator and button visibility."""
        # Clear existing children
        while child := self._status_box.get_first_child():
            self._status_box.remove(child)

        # Get current status
        try:
            status = self._wg_service.status()
            running = status == ServiceStatus.RUNNING
        except Exception:
            running = False

        # Status dot
        dot_label = "●"
        dot_class = "status-running" if running else "status-stopped"
        dot = Gtk.Label(
            label=dot_label,
            css_classes=[dot_class],
        )
        self._status_box.append(dot)

        # Status text
        status_text = get_text("status", "running") if running else get_text("status", "stopped")
        if not status_text:
            status_text = "Çalışıyor" if running else "Durduruldu"
        label = Gtk.Label(label=status_text)
        self._status_box.append(label)

        # Update button visibility based on VPN state
        self._btn_standard.set_sensitive(not running)
        self._btn_alternative.set_sensitive(not running)
        self._btn_disconnect.set_visible(running)

    def refresh(self):
        """Refresh page data."""
        self._update_status_indicator()

    def refresh_translations(self):
        """Refresh UI translations."""
        self._btn_standard.set_label(get_text("main", "standard_setup") or "Standart Kurulum")
        self._btn_alternative.set_label(get_text("main", "alternative_setup") or "Alternatif Kurulum")
        self._switch_browser.set_title(get_text("main", "browser_tunneling") or "Tarayıcılar için de tünelleme yap")
        self._switch_refresh.set_title(get_text("main", "refresh_timer") or "WireSock yineleyici kur")
        self._btn_remove.set_label(get_text("main", "remove_service") or "Hizmeti Kaldır")

    # Event handlers

    def _on_standard_setup(self, button):
        """Handle standard setup button click."""
        self.set_status(get_text("status", "installing") or "Kuruluyor...")

        def do_setup():
            error_msg = None
            try:
                # Register WGCF account if needed
                if not self._wg_service.register_wgcf():
                    return (False, get_text("errors", "wgcf_register_failed") or "WGCF kayıt başarısız")

                # Generate config
                if not self._wg_service.generate_config():
                    return (False, get_text("errors", "config_generate_failed") or "Config oluşturulamadı")

                # Setup split tunnel with selected apps
                include_browsers = self._switch_browser.get_active()
                apps = self._get_selected_apps()
                self._st_service.configure(apps=apps, include_browsers=include_browsers)

                # Apply Cloudflare DNS (required to bypass ISP DNS hijacking)
                self._dns_service.install(preset="cloudflare")

                # Start service
                if not self._wg_service.start():
                    return (False, get_text("errors", "service_start_failed") or "Servis başlatılamadı")

                # Save settings
                self._save_settings()

                return (True, None)

            except Exception as e:
                self._logger.exception(f"Standard setup failed: {e}")
                return (False, str(e))

        def on_complete(result):
            self._update_status_indicator()
            success, error = result if isinstance(result, tuple) else (result, None)
            if success:
                self.show_toast(get_text("messages", "setup_complete") or "Kurulum tamamlandı")
            else:
                self.show_toast(f"Hata: {error}" if error else "Kurulum başarısız")
            self.set_status("")

        self.run_async(do_setup, on_complete)

    def _on_alternative_setup(self, button):
        """Handle alternative setup button click."""
        self.set_status(get_text("status", "installing") or "Kuruluyor...")

        def do_setup():
            try:
                # Register WGCF account if needed
                if not self._wg_service.register_wgcf():
                    return (False, get_text("errors", "wgcf_register_failed") or "WGCF kayıt başarısız")

                # Generate config with alternative endpoint
                if not self._wg_service.generate_config(endpoint="alternative"):
                    return (False, get_text("errors", "config_generate_failed") or "Config oluşturulamadı")

                # Setup split tunnel with selected apps
                include_browsers = self._switch_browser.get_active()
                apps = self._get_selected_apps()
                self._st_service.configure(apps=apps, include_browsers=include_browsers)

                # Apply Cloudflare DNS (required to bypass ISP DNS hijacking)
                self._dns_service.install(preset="cloudflare")

                # Start service
                if not self._wg_service.start():
                    return (False, get_text("errors", "service_start_failed") or "Servis başlatılamadı")

                # Save settings
                self._save_settings()

                return (True, None)

            except Exception as e:
                self._logger.exception(f"Alternative setup failed: {e}")
                return (False, str(e))

        def on_complete(result):
            self._update_status_indicator()
            success, error = result if isinstance(result, tuple) else (result, None)
            if success:
                self.show_toast(get_text("messages", "setup_complete") or "Kurulum tamamlandı")
            else:
                self.show_toast(f"Hata: {error}" if error else "Kurulum başarısız")
            self.set_status("")

        self.run_async(do_setup, on_complete)

    def _on_disconnect(self, button):
        """Handle disconnect button click."""
        self.set_status(get_text("status", "disconnecting") or "Bağlantı kesiliyor...")

        def do_disconnect():
            try:
                self._wg_service.stop()
                # Restore original DNS settings
                self._dns_service.remove()
                return (True, None)
            except Exception as e:
                self._logger.exception(f"Disconnect failed: {e}")
                return (False, str(e))

        def on_complete(result):
            self._update_status_indicator()
            success, error = result if isinstance(result, tuple) else (result, None)
            if success:
                msg = get_text("messages", "service_stopped") or "{} durduruldu"
                self.show_toast(msg.format("WireGuard") if "{}" in msg else "WireGuard durduruldu")
            else:
                self.show_toast(f"Hata: {error}" if error else "Bağlantı kesilemedi")
            self.set_status("")

        self.run_async(do_disconnect, on_complete)

    def _on_browser_tunneling_changed(self, row, param):
        """Handle browser tunneling switch change."""
        active = row.get_active()
        self._logger.info(f"Browser tunneling: {active}")
        # Will be applied during setup

    def _on_refresh_timer_changed(self, row, param):
        """Handle refresh timer switch change."""
        active = row.get_active()
        self._logger.info(f"Refresh timer: {active}")
        # Enable/disable the refresh timer
        if active:
            self._wg_service.enable_refresh_timer()
        else:
            self._wg_service.disable_refresh_timer()

    def _on_app_toggled(self, check):
        """Handle app checkbox toggle."""
        app_id = check.get_name()  # Retrieve app_id from widget name
        active = check.get_active()
        self._enabled_apps[app_id] = active
        self._logger.info(f"App {app_id}: {'enabled' if active else 'disabled'}")
        # Save to config immediately
        self._save_settings()

    def _on_add_folder(self, button):
        """Handle add folder button click."""
        dialog = Gtk.FileDialog(
            title=get_text("dialogs", "select_folder") or "Klasör Seç",
        )
        dialog.select_folder(
            self._window,
            None,
            self._on_folder_selected,
        )

    def _on_folder_selected(self, dialog, result):
        """Handle folder selection result."""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                if path not in self._custom_apps:
                    self._custom_apps.append(path)
                    self._save_settings()  # Persist the change
                    self.show_toast(f"Eklendi: {path}")
                else:
                    self.show_toast(f"Zaten listede: {path}")
        except GLib.Error as e:
            if e.code != 2:  # Not cancelled
                self._logger.error(f"Folder selection error: {e}")

    def _on_clear_list(self, button):
        """Handle clear list button click."""
        self._custom_apps.clear()
        self._save_settings()  # Persist the change
        self.show_toast(get_text("messages", "list_cleared") or "Liste temizlendi")

    def _on_custom_setup(self, button):
        """Handle custom setup button click."""
        if not self._custom_apps:
            self.show_toast(get_text("messages", "no_custom_apps") or "Özel uygulama listesi boş")
            return

        self.set_status(get_text("status", "installing") or "Kuruluyor...")

        def do_setup():
            try:
                # Register WGCF account if needed
                if not self._wg_service.register_wgcf():
                    return (False, get_text("errors", "wgcf_register_failed") or "WGCF kayıt başarısız")

                # Generate config
                if not self._wg_service.generate_config():
                    return (False, get_text("errors", "config_generate_failed") or "Config oluşturulamadı")

                # Setup split tunnel with custom apps
                self._st_service.configure(
                    apps=self._custom_apps,
                    include_browsers=self._switch_browser.get_active()
                )

                # Apply Cloudflare DNS (for consistency with other setups)
                self._dns_service.install(preset="cloudflare")

                # Start service
                if not self._wg_service.start():
                    return (False, get_text("errors", "service_start_failed") or "Servis başlatılamadı")

                # Save settings
                self._save_settings()

                return (True, None)

            except Exception as e:
                self._logger.exception(f"Custom setup failed: {e}")
                return (False, str(e))

        def on_complete(result):
            self._update_status_indicator()
            success, error = result if isinstance(result, tuple) else (result, None)
            if success:
                self.show_toast(get_text("messages", "setup_complete") or "Kurulum tamamlandı")
            else:
                self.show_toast(f"Hata: {error}" if error else "Kurulum başarısız")
            self.set_status("")

        self.run_async(do_setup, on_complete)

    def _on_generate_config(self, button):
        """Handle generate config button click."""
        dialog = Gtk.FileDialog(
            title=get_text("dialogs", "save_config") or "Config Kaydet",
            initial_name="splitwire.conf",
        )
        dialog.save(
            self._window,
            None,
            self._on_config_save_selected,
        )

    def _on_config_save_selected(self, dialog, result):
        """Handle config save location selection."""
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                config_content = self._wg_service.generate_config_content(
                    include_browsers=self._switch_browser.get_active()
                )
                with open(path, 'w') as f:
                    f.write(config_content)
                self.show_toast(f"Config kaydedildi: {path}")
        except GLib.Error as e:
            if e.code != 2:  # Not cancelled
                self._logger.error(f"Config save error: {e}")

    def _on_remove_service(self, button):
        """Handle remove service button click."""
        # Confirmation dialog
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading=get_text("dialogs", "confirm_remove") or "Hizmeti Kaldır",
            body=get_text("dialogs", "remove_wireguard_body") or "WireGuard hizmeti kaldırılacak. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", get_text("buttons", "cancel") or "İptal")
        dialog.add_response("remove", get_text("buttons", "remove") or "Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_remove_confirmed)
        dialog.present()

    def _on_remove_confirmed(self, dialog, response):
        """Handle remove confirmation response."""
        if response == "remove":
            self.set_status(get_text("status", "removing") or "Kaldırılıyor...")

            def do_remove():
                try:
                    self._wg_service.stop()
                    self._wg_service.remove()
                    self._st_service.remove()
                    # Restore DNS settings
                    self._dns_service.remove()
                    return (True, None)
                except Exception as e:
                    self._logger.exception(f"Service removal failed: {e}")
                    return (False, str(e))

            def on_complete(result):
                self._update_status_indicator()
                success, error = result if isinstance(result, tuple) else (result, None)
                if success:
                    self.show_toast(get_text("messages", "service_removed") or "Hizmet kaldırıldı")
                else:
                    self.show_toast(f"Hata: {error}" if error else "Kaldırma başarısız")
                self.set_status("")

            self.run_async(do_remove, on_complete)

    def _on_help(self, button):
        """Handle help button click."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading=get_text("help", "wireguard_title") or "WireGuard Yardım",
            body=get_text("help", "wireguard_body") or """WireGuard, Cloudflare WARP üzerinden VPN bağlantısı sağlar.

Standart Kurulum: Discord ve seçilen uygulamalar VPN üzerinden geçer.

Alternatif Kurulum: Farklı bir endpoint kullanır.

Tarayıcılar için tünelleme: Chrome, Firefox vb. tarayıcıları da dahil eder.

Yineleyici: Bağlantıyı 30 dakikada bir yeniler.""",
        )
        dialog.add_response("ok", "Tamam")
        dialog.present()

    # Helper methods

    def _get_selected_apps(self) -> List[str]:
        """
        Get list of enabled apps for tunneling.

        Returns a combined list of:
        - Known apps that are enabled (from checkboxes)
        - Custom apps added by user

        Returns:
            List of app paths to tunnel
        """
        apps = []

        # Add enabled known apps
        for app_id, enabled in self._enabled_apps.items():
            if enabled and app_id in KNOWN_APPS:
                paths = KNOWN_APPS[app_id]
                # Add first existing path, or first path if none exist
                for path in paths:
                    if Path(path).exists():
                        apps.append(path)
                        break
                else:
                    if paths:
                        apps.append(paths[0])

        # Add custom apps
        apps.extend(self._custom_apps)

        return apps

    def _save_settings(self):
        """Save current settings to config file."""
        try:
            config = get_config()

            # Save app selections
            config.wireguard.enabled_known_apps = self._enabled_apps.copy()
            config.wireguard.custom_apps = self._custom_apps.copy()

            # Save switch states
            config.wireguard.include_browsers = self._switch_browser.get_active()
            config.wireguard.refresh_timer_enabled = self._switch_refresh.get_active()

            # Persist to disk
            save_config()
            self._logger.debug("Settings saved")

        except Exception as e:
            self._logger.error(f"Failed to save settings: {e}")

    def _load_settings(self):
        """Load settings from config file and update UI."""
        try:
            config = get_config()

            # Load app selections
            if config.wireguard.enabled_known_apps:
                self._enabled_apps.update(config.wireguard.enabled_known_apps)

            if config.wireguard.custom_apps:
                self._custom_apps = list(config.wireguard.custom_apps)

            # Update switch states
            self._switch_browser.set_active(config.wireguard.include_browsers)
            self._switch_refresh.set_active(config.wireguard.refresh_timer_enabled)

            self._logger.debug("Settings loaded")

        except Exception as e:
            self._logger.error(f"Failed to load settings: {e}")
