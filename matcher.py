import boto3
from datetime import datetime, timezone, timedelta
import os

dynamodb=boto3.resource("dynamodb",region_name="ap-south-1")
table=dynamodb.Table("placement-opportunities")

user_table = dynamodb.Table("user-profiles")

sns = boto3.client("sns", region_name="ap-south-1")
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def match_score(user_skills, job_skills):
    set1 = {s.lower().strip() for s in user_skills}
    set2 = {s.lower().strip() for s in job_skills}
    if len(set2) == 0 or len(set1) == 0:
        return 0
    matched = set1 & set2
    job_coverage = len(matched) / len(set2) * 100
    user_coverage = len(matched) / len(set1) * 100
    return round((job_coverage + user_coverage) / 2)

def lambda_handler(event,context):
    user_response = user_table.get_item(Key={"user_id": "bhoomika"})
    user = user_response["Item"]
    user_skills = user["skills"]

    high_matches=[]
    medium_matches=[]

    response=table.scan()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    all_jobs = response["Items"]
    jobs = []
    for job in all_jobs:
        if "scraped_at" not in job:
            continue
        scraped_time = datetime.fromisoformat(job["scraped_at"])
        if scraped_time >= cutoff:
            jobs.append(job)

    for job in jobs:
        job_skills=job["skills"]
        score=match_score(user_skills,job_skills)
        if score>=70:
            high_matches.append(job)
        elif score>=40:
            medium_matches.append(job)
        
    message = f"""
    Daily Placement Digest

    HIGH MATCHES ({len(high_matches)} found)
    """

    for job in high_matches:
        message+=f"{job['title']}  -  {job['company']}\n{job.get('url', '')}\n"

    message += f"\nMEDIUM MATCHES ({len(medium_matches)} found)\n"

    for job in medium_matches:
        message+=f"{job['title']} -  {job['company']}\n{job.get('url', '')}\n"

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="Daily Placement Updates"
    )

    return{
        "statusCode":200,
        "body": f"Obtained {len(high_matches)+len(medium_matches)} that matches profile\n"
    }

