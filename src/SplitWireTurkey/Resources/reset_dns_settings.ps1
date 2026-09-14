# DNS and DoH Settings Reset
# This script will reset DNS and DoH settings:
# • Set DNS settings to automatic (DHCP)
# • Disable DNS over HTTPS (DoH) feature
# • Process all physical network adapters

# Administrator permission check
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires administrator privileges!" -ForegroundColor Red
    Write-Host "Please run the script as administrator." -ForegroundColor Red
    exit
}

Write-Host "Resetting DNS and DoH settings..." -ForegroundColor Yellow
Write-Host ""

# Get physical network adapters
$adapters = Get-NetAdapter -Physical
Write-Host "Found adapters:" -ForegroundColor Cyan
foreach ($adapter in $adapters) {
    Write-Host "  - $($adapter.Name) (Index: $($adapter.InterfaceIndex))" -ForegroundColor White
}
Write-Host ""

# Reset DNS settings for each adapter
foreach ($adapter in $adapters) {
    $adapterName = $adapter.Name
    $adapterGuid = $adapter.InterfaceGuid
    
    Write-Host "Processing adapter: $adapterName" -ForegroundColor Green
    
    # Reset IPv4 and IPv6 DNS settings to automatic
    try {
        Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ResetServerAddresses -ErrorAction SilentlyContinue
        netsh interface ip set dns "$adapterName" dhcp | Out-Null
        netsh interface ipv6 set dns "$adapterName" dhcp | Out-Null
        Write-Host "  IPv4 and IPv6 DNS settings reset to automatic: $adapterName" -ForegroundColor Green
    }
    catch {
        Write-Host "  Failed to reset DNS settings: $adapterName - $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Clear DoH settings
    $dohPath = 'HKLM:System\CurrentControlSet\Services\Dnscache\InterfaceSpecificParameters\' + $adapterGuid + '\DohInterfaceSettings'
    
    try {
        # Completely clear existing DoH settings
        if (Test-Path $dohPath) {
            Remove-Item -Path $dohPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  DoH settings cleared: $adapterName" -ForegroundColor Green
        } else {
            Write-Host "  DoH settings already empty: $adapterName" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  Failed to clear DoH settings: $adapterName - $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Disable global DoH settings via registry
Write-Host "Disabling global DoH settings via registry..." -ForegroundColor Yellow
try {
    # Clear DoH settings in registry
    $globalDohPath = 'HKLM:SOFTWARE\Policies\Microsoft\Windows NT\DNSClient'
    if (Test-Path $globalDohPath) {
        Remove-ItemProperty -Path $globalDohPath -Name 'DohEnabled' -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $globalDohPath -Name 'DohServerAddress' -ErrorAction SilentlyContinue
    }
    Write-Host "Global DoH settings disabled via registry" -ForegroundColor Green
}
catch {
    Write-Host "Failed to disable global DoH settings: $($_.Exception.Message)" -ForegroundColor Red
}

# Clear DNS cache
Write-Host "Clearing DNS cache..." -ForegroundColor Yellow
Clear-DnsClientCache
Write-Host "DNS cache cleared" -ForegroundColor Green

# Show results
Write-Host "Checking DNS settings..." -ForegroundColor Yellow
$adapters = Get-NetAdapter -Physical
foreach($adapter in $adapters) {
    $ipv4 = $adapter | Get-DnsClientServerAddress
    Write-Host "Adapter: $($adapter.Name)" -ForegroundColor Cyan
    Write-Host "  IPv4 DNS: $($ipv4.ServerAddresses -join ', ')" -ForegroundColor White
}

Write-Host ""
Write-Host "DNS and DoH settings successfully reset!" -ForegroundColor Green
Write-Host "All adapters now use automatic DNS and DoH is disabled." -ForegroundColor Green

Write-Host ""
Write-Host "Script completed successfully!"
