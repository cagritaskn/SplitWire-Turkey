#!/bin/sh

# Zapret2 Otomatik Kurulum için özel blog-hidden.sh
# Bu script log dosyası oluşturur ve işlem tamamlanana kadar bekler

EXEDIR="$(dirname "$0")"
EXEDIR="$(cd "$EXEDIR"; pwd)"

# NOT: Daha önce burada bir ANSI escape-code hilesi vardı (pencereyi 1x1'e küçültüp
# minimize etmeye çalışan). Zapret1'in blog-hidden.sh'ında böyle bir şey YOK ve gizleme
# tamamen C# tarafındaki native ShowWindow(SW_HIDE) polling mekanizmasıyla (bkz.
# ContinuouslyHideZapretProcesses/ContinuouslyHideZapret2Processes -> CheckAndHideNewProcesses,
# ikisi de AYNI paylaşılan fonksiyonu kullanıyor) yapılıyor. ANSI hilesi gerçek bir gizleme
# sağlamıyordu, tam tersine pencerenin GÖRÜNÜR ama çok küçük boyutta kalmasına yol açıyordu
# (canlı testte bildirildi) -- kaldırıldı, artık Zapret1 ile birebir aynı (hiçbir pencere
# hilesi yok, sadece native polling).

# ÖNEMLİ (alimali54/zapret-win-turkey ile birebir uyumluluk için): BATCH=1, IPVS=4 ve
# DOMAINS artık burada AYRICA export edilmiyor -- çünkü blockcheck2.sh'ın kendi
# ask_params() fonksiyonu ARTIK bu değerleri (zapret-win-turkey'in resmi release
# paketinden birebir alınan "Auto-configure parameters for silent execution" bloğuyla)
# doğrudan kaynakta varsayılan olarak ayarlıyor (bkz. blockcheck2.sh içindeki not).
# DOMAINS özellikle burada override EDİLMİYOR ki blockcheck2.sh'ın kendi varsayılanı
# ("roblox.com", zapret-win-turkey ile birebir aynı) kullanılsın -- bulunan strateji
# zaten kurulum sırasında TÜM portlara/trafiğe genişletildiğinden (bkz.
# ProcessBlockcheckResults2) hangi domain'in test edildiği sonucu etkilemiyor, ama
# zapret-win-turkey'in kanıtlanmış seçimiyle birebir aynı davranmak için dokunmuyoruz.
#
# SCANLEVEL: blockcheck2.sh'ın kendi varsayılanı da artık "quick" (yine zapret-win-turkey
# ile aynı) -- ama kullanıcının Otomatik Kurulum'da Hızlı/Standart/Tam seçimini yine de
# buraya yazıyoruz (UpdateScanLevel2 bu satırı her çalıştırmadan önce günceller) ki
# Standart/Tam seçildiğinde blockcheck2'nin SCANLEVEL'e bağlı iç optimizasyonları
# (TTL döngüsü ilk başarıda durma vb.) da buna göre davransın.
export SCANLEVEL=quick

# Blockcheck2'yi çalıştır ve çıktıyı log dosyasına yönlendir
"$EXEDIR/blockcheck2.sh" 2>&1 | tee "$EXEDIR/../blockcheck.log"

# İşlem tamamlanana kadar bekle
wait $!

# Windows 7 notepad does not view unix EOL correctly
unix2dos "$EXEDIR/../blockcheck.log" 2>/dev/null || true

# Log dosyasının oluştuğunu doğrula
if [ -f "$EXEDIR/../blockcheck.log" ]; then
    echo "Log dosyası başarıyla oluşturuldu: $EXEDIR/../blockcheck.log"
else
    echo "HATA: Log dosyası oluşturulamadı!"
    exit 1
fi
