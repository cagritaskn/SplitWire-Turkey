start "zapret: http,https,quic" /min "%~dp0winws.exe" ^
--wf-tcp=80,443 --wf-udp=443,50000,50100 --dpi-desync=fake --dpi-desync-ttl=3
