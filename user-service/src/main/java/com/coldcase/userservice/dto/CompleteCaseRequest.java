package com.coldcase.userservice.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public class CompleteCaseRequest {

    @Min(0)
    @Max(100)
    private int score;

    @NotBlank
    private String rank;

    public int getScore() { return score; }
    public void setScore(int score) { this.score = score; }

    public String getRank() { return rank; }
    public void setRank(String rank) { this.rank = rank; }
}
