using System.Security.Claims;
using ColdCase.Gateway.Models;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly JwtService _jwtService;
    private readonly UserServiceClient _userServiceClient;

    public AuthController(JwtService jwtService, UserServiceClient userServiceClient)
    {
        _jwtService = jwtService;
        _userServiceClient = userServiceClient;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(new { error = "Validation failed", message = "Invalid input" });

        try
        {
            var passwordHash = BCrypt.Net.BCrypt.HashPassword(request.Password);

            var agent = await _userServiceClient.CreateAgent(new CreateAgentRequest
            {
                Username = request.Username,
                Email = request.Email,
                PasswordHash = passwordHash
            });

            if (agent == null)
                return StatusCode(500, new { error = "Registration failed", message = "Could not create agent" });

            var token = _jwtService.GenerateToken(agent.Id, agent.Username, agent.Rank);

            return Ok(new AuthResponse { Token = token, Agent = agent });
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(new { error = "Registration failed", message = ex.Message });
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable", message = "User service is not available" });
        }
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(new { error = "Validation failed", message = "Invalid input" });

        try
        {
            var agent = await _userServiceClient.GetAgentByEmail(request.Email);

            if (agent == null)
                return Unauthorized(new { error = "Login failed", message = "Invalid credentials" });

            if (!BCrypt.Net.BCrypt.Verify(request.Password, agent.PasswordHash))
                return Unauthorized(new { error = "Login failed", message = "Invalid credentials" });

            var token = _jwtService.GenerateToken(agent.Id, agent.Username, agent.Rank);

            return Ok(new AuthResponse
            {
                Token = token,
                Agent = new AgentDto
                {
                    Id = agent.Id,
                    Username = agent.Username,
                    Email = agent.Email,
                    Rank = agent.Rank,
                    CasesCompleted = agent.CasesCompleted
                }
            });
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable", message = "User service is not available" });
        }
    }

    [Authorize]
    [HttpGet("me")]
    public async Task<IActionResult> Me()
    {
        var agentId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                      ?? User.FindFirstValue("sub");

        if (string.IsNullOrEmpty(agentId))
            return Unauthorized(new { error = "Unauthorized", message = "Invalid token" });

        try
        {
            var agent = await _userServiceClient.GetAgentById(agentId);

            if (agent == null)
                return NotFound(new { error = "Not found", message = "Agent not found" });

            return Ok(agent);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable", message = "User service is not available" });
        }
    }
}
