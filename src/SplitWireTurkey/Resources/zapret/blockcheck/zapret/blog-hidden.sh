#!/bin/sh

# Zapret Otomatik Kurulum için özel blog-hidden.sh
# Bu script log dosyası oluşturur ve işlem tamamlanana kadar bekler

EXEDIR="$(dirname "$0")"
EXEDIR="$(cd "$EXEDIR"; pwd)"

# HIDDEN_MODE çevre değişkenini ayarla (blockcheck.sh için)
export HIDDEN_MODE=1

# Test domaini: blockcheck.sh'in kendi varsayilani (DOMAINS=${DOMAINS:-"roblox.com"}) roblox.com --
# ama bu uygulamanin asil hedefi Discord oldugundan, gercekten onemli olan domain uzerinden
# test yapmasi icin discord.com'a sabitliyoruz.
export DOMAINS=discord.com

# Blockcheck'i çalıştır ve çıktıyı log dosyasına yönlendir
"$EXEDIR/blockcheck.sh" 2>&1 | tee "$EXEDIR/../blockcheck.log"

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
