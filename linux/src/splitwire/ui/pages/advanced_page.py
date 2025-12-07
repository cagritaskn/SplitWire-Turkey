"""
Advanced Page for SplitWire-Turkey.

Provides service management and advanced options.
Equivalent to Windows "Gelişmiş" tab.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import TYPE_CHECKING, Dict, List

from splitwire.core import get_text
from splitwire.services import (
    get_wireguard_service,
    get_split_tunnel_service,
    get_zapret_service,
    get_byedpi_service,
    get_proxy_route_service,
    get_dns_service,
    ServiceStatus,
)
from .base_page import BasePage

if TYPE_CHECKING:
    from splitwire.ui.window import SplitWireWindow


class AdvancedPage(BasePage):
    """Advanced service management page."""

    def __init__(self, window: 'SplitWireWindow'):
        self._services = {
            "wireguard": {
                "name": "WireGuard",
                "service": get_wireguard_service(),
            },
            "split_tunnel": {
                "name": "Split Tunnel (cgproxy)",
                "service": get_split_tunnel_service(),
            },
            "zapret": {
                "name": "Zapret",
                "service": get_zapret_service(),
            },
            "byedpi": {
                "name": "ByeDPI",
                "service": get_byedpi_service(),
            },
            "proxy_route": {
                "name": "Proxy Route",
                "service": get_proxy_route_service(),
            },
            "dns": {
                "name": "DNS",
                "service": get_dns_service(),
            },
        }
        self._status_rows: Dict[str, dict] = {}
        super().__init__(window)

    def _build_ui(self):
        """Build the advanced page UI."""
        # Services group
        services_group = self.create_preferences_group(
            title=get_text("advanced", "services") or "Hizmetler"
        )
        self.append(services_group)

        # Create status row for each service
        for key, info in self._services.items():
            row = self._create_service_row(key, info["name"])
            services_group.add(row["row"])
            self._status_rows[key] = row

        # Refresh status
        self._refresh_all_status()

        # Options group
        options_group = self.create_preferences_group(
            title=get_text("advanced", "options") or "Seçenekler"
        )
        self.append(options_group)

        # Auto DNS switch
        self._switch_auto_dns = self.create_switch_row(
            title=get_text("advanced", "auto_dns") or "DNS ve DoH ayarlarını her kurulumda gerçekleştir",
            subtitle=get_text("tooltips", "auto_dns") or "WireGuard ve bypass kurulumlarında DNS'i otomatik ayarla",
            active=True,
        )
        options_group.add(self._switch_auto_dns)

        # Actions group
        actions_group = self.create_preferences_group(
            title=get_text("advanced", "actions") or "İşlemler"
        )
        self.append(actions_group)

        # Remove all services button
        self._btn_remove_all = self.create_action_button(
            label=get_text("advanced", "remove_all") or "Tüm Hizmetleri Kaldır",
            callback=self._on_remove_all,
            destructive=True,
        )
        actions_group.add(self._btn_remove_all)

        # Reset DNS button
        self._btn_reset_dns = self.create_action_button(
            label=get_text("advanced", "reset_dns") or "DNS ve DoH Ayarlarını Geri Al",
            callback=self._on_reset_dns,
            destructive=True,
        )
        actions_group.add(self._btn_reset_dns)

        # Uninstall SplitWire button
        self._btn_uninstall = self.create_action_button(
            label=get_text("advanced", "uninstall") or "SplitWire-Turkey'i Kaldır",
            callback=self._on_uninstall,
            destructive=True,
        )
        actions_group.add(self._btn_uninstall)

        # Logs section
        logs_group = self.create_preferences_group(
            title=get_text("advanced", "logs") or "Loglar"
        )
        self.append(logs_group)

        # Open logs button
        self._btn_open_logs = Gtk.Button(
            label=get_text("advanced", "open_logs") or "Logs Klasörünü Aç",
        )
        self._btn_open_logs.connect("clicked", self._on_open_logs)
        logs_group.add(self._btn_open_logs)

    def _create_service_row(self, key: str, name: str) -> dict:
        """Create a service status row."""
        row = Adw.ActionRow(
            title=name,
        )

        # Status indicator
        status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            valign=Gtk.Align.CENTER,
        )

        status_dot = Gtk.Label(
            label="●",
            css_classes=["status-stopped"],
        )
        status_box.append(status_dot)

        status_label = Gtk.Label(
            label=get_text("status", "checking") or "Kontrol ediliyor...",
        )
        status_box.append(status_label)

        row.add_suffix(status_box)

        # Remove button (hidden by default)
        remove_btn = Gtk.Button(
            label=get_text("buttons", "remove") or "Kaldır",
            css_classes=["destructive-action"],
            valign=Gtk.Align.CENTER,
            margin_start=8,
            visible=False,
        )
        remove_btn.set_name(key)  # Store service_key in widget name (GTK4 compatible)
        remove_btn.connect("clicked", self._on_remove_service)
        row.add_suffix(remove_btn)

        return {
            "row": row,
            "status_dot": status_dot,
            "status_label": status_label,
            "remove_btn": remove_btn,
        }

    def _update_service_status(self, key: str, status: ServiceStatus, installed: bool):
        """Update a service's status display."""
        if key not in self._status_rows:
            return

        row = self._status_rows[key]

        if status == ServiceStatus.RUNNING:
            row["status_dot"].set_css_classes(["status-running"])
            row["status_label"].set_label(get_text("status", "running") or "Çalışıyor")
            row["remove_btn"].set_visible(True)
        elif installed:
            row["status_dot"].set_css_classes(["status-stopped"])
            row["status_label"].set_label(get_text("status", "stopped") or "Durduruldu")
            row["remove_btn"].set_visible(True)
        else:
            row["status_dot"].set_css_classes(["status-stopped"])
            row["status_label"].set_label(get_text("status", "not_installed") or "Kurulu Değil")
            row["remove_btn"].set_visible(False)

    def _refresh_all_status(self):
        """Refresh all service statuses."""
        def do_refresh():
            results = {}
            for key, info in self._services.items():
                service = info["service"]
                try:
                    status = service.status()
                    installed = service.is_installed()
                    results[key] = (status, installed)
                except Exception as e:
                    self._logger.error(f"Error checking {key}: {e}")
                    results[key] = (ServiceStatus.UNKNOWN, False)
            return results

        def on_complete(results):
            for key, (status, installed) in results.items():
                self._update_service_status(key, status, installed)

        self.run_async(do_refresh, on_complete)

    def refresh(self):
        """Refresh page data."""
        self._refresh_all_status()

    def refresh_translations(self):
        """Refresh UI translations."""
        self._switch_auto_dns.set_title(get_text("advanced", "auto_dns") or "DNS ve DoH ayarlarını her kurulumda gerçekleştir")
        self._btn_remove_all.set_label(get_text("advanced", "remove_all") or "Tüm Hizmetleri Kaldır")
        self._btn_reset_dns.set_label(get_text("advanced", "reset_dns") or "DNS ve DoH Ayarlarını Geri Al")
        self._btn_uninstall.set_label(get_text("advanced", "uninstall") or "SplitWire-Turkey'i Kaldır")

    # Event handlers

    def _on_remove_service(self, button):
        """Handle individual service remove button."""
        key = button.get_name()  # Get service_key from widget name (GTK4 compatible)
        info = self._services.get(key)
        if not info:
            return

        name = info["name"]
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="Kaldır",
            body=f"{name} kaldırılacak. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("remove", "Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        self._pending_remove_key = key  # Store in instance variable (GTK4 compatible)
        dialog.connect("response", self._on_service_remove_confirmed)
        dialog.present()

    def _on_service_remove_confirmed(self, dialog, response):
        """Handle service remove confirmation."""
        if response == "remove":
            key = self._pending_remove_key  # Use instance variable (GTK4 compatible)
            info = self._services.get(key)
            if not info:
                return

            self.set_status(f"{info['name']} kaldırılıyor...")

            def do_remove():
                service = info["service"]
                service.stop()
                service.remove()
                return True

            def on_complete(result):
                self._refresh_all_status()
                if result:
                    self.show_toast(f"{info['name']} kaldırıldı")
                self.set_status("")

            self.run_async(do_remove, on_complete)

    def _on_remove_all(self, button):
        """Handle remove all services button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="Tüm Hizmetleri Kaldır",
            body="Tüm SplitWire hizmetleri kaldırılacak. Bu işlem geri alınamaz. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("remove", "Tümünü Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_remove_all_confirmed)
        dialog.present()

    def _on_remove_all_confirmed(self, dialog, response):
        """Handle remove all confirmation."""
        if response == "remove":
            self.set_status("Tüm hizmetler kaldırılıyor...")

            def do_remove_all():
                for key, info in self._services.items():
                    try:
                        service = info["service"]
                        service.stop()
                        service.remove()
                    except Exception as e:
                        self._logger.error(f"Error removing {key}: {e}")
                return True

            def on_complete(result):
                self._refresh_all_status()
                if result:
                    self.show_toast("Tüm hizmetler kaldırıldı")
                self.set_status("")

            self.run_async(do_remove_all, on_complete)

    def _on_reset_dns(self, button):
        """Handle reset DNS button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="DNS Ayarlarını Sıfırla",
            body="DNS ayarları varsayılana döndürülecek. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("reset", "Sıfırla")
        dialog.set_response_appearance("reset", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_reset_dns_confirmed)
        dialog.present()

    def _on_reset_dns_confirmed(self, dialog, response):
        """Handle DNS reset confirmation."""
        if response == "reset":
            self.set_status("DNS ayarları sıfırlanıyor...")

            def do_reset():
                dns_service = self._services["dns"]["service"]
                dns_service.restore_backup()
                return True

            def on_complete(result):
                self._refresh_all_status()
                if result:
                    self.show_toast("DNS ayarları sıfırlandı")
                self.set_status("")

            self.run_async(do_reset, on_complete)

    def _on_uninstall(self, button):
        """Handle uninstall SplitWire button."""
        dialog = Adw.MessageDialog(
            transient_for=self._window,
            heading="SplitWire-Turkey'i Kaldır",
            body="SplitWire-Turkey ve tüm bileşenleri kaldırılacak. Bu işlem geri alınamaz. Devam etmek istiyor musunuz?",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("uninstall", "Kaldır")
        dialog.set_response_appearance("uninstall", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_uninstall_confirmed)
        dialog.present()

    def _on_uninstall_confirmed(self, dialog, response):
        """Handle uninstall confirmation."""
        if response == "uninstall":
            self.set_status("SplitWire-Turkey kaldırılıyor...")

            def do_uninstall():
                # Remove all services first
                for key, info in self._services.items():
                    try:
                        service = info["service"]
                        service.stop()
                        service.remove()
                    except Exception as e:
                        self._logger.error(f"Error removing {key}: {e}")

                # Remove config and data directories
                import shutil
                import os

                config_dir = os.path.expanduser("~/.config/splitwire")
                data_dir = os.path.expanduser("~/.local/share/splitwire")
                cache_dir = os.path.expanduser("~/.cache/splitwire")

                for dir_path in [config_dir, data_dir, cache_dir]:
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)

                return True

            def on_complete(result):
                if result:
                    self.show_toast("SplitWire-Turkey kaldırıldı. Uygulamayı kapatın.")
                    # Quit the application
                    app = self._window.get_application()
                    if app:
                        GLib.timeout_add(2000, app.quit)
                self.set_status("")

            self.run_async(do_uninstall, on_complete)

    def _on_open_logs(self, button):
        """Handle open logs button."""
        import subprocess
        import os

        logs_dir = os.path.expanduser("~/.cache/splitwire/logs")
        os.makedirs(logs_dir, exist_ok=True)

        try:
            subprocess.Popen(["xdg-open", logs_dir])
        except Exception as e:
            self._logger.error(f"Error opening logs: {e}")
            self.show_toast(f"Hata: {e}")
