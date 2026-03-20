package com.coldcase.userservice.controller;

import com.coldcase.userservice.dto.CaseProgressResponse;
import com.coldcase.userservice.dto.CompleteCaseRequest;
import com.coldcase.userservice.service.CaseProgressService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/users/agents/{agentId}/cases")
public class CaseProgressController {

    private final CaseProgressService caseProgressService;

    public CaseProgressController(CaseProgressService caseProgressService) {
        this.caseProgressService = caseProgressService;
    }

    @PostMapping("/{caseId}/start")
    public ResponseEntity<CaseProgressResponse> startCase(@PathVariable UUID agentId,
                                                          @PathVariable Integer caseId) {
        CaseProgressResponse response = caseProgressService.startCase(agentId, caseId);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping
    public ResponseEntity<List<CaseProgressResponse>> getCaseProgressList(@PathVariable UUID agentId) {
        return ResponseEntity.ok(caseProgressService.getCaseProgressList(agentId));
    }

    @GetMapping("/{caseId}")
    public ResponseEntity<CaseProgressResponse> getCaseProgress(@PathVariable UUID agentId,
                                                                @PathVariable Integer caseId) {
        return ResponseEntity.ok(caseProgressService.getCaseProgress(agentId, caseId));
    }

    @PutMapping("/{caseId}/evidence/{evidenceId}/discover")
    public ResponseEntity<CaseProgressResponse> discoverEvidence(@PathVariable UUID agentId,
                                                                 @PathVariable Integer caseId,
                                                                 @PathVariable Integer evidenceId) {
        return ResponseEntity.ok(caseProgressService.discoverEvidence(agentId, caseId, evidenceId));
    }

    @PostMapping("/{caseId}/complete")
    public ResponseEntity<CaseProgressResponse> completeCase(@PathVariable UUID agentId,
                                                              @PathVariable Integer caseId,
                                                              @Valid @RequestBody CompleteCaseRequest request) {
        return ResponseEntity.ok(
                caseProgressService.completeCase(agentId, caseId, request.getScore(), request.getRank()));
    }
}
