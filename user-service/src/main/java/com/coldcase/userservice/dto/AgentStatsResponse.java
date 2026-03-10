package com.coldcase.userservice.dto;

import java.util.UUID;

public class AgentStatsResponse {

    private UUID id;
    private String username;
    private String rank;
    private int casesCompleted;

    public AgentStatsResponse() {}

    public AgentStatsResponse(UUID id, String username, String rank, int casesCompleted) {
        this.id = id;
        this.username = username;
        this.rank = rank;
        this.casesCompleted = casesCompleted;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getRank() { return rank; }
    public void setRank(String rank) { this.rank = rank; }

    public int getCasesCompleted() { return casesCompleted; }
    public void setCasesCompleted(int casesCompleted) { this.casesCompleted = casesCompleted; }
}
