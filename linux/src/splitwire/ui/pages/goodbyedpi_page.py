"""
GoodbyeDPI Page for SplitWire-Turkey.

On Linux, GoodbyeDPI functionality is provided by Zapret's nfqws.
This page provides a similar interface with blacklist support.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import TYPE_CHECKING
import os

from splitwire.core import get_text, get_config_manager
from splitwire.services import (
    get_zapret_service,
    ServiceStatus,
    ZapretMode,
)
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


# GoodbyeDPI-style presets (using nfqws)
GOODBYEDPI_PRESETS = {
    "Preset 1": "--dpi-desync=fake --dpi-desync-ttl=1",
    "Preset 2": "--dpi-desync=fake,split --dpi-desync-ttl=2",
    "Preset 3": "--dpi-desync=fake,disorder --dpi-desync-ttl=3",
    "Preset 4": "--dpi-desync=split2 --dpi-desync-ttl=4",
    "Preset 5": "--dpi-desync=fake,split2 --dpi-desync-ttl=5 --dpi-desync-fooling=md5sig",
    "Preset 6": "--dpi-desync=fake,disorder2 --dpi-desync-ttl=6 --dpi-desync-fooling=badsum",
}


class GoodbyeDPIPage(BasePage):
    """GoodbyeDPI (nfqws) setup page."""

    def __init__(self, window: 'SplitWireWindow'):
        self._zapret_service = get_zapret_service()
        self._config_manager = get_config_manager()
        self._blacklist_path = os.path.expanduser("~/.config/splitwire/blacklist.txt")
        super().__init__(window)

    def _build_ui(self):
        """Build the GoodbyeDPI page UI."""
        # Info banner
        info_banner = Adw.Banner(
            title="Linux'ta GoodbyeDPI işlevselliği Zapret nfqws tarafından sağlanır",
            revealed=True,
        )
        self.append(info_banner)

        # Status indicator
        self._status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=8,
            margin_top=8,
            margin_bottom=8,
        )
        self.append(self._status_box)
        self._update_status_indicator()

        # Presets group
        presets_group = self.create_preferences_group(
            title=get_text("goodbyedpi", "presets") or "Hazır Ayarlar"
        )
        self.append(presets_group)

        # Preset selection
        preset_names = list(GOODBYEDPI_PRESETS.keys())
        self._combo_preset = self.create_combo_row(
            title=get_text("goodbyedpi", "preset") or "Hazır Ayar",
            items=preset_names,
            selected=0,
            callback=self._on_preset_changed,
        )
        presets_group.add(self._combo_preset)

        # Edit preset expander
        self._edit_expander = Adw.ExpanderRow(
            title=get_text("goodbyedpi", "edit_preset") or "Hazır ayarı düzenle",
        )
        presets_group.add(self._edit_expander)

        # Parameters text view
        params_row = Adw.ActionRow()
        self._edit_expander.add_row(params_row)

        self._txt_params = Gtk.TextView(
            css_classes=["preset-editor"],
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            margin_start=8,
            margin_end=8,
            margin_top=8,
            margin_bottom=8,
        )
        self._txt_params.set_size_request(-1, 80)

        # Set default preset
        if preset_names:
            buffer = self._txt_params.get_buffer()
            buffer.set_text(GOODBYEDPI_PRESETS[preset_names[0]])

        scroll = Gtk.ScrolledWindow(
            child=self._txt_params,
            min_content_height=80,
        )
        params_row.set_child(scroll)

        # Blacklist group
        blacklist_group = self.create_preferences_group(
            title=get_text("goodbyedpi", "blacklist") or "Blacklist"
        )
        self.append(blacklist_group)

        # Use blacklist switch
        self._switch_blacklist = self.create_switch_row(
            title=get_text("goodbyedpi", "use_blacklist") or "Blacklist kullan",
            subtitle=get_text("tooltips", "goodbyedpi_use_blacklist") or "Sadece belirli domainlere uygula",
            active=False,
            callback=self._on_blacklist_toggled,
        )
        blacklist_group.add(self._switch_blacklist)

        # Edit blacklist expander
        self._blacklist_expander = Adw.ExpanderRow(
            title=get_text("goodbyedpi", "edit_blacklist") or "Blacklisti düzenle",
            visible=False,
        )
        blacklist_group.add(self._blacklist_expander)

        # Blacklist text view
        blacklist_row = Adw.ActionRow()
        self._blacklist_expander.add_row(blacklist_row)

        self._txt_blacklist = Gtk.TextView(
            css_classes=["preset-editor"],
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            margin_start=8,
            margin_end=8,
            margin_top=8,
            margin_bottom=8,
        )
        self._txt_blacklist.set_size_request(-1, 120)

        # Load existing blacklist
        self._load_blacklist()

        scroll_bl = Gtk.ScrolledWindow(
            child=self._txt_blacklist,
            min_content_height=120,
        )
        blacklist_row.set_child(scroll_bl)

        # Save blacklist button
        save_row = Adw.ActionRow()
        self._blacklist_expander.add_row(save_row)

        self._btn_save_blacklist = Gtk.Button(
            label=get_text("buttons", "save") or "Kaydet",
        )
        self._btn_save_blacklist.connect("clicked", self._on_save_blacklist)
        save_row.add_suffix(self._btn_save_blacklist)

        # Action buttons
        buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=16,
            margin_top=16,
        )
        self.append(buttons_box)

        # Install service button
        self._btn_service = Gtk.Button(
            label=get_text("goodbyedpi", "install_service") or "Hizmet Kur",
            css_classes=["suggested-action"],
            tooltip_text=get_text("tooltips", "goodbyedpi_service") or "systemd servisi olarak kur",
        )
        self._btn_service.connect("clicked", self._on_install_service)
        buttons_box.append(self._btn_service)

        # Run once button
        self._btn_once = Gtk.Button(
            label=get_text("goodbyedpi", "run_once") or "Tek Seferlik",
            tooltip_text=get_text("tooltips", "goodbyedpi_once") or "Sadece bu oturum için çalıştır",
        )
        self._btn_once.connect("clicked", self._on_run_once)
        buttons_box.append(self._btn_once)

        # Remove button
        remove_box = Gtk.Box(
            halign=Gtk.Align.CENTER,
            margin_top=16,
        )
        self.append(remove_box)

        self._btn_remove = self.create_action_button(
            label=get_text("goodbyedpi", "remove") or "GoodbyeDPI'ı Kaldır",
            callback=self._on_remove,
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

    def _update_status_indicator(self):
        """Update the status indicator."""
        while child := self._status_box.get_first_child():
            self._status_box.remove(child)

        try:
            status = self._zapret_service.status()
            running = status == ServiceStatus.RUNNING
        except Exception:
            running = False

        dot_class = "status-running" if running else "status-stopped"
        dot = Gtk.Label(label="●", css_classes=[dot_class])
        self._status_box.append(dot)

        status_text = "Çalışıyor" if running else "Durduruldu"
        label = Gtk.Label(label=status_text)
        self._status_box.append(label)

    def _load_blacklist(self):
        """Load blacklist from file."""
        try:
            if os.path.exists(self._blacklist_path):
                with open(self._blacklist_path, 'r') as f:
                    content = f.read()
                    buffer = self._txt_blacklist.get_buffer()
                    buffer.set_text(content)
            else:
                # Default blacklist
                default = """discord.com
