FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 5000

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY src/ColdCase.Gateway/ColdCase.Gateway.csproj ColdCase.Gateway/
RUN dotnet restore ColdCase.Gateway/ColdCase.Gateway.csproj
COPY src/ColdCase.Gateway/ ColdCase.Gateway/
WORKDIR /src/ColdCase.Gateway
RUN dotnet build -c Release -o /app/build

FROM build AS publish
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENV ASPNETCORE_URLS=http://+:5000
ENTRYPOINT ["dotnet", "ColdCase.Gateway.dll"]
