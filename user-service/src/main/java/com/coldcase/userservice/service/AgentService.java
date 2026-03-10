package com.coldcase.userservice.service;

import com.coldcase.userservice.dto.*;
import com.coldcase.userservice.exception.AgentNotFoundException;
import com.coldcase.userservice.exception.DuplicateEmailException;
import com.coldcase.userservice.exception.DuplicateUsernameException;
import com.coldcase.userservice.model.Agent;
import com.coldcase.userservice.repository.AgentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class AgentService {

    private final AgentRepository agentRepository;

    public AgentService(AgentRepository agentRepository) {
        this.agentRepository = agentRepository;
    }

    @Transactional
    public AgentResponse createAgent(CreateAgentRequest request) {
        if (agentRepository.existsByEmail(request.getEmail())) {
            throw new DuplicateEmailException("Email already registered: " + request.getEmail());
        }
        if (agentRepository.existsByUsername(request.getUsername())) {
            throw new DuplicateUsernameException("Username already taken: " + request.getUsername());
        }

        Agent agent = new Agent();
        agent.setUsername(request.getUsername());
        agent.setEmail(request.getEmail());
        agent.setPasswordHash(request.getPasswordHash());

        Agent saved = agentRepository.save(agent);
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public AgentResponse getAgentById(UUID id) {
        Agent agent = agentRepository.findById(id)
                .orElseThrow(() -> new AgentNotFoundException("Agent not found: " + id));
        return toResponse(agent);
    }

    @Transactional(readOnly = true)
    public AgentWithPasswordResponse getAgentByEmail(String email) {
        Agent agent = agentRepository.findByEmail(email)
                .orElseThrow(() -> new AgentNotFoundException("Agent not found with email: " + email));
        return toResponseWithPassword(agent);
    }

    @Transactional
    public AgentResponse updateAgent(UUID id, UpdateAgentRequest request) {
        Agent agent = agentRepository.findById(id)
                .orElseThrow(() -> new AgentNotFoundException("Agent not found: " + id));

        if (request.getEmail() != null && !request.getEmail().equals(agent.getEmail())) {
            if (agentRepository.existsByEmail(request.getEmail())) {
                throw new DuplicateEmailException("Email already registered: " + request.getEmail());
            }
            agent.setEmail(request.getEmail());
        }

        if (request.getUsername() != null && !request.getUsername().equals(agent.getUsername())) {
            if (agentRepository.existsByUsername(request.getUsername())) {
                throw new DuplicateUsernameException("Username already taken: " + request.getUsername());
            }
            agent.setUsername(request.getUsername());
        }

        Agent saved = agentRepository.save(agent);
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public AgentStatsResponse getAgentStats(UUID id) {
        Agent agent = agentRepository.findById(id)
                .orElseThrow(() -> new AgentNotFoundException("Agent not found: " + id));
        return new AgentStatsResponse(agent.getId(), agent.getUsername(),
                agent.getRank(), agent.getCasesCompleted());
    }

    private AgentResponse toResponse(Agent agent) {
        return new AgentResponse(
                agent.getId(), agent.getUsername(), agent.getEmail(),
                agent.getRank(), agent.getCasesCompleted(),
                agent.getCreatedAt(), agent.getUpdatedAt()
        );
    }

    private AgentWithPasswordResponse toResponseWithPassword(Agent agent) {
        return new AgentWithPasswordResponse(
                agent.getId(), agent.getUsername(), agent.getEmail(),
                agent.getRank(), agent.getCasesCompleted(),
                agent.getCreatedAt(), agent.getUpdatedAt(),
                agent.getPasswordHash()
        );
    }
}
