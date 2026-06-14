# Smart-Placement-Tracker
Serverless job opportunity aggregator on AWS that scrapes Internshala daily, matches listings to user skill profiles, and delivers ranked results.

#  Smart Placement Opportunity Tracker

A serverless job opportunity aggregator built on AWS that scrapes Internshala daily and matches listings to user skill profiles using a bidirectional scoring algorithm.

 **Live Demo:** [placement-tracker-frontend.s3-website.ap-south-1.amazonaws.com](http://placement-tracker-frontend.s3-website.ap-south-1.amazonaws.com)

---

## Features

- Scrapes 10+ Internshala internship categories daily across ML, Python, Data Science, Web Dev, AI, Java, Android, CS, Backend, and Full Stack
- Matches job listings to user skill profiles using a bidirectional scoring algorithm
- Ranks results into High Match (≥70%) and Medium Match (≥40%) categories
- Filters results to show only listings scraped in the last 24 hours — always fresh
- Clean frontend with skill tag input and clickable apply links

---

## Architecture

```
EventBridge (daily cron)
        ↓
Lambda — placement-scraper
  → Scrapes Internshala via requests + BeautifulSoup
  → Stores jobs in DynamoDB (placement-opportunities)
        ↓
Lambda — placement-api (via API Gateway)
  → Called by frontend with user skills
  → Scores each job against user skills
  → Returns ranked matches as JSON
        ↓
Frontend (S3 Static Hosting)
  → Skill input UI
  → Displays ranked job cards with clickable apply links
```

---

## Tech Stack

| Layer | Service |
|-------|---------|
| Scraper | AWS Lambda (Python), Requests, BeautifulSoup4 |
| Storage | AWS DynamoDB |
| Matching | AWS Lambda (Python) |
| Scheduler | AWS EventBridge |
| API | AWS API Gateway + Lambda |
| Frontend | HTML/CSS/JS hosted on S3 |

---

## How the Skill Matcher Works

Uses a bidirectional scoring approach — averages job coverage and user coverage:

```python
def match_score(user_skills, job_skills):
    matched = set(user_skills) & set(job_skills)
    job_coverage = len(matched) / len(job_skills) * 100
    user_coverage = len(matched) / len(user_skills) * 100
    return round((job_coverage + user_coverage) / 2)
```

This ensures fair scoring even when users enter only a few skills.

---

## Environment Variables

Set these in AWS Lambda console under Configuration → Environment Variables:

| Lambda | Key | Value |
|--------|-----|-------|
| placement-matcher | SNS_TOPIC_ARN | your SNS topic ARN |

---

## Future Enhancements

- Multi-user support — each subscriber receives a daily email digest matched to their own skills via AWS SNS
- Email subscription card on frontend — users can subscribe to daily alerts directly from the UI
- Additional sources — AICTE internship portal, LinkedIn via API
- Resume upload with skill auto-extraction using AWS Textract

---

## Author

**Bhoomika P Sarvajna**
GitHub: [@BHOOMIKASARVAJNA](https://github.com/BHOOMIKASARVAJNA)
