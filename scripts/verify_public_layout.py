#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

from workflow_security import repository_workflow_security_errors

REQUIRED = [
    "README.md", "README.ja.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "LICENSING.md", "REUSE.toml",
    "LICENSES/Apache-2.0.txt", "LICENSES/CC-BY-4.0.txt", "LICENSES/CC0-1.0.txt",
    "docs/VILLAGE_CONSTITUTION.md", "docs/VILLAGE_ARCHITECTURE.md", "docs/VILLAGE_ARCHITECTURE_V1_1.md", "docs/VILLAGE_ARCHITECTURE_V1_2.md", "docs/VILLAGE_ARCHITECTURE_V1_2_1.md", "docs/CONTINUATION_GATE.md", "docs/GITHUB_SETTINGS_REQUIRED.md",
    "docs/RESEARCH_PORTFOLIO.md", "docs/RESEARCH_BOARD.md", "docs/DEPENDENCY_GRAPH.md", "docs/CAMPAIGN_HISTORY.md", "docs/RESEARCH_EVALUATIONS.md",
    "docs/RESULTS.md", "docs/FAILED_ROUTES.md", "docs/EXPORT_GAPS.md", "docs/CONTRIBUTION_TARGETS.md",
    "docs/EVIDENCE_POLICY.md", "docs/PUBLIC_EXPORT_VALIDATION.md", "docs/CLAIM_LEVELS.md",
    "docs/REPRODUCIBILITY.md", "docs/PUBLIC_EXPORT_POLICY.md", "docs/PRIVACY_AND_SECURITY.md",
    "coordination/portfolio/PORTFOLIO.yml", "coordination/policy/MAINTAINERS.yml",
    "coordination/policy/PROTECTED_PATHS.yml", "coordination/policy/ACTOR_POLICY.yml", "coordination/policy/JOIN_PROTOCOL.yml",
    "coordination/policy/AUTONOMOUS_LOCK_PRINCIPALS.yml",
    "coordination/evaluations/README.md",
    "coordination/campaigns/CAM-OPEN-MATH-DISCOVERY/CAMPAIGN.yml",
    "coordination/campaigns/CAM-AIMATH-ND/CAMPAIGN.yml",
    "coordination/tasks/TASK-OPEN-MATH-DISCOVERY-001/TASK.yml",
    "coordination/tasks/TASK-OPEN-MATH-DISCOVERY-002/TASK.yml",
    "coordination/tasks/TASK-AIMATH-ND-001/TASK.yml",
    "coordination/tasks/TASK-AIMATH-ND-002/TASK.yml",
    "schemas/portfolio.schema.json", "schemas/campaign.schema.json", "schemas/task.schema.json",
    "schemas/lock.schema.json", "schemas/pending-claim.schema.json", "schemas/abandoned-terminal.schema.json", "schemas/claim.schema.json", "schemas/review.schema.json",
    "schemas/failed-route.schema.json", "schemas/continuation.schema.json", "schemas/decision.schema.json",
    "schemas/proposal.schema.json", "schemas/outcome.schema.json", "schemas/evaluation.schema.json",
    "scripts/build_public_manifest.py", "scripts/reproduce_public_claims.py",
    "scripts/village_core.py", "scripts/village.py", "scripts/village_rank.py", "scripts/village_v1_2.py",
    "scripts/lock_auto_activate.py", "scripts/lock_auto_activate_phase_a.py", "scripts/workflow_security.py",
    "scripts/test_village_acceptance.py", "scripts/test_village_v1_1.py", "scripts/test_village_v1_2.py", "scripts/test_village_v1_2_1.py", "scripts/test_village_v1_2_1_phase_b.py",
    "scripts/check_dco.py", "scripts/check_village_pr.py", "scripts/verify_public_layout.py",
    ".github/workflows/verify.yml", ".github/workflows/lock-auto-activate.yml",
    "research/README.md", "reviews/README.md",
    "research/fixed-433/README.md",
    "research/433-springborn-obstruction/README.md",
    "reviews/433-springborn-obstruction/INDEPENDENT_REVIEW.md",
    "research/433-existing-theory-identification/README.md",
    "reviews/433-existing-theory-identification/INDEPENDENT_REVIEW.md",
    "research/gyoda-89/README.md", "reviews/gyoda-89/INDEPENDENT_REVIEW.md",
    "research/local-tp2/STATEMENT.md", "research/b3rcc-apc/README.md",
    "research/b3rcc-apc/APC_ALL_RANK_THEOREM.md", "reviews/b3rcc-apc/APC_ALL_RANK_INDEPENDENT_REVIEW.md",
    "research/equiangular-r18-eta17/README.md", "reviews/equiangular-r18-eta17/INDEPENDENT_REVIEW.md",
    "research/dittert-n5-z2/README.md", "reviews/dittert-n5-z2/INDEPENDENT_REVIEW.md",
    "research/lonely-runner-r2/README.md", "reviews/lonely-runner-r2/INDEPENDENT_REVIEW.md",
    "research/afes-bounded/README.md", "reviews/afes-bounded/INDEPENDENT_REVIEW.md",
    "research/thue-morse-rediscovery/README.md", "reviews/thue-morse-rediscovery/INDEPENDENT_REVIEW.md",
]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    missing = [p for p in REQUIRED if not (root / p).is_file()]
    campaign_count = len(list((root / "coordination/campaigns").glob("*/CAMPAIGN.yml")))
    task_count = len(list((root / "coordination/tasks").glob("*/TASK.yml")))
    claim_meta_count = len(list((root / "research").glob("**/CLAIM.yml")))
    workflow_errors = repository_workflow_security_errors(root)
    if missing or campaign_count < 3 or task_count < 5 or claim_meta_count < 1 or workflow_errors:
        print("FAIL: public layout")
        for p in missing:
            print(" - missing:", p)
        if campaign_count < 3:
            print(" - fewer than 3 Village campaigns")
        if task_count < 5:
            print(" - fewer than 5 Village tasks")
        if claim_meta_count < 1:
            print(" - no public CLAIM.yml metadata")
        for error in workflow_errors:
            print(" - workflow security:", error)
        return 1
    print(
        f"PASS: public layout ({len(REQUIRED)} required files, "
        f"{campaign_count} campaigns, {task_count} tasks, {claim_meta_count} claim metadata records)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
