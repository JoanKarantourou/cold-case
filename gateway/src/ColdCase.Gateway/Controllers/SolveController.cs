using System.Security.Claims;
using ColdCase.Gateway.Models;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("api/case")]
[Authorize]
public class SolveController : ControllerBase
{
    private readonly AiServiceClient _aiService;
    private readonly UserServiceClient _userService;
    private readonly ILogger<SolveController> _logger;

    public SolveController(
        AiServiceClient aiService,
        UserServiceClient userService,
        ILogger<SolveController> logger)
    {
        _aiService = aiService;
        _userService = userService;
        _logger = logger;
    }

    private string? GetAgentId() =>
        User.FindFirstValue(ClaimTypes.NameIdentifier)
        ?? User.FindFirstValue("sub");

    [HttpPost("{caseId}/solve")]
    public async Task<IActionResult> SolveCase(int caseId, [FromBody] SolveCaseRequest request)
    {
        var agentId = GetAgentId();
        if (string.IsNullOrEmpty(agentId)) return Unauthorized();

        try
        {
            // 1. Submit solution to AI service for scoring
            var scoreResult = await _aiService.SolveCase(caseId, agentId, request);
            if (scoreResult == null)
                return StatusCode(500, new { error = "Scoring failed" });

            // 2. Update case progress in user service
            try
            {
                await _userService.CompleteCase(
                    agentId, caseId, scoreResult.OverallScore, scoreResult.RankEarned);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to update case progress for case {CaseId}", caseId);
            }

            return Ok(scoreResult);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable" });
        }
    }
}
