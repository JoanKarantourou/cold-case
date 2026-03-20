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
}
