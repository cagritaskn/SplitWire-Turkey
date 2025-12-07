"""
ByeDPI Page for SplitWire-Turkey.

Provides ByeDPI proxy setup with split tunneling support.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import TYPE_CHECKING

from splitwire.core import get_text
from splitwire.services import (
    get_byedpi_service,
    get_proxy_route_service,
    ServiceStatus,
    BYEDPI_PRESETS,
)
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class ByeDPIPage(BasePage):
    """ByeDPI proxy setup page."""

    def __init__(self, window: 'SplitWireWindow'):
        self._byedpi_service = get_byedpi_service()
        self._proxy_service = get_proxy_route_service()
        super().__init__(window)

    def _build_ui(self):
        """Build the ByeDPI page UI."""
        # Status indicator
        self._status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=8,
            margin_bottom=8,
        )
        self.append(self._status_box)
        self._update_status_indicator()

        # Setup group
        setup_group = self.create_preferences_group(
            title=get_text("byedpi", "setup") or "Kurulum"
        )
        self.append(setup_group)

        # Split tunneling setup button
        self._btn_split_setup = self.create_action_button(
            label=get_text("byedpi", "split_setup") or "ByeDPI Split Tunneling Kurulum",
            callback=self._on_split_setup,
            tooltip=get_text("tooltips", "byedpi_split") or "ByeDPI ile uygulama bazlı DPI bypass",
            suggested=True,
        )
        setup_group.add(self._btn_split_setup)

        # Options group
        options_group = self.create_preferences_group(
            title=get_text("byedpi", "options") or "Seçenekler"
        )
        self.append(options_group)

        # Browser tunneling switch
        self._switch_browser = self.create_switch_row(
            title=get_text("main", "browser_tunneling") or "Tarayıcılar için de tünelleme yap",
            subtitle=get_text("tooltips", "byedpi_browser_tunneling") or "Chrome, Firefox vb. tarayıcıları dahil et",
            active=False,
            callback=self._on_browser_tunneling_changed,
        )
        options_group.add(self._switch_browser)

        # Preset selection
        preset_names = list(BYEDPI_PRESETS.keys())
        self._combo_preset = self.create_combo_row(
            title=get_text("byedpi", "preset") or "Hazır Ayar",
            items=preset_names,
            selected=0,
            callback=self._on_preset_changed,
        )
        options_group.add(self._combo_preset)

        # Advanced settings expander
        self._advanced_expander = Adw.ExpanderRow(
            title=get_text("byedpi", "advanced") or "Gelişmiş Ayarlar",
            subtitle=get_text("byedpi", "custom_params") or "Özel ByeDPI parametreleri",
        )
        options_group.add(self._advanced_expander)

        # Custom parameters entry
        params_row = Adw.ActionRow(
            title=get_text("byedpi", "params") or "Parametreler",
        )
        self._advanced_expander.add_row(params_row)

        self._entry_params = Gtk.TextView(
            css_classes=["preset-editor"],
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            margin_start=8,
            margin_end=8,
            margin_top=8,
            margin_bottom=8,
        )
        self._entry_params.set_size_request(-1, 80)

        # Set default preset params
        if preset_names:
            first_preset = BYEDPI_PRESETS.get(preset_names[0])
            if first_preset:
                buffer = self._entry_params.get_buffer()
                buffer.set_text(first_preset.args or "")

        scroll = Gtk.ScrolledWindow(
            child=self._entry_params,
            min_content_height=80,
        )
        params_row.set_child(scroll)

        # Remove button
        remove_box = Gtk.Box(
            halign=Gtk.Align.CENTER,
            margin_top=16,
        )
        self.append(remove_box)

        self._btn_remove = self.create_action_button(
            label=get_text("byedpi", "remove") or "ByeDPI'ı Kaldır",
            callback=self._on_remove,
            destructive=True,
        )
        remove_box.append(self._btn_remove)

        # Status label for browser tunneling
        self._lbl_status = Gtk.Label(
            label="",
            css_classes=["dim-label"],
            wrap=True,
            margin_top=8,
        )
        self.append(self._lbl_status)

        # Help button
        help_box = Gtk.Box(
            halign=Gtk.Align.END,
            valign=Gtk.Align.END,
            vexpand=True,
        )
        self.append(help_box)
        help_btn = self.create_help_button(self._on_help)
        help_box.append(help_btn)

    def _update_status_indicator(self):
        """Update the status indicator."""
        # Clear existing children
        while child := self._status_box.get_first_child():
            self._status_box.remove(child)

        # Get current status
        try:
            status = self._byedpi_service.status()
            running = status == ServiceStatus.RUNNING
        except Exception:
            running = False

        # Status dot
        dot_class = "status-running" if running else "status-stopped"
        dot = Gtk.Label(
            label="●",
            css_classes=[dot_class],
        )
        self._status_box.append(dot)

        # Status text
        status_text = get_text("status", "running") if running else get_text("status", "stopped")
        if not status_text:
            status_text = "Çalışıyor" if running else "Durduruldu"
        label = Gtk.Label(label=status_text)
        self._status_box.append(label)

    def refresh(self):
        """Refresh page data."""
        self._update_status_indicator()

    def refresh_translations(self):
        """Refresh UI translations."""
        self._btn_split_setup.set_label(get_text("byedpi", "split_setup") or "ByeDPI Split Tunneling Kurulum")
        self._switch_browser.set_title(get_text("main", "browser_tunneling") or "Tarayıcılar için de tünelleme yap")
        self._btn_remove.set_label(get_text("byedpi", "remove") or "ByeDPI'ı Kaldır")

    # Event handlers

    def _on_split_setup(self, button):
        """Handle split tunneling setup."""
        self.set_status(get_text("status", "installing") or "Kuruluyor...")

        def do_setup():
            # Get selected preset
            selected = self._combo_preset.get_selected()
            preset_names = list(BYEDPI_PRESETS.keys())
            preset_name = preset_names[selected] if selected < len(preset_names) else "default"

            # Get custom params if modified
            buffer = self._entry_params.get_buffer()
            start, end = buffer.get_bounds()
            params = buffer.get_text(start, end, False)

            # Install and configure ByeDPI
            self._byedpi_service.install()
            self._byedpi_service.configure(
                preset=preset_name,
                custom_params=params if params else None
            )

            # Configure proxy routing
            include_browsers = self._switch_browser.get_active()
            self._proxy_service.configure(include_browsers=include_browsers)

            # Start services
            self._byedpi_service.start()
            self._proxy_service.start()

            return True

        def on_complete(result):
            self._update_status_indicator()
            if result:
                self.show_toast(get_text("messages", "setup_complete") or "Kurulum tamamlandı")
            self.set_status("")

        self.run_async(do_setup, on_complete)

    def _on_browser_tunneling_changed(self, row, param):
        """Handle browser tunneling switch change."""
        active = row.get_active()
        if active:
            self._lbl_status.set_label(get_text("byedpi", "browser_enabled") or "Tarayıcılar dahil edilecek")
        else:
            self._lbl_status.set_label("")

    def _on_preset_changed(self, row, param):
        """Handle preset selection change."""
        selected = row.get_selected()
        preset_names = list(BYEDPI_PRESETS.keys())

        if selected < len(preset_names):
            preset_name = preset_names[selected]
            preset = BYEDPI_PRESETS.get(preset_name)
            params = preset.args if preset else ""

            buffer = self._entry_params.get_buffer()
            buffer.set_text(params)

    def _on_remove(self, button):
        """Handle remove button click."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading=get_text("dialogs", "confirm_remove") or "Kaldır",
            body=get_text("dialogs", "remove_byedpi_body") or "ByeDPI kaldırılacak. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", get_text("buttons", "cancel") or "İptal")
        dialog.add_response("remove", get_text("buttons", "remove") or "Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_remove_confirmed)
        dialog.present()

    def _on_remove_confirmed(self, dialog, response):
        """Handle remove confirmation."""
        if response == "remove":
            self.set_status(get_text("status", "removing") or "Kaldırılıyor...")

            def do_remove():
                self._proxy_service.stop()
                self._proxy_service.remove()
                self._byedpi_service.stop()
                self._byedpi_service.remove()
                return True

            def on_complete(result):
                self._update_status_indicator()
                if result:
                    self.show_toast(get_text("messages", "service_removed") or "Hizmet kaldırıldı")
                self.set_status("")

            self.run_async(do_remove, on_complete)

    def _on_help(self, button):
        """Handle help button click."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading=get_text("help", "byedpi_title") or "ByeDPI Yardım",
            body=get_text("help", "byedpi_body") or """ByeDPI, DPI (Deep Packet Inspection) engellerini aşmak için SOCKS5 proxy kullanır.

Split Tunneling: Sadece Discord ve seçilen uygulamalar proxy üzerinden geçer.

Hazır Ayarlar: Farklı DPI bypass stratejileri sunar:
- Disorder: Paket sırasını boz
- Split: Paketleri böl
- Fake: Sahte paketler gönder
- OOB: Out-of-band veri kullan

Tarayıcılar için tünelleme aktifse tarayıcılar da proxy üzerinden geçer.""",
        )
        dialog.add_response("ok", "Tamam")
        dialog.present()
