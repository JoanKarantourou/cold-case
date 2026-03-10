package com.coldcase.userservice;

import com.coldcase.userservice.dto.AgentResponse;
import com.coldcase.userservice.dto.CreateAgentRequest;
import com.coldcase.userservice.exception.AgentNotFoundException;
import com.coldcase.userservice.exception.DuplicateEmailException;
import com.coldcase.userservice.model.Agent;
import com.coldcase.userservice.repository.AgentRepository;
import com.coldcase.userservice.service.AgentService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AgentServiceTest {

    @Mock
    private AgentRepository agentRepository;

    @InjectMocks
    private AgentService agentService;

    private Agent testAgent;

    @BeforeEach
    void setUp() {
        testAgent = new Agent();
        testAgent.setId(UUID.randomUUID());
        testAgent.setUsername("testuser");
        testAgent.setEmail("test@example.com");
        testAgent.setPasswordHash("hashed_password");
    }

    @Test
    void createAgent_Success() {
        CreateAgentRequest request = new CreateAgentRequest("testuser", "test@example.com", "hashed_password");

        when(agentRepository.existsByEmail("test@example.com")).thenReturn(false);
        when(agentRepository.existsByUsername("testuser")).thenReturn(false);
        when(agentRepository.save(any(Agent.class))).thenReturn(testAgent);

        AgentResponse response = agentService.createAgent(request);

        assertNotNull(response);
        assertEquals("testuser", response.getUsername());
        assertEquals("test@example.com", response.getEmail());
        verify(agentRepository).save(any(Agent.class));
    }

    @Test
    void createAgent_DuplicateEmail_Throws() {
        CreateAgentRequest request = new CreateAgentRequest("testuser", "test@example.com", "hashed_password");

        when(agentRepository.existsByEmail("test@example.com")).thenReturn(true);

        assertThrows(DuplicateEmailException.class, () -> agentService.createAgent(request));
        verify(agentRepository, never()).save(any());
    }

    @Test
    void getAgentById_Success() {
        UUID id = testAgent.getId();
        when(agentRepository.findById(id)).thenReturn(Optional.of(testAgent));

        AgentResponse response = agentService.getAgentById(id);

        assertNotNull(response);
        assertEquals(id, response.getId());
        assertEquals("testuser", response.getUsername());
    }

    @Test
    void getAgentById_NotFound_Throws() {
        UUID id = UUID.randomUUID();
        when(agentRepository.findById(id)).thenReturn(Optional.empty());

        assertThrows(AgentNotFoundException.class, () -> agentService.getAgentById(id));
    }
}
