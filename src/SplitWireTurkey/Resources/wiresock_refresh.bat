@echo off
setlocal enabledelayedexpansion

REM Önce WireSock 3.x servisini kontrol et
sc query "WireSockConnectService" >nul 2>&1
if not errorlevel 1 (
    set "SERVICE_NAME=WireSockConnectService"
    goto :process_service
)

REM Legacy WireSock servisini kontrol et
sc query "wiresock-client-service" >nul 2>&1
if not errorlevel 1 (
    set "SERVICE_NAME=wiresock-client-service"
    goto :process_service
)

goto :done

:process_service
REM Hizmet zaten çalışıyorsa dokunma (gereksiz stop/start, WireGuard NDIS
REM adaptörünün sürekli yeniden oluşturulmasına ve nadir de olsa IRQL
REM çakışmalarına yol açabiliyor). Sadece gerçekten durmuşsa müdahale et.
for /f "tokens=3" %%a in ('sc query "!SERVICE_NAME!" ^| findstr "STATE"') do set state=%%a
if /i "!state!"=="RUNNING" goto :done

REM Hizmeti başlat (zaten durmuş durumda, stop'a gerek yok)
sc start "!SERVICE_NAME!" >nul 2>&1

REM Başlatma sonrası 5 saniye bekle
timeout /t 5 /nobreak >nul

set "attempt=1"
:retry
REM Hizmet durumunu kontrol et
for /f "tokens=3" %%a in ('sc query "!SERVICE_NAME!" ^| findstr "STATE"') do set state=%%a

if /i "!state!"=="RUNNING" (
    goto :done
) else (
    if !attempt! lss 3 (
        set /a attempt+=1
        sc start "!SERVICE_NAME!" >nul 2>&1
        timeout /t 5 /nobreak >nul
        goto :retry
    )
)

:done
endlocal