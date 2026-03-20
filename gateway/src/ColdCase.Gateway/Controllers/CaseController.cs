using System.Security.Claims;
using ColdCase.Gateway.Models;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CaseController : ControllerBase
{
    private readonly AiServiceClient _aiService;
    private readonly UserServiceClient _userService;
    private readonly ILogger<CaseController> _logger;

    public CaseController(
        AiServiceClient aiService,
        UserServiceClient userService,
        ILogger<CaseController> logger)
    {
        _aiService = aiService;
        _userService = userService;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IActionResult> ListCases(
        [FromQuery] string? mood = null,
        [FromQuery] int? difficulty = null)
    {
        try
        {
            var cases = await _aiService.ListCases(mood, difficulty);
            return Ok(cases);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "AI service unavailable" });
        }
    }

    [HttpGet("{caseId}")]
    [Authorize]
    public async Task<IActionResult> GetCase(int caseId)
    {
        try
        {
            var agentId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                          ?? User.FindFirstValue("sub");
            if (string.IsNullOrEmpty(agentId))
                return Unauthorized();

            var caseDetailTask = _aiService.GetCase(caseId);
            var progressTask = _userService.GetCaseProgress(agentId, caseId);

            await Task.WhenAll(caseDetailTask, progressTask);

            var caseDetail = await caseDetailTask;
            if (caseDetail == null)
                return NotFound(new { error = "Case not found" });

            return Ok(new CaseWithProgressDto
            {
                Case = caseDetail,
                Progress = await progressTask
            });
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable" });
        }
    }

    [HttpPost("{caseId}/start")]
    [Authorize]
    public async Task<IActionResult> StartCase(int caseId)
    {
        try
        {
            var agentId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                          ?? User.FindFirstValue("sub");
            if (string.IsNullOrEmpty(agentId))
                return Unauthorized();

            var progress = await _userService.StartCase(agentId, caseId);
            return Ok(progress);
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(new { error = ex.Message });
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable" });
        }
    }

    [HttpGet("progress")]
    [Authorize]
    public async Task<IActionResult> GetMyProgress()
    {
        try
        {
            var agentId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                          ?? User.FindFirstValue("sub");
            if (string.IsNullOrEmpty(agentId))
                return Unauthorized();

            var progressList = await _userService.GetCaseProgressList(agentId);
            return Ok(progressList);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable" });
        }
    }

    [HttpPut("{caseId}/evidence/{evidenceId}/discover")]
    [Authorize]
    public async Task<IActionResult> DiscoverEvidence(int caseId, int evidenceId)
    {
        try
        {
            var agentId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                          ?? User.FindFirstValue("sub");
            if (string.IsNullOrEmpty(agentId))
                return Unauthorized();

            var progress = await _userService.DiscoverEvidence(agentId, caseId, evidenceId);
            if (progress == null)
                return NotFound(new { error = "Case progress not found" });

            return Ok(progress);
        }
        catch (HttpRequestException)
        {
            return StatusCode(503, new { error = "Service unavailable" });
        }
    }
}
