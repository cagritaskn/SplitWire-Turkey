using FluentAssertions;
using System.Text.RegularExpressions;
using Xunit;

namespace SplitWire_Turkey.Tests
{
    public class VersionHelperTests
    {
        [Fact]
        public void GetAssemblyVersion_ShouldReturnValidVersionFormat()
        {
            // Act
            var version = SplitWireTurkey.VersionHelper.GetAssemblyVersion();

            // Assert
            version.Should().NotBeNullOrEmpty();
            version.Should().MatchRegex(@"^\d+\.\d+\.\d+(\.\d+)?$", "version should be in format x.x.x or x.x.x.x");
        }

        [Fact]
        public void GetFileVersion_ShouldReturnValidVersionFormat()
        {
            // Act
            var version = SplitWireTurkey.VersionHelper.GetFileVersion();

            // Assert
            version.Should().NotBeNullOrEmpty();
            version.Should().MatchRegex(@"^\d+\.\d+\.\d+(\.\d+)?$", "version should be in format x.x.x or x.x.x.x");
        }

        [Fact]
        public void GetProductVersion_ShouldReturnValidVersionFormat()
        {
            // Act
            var version = SplitWireTurkey.VersionHelper.GetProductVersion();

            // Assert
            version.Should().NotBeNullOrEmpty();
            version.Should().MatchRegex(@"^\d+\.\d+\.\d+(\.\d+)?", "version should start with format x.x.x or x.x.x.x");
        }

        [Fact]
        public void GetAssemblyVersion_ShouldReturnConsistentValue()
        {
            // Act
            var version1 = SplitWireTurkey.VersionHelper.GetAssemblyVersion();
            var version2 = SplitWireTurkey.VersionHelper.GetAssemblyVersion();

            // Assert
            version1.Should().Be(version2, "version should be consistent across calls");
        }

        [Fact]
        public void GetFileVersion_ShouldReturnConsistentValue()
        {
            // Act
            var version1 = SplitWireTurkey.VersionHelper.GetFileVersion();
            var version2 = SplitWireTurkey.VersionHelper.GetFileVersion();

            // Assert
            version1.Should().Be(version2, "file version should be consistent across calls");
        }

        [Fact]
        public void GetProductVersion_ShouldReturnConsistentValue()
        {
            // Act
            var version1 = SplitWireTurkey.VersionHelper.GetProductVersion();
            var version2 = SplitWireTurkey.VersionHelper.GetProductVersion();

            // Assert
            version1.Should().Be(version2, "product version should be consistent across calls");
        }

        [Theory]
        [InlineData("1.0.0.0")]
        [InlineData("1.5.4")]
        [InlineData("2.0.0.0")]
        public void VersionFormats_ShouldBeValid(string expectedPattern)
        {
            // Act
            var assemblyVersion = SplitWireTurkey.VersionHelper.GetAssemblyVersion();
            var fileVersion = SplitWireTurkey.VersionHelper.GetFileVersion();
            var productVersion = SplitWireTurkey.VersionHelper.GetProductVersion();

            // Assert
            var versionRegex = new Regex(@"^\d+\.\d+\.\d+(\.\d+)?");
            
            versionRegex.IsMatch(assemblyVersion).Should().BeTrue($"Assembly version '{assemblyVersion}' should match version pattern");
            versionRegex.IsMatch(fileVersion).Should().BeTrue($"File version '{fileVersion}' should match version pattern");
            versionRegex.IsMatch(productVersion).Should().BeTrue($"Product version '{productVersion}' should match version pattern");
        }
    }
}