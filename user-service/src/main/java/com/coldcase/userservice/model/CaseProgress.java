package com.coldcase.userservice.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "case_progress", schema = "users")
public class CaseProgress {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "agent_id", nullable = false)
    private UUID agentId;

    @Column(name = "case_id", nullable = false)
    private Integer caseId;

    @Column(nullable = false)
    private String status = "NOT_STARTED";

    @Column(name = "discovered_evidence_ids", columnDefinition = "TEXT")
    private String discoveredEvidenceIds = "[]";

    @Column(name = "interrogation_count", nullable = false)
    private int interrogationCount = 0;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column
    private Integer score;

    @Column
    private Integer rating;

    @PrePersist
    protected void onCreate() {
        if (startedAt == null) {
            startedAt = LocalDateTime.now();
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

    public String getDiscoveredEvidenceIds() { return discoveredEvidenceIds; }
    public void setDiscoveredEvidenceIds(String discoveredEvidenceIds) { this.discoveredEvidenceIds = discoveredEvidenceIds; }

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
