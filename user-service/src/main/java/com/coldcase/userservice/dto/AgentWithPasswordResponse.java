package com.coldcase.userservice.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class AgentWithPasswordResponse extends AgentResponse {

    private String passwordHash;

    public AgentWithPasswordResponse() {}

    public AgentWithPasswordResponse(UUID id, String username, String email, String rank,
                                     int casesCompleted, LocalDateTime createdAt,
                                     LocalDateTime updatedAt, String passwordHash) {
        super(id, username, email, rank, casesCompleted, createdAt, updatedAt);
        this.passwordHash = passwordHash;
    }

    public String getPasswordHash() { return passwordHash; }
    public void setPasswordHash(String passwordHash) { this.passwordHash = passwordHash; }
}
