namespace ColdCase.Gateway.Models;

public class CaseSummaryDto
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string CaseNumber { get; set; } = string.Empty;
    public string Classification { get; set; } = string.Empty;
    public int Difficulty { get; set; }
    public List<string> MoodTags { get; set; } = new();
    public string Era { get; set; } = string.Empty;
    public string Synopsis { get; set; } = string.Empty;
}

public class CaseDetailDto
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string CaseNumber { get; set; } = string.Empty;
    public string Classification { get; set; } = string.Empty;
    public int Difficulty { get; set; }
    public string SettingDescription { get; set; } = string.Empty;
    public string Era { get; set; } = string.Empty;
    public List<string> MoodTags { get; set; } = new();
    public string CrimeType { get; set; } = string.Empty;
    public string Synopsis { get; set; } = string.Empty;
    public string CreatedAt { get; set; } = string.Empty;
}

public class CaseWithProgressDto
{
    public CaseDetailDto Case { get; set; } = null!;
    public CaseProgressDto? Progress { get; set; }
}

public class CaseProgressDto
{
    public string Id { get; set; } = string.Empty;
    public string AgentId { get; set; } = string.Empty;
    public int CaseId { get; set; }
    public string Status { get; set; } = string.Empty;
    public List<int> DiscoveredEvidenceIds { get; set; } = new();
    public int InterrogationCount { get; set; }
    public string? StartedAt { get; set; }
    public string? CompletedAt { get; set; }
    public int? Score { get; set; }
    public int? Rating { get; set; }
}

public class SuspectDto
{
    public int Id { get; set; }
    public int CaseId { get; set; }
    public string Name { get; set; } = string.Empty;
    public int Age { get; set; }
    public string Occupation { get; set; } = string.Empty;
    public string RelationshipToVictim { get; set; } = string.Empty;
    public List<string> PersonalityTraits { get; set; } = new();
    public string Alibi { get; set; } = string.Empty;
}

public class EvidenceDto
{
    public int Id { get; set; }
    public int CaseId { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public bool Discovered { get; set; }
    public bool IsRedHerring { get; set; }
}

public class VictimDto
{
    public int Id { get; set; }
    public int CaseId { get; set; }
    public string Name { get; set; } = string.Empty;
    public int Age { get; set; }
    public string Occupation { get; set; } = string.Empty;
    public string CauseOfDeath { get; set; } = string.Empty;
    public string Background { get; set; } = string.Empty;
}

public class CaseFileListDto
{
    public int Id { get; set; }
    public int CaseId { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string ClassificationLevel { get; set; } = string.Empty;
}

public class CaseFileDetailDto : CaseFileListDto
{
    public string Content { get; set; } = string.Empty;
}

// Interrogation models
public class StartInterrogationRequest
{
    public int CaseId { get; set; }
    public int SuspectId { get; set; }
}

public class InterrogationMessageRequest
{
    public int CaseId { get; set; }
    public int SuspectId { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<int> PresentedEvidenceIds { get; set; } = new();
}

public class EndInterrogationRequest
{
    public int CaseId { get; set; }
    public int SuspectId { get; set; }
}

public class InterrogationStartResult
{
    public bool SessionActive { get; set; }
    public string EmotionalState { get; set; } = string.Empty;
    public int MessageCount { get; set; }
    public List<InterrogationHistoryEntry> History { get; set; } = new();
    public string? OpeningStatement { get; set; }
}

public class InterrogationMessageResult
{
    public string Response { get; set; } = string.Empty;
    public string EmotionalState { get; set; } = string.Empty;
    public int MessageCount { get; set; }
    public List<DiscoveredEvidenceItem> EvidenceDiscovered { get; set; } = new();
}

public class InterrogationHistoryResult
{
    public string EmotionalState { get; set; } = string.Empty;
    public int MessageCount { get; set; }
    public List<InterrogationHistoryEntry> History { get; set; } = new();
    public List<DiscoveredEvidenceItem> EvidenceDiscovered { get; set; } = new();
}

public class InterrogationHistoryEntry
{
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}

public class DiscoveredEvidenceItem
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
}

// Forensics models
public class ForensicSubmitRequest
{
    public int CaseId { get; set; }
    public int EvidenceId { get; set; }
    public string AnalysisType { get; set; } = string.Empty;
}

public class ForensicSubmitResult
{
    public int RequestId { get; set; }
    public string Status { get; set; } = string.Empty;
    public string AnalysisType { get; set; } = string.Empty;
    public int EstimatedTimeSeconds { get; set; }
}

public class ForensicStatusResult
{
    public int RequestId { get; set; }
    public int EvidenceId { get; set; }
    public string AnalysisType { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public int EstimatedTimeSeconds { get; set; }
    public string? Result { get; set; }
    public string? CreatedAt { get; set; }
    public string? CompletedAt { get; set; }
}
