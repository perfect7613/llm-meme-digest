from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from the .env file

import os
from datetime import datetime
from typing import List
import arxiv
from groq import Groq
from pydantic import BaseModel
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Configuration
SEARCH_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]
SEARCH_TERMS = [
    "large language models",
    "LLM fine-tuning",
    "model efficiency",
    "parameter efficient tuning",
    "distillation"
]

# Updated required environment variables, including GROQ_API_KEY
required_environment_variables = [
    "BREVO_API_KEY",
    "BREVO_SENDER_EMAIL",
    "BREVO_SENDER_NAME",
    "BREVO_RECIPIENT_EMAIL",
    "BREVO_RECIPIENT_NAME",
    "GROQ_API_KEY"
]

class ArxivPaper(BaseModel):
    title: str
    abstract: str
    authors: List[str]
    published: datetime
    pdf_url: str
    arxiv_id: str

class MemeSummary(BaseModel):
    title: str
    meme_explanation: str
    reference_style: str
    paper_link: str

def validate_environment():
    """Check required environment variables"""
    missing = [var for var in required_environment_variables if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

def search_arxiv() -> List[ArxivPaper]:
    """Search Arxiv for recent papers matching our criteria"""
    client = arxiv.Client()
    
    query = " OR ".join([f'({term})' for term in SEARCH_TERMS])
    search = arxiv.Search(
        query=query,
        max_results=25,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    results = []
    for result in client.results(search):
        paper = ArxivPaper(
            title=result.title,
            abstract=result.summary,
            authors=[a.name for a in result.authors],
            published=result.published,
            pdf_url=result.pdf_url,
            arxiv_id=result.entry_id.split('/')[-1]
        )
        results.append(paper)
    
    return results

def generate_meme_summary(paper: ArxivPaper) -> MemeSummary:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""Transform this research paper into a meme explanation using:
- Internet meme formats (e.g., Drake Hotline Bling, Distracted Boyfriend)
- TV show references (e.g., Family Guy, Rick and Morty)
- Dark humor/nerdy jokes

Paper Title: {paper.title}
Abstract: {paper.abstract}...

Choose the best meme format and provide:
1. Overview of the paper in meme format
2. A call to action for the reader to explore the paper further
3. Summary of the paper in meme format


Keep it under 10000 characters and dont write which format you choose or anything just write the following points which is given only."""
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=6500
    )
    
    meme_text = response.choices[0].message.content
    return MemeSummary(
        title=paper.title,
        meme_explanation=meme_text,
        reference_style="mixed",
        paper_link=paper.pdf_url
    )

def create_email_content(summaries: List[MemeSummary]) -> str:
    """Format meme summaries into HTML email"""
    email_body = """
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h1 style="color: #2B547E;">🤖 Daily LLM Research Meme Digest 🤖</h1>
        <hr>
    """
    
    for i, summary in enumerate(summaries, 1):
        email_body += f"""
        <div style="margin: 20px 0; padding: 15px; border-left: 4px solid #2B547E;">
          <h3 style="color: #2B547E;">📄 Paper #{i}: {summary.title}</h3>
          <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
            <p style="font-style: italic;">🎭 {summary.meme_explanation}</p>
          </div>
          <p><a href="{summary.paper_link}">📚 Read Paper</a></p>
        </div>
        """
    
    email_body += """
        <hr>
        <p>🔍 Generated with AI humor (may contain dad jokes)</p>
      </body>
    </html>
    """
    return email_body

def send_email(content: str):
    """Send email using Brevo via sib_api_v3_sdk"""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    sender = {
        "name": os.getenv("BREVO_SENDER_NAME"),
        "email": os.getenv("BREVO_SENDER_EMAIL")
    }
    recipient = {
        "name": os.getenv("BREVO_RECIPIENT_NAME"),
        "email": os.getenv("BREVO_RECIPIENT_EMAIL")
    }
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[recipient],
        sender=sender,
        subject="🦄 Your Daily LLM Research Meme Summary",
        html_content=content
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully via Brevo!")
    except ApiException as e:
        print("Exception when sending email via Brevo: %s\n" % e)

def main():
    validate_environment()
    
    # Get papers from last 3 days
    papers = search_arxiv()
    print(f"Found {len(papers)} relevant papers")
    
    # Generate meme summaries (limit to top 5 for brevo)
    summaries = [generate_meme_summary(paper) for paper in papers[:5]]
    
    # Create and send email
    email_content = create_email_content(summaries)
    send_email(email_content)

if __name__ == "__main__":
    main()
