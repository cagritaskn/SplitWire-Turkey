using System;
using System.Text.RegularExpressions;
using SplitWireTurkey;
using Xunit;

namespace SplitWireTurkey.Tests
{
    public class VersionHelperTests
    {
        private static readonly Regex VersionRegex = new(@"^\d+\.\d+\.\d+(\.\d+)?", RegexOptions.Compiled);

        [Fact]
        public void GetAssemblyVersion_ReturnsParsableVersion()
        {
            var version = VersionHelper.GetAssemblyVersion();

            Assert.False(string.IsNullOrWhiteSpace(version));
            Assert.True(Version.TryParse(version, out _), $"Not a valid Version: {version}");
        }

        [Fact]
        public void GetFileVersion_ReturnsParsableVersion()
        {
            var version = VersionHelper.GetFileVersion();

            Assert.False(string.IsNullOrWhiteSpace(version));
            Assert.True(Version.TryParse(version, out _), $"Not a valid Version: {version}");
        }

        [Fact]
        public void GetProductVersion_StartsWithSemverLikePrefix()
        {
            var version = VersionHelper.GetProductVersion();

            Assert.False(string.IsNullOrWhiteSpace(version));
            Assert.Matches(VersionRegex, version);
        }

        [Fact]
        public void AllAccessors_AreDeterministic()
        {
            Assert.Equal(VersionHelper.GetAssemblyVersion(), VersionHelper.GetAssemblyVersion());
            Assert.Equal(VersionHelper.GetFileVersion(), VersionHelper.GetFileVersion());
            Assert.Equal(VersionHelper.GetProductVersion(), VersionHelper.GetProductVersion());
        }
    }
}
