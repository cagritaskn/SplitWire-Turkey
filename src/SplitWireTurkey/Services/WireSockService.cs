using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Windows;

namespace SplitWireTurkey.Services
{
    public class WireSockService
    {
        public string FindWireSockPath()
        {
            var drives = DriveInfo.GetDrives();
            foreach (var drive in drives)
            {
                if (!drive.IsReady) continue;

                var paths = new[]
                {
                    // Yeni sürüm (WireSock Secure Connect 3.x CLI)
                    Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                    Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                    // WireSock Secure Connect 3.x GUI istemcisi -- gerçek dosya adı "WireSockConnect.exe"
                    // (canlı olarak kurulu sürümde doğrulandı: bin\ klasöründe "wiresock-client.exe" DEĞİL
                    // "WireSockConnect.exe" var -- eski isim muhtemelen bir önceki WireSock sürümünden kalma).
                    Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                    Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                    // WireSock Secure Connect 2.x (eski isim, hâlâ karşılaşılabilir diye bırakıldı)
                    Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "wiresock-client.exe"),
                    Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "wiresock-client.exe"),
                    // Eski sürüm (WireSock VPN Client) - 1.4.7.1
                    Path.Combine(drive.Name, "Program Files", "WireSock VPN Client", "bin", "wiresock-client.exe"),
                    Path.Combine(drive.Name, "Program Files (x86)", "WireSock VPN Client", "bin", "wiresock-client.exe")
                };

