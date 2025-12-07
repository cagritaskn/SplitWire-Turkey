# SplitWire-Turkey Linux

A comprehensive network restriction bypass tool for Linux, providing DPI bypass and split tunneling capabilities.

## Features

- **WireGuard VPN** with split tunneling support via Cloudflare WARP
- **DPI Bypass** using Zapret/nfqws (GoodbyeDPI equivalent for Linux)
- **ByeDPI Proxy** for application-specific routing via cgroups
- **DNS Management** with DoH (DNS over HTTPS) support
- **Discord Repair** and alternative client installation
- **Modern GTK4/Libadwaita** interface
- **Multi-language** support (Turkish, English, Russian, Spanish)
- **systemd Integration** for persistent services

## Screenshots

*Coming soon*

## System Requirements

- **OS**: Ubuntu 22.04+, Debian 12+, Linux Mint 21+, Pop!_OS 22.04+
- **Architecture**: x86_64 (amd64)
- **Python**: 3.10+
- **Desktop**: GTK4 + Libadwaita support

## Installation

### Quick Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/cagritaskn/SplitWire-Turkey/main/linux/scripts/install.sh | sudo bash
```

### Manual Installation

1. **Install dependencies:**
   ```bash
   sudo ./scripts/setup-deps.sh
   ```

2. **Run installer:**
   ```bash
   sudo ./scripts/install.sh
   ```

### Debian Package

```bash
# Build the package
dpkg-buildpackage -us -uc -b

# Install
sudo dpkg -i ../splitwire-turkey_1.0.0_all.deb
sudo apt-get install -f  # Install dependencies
```

## Usage

### Starting the Application

```bash
# From terminal
splitwire

# Or from application menu
# Search for "SplitWire"
```

### Bypass Methods

#### 1. WireGuard (Split Tunneling)

Uses Cloudflare WARP via WireGuard with split tunneling to route only specific applications through VPN.

1. Open SplitWire
2. Go to "Ana Sayfa" (Main Page)
3. Click "WireGuard Kur" (Install WireGuard)
4. Select applications for split tunneling

#### 2. Zapret (System-wide DPI Bypass)

Uses nfqws for packet manipulation to bypass DPI inspection.

1. Go to "Zapret" page
2. Choose a preset or run "Otomatik Tarama" (Auto Scan)
3. Click "Hizmet Kur" (Install Service)

**Presets:**
- `turkey_discord` - Optimized for Discord
- `turkey_general` - General purpose
- `turkey_youtube` - Optimized for YouTube
- `preset_split` - Split mode
- `preset_fake` - Fake packet mode
- `preset_disorder` - Disorder mode

#### 3. ByeDPI (Application-specific)

Routes specific applications through a local SOCKS5 proxy.

1. Go to "ByeDPI" page
2. Select applications to route
3. Click "Başlat" (Start)

### DNS Configuration

1. Go to "Gelişmiş" (Advanced) page
2. Select DNS provider (Cloudflare, Google, Quad9)
3. Enable/disable DoH (DNS over HTTPS)
4. Click "DNS Uygula" (Apply DNS)

### Discord Repair

If Discord is stuck on "Checking for updates":

1. Go to "Onarım" (Repair) page
2. Try "Discord Onar" (Repair Discord)
3. If unsuccessful, try installing alternative clients

## Services

SplitWire creates the following systemd services:

| Service | Description |
|---------|-------------|
| `splitwire-wg.service` | WireGuard VPN tunnel |
| `splitwire-wg-refresh.timer` | Periodic connection refresh |
| `splitwire-zapret.service` | Zapret DPI bypass |
| `splitwire-byedpi.service` | ByeDPI proxy |
| `splitwire-cgproxy.service` | Application routing |

**Managing services:**
```bash
# Check status
systemctl status splitwire-wg

# View logs
journalctl -u splitwire-zapret -f

# Stop all services
sudo systemctl stop splitwire-wg splitwire-zapret splitwire-byedpi
```

## Uninstallation

### Using Uninstaller

```bash
sudo ./scripts/uninstall.sh
```

### Options

```bash
# Keep configuration files
sudo ./scripts/uninstall.sh --keep-config

# Keep Zapret installation
sudo ./scripts/uninstall.sh --keep-zapret

# Full removal including user data
sudo ./scripts/uninstall.sh --purge
```

### Debian Package

```bash
# Remove package
sudo apt remove splitwire-turkey

# Remove with configuration
sudo apt purge splitwire-turkey
```

## Troubleshooting

### "Register failed" Error

Cloudflare API may be blocked in your region. Try:
1. Use a VPN temporarily to register
2. Use alternative bypass methods (Zapret, ByeDPI)

### Discord Stuck on "Checking for updates"

1. Restart your router (wait 15-30 seconds)
2. Restart your computer
3. Use Discord Repair in SplitWire
4. Try installing Discord PTB or WebCord

### Services Not Starting

```bash
# Check service status
systemctl status splitwire-wg

# Check logs
journalctl -u splitwire-wg -n 50

# Reload systemd
sudo systemctl daemon-reload
```

### Permission Issues

Ensure you're in the `splitwire` group:
```bash
sudo usermod -aG splitwire $USER
# Log out and back in
```

## Configuration

Configuration files are stored in:
- System: `/etc/splitwire/`
- User: `~/.config/splitwire/`

### Main Config (`config.json`)

```json
{
    "version": "1.0.0",
    "language": "tr",
    "theme": "system",
    "auto_dns": true,
    "dns_server": "cloudflare",
    "doh_enabled": true
}
```

### Blacklist (`blacklist.txt`)

Domains for DPI bypass (one per line):
```
discord.com
discord.gg
discordapp.com
```

## Building from Source

### Requirements

- Python 3.10+
- GTK4 development libraries
- PyGObject

### Steps

```bash
# Clone repository
git clone https://github.com/cagritaskn/SplitWire-Turkey.git
cd SplitWire-Turkey/linux

# Install dependencies
sudo ./scripts/setup-deps.sh

# Install in development mode
pip install -e .

# Run
python -m splitwire
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

```
Copyright (c) 2025 Cagri Taskin

This project is licensed under the MIT License.
See LICENSE file for details.
```

## Credits

- **[wgcf](https://github.com/ViRb3/wgcf)** by ViRb3
- **[zapret](https://github.com/bol-van/zapret)** by bol-van
- **[ciadpi](https://github.com/hufrea/byedpi)** by hufrea
- **[cgproxy](https://github.com/springzfx/cgproxy)** concept

## Disclaimer

**This software is for educational purposes only.**

- This tool is for coding education and personal use only
- Not intended for commercial use
- The developer is not responsible for any damage from using this software
- Users use this software at their own risk
- Compliance with legal regulations is the user's responsibility
