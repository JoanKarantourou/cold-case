package com.coldcase.userservice.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class AgentResponse {

    private UUID id;
    private String username;
    private String email;
    private String rank;
    private int casesCompleted;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public AgentResponse() {}

    public AgentResponse(UUID id, String username, String email, String rank,
                         int casesCompleted, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.rank = rank;
        this.casesCompleted = casesCompleted;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getRank() { return rank; }
    public void setRank(String rank) { this.rank = rank; }

    public int getCasesCompleted() { return casesCompleted; }
    public void setCasesCompleted(int casesCompleted) { this.casesCompleted = casesCompleted; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
