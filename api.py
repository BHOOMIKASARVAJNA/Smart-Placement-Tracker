import boto3
import json
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("placement-opportunities")

def match_score(user_skills, job_skills):
    set1 = {s.lower().strip() for s in user_skills}
    set2 = {s.lower().strip() for s in job_skills}
    if len(set2) == 0 or len(set1) == 0:
        return 0
    matched = set1 & set2
    job_coverage = len(matched) / len(set2) * 100
    user_coverage = len(matched) / len(set1) * 100
    return round((job_coverage + user_coverage) / 2)

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    user_skills = body.get("skills", [])

    print(f"USER SKILLS RECEIVED: {user_skills}")

    high_matches = []
    medium_matches = []

    response = table.scan()
    all_jobs = response["Items"]

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    jobs = []
    for job in all_jobs:
        if "scraped_at" not in job:
            continue
        scraped_time = datetime.fromisoformat(job["scraped_at"])
        if scraped_time >= cutoff:
            jobs.append(job)

    for job in jobs[:3]:
        print(f"JOB: {job.get('title')} | SKILLS: {job.get('skills')}")

    for job in jobs:
        job_skills = job.get("skills", [])
        score = match_score(user_skills, job_skills)
        job["score"] = score
        if score >= 70:
            high_matches.append(job)
        elif score >= 40:
            medium_matches.append(job)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "high": high_matches,
            "medium": medium_matches
        })
    }