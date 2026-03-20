using System.Security.Claims;
using ColdCase.Gateway.Models;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class InterrogationController : ControllerBase
{
    private readonly AiServiceClient _aiService;
    private readonly UserServiceClient _userService;
    private readonly ILogger<InterrogationController> _logger;

    public InterrogationController(
        AiServiceClient aiService,
        UserServiceClient userService,
        ILogger<InterrogationController> logger)
    {
        _aiService = aiService;
        _userService = userService;
        _logger = logger;
    }

    private string? GetAgentId() =>
        User.FindFirstValue(ClaimTypes.NameIdentifier)
        ?? User.FindFirstValue("sub");

    [HttpPost("start")]
    public async Task<IActionResult> StartInterrogation([FromBody] StartInterrogationRequest request)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var result = await _aiService.StartInterrogation(
                request.CaseId, request.SuspectId, agentId);
            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpPost("message")]
    public async Task<IActionResult> SendMessage([FromBody] InterrogationMessageRequest request)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var result = await _aiService.SendInterrogationMessage(
                request.CaseId, request.SuspectId, agentId,
                request.Message, request.PresentedEvidenceIds);

            // If evidence was discovered, update user service
            if (result?.EvidenceDiscovered != null)
            {
                foreach (var ev in result.EvidenceDiscovered)
                {
                    try
                    {
                        await _userService.DiscoverEvidence(
                            agentId, request.CaseId, ev.Id);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex,
                            "Failed to update evidence discovery for evidence {Id}", ev.Id);
                    }
                }
            }

            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpGet("history/{caseId}/{suspectId}")]
    public async Task<IActionResult> GetHistory(int caseId, int suspectId)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var result = await _aiService.GetInterrogationHistory(
                caseId, suspectId, agentId);
            if (result == null)
                return NotFound(new { error = "No interrogation session found" });
            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpPost("end")]
    public async Task<IActionResult> EndInterrogation([FromBody] EndInterrogationRequest request)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var result = await _aiService.EndInterrogation(
                request.CaseId, request.SuspectId, agentId);
            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }
}
