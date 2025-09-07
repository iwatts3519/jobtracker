import anthropic
import os
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self._initialize_claude()
    
    def _initialize_claude(self):
        """Initialize Anthropic Claude client with API key"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_api_key_here':
            logger.warning("Anthropic API key not configured. AI features will be disabled.")
            return
        
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info("Anthropic Claude client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def customize_cv(self, cv_text: str, job_description: str, job_title: str = "", company: str = "") -> Optional[str]:
        """
        Customize a CV based on job description using AI
        
        Args:
            cv_text: Original CV content
            job_description: Job description to tailor CV for
            job_title: Optional job title
            company: Optional company name
            
        Returns:
            Customized CV text or None if service unavailable
        """
        if not self.is_available():
            return None
            
        try:
            system_prompt = """You are an expert CV/resume customization specialist. Your task is to optimize a CV for a specific job application while maintaining truthfulness and professionalism.

Guidelines:
1. Tailor the CV to highlight relevant experience and skills mentioned in the job description
2. Reorder sections and bullet points to emphasize the most relevant qualifications first
3. Use keywords from the job description naturally throughout the CV
4. Optimize the professional summary/objective to align with the role
5. Maintain all factual information - never invent experience or skills
6. Keep the same format and structure as much as possible
7. Ensure the CV remains professional and ATS-friendly
8. Do not exceed the original CV length significantly

Return only the customized CV text."""

            job_context = f"Job Title: {job_title}\nCompany: {company}\n" if job_title or company else ""
            
            user_prompt = f"""{job_context}Job Description:
{job_description}

Original CV:
{cv_text}

Please customize this CV for the job described above."""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            customized_cv = response.content[0].text.strip()
            logger.info(f"Successfully customized CV for {job_title} at {company}")
            return customized_cv
            
        except Exception as e:
            logger.error(f"Failed to customize CV: {e}")
            return None
    
    def generate_cover_letter(self, cv_text: str, job_description: str, job_title: str = "", 
                            company: str = "", user_name: str = "") -> Optional[str]:
        """
        Generate a cover letter based on CV and job description
        
        Args:
            cv_text: User's CV content
            job_description: Job description
            job_title: Job title
            company: Company name
            user_name: User's name for personalization
            
        Returns:
            Generated cover letter or None if service unavailable
        """
        if not self.is_available():
            return None
            
        try:
            system_prompt = """You are an expert cover letter writer. Create compelling, personalized cover letters that highlight the candidate's most relevant qualifications for the specific role.

Guidelines:
1. Write in a professional yet engaging tone
2. Create a strong opening that grabs attention
3. Highlight 2-3 key qualifications that directly match the job requirements
4. Show genuine interest in the company and role
5. Include a clear call to action
6. Keep it concise (3-4 paragraphs max)
7. Use specific examples from the CV when possible
8. Avoid generic phrases and clichés
9. Format as a proper business letter

Return only the cover letter text."""

            user_prompt = f"""Please write a cover letter for the following position:

Job Title: {job_title}
Company: {company}
Candidate Name: {user_name or "[Your Name]"}

Job Description:
{job_description}

Candidate's CV:
{cv_text}

Create a compelling cover letter that demonstrates why this candidate is perfect for this role."""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.4,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            cover_letter = response.content[0].text.strip()
            logger.info(f"Successfully generated cover letter for {job_title} at {company}")
            return cover_letter
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return None
    
    def research_company(self, company_name: str, job_title: str = "") -> Optional[Dict[str, Any]]:
        """
        Generate company research insights using AI
        
        Args:
            company_name: Name of the company
            job_title: Optional job title for context
            
        Returns:
            Dictionary with research insights or None
        """
        if not self.is_available():
            return None
            
        try:
            system_prompt = """You are a professional researcher specializing in company analysis for job seekers. Provide structured insights about companies to help candidates prepare for applications and interviews.

Guidelines:
1. Provide factual, well-researched information
2. Include company culture insights
3. Mention recent news, developments, or achievements
4. Identify key talking points for interviews
5. Suggest questions the candidate might ask
6. Be honest about limitations of available information
7. Structure the response clearly

Format your response as a JSON object with these keys:
- "overview": Brief company description
- "culture": Company culture insights
- "recent_news": Recent developments or news
- "interview_tips": Preparation suggestions
- "questions_to_ask": Suggested questions for interviews
- "key_talking_points": Important points to mention in applications/interviews"""

            context = f" for a {job_title} position" if job_title else ""
            user_prompt = f"Please research {company_name}{context} and provide insights that would help a job candidate."

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=3000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            research_text = response.content[0].text.strip()
            logger.info(f"Successfully researched company: {company_name}")
            
            # Try to parse as JSON, fall back to text if needed
            try:
                import json
                research_data = json.loads(research_text)
                return research_data
            except json.JSONDecodeError:
                return {"overview": research_text}
            
        except Exception as e:
            logger.error(f"Failed to research company {company_name}: {e}")
            return None

# Global AI service instance
ai_service = AIService()