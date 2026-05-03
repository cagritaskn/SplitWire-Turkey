using SplitWireTurkey;
using Xunit;

namespace SplitWireTurkey.Tests
{
    /// <summary>
    /// LanguageManager is a static class — all tests live in a single
    /// non-parallel collection so the shared state is deterministic.
    /// </summary>
    [Collection("LanguageManager")]
    public class LanguageManagerTests
    {
        [Fact]
        public void LoadLanguage_WithSupportedCode_ReturnsTrue()
        {
            Assert.True(LanguageManager.LoadLanguage("TR"));
            Assert.Equal("TR", LanguageManager.CurrentLanguage);
        }

        [Theory]
        [InlineData(null)]
        [InlineData("")]
        [InlineData("   ")]
        public void LoadLanguage_WithNullOrBlank_ReturnsFalseAndDoesNotThrow(string code)
        {
            // Must never throw NullReferenceException / ArgumentNullException.
            var result = LanguageManager.LoadLanguage(code);
            Assert.False(result);
        }

        [Fact]
        public void LoadLanguage_WithUnknownCode_FallsBackAndStillExposesKeys()
        {
            // Unknown language file does not exist on disk, but the
            // Turkish fallback dictionary should still resolve common keys.
            var ok = LanguageManager.LoadLanguage("XX");
            Assert.True(ok);

            var translated = LanguageManager.GetText("buttons", "exit");
            Assert.NotEqual("buttons.exit", translated);
            Assert.False(string.IsNullOrWhiteSpace(translated));
        }

        [Fact]
        public void GetText_TopLevelKey_ReturnsLocalizedString()
        {
            LanguageManager.LoadLanguage("EN");
            // No top-level scalar keys exist by default, so this also
            // verifies that an unknown flat key returns the key itself.
            Assert.Equal("nonexistent_top_level_key",
                LanguageManager.GetText("nonexistent_top_level_key"));
        }

        [Fact]
        public void GetText_NestedKey_ReturnsLocalizedString_ForTurkish()
        {
            LanguageManager.LoadLanguage("TR");

            Assert.Equal("WireSock", LanguageManager.GetText("tabs", "main"));
            Assert.Equal("Çıkış", LanguageManager.GetText("buttons", "exit"));
        }

        [Fact]
        public void GetText_NestedKey_ReturnsLocalizedString_ForEnglish()
        {
            LanguageManager.LoadLanguage("EN");

            Assert.Equal("Exit", LanguageManager.GetText("buttons", "exit"));
            Assert.Equal("Administrator Privileges Required",
                LanguageManager.GetText("messages", "admin_required_title"));
        }

        [Fact]
        public void GetText_UnknownNestedKey_ReturnsCategoryDotKey()
        {
            LanguageManager.LoadLanguage("TR");

            Assert.Equal("buttons.does_not_exist",
                LanguageManager.GetText("buttons", "does_not_exist"));
            Assert.Equal("no_such_category.foo",
                LanguageManager.GetText("no_such_category", "foo"));
        }

        [Fact]
        public void GetText_NullKey_ReturnsNull()
        {
            LanguageManager.LoadLanguage("TR");

            Assert.Null(LanguageManager.GetText(key: null));
            Assert.Null(LanguageManager.GetText(category: null, key: "x"));
            Assert.Null(LanguageManager.GetText(category: "x", key: null));
        }

        [Fact]
        public void GetText_FormatsArguments()
        {
            // Use a key that exists in TR and contains a {0} placeholder.
            // messages.unexpected_error_message contains "Beklenmeyen bir hata oluştu:\n{0}".
            LanguageManager.LoadLanguage("TR");

            var formatted = LanguageManager.GetText("messages", "unexpected_error_message", "boom");
            Assert.Contains("boom", formatted);
            Assert.DoesNotContain("{0}", formatted);
        }
    }

    [CollectionDefinition("LanguageManager", DisableParallelization = true)]
    public class LanguageManagerCollection { }
}
