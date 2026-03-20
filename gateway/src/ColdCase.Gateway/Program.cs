using System.Text;
using ColdCase.Gateway.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// JWT Authentication
var jwtKey = builder.Configuration["Jwt:Key"] ?? "ColdCaseAI_DevSigningKey_2024_SuperSecret!";
var jwtIssuer = builder.Configuration["Jwt:Issuer"] ?? "coldcase-ai";
var jwtAudience = builder.Configuration["Jwt:Audience"] ?? "coldcase-api";

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtIssuer,
            ValidAudience = jwtAudience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };
    });

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("ColdCasePolicy", policy =>
    {
        policy.WithOrigins("http://localhost:4200", "http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// YARP Reverse Proxy
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

// Application Services
builder.Services.AddSingleton<JwtService>();
builder.Services.AddHttpClient<UserServiceClient>();
builder.Services.AddHttpClient<AiServiceClient>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("ColdCasePolicy");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.MapReverseProxy();

app.Run();

public partial class Program { }
