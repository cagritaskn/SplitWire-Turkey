# SplitWire-Turkey Linux

Linux icin kapsamli bir ag kisitlamasi asim araci. DPI asimi ve ayrik tunelleme ozellikleri saglar.

## Ozellikler

- **WireGuard VPN** - Cloudflare WARP ile ayrik tunelleme destegi
- **DPI Asimi** - Zapret/nfqws kullanarak (Linux icin GoodbyeDPI karsiligi)
- **ByeDPI Proxy** - cgroups ile uygulamaya ozel yonlendirme
- **DNS Yonetimi** - DoH (DNS over HTTPS) destegi
- **Discord Onarim** - Alternatif istemci kurulumu
- **Modern GTK4/Libadwaita** arayuzu
- **Coklu dil** destegi (Turkce, Ingilizce, Rusca, Ispanyolca)
- **systemd Entegrasyonu** - Kalici hizmetler

## Ekran Goruntuleri

*Yakinda*

## Sistem Gereksinimleri

- **Isletim Sistemi**: Ubuntu 22.04+, Debian 12+, Linux Mint 21+, Pop!_OS 22.04+
- **Mimari**: x86_64 (amd64)
- **Python**: 3.10+
- **Masaustu**: GTK4 + Libadwaita destegi

## Kurulum

### Hizli Kurulum (Onerilen)

```bash
curl -sSL https://raw.githubusercontent.com/cagritaskn/SplitWire-Turkey/main/linux/scripts/install.sh | sudo bash
```

### Manuel Kurulum

1. **Bagimlikari yukleyin:**
   ```bash
   sudo ./scripts/setup-deps.sh
   ```

2. **Kurulum scriptini calistirin:**
   ```bash
   sudo ./scripts/install.sh
   ```

### Debian Paketi

```bash
# Paketi derleyin
dpkg-buildpackage -us -uc -b

# Yukleyin
sudo dpkg -i ../splitwire-turkey_1.0.0_all.deb
sudo apt-get install -f  # Bagimliliklari yukle
```

## Kullanim

### Uygulamayi Baslatma

```bash
# Terminalden
splitwire

# Veya uygulama menusunden
# "SplitWire" arayin
```

### Asim Yontemleri

#### 1. WireGuard (Ayrik Tunelleme)

Cloudflare WARP'i WireGuard ile kullanarak yalnizca belirli uygulamalari VPN uzerinden yonlendirir.

1. SplitWire'i acin
2. "Ana Sayfa"ya gidin
3. "WireGuard Kur" butonuna tiklayin
4. Ayrik tunelleme icin uygulamalari secin

#### 2. Zapret (Sistem Geneli DPI Asimi)

DPI incelemesini asmak icin paket manipulasyonu yapan nfqws kullanir.

1. "Zapret" sayfasina gidin
2. Hazir ayar secin veya "Otomatik Tarama" calistirin
3. "Hizmet Kur" butonuna tiklayin

**Hazir Ayarlar:**
- `turkey_discord` - Discord icin optimize
- `turkey_general` - Genel amacli
- `turkey_youtube` - YouTube icin optimize
- `preset_split` - Split modu
- `preset_fake` - Sahte paket modu
- `preset_disorder` - Disorder modu

#### 3. ByeDPI (Uygulamaya Ozel)

Belirli uygulamalari yerel SOCKS5 proxy uzerinden yonlendirir.

1. "ByeDPI" sayfasina gidin
2. Yonlendirilecek uygulamalari secin
3. "Baslat" butonuna tiklayin

### DNS Yapilandirmasi

1. "Gelismis" sayfasina gidin
2. DNS saglayicisini secin (Cloudflare, Google, Quad9)
3. DoH'u (DNS over HTTPS) etkinlestirin/devre disi birakin
4. "DNS Uygula" butonuna tiklayin

### Discord Onarim

Discord "Checking for updates" ekraninda takiliyorsa:

1. "Onarim" sayfasina gidin
2. "Discord Onar" secenegini deneyin
3. Basarisiz olursa alternatif istemcileri kurun

## Hizmetler

SplitWire asagidaki systemd hizmetlerini olusturur:

