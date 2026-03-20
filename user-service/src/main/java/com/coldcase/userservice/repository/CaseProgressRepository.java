package com.coldcase.userservice.repository;

import com.coldcase.userservice.model.CaseProgress;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface CaseProgressRepository extends JpaRepository<CaseProgress, UUID> {
    List<CaseProgress> findByAgentId(UUID agentId);
    Optional<CaseProgress> findByAgentIdAndCaseId(UUID agentId, Integer caseId);
    boolean existsByAgentIdAndCaseId(UUID agentId, Integer caseId);
}
