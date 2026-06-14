import requests
from bs4 import BeautifulSoup
import hashlib
import boto3
from datetime import datetime, timezone

dynamodb=boto3.resource("dynamodb",region_name="ap-south-1")
table = dynamodb.Table("placement-opportunities")

lambda_client = boto3.client("lambda", region_name="ap-south-1")

urls=["https://internshala.com/internships/machine-learning-internship/",
"https://internshala.com/internships/python-internship/",
"https://internshala.com/internships/data-science-internship/",
"https://internshala.com/internships/web-development-internship/",
"https://internshala.com/internships/artificial-intelligence-internship/",
"https://internshala.com/internships/java-internship/",
"https://internshala.com/internships/android-app-development-internship/",
"https://internshala.com/internships/computer-science-internship/",
"https://internshala.com/internships/backend-development-internship/",
"https://internshala.com/internships/full-stack-development-internship/"]

def lambda_handler(event,context):
    jobs=[]

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        internships = soup.find_all("div", class_="internship_meta duration_meta")

        for internship in internships:
            title = internship.find("a", class_="job-title-href")
            company = internship.find("p", class_="company-name")
            skills = internship.find_all("div", class_="job_skill")

            if(title is not None):
                job_id= hashlib.md5(f"{title}{company}".encode()).hexdigest()
                job={
                    "job_id": job_id,
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "skills": [skill.get_text(strip=True) for skill in skills],
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "url": "https://internshala.com" + title.get("href", "")
                }
                jobs.append(job)
                table.put_item(Item=job)

    print(f"The total num of jobs {len(jobs)}");
    
    lambda_client.invoke(
    FunctionName="placement-matcher",
    InvocationType="Event"
    )
    
    return{
        "statusCode":200,
        "body": f"Scraped and saved {len(jobs)} jobs"
    }

    