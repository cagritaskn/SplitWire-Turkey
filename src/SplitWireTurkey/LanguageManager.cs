using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace SplitWireTurkey
{
    /// <summary>
    /// Dil yönetimi için sınıf
    /// </summary>
    public static class LanguageManager
    {
        private const string FallbackLanguage = "TR";

        private static Dictionary<string, object> _currentTranslations = new Dictionary<string, object>();
        private static Dictionary<string, object> _fallbackTranslations = new Dictionary<string, object>();
        private static string _currentLanguage = FallbackLanguage;

        /// <summary>
        /// Mevcut dil
        /// </summary>
        public static string CurrentLanguage => _currentLanguage;

        /// <summary>
        /// Dil dosyasını yükler
        /// </summary>
        public static bool LoadLanguage(string languageCode)
        {
            if (string.IsNullOrWhiteSpace(languageCode))
            {
                return false;
            }

            try
            {
                _currentLanguage = languageCode;

                // Always keep the Turkish dictionary in memory as a fallback for
                // missing keys when a partial translation is loaded.
                _fallbackTranslations = LoadDictionary(FallbackLanguage) ?? new Dictionary<string, object>();

                var loaded = LoadDictionary(languageCode);
                if (loaded == null && !string.Equals(languageCode, FallbackLanguage, StringComparison.OrdinalIgnoreCase))
                {
                    loaded = _fallbackTranslations;
                }

                if (loaded == null)
                {
                    return false;
                }

                _currentTranslations = loaded;
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Dil yüklenirken hata: {ex.Message}");
                return false;
            }
        }

        private static Dictionary<string, object> LoadDictionary(string languageCode)
        {
            var path = Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                "res",
                "Languages",
                $"{languageCode.ToLower()}.json");

            if (!File.Exists(path))
            {
                return null;
            }

            var json = File.ReadAllText(path);
            return JsonSerializer.Deserialize<Dictionary<string, object>>(json);
        }

        /// <summary>
        /// Çeviri metnini alır
        /// </summary>
        public static string GetText(string key, params object[] args)
        {
            if (key == null)
            {
                return null;
            }

            try
            {
                if (TryResolve(_currentTranslations, key, args, out var text)
                    || TryResolve(_fallbackTranslations, key, args, out text))
                {
                    return text;
                }

                return key;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Çeviri alınırken hata: {ex.Message}");
                return key;
            }
        }

        private static bool TryResolve(
            Dictionary<string, object> dictionary,
            string key,
            object[] args,
            out string text)
        {
            text = null;
            if (dictionary == null || !dictionary.TryGetValue(key, out var value))
            {
                return false;
            }

            if (value is JsonElement element && element.ValueKind == JsonValueKind.String)
            {
                var raw = element.GetString();
                if (string.IsNullOrEmpty(raw))
                {
                    return false;
                }

                text = FormatSafe(raw, args);
                return true;
            }

            return false;
        }

        private static string FormatSafe(string text, object[] args)
        {
            if (args == null || args.Length == 0)
            {
                return text;
            }

            try
            {
                return string.Format(text, args);
            }
            catch
            {
                return text;
            }
        }

        /// <summary>
        /// İç içe geçmiş çeviri anahtarından metin alır (örn: "tabs.main")
        /// </summary>
        public static string GetText(string category, string key, params object[] args)
        {
            if (category == null || key == null)
            {
                return null;
            }

            try
            {
                if (TryResolveNested(_currentTranslations, category, key, args, out var text)
                    || TryResolveNested(_fallbackTranslations, category, key, args, out text))
                {
                    return text;
                }

                return $"{category}.{key}";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"İç içe çeviri alınırken hata: {ex.Message}");
                return $"{category}.{key}";
            }
        }

        private static bool TryResolveNested(
            Dictionary<string, object> dictionary,
            string category,
            string key,
            object[] args,
            out string text)
        {
            text = null;
            if (dictionary == null || !dictionary.TryGetValue(category, out var value))
            {
                return false;
            }

            if (value is JsonElement element && element.ValueKind == JsonValueKind.Object
                && element.TryGetProperty(key, out var leaf)
                && leaf.ValueKind == JsonValueKind.String)
            {
                var raw = leaf.GetString();
                if (string.IsNullOrEmpty(raw))
                {
                    return false;
                }

                text = FormatSafe(raw, args);
                return true;
            }

            return false;
        }
    }
}
