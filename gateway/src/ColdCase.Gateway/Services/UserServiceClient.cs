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

    private class ErrorResponse
    {
        public string? Error { get; set; }
        public string? Message { get; set; }
    }
}
