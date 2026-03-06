package com.coldcase.userservice.repository;

import com.coldcase.userservice.model.Agent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface AgentRepository extends JpaRepository<Agent, UUID> {
    Optional<Agent> findByEmail(String email);
    Optional<Agent> findByUsername(String username);
    boolean existsByEmail(String email);
    boolean existsByUsername(String username);
}
