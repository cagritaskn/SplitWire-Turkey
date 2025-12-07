<p align="center">
  <img width="auto" height="128" src="https://github.com/cagritaskn/SplitWire-Turkey/blob/main/src/SplitWireTurkey/Resources/splitwire-logo-128.png">
</p>

# <p align="center"><strong>SplitWire-Turkey Linux</strong></p>

<div align="center">

> [!WARNING]
> **🚧 GELİŞTİRME AŞAMASINDA / UNDER DEVELOPMENT 🚧**
>
> Bu repo, SplitWire-Turkey'in Linux sürümünü içermektedir. Proje henüz tamamlanmamıştır ve aktif olarak geliştirilmektedir. Kullanıma hazır değildir.
>
> This repository contains the Linux version of SplitWire-Turkey. The project is not yet complete and is actively under development. It is not ready for use.

<strong>Multilingual README (TR/EN/RU/ES)</strong>

[![TR](https://img.shields.io/badge/README-TR-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)
[![EN](https://img.shields.io/badge/README-EN-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)
[![RU](https://img.shields.io/badge/README-RU-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)
[![ES](https://img.shields.io/badge/README-ES-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

</div>

# SplitWire-Turkey

**SplitWire-Turkey**, Türkiye'deki internet kullanıcıları için özel olarak tasarlanmış bir DPI aşımı ve tünelleme otomasyonu projesidir. İnternet bağlantı hızınızı etkilemeden kısıt aşımı yapmaya yarayan açık kaynak bir Windows uygulamasıdır. Bu araç, tek bir arayüzden birçok kısıt aşım yöntemini otomatik olarak kurmaya ve yönetmeye yarar. Hizmet kurulumu yaptığı için bilgisayarınızı yeniden başlattığınızda ilgili uygulamalara erişmek için fazladan bir işlem yapmanıza gerek kalmaz. Tamamen açık kaynak kodlu olan bu uygulamanın kaynak kodları repository'de bulunan /src klasörünün içinde mevcuttur.

---

## Videolu Kullanım Rehberi
**Recep Baltaş'ın hazırladığı aşağıdaki videolu rehberden kurulum ve kullanım talimatlarını takip edebilirsiniz:**

<a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <img src="https://img.youtube.com/vi/LtwsTy568rw/maxresdefault.jpg" width="310"> </a> <br> <a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <strong>SplitWire-Turkey Videolu Kullanım Rehberi</strong> </a>

---

# İndirme ve Kurulum 

## Setup Dosyası ile Kurulum (Tavsiye Edilir) [![Download Setup](https://img.shields.io/badge/Download-Setup-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-Setup-Windows-1.5.5.exe)
- **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-Setup-Windows-1.5.5.exe)** kurulum paketini indirip SplitWire-Turkey kurulumunu gerçekleştirin. (SmartScreen "Windows kişisel bilgisayarınızı korudu" uyarısı alırsanız "Ek bilgi" yazısına tıkladıktan sonra "Yine de çalıştır" butonuna tıklayın, virüs taraması ve bu uyarı hakkında bilgi aşağıda verilmiştir)
- **SplitWire-Turkey** uygulamasını açın. 
- Uygulamanın kullanımı için **Kullanım Rehberleri** başlığını takip edin.

## ZIP Dosyası ile Kullanım (Tavsiye Edilmez) [![Download ZIP](https://img.shields.io/badge/Download-ZIP-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-ZIP-Windows-1.5.5.zip)
- **[SplitWire-Turkey ZIP](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-ZIP-Windows-1.5.5.zip)** dosyasını indirerek bir klasöre ayıklayın. 
- ZIP dosyasını ayıkladığınız klasörde bulunan **SplitWire-Turkey.exe** uygulamasını açın. (SmartScreen "Windows kişisel bilgisayarınızı korudu" uyarısı alırsanız "Ek bilgi" yazısına tıkladıktan sonra "Yine de çalıştır" butonuna tıklayın, virüs taraması ve bu uyarı hakkında bilgi aşağıda verilmiştir)
- Uygulamanın kullanımı için **Kullanım Rehberleri** başlığını takip edin.

**Not:** WebCord'u program içerisinden indirme esnasında sorun yaşarsanız WebCord'un halihazırda SplitWire-Turkey ile birleştirilmiş [SplitWire-Turkey-ZIP-Windows-1.5.5-WebCord-Included.zip](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-ZIP-Windows-1.5.5-WebCord-Included.zip)  dosyasını indirerek kullanabilirsiniz.



---

# Kullanım Rehberleri

## WireSock Kullanımı

**Not:** Bu bölümdeki kurulumlar, yalnızca Discord uygulaması için (Eğer tarayıcı tünellemesini aktifleştirdiyseniz tarayıcılar da dahil) çalışır. Bu kurulumları gerçekleştirdikten sonra sisteminizi her yeniden başlatışınızda ilgili yöntem otomatik olarak çalışmaya başlar.

- **WS Standart Kurulum:** Wgcf ve WireSock 2.4.23.1 araçlarını kullanarak yalnızca Discord için tünelleme gerçekleştirir. (Tarayıcılar için de tünelleme yap seçeneği açık ise internet tarayıcılarında da tünelleme yapılır)

- **WS Alternatif Kurulum:** Wgcf ve WireSock 1.4.7.1 araçlarını kullanarak YALNIZCA Discord için tünelleme gerçekleştirilir. (Tarayıcılar için de tünelleme yap seçeneği açık ise internet tarayıcılarında da tünelleme yapılır)

- **Tarayıcılar için de tünelleme yap:** Discord uygulaması yanında; Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi, Zen, Chromium ve Edge gibi popüler internet tarayıcıları için de tünelleme yapılır.

- **WireSock yineleyici kur:** WireSock'u belirli aralıklarla yeniden başlatan WTS görevini oluşturur. Yalnızca sorun yaşarsanız aktifleştirip kurulum yapın. Bu Windows Task Scheduler görevi, WireSock hizmetini belirli aralıklarla yeniden başlatır.

- **Klasör listesini özelleştir:** Discord haricinde bir uygulama için tünelleme yapmak isterseniz bu bölümü kullanabilirsiniz.
  - **Klasör Ekle:** Tünelleyeceğiniz uygulamanın bulunduğu klasörü seçerek listeye ekler.
  - **Listeyi Temizle:** Klasör listesini temizler.
  - **Özel Kurulum:** Hazırladığın klasör listesi için Wgcf ve WireSock kullanarak kurulum yapar.
  - **Özel Config Oluştur:** Hazırladığınız klasör listesi için konfigürasyon dosyası oluşturur.

- **Çıkış:** Programı kapatır.

**Not 2:** Eğer Discord uygulaması Checking for updates… ekranında kalırsa modeminizi kapatıp 15 saniye bekledikten sonra tekrar açın ve ardından bilgisayarınızı yeniden başlatın.

---

## ByeDPI Sayfası Kullanımı 

**Not:** Bu bölümdeki kurulumlar, yalnızca Discord uygulaması için (Eğer tarayıcı tünellemesini aktifleştirdiyseniz tarayıcılar da dahil) çalışır. Bu kurulumları gerçekleştirdikten sonra sisteminizi her yeniden başlatışınızda ilgili yöntem otomatik olarak çalışmaya başlar.

- **ByeDPI Split Tunneling Kurulum:** ByeDPI ve ProxiFyre araçlarını kullanarak yalnızca Discord uygulaması için DPI aşımı gerçekleştirilir. (Tarayıcılar için de tünelleme yap seçeneği açık ise internet tarayıcılarında da DPI aşımı yapılır)

- **Tarayıcılar için de tünelleme yap:** Discord uygulaması yanında; Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi ve Edge gibi popüler internet tarayıcıları için de DPI aşımı yapılır. Tarayıcılar için tünelleme seçeneğini değiştirip tekrar kurulum yapmak için önce ByeDPI' Kaldır butonuna tıklayarak ByeDPI'ı kaldırmalısınız.

- **ByeDPI DLL Kurulum:** ByeDPI ve drover (DLL hijacking yöntemi) kullanılarak **YALNIZCA** Discord uygulaması için DPI aşımı gerçekleştirilir. Bu yöntem yalnızca Discord uygulaması için çalışır, tarayıcılar veya diğer programlar için çalışmaz.

- **ByeDPI'ı Kaldır:** ByeDPI'ı kaldırıp drover dosyalarını siler.

**Not 2:** Eğer Discord uygulaması Checking for updates… ekranında kalırsa modeminizi kapatıp 15 saniye bekledikten sonra tekrar açın ve ardından bilgisayarınızı yeniden başlatın.

---

## Zapret Sayfası Kullanımı 

**Not:** Bu bölümdeki kurulumlar, sistem geneli çalışır. Hız kaybına sebep olmasa da bazı web site ve uygulamalarda bağlantı sorunlarına yol açabilir. Bu kurulumları gerçekleştirdikten sonra sisteminizi her yeniden başlatışınızda ilgili yöntem otomatik olarak çalışmaya başlar.

- **Zapret Otomatik Kurulum:** Zapret'in blockcheck isimli strateji bulma yazılımı ile sisteminiz ve internet servis sağlayıcınız için ideal parametreler bulunur ve bu parametreler ile Zapret kurulumu yapılarak DPI aşımı sağlanır.

- **Tarama:** İdeal parametreleri bulmak için gerçekleştirilen taramanın hızını seçer.
  - **Hızlı:** 2-10 dakika arası sürebilir.
  - **Standart:** 5-30 dakika arası sürebilir.
  - **Tam:** 10-50 dakika arası sürebilir.

> Bu süreler tahmini sürelerdir. Sisteminize ve internet sağlayıcınızın paket inceleme politikalarına göre değişiklik gösterebilir.

- **Hazır Ayar:** Zapret için önceden belirlenmiş parametrelerden birini seçer. (Bal Porsuğu'na hazır ayarlar için teşekkürler)

- **Hazır Ayarı Düzenle:** Seçtiğiniz hazır ayar üzerinde ince ayar ya da değişiklik yapmanızı sağlayan metin kutusunu açar. Bu kutuda düzenleme yaptıktan sonra aşağıdaki butonları kullanarak kutudaki parametreler ile kurulum sağlayabilir ya da tek seferlik çalıştırabilirsiniz.

- **Önayarlı Hizmet Kur:** Seçtiğiniz hazır ayar ile (Ya da düzenleme yaptıysanız düzenlenmiş hali ile) Zapret hizmetini kurar.

- **Önayarlı Tek Seferlik:** Seçtiğiniz hazır ayar ile (Ya da düzenleme yaptıysanız düzenlenmiş hali ile) Zapret'i tek seferlik çalıştırır. Açılan konsol penceresini kapattığınızda Zapret çalışmayı durdurur.

- **Zapret'i Kaldır:** Zapret'i kaldırır.

**Not 2:** Eğer Discord uygulaması Checking for updates… ekranında kalırsa modeminizi kapatıp 15 saniye bekledikten sonra tekrar açın ve ardından bilgisayarınızı yeniden başlatın.

---

## GoodbyeDPI Sayfası Kullanımı

**Not:** Bu bölümdeki kurulum, sistem geneli çalışır. Hız kaybına sebep olmasa da bazı web site ve uygulamalarda bağlantı sorunlarına yol açabilir. Bu gibi sorunların önüne geçmek için "Blacklist kullan" seçeneğini aktifleştirebilirsiniz. Bu kurulumu gerçekleştirdikten sonra sisteminizi her yeniden başlatışınızda ilgili yöntem otomatik olarak çalışmaya başlar.

- **Hazır Ayar:** GoodbyeDPI için önceden belirlenmiş parametrelerden birini seçer.

- **Hazır Ayarı Düzenle:** Seçtiğiniz hazır ayar üzerinde ince ayar ya da değişiklik yapmanızı sağlayan metin kutusunu açar. Bu kutuda düzenleme yaptıktan sonra aşağıdaki butonları kullanarak kutudaki parametreler ile kurulum sağlayabilir ya da tek seferlik çalıştırabilirsiniz.

- **Blacklist Kullan:** GoodbyeDPI'ı yalnızca tercih edilen domainler için çalıştırır. Varsayılan olarak Discord, Roblox ve Wattpad için blacklist kullanılır.

- **Blacklisti Düzenle:** GoodbyeDPI'ın üzerinde etkili olacağı domain listesini düzenleyebileceğiniz metin kutusunu açar. Düzenlemeyi yaptıktan sonra Kaydet butonuna basarak değişiklikleri kaydedebilirsiniz.

- **Hizmet Kur:** Üst kısımda belirttiğiniz tercihlere göre (Hazır ayar ve blacklist tercihleri) GoodbyeDPI hizmetini kurar.

- **Tek Seferlik:** Üst kısımda belirttiğiniz tercihlere göre (Hazır ayar ve blacklist tercihleri) GoodbyeDPI'ı tek seferlik çalıştırır. Açılan konsol penceresini kapattığınızda GoodbyeDPI çalışmayı durdurur.

- **GoodbyeDPI'ı Kaldır:** GoodbyeDPI'ı kaldırır.

**Not 2:** Eğer Discord uygulaması Checking for updates… ekranında kalırsa modeminizi kapatıp 15 saniye bekledikten sonra tekrar açın ve ardından bilgisayarınızı yeniden başlatın.

---

## Onarım Sayfası Kullanımı

**Not:** Bu sayfadaki butonları kullanarak Discord'un "Checking for updates…" ve "Starting…" ekranlarında takılı kalması sorunlarını çözmeyi deneyebilirsiniz. Önce Discord'u Onar butonunu kullanarak Discord'un sisteminizde yüklü olan standart versiyonunu onarmayı, bu başarısız olursa Discord PTB Yükle butonunu kullanarak alternatif "Public Test Build" versiyonunu indirerek sorununuzu çözmeyi deneyebilirsiniz. Discord PTB versiyonu, stabil genel kanaldan dağıtılan standart Discord versiyonundan güncelleme ve indirme yolları açısından farklı olan resmi bir Discord varyantıdır.

- **Discord'u Onar:** Discord'u tamamen kaldırır, Discord önbelleğini temizler (Hesabınızdan çıkış yapılır), ByeDPI kurulumunu yapar ve Discord'u, Discord resmi sitesinden yeniden indirerek yükler.

- **Discord PTB Yükle:** Discord PTB sürümünü yüklü ise kaldırıp Discord resmi sitesinden Discord PTB sürümünü indirip yükler.

- **WebCord Yükle:** Discord web sitesinin Electron ile yazılmış açık kaynaklı bir sarmalayıcısı olan WebCord'u yükler. Eğer halihazırda yüklü bir aşım yöntemi yoksa ByeDPI da kurar.

- **Discord PTB için temiz kurulum yap:** Discord PTB Yükle butonuna tıklandığında bu seçenek aktif ise Discord PTB'yi yüklerken standart Discord'u kaldırır.

- **WebCord için kısayol oluştur:** WebCord kurulumu sırasında masaüstünden kolay erişim için WebCord kısayolu oluşturur.

- **Durum Kontrolleri:** Yüklü Discord sürümlerini gösterir ve yükleme/kaldırma ile çalıştırma işlemlerini yapar.

**Not 2:** Eğer onarım sonucunda da sorun yaşıyorsanız, modeminizi kapatıp 15 saniye bekledikten sonra tekrar açarak sorunun giderilip giderilmediğini test edebilirsiniz. Sorununuz devam ederse Github sayfasının Issues kısmından hata raporu oluşturabilirsiniz. Github sayfasının linki yukarıdaki Hakkında kısmında mevcut.

---

## Gelişmiş Sayfası Kullanımı

- **Hizmetler:** SplitWire-Turkey'in kurduğu ya da kullanıcının kurduğu DPI aşma ve tünelleme ile ilgili hizmetlerin listesini gösterir.

- **DNS ve DoH ayarlarını her kurulumda gerçekleştir:** SplitWire-Turkey içerisinde yapılabilecek tüm aşım yöntemi kurulumlarında Google DNS ve Quad9 (DoH aktif şekilde) ayarlanır. Bu anahtarı kapatarak otomatik DNS ve DoH ayarlanmasını engelleyebilirsiniz.

- **Tüm Hizmetleri Kaldır:** Listedeki tüm hizmetleri doğru sıra ile kaldırır, Discord klasöründe drover dosyalarını siler ve WireSock Refresh Task Scheduler görevini kaldırır.

- **DNS ve DoH Ayarlarını Geri Al:** SplitWire-Turkey içerisinde bulunan herhangi bir kurulum gerçekleştirildiğinde yapılan DNS ve DoH ayarlarını sıfırlayarak DNS ayarını "Otmatik (DHCP)" ve DoH ayarını "Kapalı" hale getirir.

- **SplitWire-Turkey'i Kaldır:** SplitWire-Turkey'in yaptığı tüm değişiklikleri geri alıp sisteminizi eski hale getirdikten sonra SplitWire-Turkey'i kaldırma aracını başlatır.

**Not:** WinDivert hizmeti, Zapret ya da GoodbyeDPI hizmetleri durdurulmadan kaldırılamaz. Bu sebeple birden fazla onay istenebilir.

---

## Dil Seçenekleri / Language Options / Варианты языка / Opciones de Idioma

- SplitWire-Turkey'i çalıştırdığınızda SplitWire-Turkey logosunun altında bulunan dil menüsü butonu ile dil seçeneklerini görüp programın dilini dğeiştirebilirsiniz. Şuan için Türkçe, English, Русский ve Español dilleri mevcut. [Türkçe README dosyasını açmak için buraya tıklayın](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)

- When you run SplitWire-Turkey, you can view language options and change the program's language using the language menu button located below the SplitWire-Turkey logo. Currently, Turkish, English, Русский and Español languages are available. [Click here to open English README file.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)

- При запуске SplitWire-Turkey вы можете просматривать языковые опции и изменять язык программы с помощью кнопки языкового меню, расположенной под логотипом SplitWire-Turkey. В настоящее время доступны турецкий, английский, русский и испанский языки. [Нажмите здесь, чтобы открыть файл README на русском языке.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)

- Al ejecutar SplitWire-Turkey, puede ver las opciones de idioma y cambiar el idioma del programa usando el botón del menú de idioma ubicado debajo del logotipo de SplitWire-Turkey. Actualmente, están disponibles los idiomas turco, inglés, ruso y español. [Haga clic aquí para abrir el archivo README en español.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

---

## Önemli Notlar

> [!CAUTION]
> Windows Defender dışında bir antivirüs yazılımı kullanıyorsanız "Program Files\SplitWire-Turkey\res\byedpi\ciadpi.exe" ve "Program Files\SplitWire-Turkey\res\proxifyre\ProxiFyre.exe" isimli yürütülebilir dosyaları için ilgili antivirüs yazılımı güvenlik duvarında izin verecek kuralları el ile eklemeniz gerekebilir. Windows Defender için güvenlik duvarı kuralları otomatik olarak eklenir, ekstra bir işlem yapmanıza gerek yoktur. **Kullandığınız antivirüs yazılımının kendisine ait ağ güvenlik duvarı özelliği yoksa ya da Windows Defender dışında bir antivirüs yazılımı kullanmıyorsanız, bu uyarıyı görmezden gelebilirsiniz.**

> [!NOTE]
> WinDivert dosyalarının kullanımı Kaspersky isimli antivirüs yazılımı tarafından engellendiği için, sisteminizde Kaspersky yüklü iken GoodbyeDPI ve Zapret sekmelerini kullanamazsınız. Kaspersky'i sisteminizden tamamen kaldırdıktan sonra **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.5/SplitWire-Turkey-Setup-Windows-1.5.5.exe)** dosyasını indirip tekrar kurulum yaparsanız bu sekmeler aktif hale gelecektir. C:\Program Files\SplitWire-Turkey ve C:\Users\\-Kullanıcı Adı-\AppData\Local\SplitWire-Turkey klasörlerini Kaspersky istisnalarına ekleyip, SplitWire-Turkey'i tekrar indirip kurulum yaparak bu sorunu çözmeyi de deneyebilirsiniz.

> [!NOTE]
> Herhangi bir sebeple SplitWire-Turkey v1.5 ve sonrasındaki sürümlerde bulunan WinDivert dosyaları ile ilgili sorun yaşarsanız [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0) adresinden eski sürümü indirip kullanabilirsiniz.

---

## SplitWire-Turkey macOS Sürümü

SplitWire-Turkey şuan için yalnızca Windows işletim sistemi için desteklenmektedir. MacOS işletim sistemi için, [a-mertdincer](https://github.com/a-mertdincer)'in paylaştığı [SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS) isimli uygulamayı kullanabilirsiniz.

---

## SplitWire-Turkey Linux Sürümü

Linux sürümü aktif olarak geliştirilmektedir. Detaylı bilgi için [linux/README.md](linux/README.md) dosyasına bakabilirsiniz.

### Desteklenen Dağıtımlar
- Ubuntu 22.04+
- Debian 12+
- Linux Mint 21+
- Pop!_OS 22.04+

### Linux Özellikleri
- **WireGuard VPN** - Cloudflare WARP ile ayrık tünelleme
- **Zapret** - nfqws ile DPI aşımı (GoodbyeDPI Linux karşılığı)
- **ByeDPI** - ciadpi ile uygulama bazlı proxy
- **Modern GTK4/Libadwaita** arayüzü
- **systemd** entegrasyonu

### Linux Kurulumu

```bash
# Hızlı kurulum
curl -sSL https://raw.githubusercontent.com/cagritaskn/SplitWire-Turkey/main/linux/scripts/install.sh | sudo bash

# Veya manuel kurulum
cd linux
sudo ./scripts/setup-deps.sh
sudo ./scripts/install.sh
```

Detaylı kurulum ve kullanım bilgileri için: [Linux README (EN)](linux/README.md) | [Linux README (TR)](linux/README_TR.md)

---

## Karşılaşılabilecek Sorunlar ve Hata Bildirimi
- "Register failed"/"Config dosyası bulunamadı" hatası: Bazı internet sağlayıcıları ya da CloudFlare'in kendisi, ücretsiz API'sinin kullanımını çeşitli sebeplerle engelleyebiliyor. Bunun en sık görülen sebebi "abusive usage" olarak tanımlanan bölgesel aşırı kullanma istismarıdır. Bu sebeple wgcf, kayıt gerçekleştiremez ve konfigürasyon dosyası oluşturamaz ve bunun sonucunda "Register işlemi başarısız oldu. Return code: 1" hatası alınır. Böyle bir durumda maalesef Standart Kurulum, Alternatif Kurulum ve Özelleştirilmiş Kurulum yöntemleri işlevini yerine getiremez ve gerekli konfigürasyon dosyası oluşturulamaz. Geçici olarak bir VPN ya da proxy kullanılarak bu yasak aşılabilse dahi; Cloudflare API'sinden geçici olarak tünellenmiş şekilde oluşturulan private-key ve konfigürasyon dosyası, yalnızca tünellenilmiş haldeki makine için geçerli olacağından kullanıma yine engel olacaktır. Bu hatayı alıyorsanız diğer yöntemleri kullanmayı deneyebilirsiniz.

- Hizmet kurulumları sırasında hata: Hizmetler penceresi açıkken bu uygulamayı kullanmayın.

- "Checking for updates" ekranında kalma: Modeminizi kapatıp 15-30 saniye arasında bekledikten sonra tekrar başlatın. Daha sonra bilgisayarınızı yeniden başlatıp sorunun giderilip giderilmediğini test edin. Eğer giderilmediyse SplitWire-Turkey'i çalıştırıp Onarım sekmesini açın ve Discord'u Onar butonuna tıklayın. Bilgisayarınızı yeniden başlattıktan sonra sorunun giderilip giderilmediğini kontrol edin. Eğer yine sonuç alamazsanız SplitWire-Turkey'i çalıştırıp Onarım sekmesini açın ve Discord PTB Yükle butonuna tıklayıp kurulum tamamlandıktan sonra Başlat > Discord PTB yolu ile Discord PTB'yi çalıştırıp sorunun giderilip giderilmediğini kontrol edin.

- "Starting..." ekranında kalma: SplitWire-Turkey'i çalıştırıp Onarım sekmesini açın ve Discord'u Onar butonuna tıklayın. Bilgisayarınızı yeniden başlattıktan sonra sorunun giderilip giderilmediğini kontrol edin. Eğer yine sonuç alamazsanız SplitWire-Turkey'i çalıştırıp Onarım sekmesini açın ve Discord PTB Yükle butonuna tıklayıp kurulum tamamlandıktan sonra Başlat > Discord PTB yolu ile Discord PTB'yi çalıştırıp sorunun giderilip giderilmediğini kontrol edin. Sorununuz yine çözülmediyse C:\Users\\-Kullanıcı Adı-\AppData\Local\Discord\ konumundaki Update.exe'ye sağ tıklayıp Özellikler'i seçip, açılan pencerede Uyumluluk sekmesine gelip, "Bu programın çalıştırılacağı uyumluluk modu:" kutucuğunu tikleyip, Windows 8'i seçtikten sonra Uygula ve Tamam butonlarına basıp bilgisayarınızı yeniden başlatın ve sorunun giderilip giderilmediğini kontrol edin. Eğer yine sorununuz çözülmediyse bir önceki adımın aynısını uygulayıp bu sefer "Bu programın çalıştırılacağı uyumluluk modu:" kutucuğunu tikleyip, Windows 7'yi seçtikten sonra Uygula ve Tamam butonlarına basıp bilgisayarınızı yeniden başlatın ve sorunun giderilip giderilmediğini kontrol edin.

- Discord "Mesajlar yüklenemedi" hatası: Discord'un kendisi şüpheli IP değişiklikleri tespit ettiğinde ya da Cloudflare WARP kötüye kullanım tespit ettiğinde bu sorun yaşanıyor. Bu sorunu yaşarsanız, modeminizi kapatıp 15-30 saniye arasında bekledikten sonra tekrar başlatın. Daha sonra bilgisayarınızı yeniden başlatıp sorunun giderilip giderilmediğini test edin. Bu şekilde de çözüme ulaşamazsanız C:\Users\\-Kullanıcı Adı-\AppData\Roaming\discord klasörünü silerek Discord önbelleğini sıfırlamayı deneyebilirsiniz. (Bu yöntem Discord hesabınızdan çıkış yapacaktır, tekrar giriş yapmanız istenir) Eğer bu şekilde de çözüme ulaşamazsanız diğer yöntemleri deneyin.

- Hata raporu oluşturma: [SplitWire-Turkey Issues sayfası](https://github.com/cagritaskn/SplitWire-Turkey/issues)'na giderek sağ üstte bulunan **New Issue** butonuna tıklayıp, AppData\Local\SplitWire-Turkey\Logs klasöründeki .log dosyalarını da raporunuza ekleyerek bildirimde bulunabilirsiniz. Logs klasörünü SplitWire-Turkey programının Hakkında sayfasının en altında bulunan Logs Klasörünü Aç butonu ile açabilirsiniz.

---

## SplitWire-Turkey'i Sistemden Kaldırma ve Tüm Değişiklikleri Geri Alma
**SplitWire-Turkey'i** sisteminizden kaldırmanın birçok yolu vardır. Bunlar program içerisindeki **Gelişmiş** sekmesinde **SplitWire-Turkey'i Kaldır** butonunu kullanmak, programın kurulu olduğu konumdaki **unins000.exe** isimli kaldırma paketini kullanmak, Windows Program ekle veya kaldır penceresinde **SplitWire-Turkey**'i bulup sağdaki seçeneklerden Kaldır butonuna tıklayarak kaldırmak olarak sıralanabilir. Bu yollardan herhangi birini izleyerek tüm değişiklikleri geri alıp SplitWire-Turkey'i sisteminizden tamamen kaldırabilirsiniz.

> Eğer ZIP dosyasını indirip ayıklayarak kullanım sağlıyorsanız; **SplitWire-Turkey** içerisinde **Gelişmiş** sekmesinde **SplitWire-Turkey'i Kaldır** butonunu kullandıktan sonra, ZIP dosyasını ayıkladığınız klasörü ve C:\Users\-Kullanıcı Adı-\AppData\Local\SplitWire-Turkey klasörünü kullanarak tüm değişiklikleri geri alıp SplitWire-Turkey'i sisteminizden tamamen kaldırabilirsiniz.

---

## Virüs & SmartScreen Uyarısı
Program açık kaynak kodlu olduğundan tüm kodu görüp inceleyebilirsiniz. Tüm program açık kaynak kodludur ve kaynak kodu /src klasörü içerisinden incelenebilir, tercih edilirse tekrar derlenebilir. Programı kullanmak istemeyen ve güvenmeyen kullanıcılar, programı kullanmak zorunda değildir, programı kullanmak kullanıcının inisiyatifindedir.
Dilerseniz tüm klasörü, kurulum dosyasını, .zip dosyasını ya da kaynak kodlarını [VirusTotal](https://www.virustotal.com/gui/home/upload) gibi bir sitede taratıp sonuçları inceleyebilir, dilerseniz C# dili biliyorsanız veya bilen bir tanıdığınız varsa başvurup kodun ne yapmaya çalıştığını anlayabilirsiniz.

> [!NOTE]
> **SmartScreen "Windows kişisel bilgisayarınızı korudu"** uyarısı, imzalanmamış yazılımların tamamında çalıştırmadan önce görünür. Bunun sebebi, yazılımların uluslararası kod imzalama sertifikasına tabi olma zorunluluğudur. Ancak bu imzalama işlemi döviz kuru üzerinden düzenli ödeme gerektirdiğinden ve ben bağımsız, gelir elde etmeyen bir geliştirici olduğumdan dolayı yazılımı imzalama girişiminde bulunamıyorum.

> [!NOTE]
> **[SplitWire-Turkey Setup dosyası VirusTotal sonuçlarında](https://www.virustotal.com/gui/file/ea2c0c4a81e2256f9d09d59dfdcba0fbd8daca66086808d48290240f20d8ce5b?nocache=1)** Dosyalarda küçük bir kullanıcı kesimi tarafından kullanılan antivirüs yazılımları tarafından hatalı algılanmış (false positive) virüs ya da zararlı yazılım bildirimleri algılanabilir ancak bunlar az kullanılan ve tespit yöntemleri güvenilir olmayan yazılımlardır. Algılanma sebebi, SplitWire-Turkey'in tek program içerisinden birden çok uygulama kurması ve sistem üzerinde birçok değişiklik yapmasıdır. (DNS değişikliği hizmet ve program paketi kurma, kaldırma gibi) Kaspersky ile ilgili durum ve tereddütleriniz için aşağıda verilen notları okumanızı tavsiye ederim.

> [!NOTE]
> **[SplitWire-Turkey ZIP dosyası VirusTotal sonuçlarında](https://www.virustotal.com/gui/file/2937aaaa52a6d90659f9b6fdfcfd05a55120e988f5328969c4a05a83b11581a3?nocache=1)** Dosyalarda küçük bir kullanıcı kesimi tarafından kullanılan antivirüs yazılımları tarafından hatalı algılanmış (false positive) virüs ya da zararlı yazılım bildirimleri algılanabilir ancak bunlar az kullanılan ve tespit yöntemleri güvenilir olmayan yazılımlardır. Algılanma sebebi, SplitWire-Turkey'in tek program içerisinden birden çok uygulama kurması ve sistem üzerinde birçok değişiklik yapmasıdır. (DNS değişikliği hizmet ve program paketi kurma, kaldırma gibi) Kaspersky ile ilgili durum ve tereddütleriniz için aşağıda verilen notları okumanızı tavsiye ederim.

> [!NOTE]
> **WinDivert** dosyaları Kaspersky ve birkaç antivirüs yazılımı tarafından RiskTool olarak algılanıyor. **not-a-virus:HEUR:RiskTool.Multi.WinDivert.gen** uyarı adından da anlaşılabileceği üzere bu dosyaların; **bir virüs değil**, yanlış kaynaklardan indirilen dosyalar ile kullanıldığında zararlı olabilecek bir araç olduğunu söylüyor. SplitWire-Turkey ve içerisindeki tüm eklentiler açık kaynaklı olduğundan WinDivert kütüphanesinin nasıl kullanıldığını takip edip, anlayabilirsiniz. Tespit açıklamalarına bakarsanız NotAVirus kelimesini görebilirisiniz. Bu tespit türü, GoodbyeDPI ve Zapret'in kullandığı açık kaynak WinDivert kütüphanesinin Windows üzerindeki ağ paketlerini manipüle etmesi sebebiyle bir risk aracı olarak tanımlanmasıdır. Bu kütüphane açık kaynaklı olup [WinDivert Github](https://github.com/basil00/WinDivert) adresinden erişilebilir. Maalesef hem Rus hem Türk yazılım geliştiricilerinin tüm çabalarına rağmen Rus hükümeti yanlısı Kaspersky ve onunla birlikte birkaç antivirüs yazılım şirketi raporları ve itirazları kabul etmediğinden ilgili antivirüs yazılımları sisteminizde yüklü ise WinDivert kullanan yöntemleri çalıştıramazsınız. Kaspersky ve diğer false positive veren antivirüs yazılımlarını sisteminizden kaldırarak tekrar kurulum yapıp WinDivert kullanan yöntemleri çalıştırabilir ya da [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0) adresinden eski WinDivert içermeyen sürümü indirip kullanabilirsiniz.

> [!NOTE]
> **Not-a-virus uyarıları genellikle bir uygulamanın tercih edildiğinde kötüye kullanılabileceği anlamına gelir.**
Not-a-virus:HEUR:RiskTool.Multi.WinDivertTool uyarısı, bu türden bir uyarıdır.
WinDivert kütüphanesi açık kaynaklı, Windows işletim sistemlerinde ağ paketlerini manipüle etmeye yarayan bir kütüphanedir. Bu kütüphane çeşitli yazılımlar ile işlevesellik kazanır. GoodbyeDPI'da bunlardan birisidir. GoodbyeDPI'ın WinDivert kütüphanesini kullanmaktaki amacı ağ paketlerinde ufak değişiklikler yaparak servis sağlayıcının doğru şekilde incelemesini engellemektir.
Ancak WinDivert'i kötü amaçla kullanabilecek yazılımlar da yazılabilir. Örneğin paketleri tamamen değiştirerek phishing, MITM saldırıları veya kullanıcı girdilerinin kaydı/gönderilmesi işlemleri yapan bir yazılım hazırlanabilir. **Ancak bu WinDivert kütüphanesini kötü amaçlı yapmaz. WinDivert kütüphanesini kötü amaçla kullanan yazılımı kötü amaçlı yapar.**
Kaspersky isimli antivirüs yazılımı ise bu konuda haklı ya da haksız olarak uyarı verse de asıl olay, Rus hükümetinin baskılarına boyun eğmesinden gelir. Rusya'da da bildiğiniz üzere bir internet özgürlüğü kısıtlaması var. Hükümet, kendi çatısı altındaki şirketlere olabildiğince aşım yöntemlerini engellemek için baskı yapıyor. Kaspersky isimli şirket de bu baskılara karşı durmuyor ve kabulleniyor. Birçok yolla aşım yapmaya yarayan yöntemlerin önüne geçmeye çalışıyor.
**Kısacası doğru kaynaktan indirme yaptığınız sürece SplitWire-Turkey bilgisayarınıza zarar veremez. İndirme yapacağınız her zaman, önce aderes çubuğuna bakıp URL'ye dikkat edin. SplitWire-Turkey'i yalnızca [bu sayfadan](https://github.com/cagritaskn/SplitWire-Turkey/releases/) indirip kullanın.**

---

## Teşekkürler ve Atıflar

- Yazılımın geliştirilmesine katkıda bulunan **[Techolay.net](https://techolay.net/sosyal/)** kurucusu **[Recep Baltaş](https://www.youtube.com/@Techolay/)**'a çok teşekkür ederim.
- **[ByeDPI Split Tunneling metodu](https://www.youtube.com/watch?v=rkBL_kHBfm4)** rehberi, Zapret presetleri ve tüm emekleri için **[Bal Porsuğu](https://www.youtube.com/@sauali)**'na çok teşekkür ederim.
- **[wgcf](https://github.com/ViRb3/wgcf)** by **[ViRb3](https://github.com/ViRb3)**
- **[ProxiFyre](https://github.com/wiresock/proxifyre)** by **[Vadim Smirnov](https://github.com/wiresock)**
- **[ByeDPI](https://github.com/hufrea/byedpi)** by **[hufrea](https://github.com/hufrea/)**
- **[WireSock](https://www.wiresock.net/)** by **[Vadim Smirnov](https://github.com/wiresock)**
- **[drover](https://github.com/hdrover/discord-drover)** by **[hdrover](https://github.com/hdrover)**
- **[GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI)** by **[ValdikSS](https://github.com/ValdikSS)**
- **[zapret](https://github.com/bol-van/zapret)** by **[bol-van](https://github.com/bol-van)**
- **[WinDivert](https://github.com/basil00/WinDivert)** by **[basil00](https://github.com/basil00)**
- **[WebCord](https://github.com/SpacingBat3/WebCord)** by **[SpacingBat3](https://github.com/SpacingBat3)**
- **[SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS)** by **[a-mertdincer](https://github.com/a-mertdincer)**
- **Projeye katkısı olan diğer kişilere ve Patreon ile Github sponsorlarına da çok teşekkür ederim**

---

## Nasıl Çalışır

- Standart, Alternatif ve Özelleştirilmiş Kurulum
Öncelikle wgcf ile profil dosyası oluşturup WireSock istemcisi ile bu profil dosyasını kullanır ve yanlızca Discord için ayrık tünelleme başlatır.

- ByeDPI Split Tunneling ve ByeDPI DLL Kurulum
Öncelikle ByeDPI hizmeti kurulur ve ST metodunda ProxiFyre kullanarak bu proxy seçili uygulamalar için çalıştırılır, DLL metodunda ise drover dosyaları otomatik DLL enjeksiyonu ile Discord'un localhost'ta ByeDPI tarafından başlatılan proxy'nin kullanılmasını sağlar.

- Zapret Otomatik Kurulum
Blockcheck teknolojisi ile sisteminiz ve internet sağlayıcınız için ideal parametreleri bulur ve bu parametreler ile tercihlerinizi birleştirerek hizmet kurulumu sağlar. Tarama hızı seçimi parametre taramasının ne kadar basit ya da derin yapılacağını ayarlar.

- Zapret Önayarlı Kurulum ve Tek Seferlik
Önceden belirlenmiş hazır ayarlar (ya da düzenleme yaptıysanız düzenlenmiş halleri) ile Zapret hizmeti kurulur ya da tek seferlik çalıştırılır.

- GoodbyeDPI Hizmet Kurulum ve Tek Seferlik
Önceden belirlenmiş hazır ayarlar (ya da düzenleme yaptıysanız düzenlenmiş halleri) ile GoodbyeDPI hizmeti kurulur ya da tek seferlik çalıştırılır.  Blacklist kullan seçeneği aktifse, yalnızca blacklist içindeki domainler için aşım uygulanır. (Varsayılan olarak Roblox, Discord ve Wattpad için ayarlıdır)

- Tüm Hizmetleri Kaldır
SplitWire-Turkey'in kurduğu ya da kullanıcı tarafından kurulan aşım hizmetleri listelenir ve tamamı doğru sıra ile kaldırılır. Bu işlemden sonra sisteminizde herhangi bir aşım yöntemi kalmaz.

- DNS ve DoH Ayarlarını Geri Al
SplitWire-Turkey içerisinde yaptığınız her kurulumdan önce, temiz kurulum için tüm hizmetler temizlenip ardından Windows 11 destekli DoH ayarı aktif hale getirilip IPv4 ve IPv6 DNS ataması yapılır (Google birincil ve Quad9 ikincil DNS). (Windows 10 ve aşağısındaki sürümler için DoH aktifleştirme desteklenmez). DNS ve DoH Ayarlarını Geri Al butonu ise bu ayarları geri alıp DNS atamalarını Otomatik (DHCP) haline geri döndürüp, Windows 11'de DoH'u kapatır. (Windows 10 ve aşağısındaki sürümler için zaten DoH aktifleştirilmez)

- SplitWire-Turkey'i Kaldır
Bu buton, tüm temizlik işlemlerini gerçekleştirip unins000.exe isimli kaldırma paketini çalıştırır. Bu butonla başlatılan işlemler tamamlandığında SplitWire-Turkey, daha önce sisteminize hiç kurulmamış gibi olur.

---

## Tekrar Derleme (Recompiling)

### C# Kullanarak Programı Tekrar Derleme
Gereksinimler:
- **.NET 8.0 SDK** veya üzeri
- **Visual Studio 2022** veya **Visual Studio Code**
- **Windows 10/11** işletim sistemi

### Derleme Adımları

1. **Kaynak Kodu İndirin**
   ```bash
   git clone https://github.com/cagritaskn/SplitWire-Turkey.git
   cd SplitWire-Turkey/src
   ```

2. **Bağımlılıkları Yükleyin**
   ```bash
   cd SplitWireTurkey
   dotnet restore
   ```

3. **Uygulamayı Derleyin**
   ```bash
   # Basit derleme
   dotnet build -c Release
   
   # Veya batch script kullanın (Önerilen)
   ..\build_simple.bat
   ```

### InnoSetup Kullanarak Kurulum Yürütülebilirini Tekrar Derleme
Gereksinimler:
- **InnoSetup 6**
- **Windows 10/11** işletim sistemi

### Derleme Adımları

1. **C# Programını Derleyin ve Çıktı SplitWire-Turkey.exe'nin Bulunduğu Klasörde Gidin**

2. **Prerequisites Klasörü ile Resources Klasörü ve İçeriklerini Bulunduğunuz Klasöre Kopyalayın** (Desktop Runtime Dosyalarının Prerequisites klasörüne yüklenmesi mümkün değil, çünkü dosya boyut sınırını aşıyor. Bunun yerine manuel olarak windowsdesktop-runtime-6.0.35-win-x64.exe ve windowsdesktop-runtime-6.0.35-win-x86.exe dosyalarını bu klasöre siz yerleştirmelisiniz.)

3. **Bulunduğunuz Klasörde Bir Komut Satırı Açıp Kurulum Yürütülebilirini Derleyin**
   ```bash
   iscc "SplitWire-Turkey-Setup.iss"
   ```

---

## Telif Hakkı

```
Copyright © 2025 Çağrı Taşkın

Bu proje MIT lisansı altında lisanslanmıştır.
Detaylar için LICENSE dosyasına bakın.
```

---

## Bağış ve Destek

Bu programı kullanmak tamamen ücretsizdir. Kullanımından herhangi bir gelir elde etmiyorum. Ancak çalışmalarıma devam edebilmem için aşağıda bulunan bağış adreslerinden beni destekleyebilirsiniz. Github üzerinden (bu sayfanın en üstünden) projeye yıldız da bırakabilirsiniz.

**GitHub Sponsor:**

[![Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/cagritaskn)

**Patreon:**

[![Static Badge](https://img.shields.io/badge/cagritaskn-purple?logo=patreon&label=Patreon)](https://www.patreon.com/cagritaskn/membership)

---

## Sorumluluk Reddi Beyanı

**Bu yazılım eğitim amaçlı oluşturulmuştur.**

- Bu araç sadece kodlama eğitimi ve kişisel kullanım amaçlıdır
- Ticari kullanım için uygun değildir
- Geliştirici, bu yazılımın kullanımından doğabilecek herhangi bir zarardan sorumlu değildir
- Kullanıcılar bu yazılımı kendi sorumluluklarında kullanırlar
- Discord isimli programın seçilmesi, ilgili yazılımın DPI ile erişilemez kılınan bir program üzerinde denenmesi gerekmesidir
- Yasal düzenlemelere uygun kullanım kullanıcının sorumluluğundadır
> [!IMPORTANT]
> Bu programın kullanımından doğan her türlü yasal sorumluluk kullanan kişiye aittir. Uygulama yalnızca eğitim ve araştırma amaçları ile yazılmış ve düzenlenmiş olup; bu uygulamayı bu şartlar altında kullanmak ya da kullanmamak kullanıcının kendi seçimidir. Açık kaynak kodlarının paylaşıldığı Github isimli platformdaki bu proje, bilgi paylaşımı ve kodlama eğitimi amaçları ile yazılmış ve düzenlenmiştir.