                foreach (var path in paths)
                {
                    if (File.Exists(path))
                        return path;
                }
            }
            return null;
        }

        public string FindWireSockPathOptimized()
        {
            // Sadece C, D ve E sürücülerini tara
            var targetDrives = new[] { "C:", "D:", "E:" };
            
            foreach (var driveLetter in targetDrives)
            {
                try
                {
                    var drive = new DriveInfo(driveLetter);
                    if (!drive.IsReady) continue;

                    var paths = new[]
                    {
                        // Yeni sürüm (WireSock Secure Connect 3.x CLI)
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                        // WireSock Secure Connect 3.x GUI istemcisi -- gerçek dosya adı "WireSockConnect.exe"
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                        // WireSock Secure Connect 2.x (eski isim, hâlâ karşılaşılabilir diye bırakıldı)
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "wiresock-client.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "wiresock-client.exe"),
                        // Eski sürüm (WireSock VPN Client) - 1.4.7.1
                        Path.Combine(drive.Name, "Program Files", "WireSock VPN Client", "bin", "wiresock-client.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock VPN Client", "bin", "wiresock-client.exe")
                    };

                    foreach (var path in paths)
                    {
                        if (File.Exists(path))
                            return path;
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Sürücü {driveLetter} kontrol edilirken hata: {ex.Message}");
                    continue;
                }
            }
            return null;
        }

        public bool IsModernWireSock(string path)
        {
            return !string.IsNullOrEmpty(path) && path.EndsWith("wiresock-connect-cli.exe", StringComparison.OrdinalIgnoreCase);
        }

        public async Task<bool> InstallServiceAsync(string configPath)
        {
            try
            {
                var wiresockExe = FindWireSockPath();
                if (string.IsNullOrEmpty(wiresockExe) || !File.Exists(wiresockExe))
                {
                    System.Windows.MessageBox.Show(LanguageManager.GetText("messages", "wiresock_not_found"), 
                        LanguageManager.GetText("messages", "wiresock_not_found_title"), MessageBoxButton.OK, MessageBoxImage.Information);
                    return false;
                }

                if (IsModernWireSock(wiresockExe))
                {
                    // ÖNEMLİ (kullanıcının canlı testinde bulunan gerçek kök sebep): resmi WireSock
                    // v3 dokümantasyonuna göre wiresock-connect-cli.exe'nin "connect"/"import"/"list"
                    // komutları ürünün KENDİ ürün kurulumunun (WiX Burn .exe) önceden kurup
                    // BAŞLATMIŞ olması gereken arka plan servisine (WireSockAppService/
                    // WireSockConnectService) KARŞI konuşuyor -- CLI bu servisleri KENDİSİ kurmuyor.
                    // "net start" bir servis hiç KURULU değilse de sessizce başarısız olabiliyor,
                    // ve daha vahimi: "connect ... -exit" komutu, arkada gerçek bir servis çalışmasa
                    // BİLE 0 (başarı) exit code'u ile dönebiliyor (canlı testte doğrulandı: log
                    // "başarıyla kuruldu" diyordu ama `sc query WireSockConnectService` "1060: kurulu
                    // değil" döndürüyordu). Bu yüzden artık ÖNCE servislerin GERÇEKTEN KAYITLI olup
                    // olmadığını kontrol ediyoruz -- değilse, temel WireSock ürün kurulumu eksik/
                    // yarım kalmış demektir (büyük olasılıkla WiX Burn'ün /norestart ile bastırdığı,
                    // sürücü kaydını TAMAMLAMAK için gereken bir yeniden başlatma bekleniyordur) ve
                    // "connect" denemeden AÇIKÇA hata veriyoruz -- yanlış "başarılı" raporu vermek
                    // yerine.
                    var servicesRegisteredBefore = await IsServiceRunningAsync();
                    if (!servicesRegisteredBefore)
                    {
                        Debug.WriteLine("WireSockAppService/WireSockConnectService kayıtlı değil -- temel ürün kurulumu eksik veya yarım kalmış olabilir.");
                        System.Windows.MessageBox.Show(
                            "WireSock arka plan servisleri (WireSockAppService/WireSockConnectService) sistemde kayıtlı değil. " +
                            "Bu genellikle WireSock'un temel kurulumunun (sürücü kaydı) tamamlanması için bir SİSTEM YENİDEN BAŞLATMASI " +
                            "gerektiği anlamına gelir. Lütfen bilgisayarı yeniden başlatıp kurulumu tekrar deneyin.",
                            LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Warning);
                        return false;
                    }

                    // 1. WireSock arka plan servislerini başlat (çalışmıyorsa)
                    await ExecuteCommandAsync("net", "start WireSockAppService");
                    await ExecuteCommandAsync("net", "start WireSockConnectService");

                    var profileName = Path.GetFileNameWithoutExtension(configPath);
                    if (string.IsNullOrWhiteSpace(profileName))
                        profileName = "wgcf-profile";

                    // 2. Varsa eski profili temizle
                    await ExecuteCommandAsync(wiresockExe, $"delete \"{profileName}\"");

                    // 3. Yeni profili içe aktar
                    var importResult = await ExecuteCommandAsync(wiresockExe, $"import \"{configPath}\"");
                    if (importResult != 0)
                    {
                        Debug.WriteLine($"WireSock 3.x profil içe aktarılamadı (Exit Code: {importResult})");
                    }

                    // 4. Profile bağlan ve arka planda çalışması için -exit parametresi ver
                    var connectResult = await ExecuteCommandAsync(wiresockExe, $"connect \"{profileName}\" -exit");
                    Debug.WriteLine($"WireSock connect exit code: {connectResult}");

                    // 5. Hizmetin GERÇEKTEN kayıtlı/çalışır durumda olduğunu doğrula -- SADECE
                    // connectResult==0'a güvenmiyoruz artık (yukarıdaki not), gerçek servis
                    // durumunu birkaç kez (servis "connect" sonrası anında sorgulanamayabilir)
                    // kontrol ediyoruz.
                    var isRunning = false;
                    for (int attempt = 0; attempt < 4 && !isRunning; attempt++)
                    {
                        if (attempt > 0) await Task.Delay(1000);
                        isRunning = await IsServiceRunningAsync();
                    }

                    if (isRunning)
                    {
                        return true;
                    }
                    else
                    {
                        System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wiresock_install_failed"), connectResult),
                            LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                        return false;
                    }
                }
                else
                {
                    // Legacy WireSock 1.4.7.1 / 2.x
                    var installArgs = $"install -start-type 2 -config \"{configPath}\" -log-level none";
                    var result = await ExecuteCommandAsync(wiresockExe, installArgs);

                    if (result == 0)
                    {
                        // Hizmet kurulduktan sonra başlatmayı dene
                        var startResult = await ExecuteCommandAsync("net", "start wiresock-client-service");
                        if (startResult != 0)
                        {
                            // net start başarısız olursa sc start ile dene
                            startResult = await ExecuteCommandAsync("sc", "start wiresock-client-service");
                        }

                        if (startResult == 0)
                        {
                            return true;
                        }
                        else
                        {
                            System.Windows.MessageBox.Show(LanguageManager.GetText("messages", "wiresock_service_installed_not_started"), 
                                LanguageManager.GetText("messages", "wiresock_service_warning"), MessageBoxButton.OK, MessageBoxImage.Warning);
                            return true; // Still return true since service was installed
                        }
                    }
                    else
                    {
                        // Check if service was actually installed despite the error
                        var serviceQueryResult = await ExecuteCommandAsync("sc", "query wiresock-client-service");
                        if (serviceQueryResult == 0)
                        {
                            System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wiresock_service_installed_warning"), result), 
                                LanguageManager.GetText("messages", "wiresock_service_warning"), MessageBoxButton.OK, MessageBoxImage.Warning);
                            return true;
                        }
                        else
                        {
                            System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wiresock_install_failed"), result), 
                                LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                            return false;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wiresock_service_error"), ex.Message), 
                    LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }
        }

        public async Task<bool> RemoveServiceAsync()
        {
            try
            {
                var wiresockExe = FindWireSockPath();
                if (!string.IsNullOrEmpty(wiresockExe) && File.Exists(wiresockExe) && IsModernWireSock(wiresockExe))
                {
                    // Modern WireSock: Tünel bağlantısını kes ve profili temizle
                    try { await ExecuteCommandAsync(wiresockExe, "disconnect"); } catch { }
                    try { await ExecuteCommandAsync(wiresockExe, "delete \"wgcf-profile\""); } catch { }
                }
                else if (!string.IsNullOrEmpty(wiresockExe) && File.Exists(wiresockExe))
                {
                    try { await ExecuteCommandAsync(wiresockExe, "uninstall"); } catch { }
                }

                // Modern WireSock ve Legacy servislerini durdur
                await ExecuteCommandAsync("sc", "stop WireSockAppService");
                await ExecuteCommandAsync("sc", "stop WireSockConnectService");
                await ExecuteCommandAsync("sc", "stop wiresock-client-service");
                await Task.Delay(1000);

                // Servisleri sistemden sil
                await ExecuteCommandAsync("sc", "delete WireSockAppService");
                await ExecuteCommandAsync("sc", "delete WireSockConnectService");
                await ExecuteCommandAsync("sc", "delete wiresock-client-service");

                // WireSockRefresh görevini kaldır
                await ExecuteCommandAsync("schtasks", "/delete /tn \"WireSockRefresh\" /f");

                return true;
            }
            catch (Exception ex)
            {
                System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wiresock_remove_error"), ex.Message), 
                    LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }
        }

        private async Task<int> ExecuteCommandAsync(string command, string arguments)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = command,
                        Arguments = arguments,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    using var process = new Process { StartInfo = startInfo };
                    process.Start();
                    process.WaitForExit();
                    return process.ExitCode;
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Command execution failed: {ex.Message}");
                    return -1;
                }
            });
        }

        public bool IsWireSockInstalled()
        {
            return !string.IsNullOrEmpty(FindWireSockPath());
        }

        public async Task<bool> IsWireSockInstalledAsync()
        {
            return await Task.Run(() => !string.IsNullOrEmpty(FindWireSockPathOptimized()));
        }

        // ÖNEMLİ (kullanıcının "WireSock hizmeti yine kurulmadı" bildirimiyle bulunan kök sebep):
        // eskiden IsLatestWireSockInstalled sadece DOSYA varlığına bakıyordu. Ama bir önceki
        // kurulumdan WireSock'un dosyaları diskte kalıp SADECE servisleri (WireSockAppService/
        // WireSockConnectService) kaldırılmış olabilir (ör. başka bir motorun temiz kurulumu
        // sırasında -- artık WireSock'un kendi akışları bunu yapmıyor ama geçmiş bir çalıştırmadan
        // kalmış olabilir). Bu durumda kod "zaten kurulu" sanıp DownloadAndInstallWireSock()'u hiç
        // ÇALIŞTIRMIYORDU -- silinen servisler bir daha asla yeniden kurulmuyordu. Artık dosya
        // varlığına EK OLARAK servislerin GERÇEKTEN kayıtlı olduğunu da (senkron sc query ile)
        // doğruluyoruz.
        private bool IsAnyWireSockServiceRegisteredSync()
        {
            foreach (var svc in new[] { "WireSockAppService", "WireSockConnectService", "wiresock-client-service" })
            {
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "sc",
                        Arguments = $"query {svc}",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    using var process = Process.Start(psi);
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                    {
                        return true;
                    }
                }
                catch { /* servis kontrolü başarısız olursa diğer isme geç */ }
            }
            return false;
        }

        public bool IsLatestWireSockInstalled()
        {
            // Sadece C, D ve E sürücülerini tara (optimize edilmiş)
            var targetDrives = new[] { "C:", "D:", "E:" };

            foreach (var driveLetter in targetDrives)
            {
                try
                {
                    var drive = new DriveInfo(driveLetter);
                    if (!drive.IsReady) continue;

                    var paths = new[]
                    {
                        // Modern WireSock Secure Connect 3.x
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "command-line", "wiresock-connect-cli.exe"),
                        // WireSock Secure Connect 3.x GUI istemcisi -- gerçek dosya adı "WireSockConnect.exe"
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "WireSockConnect.exe"),
                        // WireSock Secure Connect 2.x (eski isim, hâlâ karşılaşılabilir diye bırakıldı)
                        Path.Combine(drive.Name, "Program Files", "WireSock Secure Connect", "bin", "wiresock-client.exe"),
                        Path.Combine(drive.Name, "Program Files (x86)", "WireSock Secure Connect", "bin", "wiresock-client.exe")
                    };

                    foreach (var path in paths)
                    {
                        // Dosya varlığı TEK BAŞINA yeterli değil -- servisler de kayıtlı olmalı,
                        // yoksa "zaten kurulu" yanlış pozitifi kurulumu atlatıp bir daha hiç
                        // düzeltilemeyecek bir duruma yol açıyordu.
                        if (File.Exists(path) && IsAnyWireSockServiceRegisteredSync())
                            return true;
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"IsLatestWireSockInstalled - Sürücü {driveLetter} kontrol edilirken hata: {ex.Message}");
                    continue;
                }
            }
            return false;
        }

        public async Task<bool> IsServiceRunningAsync()
        {
            try
            {
                // Modern WireSock servislerini kontrol et
                var appResult = await ExecuteCommandAsync("sc", "query WireSockAppService");
                if (appResult == 0)
                {
                    return true;
                }

                var modernResult = await ExecuteCommandAsync("sc", "query WireSockConnectService");
                if (modernResult == 0)
                {
                    return true;
                }

                // Legacy wiresock-client-service durumunu kontrol et
                var legacyResult = await ExecuteCommandAsync("sc", "query wiresock-client-service");
                return legacyResult == 0;
            }
            catch
            {
                return false;
            }
        }

        public async Task<bool> StartServiceAsync()
        {
            try
            {
                var wiresockExe = FindWireSockPath();
                if (IsModernWireSock(wiresockExe))
                {
                    await ExecuteCommandAsync("net", "start WireSockAppService");
                    await ExecuteCommandAsync("net", "start WireSockConnectService");
                    var connectResult = await ExecuteCommandAsync(wiresockExe, "connect wgcf-profile -exit");
                    return connectResult == 0 || await IsServiceRunningAsync();
                }

                var result = await ExecuteCommandAsync("net", "start wiresock-client-service");
                if (result != 0)
                {
                    result = await ExecuteCommandAsync("sc", "start wiresock-client-service");
                }
                return result == 0;
            }
            catch
            {
                return false;
            }
        }
    }
} 