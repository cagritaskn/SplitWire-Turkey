"""
Zapret Page for SplitWire-Turkey.

Provides Zapret DPI bypass setup with blockcheck integration.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import TYPE_CHECKING

from splitwire.core import get_text
from splitwire.services import (
    get_zapret_service,
    get_blockcheck_service,
    ServiceStatus,
    ScanMode,
    DEFAULT_PRESETS,
)
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class ZapretPage(BasePage):
    """Zapret DPI bypass setup page."""

    def __init__(self, window: 'SplitWireWindow'):
        self._zapret_service = get_zapret_service()
        self._blockcheck_service = get_blockcheck_service()
        self._scan_in_progress = False
        super().__init__(window)

    def _build_ui(self):
        """Build the Zapret page UI."""
        # Status indicator
        self._status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=8,
            margin_bottom=8,
        )
        self.append(self._status_box)
        self._update_status_indicator()

        # Auto setup group
        auto_group = self.create_preferences_group(
            title=get_text("zapret", "auto_setup") or "Otomatik Kurulum"
        )
        self.append(auto_group)

        # Auto setup button
        self._btn_auto = self.create_action_button(
            label=get_text("zapret", "auto_install") or "Zapret Otomatik Kurulum",
            callback=self._on_auto_setup,
            tooltip=get_text("tooltips", "zapret_auto") or "Blockcheck ile en uygun ayarları otomatik bul",
            suggested=True,
        )
        auto_group.add(self._btn_auto)

        # Scan level selection
        self._combo_scan = self.create_combo_row(
            title=get_text("zapret", "scan_level") or "Tarama",
            items=[
                get_text("zapret", "scan_quick") or "Hızlı",
                get_text("zapret", "scan_standard") or "Standart",
                get_text("zapret", "scan_full") or "Tam",
            ],
            selected=1,
        )
        auto_group.add(self._combo_scan)

        # Progress indicator (hidden by default)
        self._progress_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=8,
            visible=False,
        )
        auto_group.add(self._progress_box)

        self._progress_bar = Gtk.ProgressBar(
            show_text=True,
        )
        self._progress_box.append(self._progress_bar)

        self._progress_label = Gtk.Label(
            css_classes=["dim-label"],
        )
        self._progress_box.append(self._progress_label)

        # Presets group
        presets_group = self.create_preferences_group(
            title=get_text("zapret", "presets") or "Hazır Ayarlar"
        )
        self.append(presets_group)

        # Preset selection
        preset_names = list(DEFAULT_PRESETS.keys())
        self._combo_preset = self.create_combo_row(
            title=get_text("zapret", "preset") or "Hazır Ayar",
            items=preset_names,
            selected=0,
            callback=self._on_preset_changed,
        )
        presets_group.add(self._combo_preset)

        # Edit preset expander
        self._edit_expander = Adw.ExpanderRow(
            title=get_text("zapret", "edit_preset") or "Hazır ayarı düzenle",
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
        self._txt_params.set_size_request(-1, 100)

        # Set default preset params
        if preset_names:
            first_preset = DEFAULT_PRESETS.get(preset_names[0])
            if first_preset:
                buffer = self._txt_params.get_buffer()
                buffer.set_text(first_preset.params)

        scroll = Gtk.ScrolledWindow(
            child=self._txt_params,
            min_content_height=100,
        )
        params_row.set_child(scroll)

        # Service buttons
        buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=16,
            margin_top=16,
        )
        self.append(buttons_box)

        # Install service button
        self._btn_service = Gtk.Button(
            label=get_text("zapret", "install_service") or "Önayarlı Hizmet Kur",
            tooltip_text=get_text("tooltips", "preset_service") or "Seçili ayarla sistemd hizmeti kur",
        )
        self._btn_service.connect("clicked", self._on_install_service)
        buttons_box.append(self._btn_service)

        # One-time run button
        self._btn_once = Gtk.Button(
            label=get_text("zapret", "run_once") or "Önayarlı Tek Seferlik",
            tooltip_text=get_text("tooltips", "preset_once") or "Seçili ayarı tek seferlik çalıştır",
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
            label=get_text("zapret", "remove") or "Zapret'i Kaldır",
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

    def refresh(self):
        """Refresh page data."""
        self._update_status_indicator()

    def refresh_translations(self):
        """Refresh UI translations."""
        self._btn_auto.set_label(get_text("zapret", "auto_install") or "Zapret Otomatik Kurulum")
        self._btn_service.set_label(get_text("zapret", "install_service") or "Önayarlı Hizmet Kur")
        self._btn_once.set_label(get_text("zapret", "run_once") or "Önayarlı Tek Seferlik")
        self._btn_remove.set_label(get_text("zapret", "remove") or "Zapret'i Kaldır")

    # Event handlers

    def _on_auto_setup(self, button):
        """Handle auto setup (blockcheck)."""
        if self._scan_in_progress:
            return

        self._scan_in_progress = True
        self._progress_box.set_visible(True)
        self._btn_auto.set_sensitive(False)

        # Get scan mode
        scan_idx = self._combo_scan.get_selected()
        scan_modes = [ScanMode.QUICK, ScanMode.STANDARD, ScanMode.FULL]
        scan_mode = scan_modes[scan_idx]

        def do_scan():
            # Install zapret first if needed
            if not self._zapret_service.is_installed():
                GLib.idle_add(self._update_progress, 0.1, "Zapret kuruluyor...")
                self._zapret_service.install()

            # Run blockcheck
            GLib.idle_add(self._update_progress, 0.2, "Tarama başlatılıyor...")

            result = self._blockcheck_service.start_scan(
                mode=scan_mode,
                progress_callback=self._on_scan_progress
            )

            return result

        def on_complete(result):
            self._scan_in_progress = False
            self._progress_box.set_visible(False)
            self._btn_auto.set_sensitive(True)

            if result and result.best_strategy:
                # Apply best strategy
                self._zapret_service.configure(params=result.best_strategy.params)
                self._zapret_service.start()
                self._update_status_indicator()
                self.show_toast(f"En iyi strateji bulundu: {result.best_strategy.name}")
            else:
                self.show_toast("Uygun strateji bulunamadı")

        self.run_async(do_scan, on_complete)

    def _on_scan_progress(self, progress):
        """Handle scan progress updates."""
        GLib.idle_add(
            self._update_progress,
            progress.percent / 100.0,
            f"Test ediliyor: {progress.current_strategy}"
        )

    def _update_progress(self, fraction, text):
        """Update progress bar."""
        self._progress_bar.set_fraction(fraction)
        self._progress_bar.set_text(f"%{int(fraction * 100)}")
        self._progress_label.set_label(text)

    def _on_preset_changed(self, row, param):
        """Handle preset selection change."""
        selected = row.get_selected()
        preset_names = list(DEFAULT_PRESETS.keys())

        if selected < len(preset_names):
            preset_name = preset_names[selected]
            preset = DEFAULT_PRESETS.get(preset_name)
            if preset:
                buffer = self._txt_params.get_buffer()
                buffer.set_text(preset.params)

    def _on_install_service(self, button):
        """Handle install service button."""
        self.set_status("Hizmet kuruluyor...")

        def do_install():
            # Get params
            buffer = self._txt_params.get_buffer()
            start, end = buffer.get_bounds()
            params = buffer.get_text(start, end, False)

            # Install and configure
            if not self._zapret_service.is_installed():
                self._zapret_service.install()

            self._zapret_service.configure(params=params)
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
            buffer = self._txt_params.get_buffer()
            start, end = buffer.get_bounds()
            params = buffer.get_text(start, end, False)

            self._zapret_service.run_once(params=params)
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
            body="Zapret kaldırılacak. Devam etmek istiyor musunuz?",
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
                    self.show_toast("Zapret kaldırıldı")
                self.set_status("")

            self.run_async(do_remove, on_complete)

    def _on_help(self, button):
        """Handle help button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="Zapret Yardım",
            body="""Zapret, DPI (Deep Packet Inspection) engellerini aşmak için paket manipülasyonu yapar.

Otomatik Kurulum: Blockcheck ile en uygun ayarları test eder ve uygular.

Tarama Seviyeleri:
- Hızlı: 3 temel strateji
- Standart: 7 strateji
- Tam: 12+ strateji

Hazır Ayarlar:
- Turkey Discord: Discord için optimize edilmiş
- Turkey General: Genel kullanım
- Turkey YouTube: YouTube için optimize edilmiş

Hizmet Kur: systemd servisi olarak çalıştırır
Tek Seferlik: Sadece bu oturum için çalıştırır""",
        )
        dialog.add_response("ok", "Tamam")
        dialog.present()
