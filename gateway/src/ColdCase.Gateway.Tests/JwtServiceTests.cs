using System.IdentityModel.Tokens.Jwt;
using ColdCase.Gateway.Services;
using Microsoft.Extensions.Configuration;

namespace ColdCase.Gateway.Tests;

public class JwtServiceTests
{
    private readonly JwtService _jwtService;

    public JwtServiceTests()
    {
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Jwt:Key"] = "ColdCaseAI_DevSigningKey_2024_SuperSecret!",
                ["Jwt:Issuer"] = "coldcase-ai",
                ["Jwt:Audience"] = "coldcase-api",
                ["Jwt:ExpiryHours"] = "24"
            })
            .Build();

        _jwtService = new JwtService(config);
    }

    [Fact]
    public void GenerateToken_ReturnsValidJwt()
    {
        var token = _jwtService.GenerateToken("agent-123", "testuser", "ROOKIE");

        Assert.NotNull(token);
        Assert.NotEmpty(token);

        var handler = new JwtSecurityTokenHandler();
        var jwt = handler.ReadJwtToken(token);

        Assert.Equal("coldcase-ai", jwt.Issuer);
        Assert.Contains("coldcase-api", jwt.Audiences);
        Assert.Equal("agent-123", jwt.Subject);
        Assert.Equal("testuser", jwt.Claims.First(c => c.Type == "username").Value);
        Assert.Equal("ROOKIE", jwt.Claims.First(c => c.Type == "rank").Value);
    }

    [Fact]
    public void GenerateToken_HasCorrectExpiry()
    {
        var token = _jwtService.GenerateToken("agent-123", "testuser", "ROOKIE");

        var handler = new JwtSecurityTokenHandler();
        var jwt = handler.ReadJwtToken(token);

        var expectedExpiry = DateTime.UtcNow.AddHours(24);
        var actualExpiry = jwt.ValidTo;

        Assert.True(Math.Abs((expectedExpiry - actualExpiry).TotalMinutes) < 1);
    }

    [Fact]
    public void ValidateToken_WithValidToken_ReturnsPrincipal()
    {
        var token = _jwtService.GenerateToken("agent-456", "agentsmith", "DETECTIVE");

        var principal = _jwtService.ValidateToken(token);

        Assert.NotNull(principal);
    }

    [Fact]
    public void ValidateToken_WithInvalidToken_ReturnsNull()
    {
        var principal = _jwtService.ValidateToken("invalid-token");

        Assert.Null(principal);
    }
}
