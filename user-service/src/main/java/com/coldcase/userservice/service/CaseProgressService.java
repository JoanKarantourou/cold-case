package com.coldcase.userservice.service;

import com.coldcase.userservice.dto.CaseProgressResponse;
import com.coldcase.userservice.exception.AgentNotFoundException;
import com.coldcase.userservice.exception.CaseAlreadyStartedException;
import com.coldcase.userservice.exception.CaseProgressNotFoundException;
import com.coldcase.userservice.model.CaseProgress;
import com.coldcase.userservice.repository.AgentRepository;
import com.coldcase.userservice.repository.CaseProgressRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class CaseProgressService {

    private final CaseProgressRepository caseProgressRepository;
    private final AgentRepository agentRepository;
    private final ObjectMapper objectMapper;

    public CaseProgressService(CaseProgressRepository caseProgressRepository,
                               AgentRepository agentRepository,
                               ObjectMapper objectMapper) {
        this.caseProgressRepository = caseProgressRepository;
        this.agentRepository = agentRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public CaseProgressResponse startCase(UUID agentId, Integer caseId) {
        if (!agentRepository.existsById(agentId)) {
            throw new AgentNotFoundException("Agent not found: " + agentId);
        }

        if (caseProgressRepository.existsByAgentIdAndCaseId(agentId, caseId)) {
            throw new CaseAlreadyStartedException(
                    "Case " + caseId + " already started by agent " + agentId);
        }

        CaseProgress progress = new CaseProgress();
        progress.setAgentId(agentId);
        progress.setCaseId(caseId);
        progress.setStatus("IN_PROGRESS");

        CaseProgress saved = caseProgressRepository.save(progress);
        return new CaseProgressResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<CaseProgressResponse> getCaseProgressList(UUID agentId) {
        return caseProgressRepository.findByAgentId(agentId).stream()
                .map(CaseProgressResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public CaseProgressResponse getCaseProgress(UUID agentId, Integer caseId) {
        CaseProgress progress = caseProgressRepository.findByAgentIdAndCaseId(agentId, caseId)
                .orElseThrow(() -> new CaseProgressNotFoundException(
                        "Case progress not found for agent " + agentId + " and case " + caseId));
        return new CaseProgressResponse(progress);
    }

    @Transactional
    public CaseProgressResponse discoverEvidence(UUID agentId, Integer caseId, Integer evidenceId) {
        CaseProgress progress = caseProgressRepository.findByAgentIdAndCaseId(agentId, caseId)
                .orElseThrow(() -> new CaseProgressNotFoundException(
                        "Case progress not found for agent " + agentId + " and case " + caseId));

        List<Integer> evidenceIds = parseEvidenceIds(progress.getDiscoveredEvidenceIds());

        if (!evidenceIds.contains(evidenceId)) {
            evidenceIds.add(evidenceId);
            progress.setDiscoveredEvidenceIds(writeEvidenceIds(evidenceIds));
            progress = caseProgressRepository.save(progress);
        }

        return new CaseProgressResponse(progress);
    }

    @Transactional
    public CaseProgressResponse completeCase(UUID agentId, Integer caseId, Integer score, String rank) {
        CaseProgress progress = caseProgressRepository.findByAgentIdAndCaseId(agentId, caseId)
                .orElseThrow(() -> new CaseProgressNotFoundException(
                        "Case progress not found for agent " + agentId + " and case " + caseId));

        progress.setStatus("SOLVED");
        progress.setScore(score);
        progress.setCompletedAt(LocalDateTime.now());
        progress = caseProgressRepository.save(progress);

        // Update agent stats
        var agent = agentRepository.findById(agentId)
                .orElseThrow(() -> new AgentNotFoundException("Agent not found: " + agentId));
        agent.setCasesCompleted(agent.getCasesCompleted() + 1);

        // Update rank if the new rank is higher
        String[] rankOrder = {"ROOKIE", "DETECTIVE", "SENIOR DETECTIVE", "SPECIAL AGENT", "CHIEF INVESTIGATOR"};
        int currentRankIdx = java.util.Arrays.asList(rankOrder).indexOf(agent.getRank());
        int newRankIdx = java.util.Arrays.asList(rankOrder).indexOf(rank);
        if (newRankIdx > currentRankIdx) {
            agent.setRank(rank);
        }

        agentRepository.save(agent);

        return new CaseProgressResponse(progress);
    }

    private List<Integer> parseEvidenceIds(String json) {
        try {
            if (json == null || json.isBlank()) {
                return new ArrayList<>();
            }
            return new ArrayList<>(objectMapper.readValue(json, new TypeReference<List<Integer>>() {}));
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    private String writeEvidenceIds(List<Integer> ids) {
        try {
            return objectMapper.writeValueAsString(ids);
        } catch (Exception e) {
            return "[]";
        }
    }
}
