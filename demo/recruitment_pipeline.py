"""
Nexova Solutions — Demo: Full Recruitment Pipeline

This script demonstrates the core AI-powered recruitment flow:

1. A job position is created (client requests a hire)
2. Candidates are registered into the system
3. Each candidate is scored against the job (LLM + embeddings + SHAP)
4. Top candidates are matched and ranked
5. The Communication Agent sends personalized emails to candidates
6. The Orchestrator routes events between service and agent

Run: python -m demo.recruitment_pipeline
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.selection.service import SelectionService, Candidate, JobPosition
from agents.selection.agent import SelectionCommunicationAgent
from agents.orchestrator import AgentOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("demo.recruitment")
# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)


def print_separator(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def main():
    logger.info("🚀 Nexova Solutions — Recruitment Pipeline Demo")
    logger.info("Simulating the AI-powered selection process (core business)\n")

    # ─── Setup ────────────────────────────────────────────────────────────────
    service = SelectionService()
    agent = SelectionCommunicationAgent()
    orchestrator = AgentOrchestrator()

    # ─── Step 1: A client requests a new hire ─────────────────────────────────
    print_separator("STEP 1: CLIENT CREATES A JOB POSITION")

    job = JobPosition(
        id="job-ds-001",
        title="Senior Data Scientist",
        department="Technology",
        description=(
            "Lead a team of data scientists to build and deploy ML models "
            "that optimize recruitment processes for our clients."
        ),
        required_skills=[
            "Python", "Machine Learning", "SQL", "Deep Learning",
            "Natural Language Processing", "Cloud Computing",
        ],
        preferred_skills=["Team Leadership", "MLOps", "Docker"],
        experience_min=5,
        location="Valencia, Spain (hybrid)",
        client_id="client-tech-01",
    )
    service.create_job(job)
    logger.info(f"✓ Job created: {job.title} (ID: {job.id})")
    logger.info(f"  Required skills: {', '.join(job.required_skills)}")
    logger.info(f"  Min experience: {job.experience_min} years")

    # ─── Step 2: Candidates apply (are registered) ────────────────────────────
    print_separator("STEP 2: CANDIDATES APPLY")

    candidates_data = [
        Candidate(
            id="cand-001",
            first_name="Ana",
            last_name="Martínez",
            email="ana.martinez@nexova-demo.com",
            skills=["Python", "Machine Learning", "SQL", "Deep Learning", "NLP", "Cloud Computing"],
            languages=[{"language": "Spanish", "level": "native"}, {"language": "English", "level": "C1"}],
            experience_years=7.0,
            current_role="Senior Data Scientist",
        ),
        Candidate(
            id="cand-002",
            first_name="James",
            last_name="Wilson",
            email="james.wilson@nexova-demo.com",
            skills=["Python", "SQL", "Tableau", "Statistics", "Excel"],
            languages=[{"language": "English", "level": "native"}, {"language": "Spanish", "level": "B1"}],
            experience_years=4.0,
            current_role="Data Analyst",
        ),
        Candidate(
            id="cand-003",
            first_name="María",
            last_name="García",
            email="maria.garcia@nexova-demo.com",
            skills=["Python", "Machine Learning", "SQL", "Docker", "MLOps", "Team Leadership"],
            languages=[{"language": "Spanish", "level": "native"}, {"language": "English", "level": "C2"}],
            experience_years=9.0,
            current_role="ML Team Lead",
        ),
        Candidate(
            id="cand-004",
            first_name="Carlos",
            last_name="López",
            email="carlos.lopez@nexova-demo.com",
            skills=["Java", "C++", "Assembly", "Embedded Systems"],
            languages=[{"language": "Spanish", "level": "native"}, {"language": "English", "level": "B2"}],
            experience_years=12.0,
            current_role="Embedded Systems Engineer",
        ),
        Candidate(
            id="cand-005",
            first_name="Sarah",
            last_name="Thompson",
            email="sarah.thompson@nexova-demo.com",
            skills=["Python", "Machine Learning", "SQL", "Deep Learning", "NLP", "Cloud Computing", "Docker", "MLOps"],
            languages=[{"language": "English", "level": "native"}, {"language": "French", "level": "B2"}],
            experience_years=6.0,
            current_role="Data Scientist",
        ),
    ]

    for c in candidates_data:
        service.register_candidate(c)
        # Simulate event: candidate.registered → agent sends acknowledgment
        orchestrator.route_event("candidate.registered", {
            "candidate_id": c.id,
            "candidate_name": f"{c.first_name} {c.last_name}",
            "candidate_email": c.email,
            "job_title": job.title,
            "language": agent.determine_language(c.languages),
        })
        logger.info(f"✓ Candidate registered: {c.first_name} {c.last_name} ({c.email})")
        logger.info(f"  Skills: {', '.join(c.skills[:4])}{'...' if len(c.skills) > 4 else ''}")

    # ─── Step 3: AI-Powered Candidate Scoring ─────────────────────────────────
    print_separator("STEP 3: AI CANDIDATE SCORING & RANKING")
    logger.info("Scoring each candidate against the job position...\n")

    print(f"{'Candidate':<25} {'Score':<8} {'Skill Match':<12} {'Exp Match':<12}  {'Top Factor':<20}")
    print("-" * 80)

    for c in candidates_data:
        result = service.score_candidate_for_job(c.id, job.id)
        top_factor = max(result.feature_importance, key=result.feature_importance.get)
        print(
            f"{c.first_name + ' ' + c.last_name:<25} "
            f"{result.score:<8.1f} "
            f"{result.feature_importance['skill_match']:<12.1f} "
            f"{result.feature_importance['experience_match']:<12.1f}  "
            f"{top_factor:<20}"
        )

    # ─── Step 4: Get Ranked Matches ──────────────────────────────────────────
    print_separator("STEP 4: TOP CANDIDATES (RANKED MATCHING)")
    
    top_matches = service.match_candidates_to_job(job.id, top_k=3)
    
    logger.info(f"Top {len(top_matches)} candidates for '{job.title}':\n")
    for i, match in enumerate(top_matches, 1):
        c = service.get_candidate(match.candidate_id)
        print(f"  #{i} {c.first_name} {c.last_name:<20} Score: {match.score:.1f}/100")
        print(f"     {match.explanation}")
        print()

    # ─── Step 5: Interview Scheduling ────────────────────────────────────────
    print_separator("STEP 5: INTERVIEW SCHEDULING & COMMUNICATION")

    # Schedule interviews for top 2 candidates
    top_2 = [m.candidate_id for m in top_matches[:2]]
    for cid in top_2:
        c = service.get_candidate(cid)
        result = service.schedule_interview(
            candidate_id=cid,
            job_id=job.id,
            date_time="2026-12-18T10:00:00",
            interview_type="video",
        )
        language = agent.determine_language(c.languages)
        logger.info(f"✓ Interview scheduled for {c.first_name} {c.last_name}")

        # Route interview event → agent sends confirmation
        orchestrator.route_event("interview.scheduled", {
            "candidate_id": cid,
            "candidate_name": f"{c.first_name} {c.last_name}",
            "candidate_email": c.email,
            "job_title": job.title,
            "language": language,
            "interview_details": {
                "date": "December 18, 2026",
                "time": "10:00 AM CET",
                "type": "video",
                "location": "Google Meet (link will be sent separately)",
            },
        })
        logger.info(f"  ✉ Interview confirmation sent to {c.email}")
    
    # ─── Step 6: Candidate Rejection ─────────────────────────────────────────
    print_separator("STEP 6: REJECTION HANDLING")
    
    # Reject the lowest-scoring candidate
    lowest = [m.candidate_id for m in top_matches][-1]
    c = service.get_candidate(lowest)
    service.update_candidate_status(lowest, "rejected")
    language = agent.determine_language(c.languages)
    
    orchestrator.route_event("candidate.status_changed", {
        "candidate_id": lowest,
        "candidate_name": f"{c.first_name} {c.last_name}",
        "candidate_email": c.email,
        "job_title": job.title,
        "new_status": "rejected",
        "language": language,
    })
    logger.info(f"✓ Rejection sent to {c.first_name} {c.last_name} ({c.email})")

    # ─── Summary ─────────────────────────────────────────────────────────────
    print_separator("📊 SUMMARY — DEMO COMPLETE")

    # Check communication records
    for c in candidates_data:
        history = agent.get_communication_history(c.id)
        if history:
            print(f"  📧 {c.first_name} {c.last_name}: {len(history)} email(s) sent")
            for h in history:
                print(f"      - [{h['type']}] {h['subject'][:60]}...")
        else:
            print(f"  📧 {c.first_name} {c.last_name}: No communications")

    print(f"\n{'=' * 70}")
    print(f"  ✅ AI Recruitment Pipeline Demo Complete")
    print(f"  • 1 job position created")
    print(f"  • {len(candidates_data)} candidates registered & scored")
    print(f"  • Top candidates matched via AI ranking")
    print(f"  • Interviews scheduled & confirmed via agent")
    print(f"  • Rejection handled with personalized feedback")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()