using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.SignalR;

namespace ColdCase.Gateway.Hubs;

[Authorize]
public class InvestigationHub : Hub
{
    private readonly ILogger<InvestigationHub> _logger;

    public InvestigationHub(ILogger<InvestigationHub> logger)
    {
        _logger = logger;
    }

    public override async Task OnConnectedAsync()
    {
        var agentId = Context.UserIdentifier;
        _logger.LogInformation("Agent {AgentId} connected to InvestigationHub", agentId);
        await base.OnConnectedAsync();
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        var agentId = Context.UserIdentifier;
        _logger.LogInformation("Agent {AgentId} disconnected from InvestigationHub", agentId);
        await base.OnDisconnectedAsync(exception);
    }

    /// <summary>Notify agent that new evidence has been discovered.</summary>
    public static async Task NotifyEvidenceDiscovered(
        IHubContext<InvestigationHub> hubContext,
        string agentId,
        int evidenceId,
        string evidenceTitle)
    {
        await hubContext.Clients.User(agentId).SendAsync(
            "EvidenceDiscovered",
            new { evidenceId, title = evidenceTitle });
    }

    /// <summary>Notify agent that forensic analysis is complete.</summary>
    public static async Task NotifyForensicsComplete(
        IHubContext<InvestigationHub> hubContext,
        string agentId,
        int requestId,
        int evidenceId,
        string analysisType)
    {
        await hubContext.Clients.User(agentId).SendAsync(
            "ForensicsComplete",
            new { requestId, evidenceId, analysisType });
    }

    /// <summary>Send a system alert to a specific agent.</summary>
    public static async Task SendSystemAlert(
        IHubContext<InvestigationHub> hubContext,
        string agentId,
        string message)
    {
        await hubContext.Clients.User(agentId).SendAsync(
            "SystemAlert",
            new { message });
    }
}