discord.gg
discordapp.com
discordapp.net
discord.media
discordcdn.com"""
                buffer = self._txt_blacklist.get_buffer()
                buffer.set_text(default)
        except Exception as e:
            self._logger.error(f"Error loading blacklist: {e}")

    def refresh(self):
        """Refresh page data."""
        self._update_status_indicator()

    def refresh_translations(self):
        """Refresh UI translations."""
        self._switch_blacklist.set_title(get_text("goodbyedpi", "use_blacklist") or "Blacklist kullan")
        self._btn_service.set_label(get_text("goodbyedpi", "install_service") or "Hizmet Kur")
        self._btn_once.set_label(get_text("goodbyedpi", "run_once") or "Tek Seferlik")
        self._btn_remove.set_label(get_text("goodbyedpi", "remove") or "GoodbyeDPI'ı Kaldır")

    # Event handlers

    def _on_preset_changed(self, row, param):
        """Handle preset selection change."""
        selected = row.get_selected()
        preset_names = list(GOODBYEDPI_PRESETS.keys())

        if selected < len(preset_names):
            preset_name = preset_names[selected]
            params = GOODBYEDPI_PRESETS[preset_name]
            buffer = self._txt_params.get_buffer()
            buffer.set_text(params)

    def _on_blacklist_toggled(self, row, param):
        """Handle blacklist switch toggle."""
        active = row.get_active()
        self._blacklist_expander.set_visible(active)

    def _on_save_blacklist(self, button):
        """Save blacklist to file."""
        try:
            os.makedirs(os.path.dirname(self._blacklist_path), exist_ok=True)

            buffer = self._txt_blacklist.get_buffer()
            start, end = buffer.get_bounds()
            content = buffer.get_text(start, end, False)

            with open(self._blacklist_path, 'w') as f:
                f.write(content)

            self.show_toast("Blacklist kaydedildi")
        except Exception as e:
            self._logger.error(f"Error saving blacklist: {e}")
            self.show_toast(f"Hata: {e}")

    def _get_params(self) -> str:
        """Get current parameters with optional blacklist."""
        buffer = self._txt_params.get_buffer()
        start, end = buffer.get_bounds()
        params = buffer.get_text(start, end, False)

        if self._switch_blacklist.get_active() and os.path.exists(self._blacklist_path):
            params += f" --hostlist={self._blacklist_path}"

        return params

    def _on_install_service(self, button):
        """Handle install service button."""
        self.set_status("Hizmet kuruluyor...")

        def do_install():
            params = self._get_params()

            if not self._zapret_service.is_installed():
                self._zapret_service.install()

            self._zapret_service.configure(
                mode=ZapretMode.NFQWS,
                params=params
            )
            self._zapret_service.start()
            return True

        def on_complete(result):
            self._update_status_indicator()
            if result:
                self.show_toast("Hizmet kuruldu ve başlatıldı")
            self.set_status("")

        self.run_async(do_install, on_complete)

    def _on_run_once(self, button):
        """Handle run once button."""
        self.set_status("Çalıştırılıyor...")

        def do_run():
            params = self._get_params()
            self._zapret_service.run_once(mode=ZapretMode.NFQWS, params=params)
            return True

        def on_complete(result):
            self._update_status_indicator()
            if result:
                self.show_toast("Tek seferlik çalıştırıldı")
            self.set_status("")

        self.run_async(do_run, on_complete)

    def _on_remove(self, button):
        """Handle remove button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="Kaldır",
            body="GoodbyeDPI (nfqws) kaldırılacak. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("remove", "Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_remove_confirmed)
        dialog.present()

    def _on_remove_confirmed(self, dialog, response):
        """Handle remove confirmation."""
        if response == "remove":
            self.set_status("Kaldırılıyor...")

            def do_remove():
                self._zapret_service.stop()
                self._zapret_service.remove()
                return True

            def on_complete(result):
                self._update_status_indicator()
                if result:
                    self.show_toast("GoodbyeDPI kaldırıldı")
                self.set_status("")

            self.run_async(do_remove, on_complete)

    def _on_help(self, button):
        """Handle help button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="GoodbyeDPI Yardım",
            body="""GoodbyeDPI, Windows'ta WinDivert kullanır. Linux'ta bu işlev Zapret'in nfqws bileşeni tarafından sağlanır.

Hazır Ayarlar:
- Preset 1-6: Farklı DPI bypass stratejileri

Blacklist:
- Sadece belirli domainlere bypass uygular
- Her satıra bir domain yazın

Hizmet Kur: systemd servisi olarak çalıştırır
Tek Seferlik: Sadece bu oturum için çalıştırır

Not: Bu sayfa Zapret'in nfqws modunu kullanır.""",
        )
        dialog.add_response("ok", "Tamam")
        dialog.present()