| Hizmet | Aciklama |
|--------|----------|
| `splitwire-wg.service` | WireGuard VPN tuneli |
| `splitwire-wg-refresh.timer` | Periyodik baglanti yenileme |
| `splitwire-zapret.service` | Zapret DPI asimi |
| `splitwire-byedpi.service` | ByeDPI proxy |
| `splitwire-cgproxy.service` | Uygulama yonlendirme |

**Hizmetleri yonetme:**
```bash
# Durumu kontrol et
systemctl status splitwire-wg

# Loglari goruntule
journalctl -u splitwire-zapret -f

# Tum hizmetleri durdur
sudo systemctl stop splitwire-wg splitwire-zapret splitwire-byedpi
```

## Kaldirma

### Kaldirma Scripti Kullanarak

```bash
sudo ./scripts/uninstall.sh
```

### Secenekler

```bash
# Yapilandirma dosyalarini koru
sudo ./scripts/uninstall.sh --keep-config

# Zapret kurulumunu koru
sudo ./scripts/uninstall.sh --keep-zapret

# Kullanici verileri dahil tam kaldirma
sudo ./scripts/uninstall.sh --purge
```

### Debian Paketi

```bash
# Paketi kaldir
sudo apt remove splitwire-turkey

# Yapilandirma ile birlikte kaldir
sudo apt purge splitwire-turkey
```

## Sorun Giderme

### "Register failed" Hatasi

Cloudflare API bolgenizde engellenebilir. Deneyin:
1. Kayit olmak icin gecici olarak VPN kullanin
2. Alternatif asim yontemlerini kullanin (Zapret, ByeDPI)

### Discord "Checking for updates" Ekraninda Takili Kalma

1. Modeminizi yeniden baslatin (15-30 saniye bekleyin)
2. Bilgisayarinizi yeniden baslatin
3. SplitWire'daki Discord Onarim'i kullanin
4. Discord PTB veya WebCord kurmayi deneyin

### Hizmetler Baslamiyor

```bash
# Hizmet durumunu kontrol et
systemctl status splitwire-wg

# Loglari kontrol et
journalctl -u splitwire-wg -n 50

# systemd'yi yeniden yukle
sudo systemctl daemon-reload
```

### Izin Sorunlari

`splitwire` grubunda oldugunuzdan emin olun:
```bash
sudo usermod -aG splitwire $USER
# Cikis yapin ve tekrar giris yapin
```

## Yapilandirma

Yapilandirma dosyalari:
- Sistem: `/etc/splitwire/`
- Kullanici: `~/.config/splitwire/`

### Ana Yapilandirma (`config.json`)

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

DPI asimi icin domainler (satirda bir tane):
```
discord.com
discord.gg
discordapp.com
```

## Kaynaktan Derleme

### Gereksinimler

- Python 3.10+
- GTK4 gelistirme kutuphaneleri
- PyGObject

### Adimlar

```bash
# Repoyu klonlayin
git clone https://github.com/cagritaskn/SplitWire-Turkey.git
cd SplitWire-Turkey/linux

# Bagimliliklari yukleyin
sudo ./scripts/setup-deps.sh

# Gelistirme modunda yukleyin
pip install -e .

# Calistirin
python -m splitwire
```

## Katki

1. Repoyu forklayim
2. Ozellik dalı olusturun
3. Degisikliklerinizi yapin
4. Pull request gonderin

## Lisans

```
Telif Hakki (c) 2025 Cagri Taskin

Bu proje MIT Lisansi altinda lisanslanmistir.
Detaylar icin LICENSE dosyasina bakin.
```

## Tesekkurler

- **[wgcf](https://github.com/ViRb3/wgcf)** - ViRb3
- **[zapret](https://github.com/bol-van/zapret)** - bol-van
- **[ciadpi](https://github.com/hufrea/byedpi)** - hufrea
- **[cgproxy](https://github.com/springzfx/cgproxy)** konsepti

## Sorumluluk Reddi

**Bu yazilim egitim amaciyla olusturulmustur.**

- Bu arac yalnizca kodlama egitimi ve kisisel kullanim amacidir
- Ticari kullanim icin uygun degildir
- Gelistirici, bu yazilimin kullanimindan dogabilecek herhangi bir zarardan sorumlu degildir
- Kullanicilar bu yazilimi kendi sorumluluklarinda kullanirlar
- Yasal duzenlemelere uygun kullanim kullanicinin sorumluluğundadir
