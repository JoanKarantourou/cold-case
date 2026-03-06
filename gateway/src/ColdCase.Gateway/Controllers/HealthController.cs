using Microsoft.AspNetCore.Mvc;

namespace ColdCase.Gateway.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet("/health")]
    public IActionResult GetHealth()
    {
        return Ok(new
        {
            status = "healthy",
            service = "gateway",
            timestamp = DateTime.UtcNow
        });
    }
}
