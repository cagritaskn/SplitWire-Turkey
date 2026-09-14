@echo off
cd /d "%~dp0"

REM Zapret tek seferlik çalıştırma
REM Parametreler komut satırından alınacak

if "%1"=="" (
    echo HATA: Parametre belirtilmedi!
    echo Kullanım: onetime_batch.cmd [zapret_parametreleri]
    pause
    exit /b 1
)

echo Zapret tek seferlik çalıştırılıyor...
echo Parametreler: %*

REM Zapret2'yi çalıştır
REM --lua-init iki modülü yükler: gerçek bol-van/zapret2 motoru her --lua-desync=<fonksiyon>
REM tekniğinin GERÇEK implementasyonunu bu iki dosyadan alıyor -- bunlar olmadan winws.exe
REM sessizce hiçbir şey yapmadan durur.
"%~dp0winws.exe" --lua-init=@%~dp0lua\zapret-lib.lua --lua-init=@%~dp0lua\zapret-antidpi.lua %* --hostlist-exclude=%~dp0splitwire-exclude.txt

if %ERRORLEVEL% EQU 0 (
    echo Zapret başarıyla çalıştırıldı.
) else (
    echo Zapret çalıştırılırken hata oluştu. Hata kodu: %ERRORLEVEL%
)

pause

