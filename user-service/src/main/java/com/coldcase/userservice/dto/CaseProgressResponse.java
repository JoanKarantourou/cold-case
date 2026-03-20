package com.coldcase.userservice.dto;

import com.coldcase.userservice.model.CaseProgress;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class CaseProgressResponse {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    private UUID id;
    private UUID agentId;
    private Integer caseId;
    private String status;
    private List<Integer> discoveredEvidenceIds;
    private int interrogationCount;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    private Integer score;
    private Integer rating;

    public CaseProgressResponse() {}

    public CaseProgressResponse(CaseProgress entity) {
        this.id = entity.getId();
        this.agentId = entity.getAgentId();
        this.caseId = entity.getCaseId();
        this.status = entity.getStatus();
        this.discoveredEvidenceIds = parseEvidenceIds(entity.getDiscoveredEvidenceIds());
        this.interrogationCount = entity.getInterrogationCount();
        this.startedAt = entity.getStartedAt();
        this.completedAt = entity.getCompletedAt();
        this.score = entity.getScore();
        this.rating = entity.getRating();
    }

    private List<Integer> parseEvidenceIds(String json) {
        try {
            if (json == null || json.isBlank()) {
                return Collections.emptyList();
            }
            return objectMapper.readValue(json, new TypeReference<List<Integer>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public UUID getAgentId() { return agentId; }
    public void setAgentId(UUID agentId) { this.agentId = agentId; }

    public Integer getCaseId() { return caseId; }
    public void setCaseId(Integer caseId) { this.caseId = caseId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public List<Integer> getDiscoveredEvidenceIds() { return discoveredEvidenceIds; }
    public void setDiscoveredEvidenceIds(List<Integer> discoveredEvidenceIds) { this.discoveredEvidenceIds = discoveredEvidenceIds; }

    public int getInterrogationCount() { return interrogationCount; }
    public void setInterrogationCount(int interrogationCount) { this.interrogationCount = interrogationCount; }

    public LocalDateTime getStartedAt() { return startedAt; }
    public void setStartedAt(LocalDateTime startedAt) { this.startedAt = startedAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }

    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }

    public Integer getRating() { return rating; }
    public void setRating(Integer rating) { this.rating = rating; }
}
