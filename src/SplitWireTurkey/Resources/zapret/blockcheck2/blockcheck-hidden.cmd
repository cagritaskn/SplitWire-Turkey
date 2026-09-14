@echo off

cd /d "%~dp0"
FOR /F "tokens=* USEBACKQ" %%F IN (`..\cygwin\bin\cygpath -C OEM -a -m zapret\blog-hidden.sh`) DO (
SET P='%%F'
)

REM Zapret Otomatik Kurulum için bash.exe penceresi gizli çalıştırılıyor
REM HIDDEN_MODE=1 çevre değişkeni ile bash penceresi gizlenecek
set HIDDEN_MODE=1

REM Bash script'i çalıştır (MainWindow.xaml.cs'de pencere gizlenecek)
"%~dp0..\tools\elevator" ..\cygwin\bin\bash -i "%P%"
