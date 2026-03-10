package com.coldcase.userservice.controller;

import com.coldcase.userservice.dto.*;
import com.coldcase.userservice.service.AgentService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/users")
public class AgentController {

    private final AgentService agentService;

    public AgentController(AgentService agentService) {
        this.agentService = agentService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "service", "user-service",
                "timestamp", Instant.now().toString()
        ));
    }

    @PostMapping("/agents")
    public ResponseEntity<AgentResponse> createAgent(@Valid @RequestBody CreateAgentRequest request) {
        AgentResponse agent = agentService.createAgent(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(agent);
    }

    @GetMapping("/agents/{id}")
    public ResponseEntity<AgentResponse> getAgentById(@PathVariable UUID id) {
        return ResponseEntity.ok(agentService.getAgentById(id));
    }

    @PutMapping("/agents/{id}")
    public ResponseEntity<AgentResponse> updateAgent(@PathVariable UUID id,
                                                     @Valid @RequestBody UpdateAgentRequest request) {
        return ResponseEntity.ok(agentService.updateAgent(id, request));
    }

    @GetMapping("/agents/by-email/{email}")
    public ResponseEntity<AgentWithPasswordResponse> getAgentByEmail(@PathVariable String email) {
        return ResponseEntity.ok(agentService.getAgentByEmail(email));
    }

    @GetMapping("/agents/{id}/stats")
    public ResponseEntity<AgentStatsResponse> getAgentStats(@PathVariable UUID id) {
        return ResponseEntity.ok(agentService.getAgentStats(id));
    }
}
