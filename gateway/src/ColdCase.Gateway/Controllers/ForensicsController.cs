using System.Security.Claims;
using ColdCase.Gateway.Models;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ForensicsController : ControllerBase
{
    private readonly AiServiceClient _aiService;
    private readonly ILogger<ForensicsController> _logger;

    public ForensicsController(
        AiServiceClient aiService,
        ILogger<ForensicsController> logger)
    {
        _aiService = aiService;
        _logger = logger;
    }

    private string? GetAgentId() =>
        User.FindFirstValue(ClaimTypes.NameIdentifier)
        ?? User.FindFirstValue("sub");

    [HttpPost("submit")]
    public async Task<IActionResult> SubmitForensics([FromBody] ForensicSubmitRequest request)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var result = await _aiService.SubmitForensics(
                request.CaseId, request.EvidenceId, request.AnalysisType, agentId);
            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpGet("{caseId}/status/{requestId}")]
    public async Task<IActionResult> GetStatus(int caseId, int requestId)
    {
        try
        {
            var result = await _aiService.GetForensicStatus(caseId, requestId);
            if (result == null)
                return NotFound(new { error = "Forensic request not found" });
            return Ok(result);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpGet("{caseId}/requests")]
    public async Task<IActionResult> GetRequests(int caseId)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            var results = await _aiService.GetForensicRequests(caseId, agentId);
            return Ok(results);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }
}
