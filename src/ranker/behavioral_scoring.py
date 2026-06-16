"""Behavioral scoring — process Redrob signals into hiring-relevant scores."""

from datetime import datetime, timezone


def compute_behavioral_score(signals: dict) -> dict:
    """Compute behavioral/availability scores from redrob_signals.

    Returns dict of individual signal scores and a composite.
    """
    if not signals:
        return {
            "open_to_work": 0.0,
            "response_rate": 0.0,
            "response_time": 0.0,
            "notice_period": 0.0,
            "recency": 0.0,
            "github_activity": 0.0,
            "verification": 0.0,
            "platform_engagement": 0.0,
            "composite": 0.0,
        }

    otw = 1.0 if signals.get("open_to_work_flag", False) else 0.5

    rr = signals.get("recruiter_response_rate", 0)
    if rr >= 0.7:
        response_rate = 1.0
    elif rr >= 0.5:
        response_rate = 0.8
    elif rr >= 0.3:
        response_rate = 0.6
    elif rr > 0:
        response_rate = 0.3
    else:
        response_rate = 0.1

    avg_hours = signals.get("avg_response_time_hours", 200)
    if avg_hours <= 48:
        response_time = 1.0
    elif avg_hours <= 96:
        response_time = 0.85
    elif avg_hours <= 168:
        response_time = 0.7
    else:
        response_time = 0.4

    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        notice_period = 1.0
    elif notice <= 45:
        notice_period = 0.9
    elif notice <= 60:
        notice_period = 0.75
    elif notice <= 90:
        notice_period = 0.55
    else:
        notice_period = 0.3

    last_active_str = signals.get("last_active_date", "")
    recency = 0.3
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_since = (datetime.now(timezone.utc) - last_active).days
            if days_since <= 7:
                recency = 1.0
            elif days_since <= 30:
                recency = 0.85
            elif days_since <= 90:
                recency = 0.65
            elif days_since <= 180:
                recency = 0.45
            else:
                recency = 0.25
        except (ValueError, TypeError):
            recency = 0.3

    gh_score = signals.get("github_activity_score", -1)
    if gh_score >= 50:
        github_activity = 1.0
    elif gh_score >= 20:
        github_activity = 0.8
    elif gh_score >= 5:
        github_activity = 0.6
    elif gh_score >= 0:
        github_activity = 0.4
    else:
        github_activity = 0.2

    verified_email = 1.0 if signals.get("verified_email", False) else 0.3
    verified_phone = 1.0 if signals.get("verified_phone", False) else 0.3
    linkedin = 0.8 if signals.get("linkedin_connected", False) else 0.5
    verification = (verified_email + verified_phone + linkedin) / 3.0

    profile_views = signals.get("profile_views_received_30d", 0)
    saved_by = signals.get("saved_by_recruiters_30d", 0)
    search_appearance = signals.get("search_appearance_30d", 0)
    completeness = signals.get("profile_completeness_score", 0)

    views_score = min(profile_views / 30.0, 1.0)
    saved_score = min(saved_by / 10.0, 1.0)
    appearance_score = min(search_appearance / 200.0, 1.0)
    completeness_score = completeness / 100.0
    interview_rate = signals.get("interview_completion_rate", 0)

    platform_engagement = (
        0.25 * views_score
        + 0.25 * saved_score
        + 0.15 * appearance_score
        + 0.15 * completeness_score
        + 0.20 * interview_rate
    )

    composite = (
        0.20 * otw
        + 0.15 * response_rate
        + 0.05 * response_time
        + 0.15 * notice_period
        + 0.10 * recency
        + 0.10 * github_activity
        + 0.10 * verification
        + 0.15 * platform_engagement
    )

    return {
        "open_to_work": otw,
        "response_rate": response_rate,
        "response_time": response_time,
        "notice_period": notice_period,
        "recency": recency,
        "github_activity": github_activity,
        "verification": verification,
        "platform_engagement": platform_engagement,
        "composite": composite,
    }
