using System.Net;
using System.Net.Http.Json;
using ColdCase.Gateway.Models;

namespace ColdCase.Gateway.Services;

public class UserServiceClient
{
    private readonly HttpClient _httpClient;

    public UserServiceClient(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _httpClient.BaseAddress = new Uri(configuration["UserService:BaseUrl"] ?? "http://localhost:8080");
    }

    public async Task<AgentDto?> CreateAgent(CreateAgentRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/users/agents", request);

        if (response.StatusCode == HttpStatusCode.Conflict)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            throw new InvalidOperationException(error?.Message ?? "Agent already exists");
        }

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<AgentDto>();
    }

    public async Task<AgentWithPasswordDto?> GetAgentByEmail(string email)
    {
        var response = await _httpClient.GetAsync($"/api/users/agents/by-email/{Uri.EscapeDataString(email)}");

        if (response.StatusCode == HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<AgentWithPasswordDto>();
    }

    public async Task<AgentDto?> GetAgentById(string id)
    {
        var response = await _httpClient.GetAsync($"/api/users/agents/{id}");

        if (response.StatusCode == HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<AgentDto>();
    }

    public async Task<CaseProgressDto?> StartCase(string agentId, int caseId)
    {
        var response = await _httpClient.PostAsync(
            $"/api/users/agents/{agentId}/cases/{caseId}/start", null);

        if (response.StatusCode == HttpStatusCode.Conflict)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            throw new InvalidOperationException(error?.Message ?? "Case already started");
        }

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseProgressDto>();
    }

    public async Task<List<CaseProgressDto>> GetCaseProgressList(string agentId)
    {
        var response = await _httpClient.GetAsync($"/api/users/agents/{agentId}/cases");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<CaseProgressDto>>() ?? new();
    }

    public async Task<CaseProgressDto?> GetCaseProgress(string agentId, int caseId)
    {
        var response = await _httpClient.GetAsync($"/api/users/agents/{agentId}/cases/{caseId}");

        if (response.StatusCode == HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseProgressDto>();
    }

    public async Task<CaseProgressDto?> DiscoverEvidence(string agentId, int caseId, int evidenceId)
    {
        var response = await _httpClient.PutAsync(
            $"/api/users/agents/{agentId}/cases/{caseId}/evidence/{evidenceId}/discover", null);

        if (response.StatusCode == HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseProgressDto>();
    }

    public async Task<CaseProgressDto?> CompleteCase(string agentId, int caseId, int score, string rank)
    {
        var payload = new { score, rank };
        var response = await _httpClient.PostAsJsonAsync(
            $"/api/users/agents/{agentId}/cases/{caseId}/complete", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CaseProgressDto>();
    }

    private class ErrorResponse
    {
        public string? Error { get; set; }
        public string? Message { get; set; }
    }
}
