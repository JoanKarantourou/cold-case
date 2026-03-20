using System.Net;
using System.Net.Http.Json;
using ColdCase.Gateway.Models;

namespace ColdCase.Gateway.Services;

public class AiServiceClient
{
    private readonly HttpClient _httpClient;

    public AiServiceClient(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _httpClient.BaseAddress = new Uri(configuration["AiService:BaseUrl"] ?? "http://localhost:8000");
    }

    public async Task<List<CaseSummaryDto>> ListCases(string? mood = null, int? difficulty = null)
    {
        var query = new List<string>();
        if (!string.IsNullOrEmpty(mood)) query.Add($"mood={Uri.EscapeDataString(mood)}");
        if (difficulty.HasValue) query.Add($"difficulty={difficulty}");

        var url = "/api/ai/cases";
        if (query.Count > 0) url += "?" + string.Join("&", query);

        var response = await _httpClient.GetAsync(url);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<CaseSummaryDto>>() ?? new();
    }

    public async Task<CaseDetailDto?> GetCase(int caseId)
    {
        var response = await _httpClient.GetAsync($"/api/ai/cases/{caseId}");
        if (response.StatusCode == HttpStatusCode.NotFound) return null;
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseDetailDto>();
    }

    public async Task<List<CaseFileListDto>> GetCaseFiles(int caseId)
    {
        var response = await _httpClient.GetAsync($"/api/ai/cases/{caseId}/files");
        if (response.StatusCode == HttpStatusCode.NotFound) return new();
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<CaseFileListDto>>() ?? new();
    }

    public async Task<CaseFileDetailDto?> GetCaseFile(int caseId, int fileId)
    {
        var response = await _httpClient.GetAsync($"/api/ai/cases/{caseId}/files/{fileId}");
        if (response.StatusCode == HttpStatusCode.NotFound) return null;
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseFileDetailDto>();
    }

    public async Task<List<SuspectDto>> GetSuspects(int caseId)
    {
        var response = await _httpClient.GetAsync($"/api/ai/cases/{caseId}/suspects");
        if (response.StatusCode == HttpStatusCode.NotFound) return new();
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<SuspectDto>>() ?? new();
    }

    public async Task<List<EvidenceDto>> GetEvidence(int caseId, string? agentId = null)
    {
        var url = $"/api/ai/cases/{caseId}/evidence";
        if (!string.IsNullOrEmpty(agentId)) url += $"?agent_id={agentId}";
        var response = await _httpClient.GetAsync(url);
        if (response.StatusCode == HttpStatusCode.NotFound) return new();
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<EvidenceDto>>() ?? new();
    }

    public async Task<List<VictimDto>> GetVictims(int caseId)
    {
        var response = await _httpClient.GetAsync($"/api/ai/cases/{caseId}/victims");
        if (response.StatusCode == HttpStatusCode.NotFound) return new();
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<VictimDto>>() ?? new();
    }

    // Interrogation methods
    public async Task<InterrogationStartResult?> StartInterrogation(int caseId, int suspectId, string agentId)
    {
        var payload = new { case_id = caseId, suspect_id = suspectId, agent_id = agentId };
        var response = await _httpClient.PostAsJsonAsync("/api/ai/interrogation/start", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<InterrogationStartResult>();
    }

    public async Task<InterrogationMessageResult?> SendInterrogationMessage(
        int caseId, int suspectId, string agentId, string message, List<int> presentedEvidenceIds)
    {
        var payload = new
        {
            case_id = caseId,
            suspect_id = suspectId,
            agent_id = agentId,
            message,
            presented_evidence_ids = presentedEvidenceIds
        };
        var response = await _httpClient.PostAsJsonAsync("/api/ai/interrogation/message", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<InterrogationMessageResult>();
    }

    public async Task<InterrogationHistoryResult?> GetInterrogationHistory(
        int caseId, int suspectId, string agentId)
    {
        var response = await _httpClient.GetAsync(
            $"/api/ai/interrogation/history/{caseId}/{suspectId}/{agentId}");
        if (response.StatusCode == HttpStatusCode.NotFound) return null;
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<InterrogationHistoryResult>();
    }

    public async Task<object?> EndInterrogation(int caseId, int suspectId, string agentId)
    {
        var payload = new { case_id = caseId, suspect_id = suspectId, agent_id = agentId };
        var response = await _httpClient.PostAsJsonAsync("/api/ai/interrogation/end", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<object>();
    }

    // Forensics methods
    public async Task<ForensicSubmitResult?> SubmitForensics(
        int caseId, int evidenceId, string analysisType, string agentId)
    {
        var payload = new { evidence_id = evidenceId, analysis_type = analysisType, agent_id = agentId };
        var response = await _httpClient.PostAsJsonAsync(
            $"/api/ai/cases/{caseId}/forensics/submit", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ForensicSubmitResult>();
    }

    public async Task<ForensicStatusResult?> GetForensicStatus(int caseId, int requestId)
    {
        var response = await _httpClient.GetAsync(
            $"/api/ai/cases/{caseId}/forensics/{requestId}");
        if (response.StatusCode == HttpStatusCode.NotFound) return null;
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ForensicStatusResult>();
    }

    public async Task<List<ForensicStatusResult>> GetForensicRequests(int caseId, string agentId)
    {
        var response = await _httpClient.GetAsync(
            $"/api/ai/cases/{caseId}/forensics?agent_id={Uri.EscapeDataString(agentId)}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<ForensicStatusResult>>() ?? new();
    }
}
