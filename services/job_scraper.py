import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import logging
from typing import Optional, Dict, Any
import time
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_job_info(self, url: str) -> Dict[str, Any]:
        """
        Extract job information from a job posting URL
        
        Args:
            url: Job posting URL
            
        Returns:
            Dictionary with extracted job information
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            if 'linkedin.com' in domain:
                return self._scrape_linkedin(url)
            elif 'indeed.com' in domain:
                return self._scrape_indeed(url)
            else:
                # Generic scraping for other sites
                return self._scrape_generic(url)
                
        except Exception as e:
            logger.error(f"Failed to extract job info from {url}: {e}")
            return {
                'title': '',
                'company': '',
                'location': '',
                'description': '',
                'error': str(e)
            }
    
    def _scrape_linkedin(self, url: str) -> Dict[str, Any]:
        """Scrape LinkedIn job posting"""
        try:
            # LinkedIn has anti-scraping measures, so we'll extract what we can from the URL
            job_id = self._extract_linkedin_job_id(url)
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {
                    'title': '',
                    'company': '',
                    'location': '',
                    'description': 'Unable to access LinkedIn job posting. LinkedIn has anti-scraping measures.',
                    'job_id': job_id
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract basic information
            title = self._extract_text_by_selectors(soup, [
                'h1.top-card-layout__title',
                '.job-title',
                'h1'
            ])
            
            company = self._extract_text_by_selectors(soup, [
                '.topcard__org-name-link',
                '.job-details-jobs-unified-top-card__company-name',
                '.company-name'
            ])
            
            location = self._extract_text_by_selectors(soup, [
                '.topcard__flavor',
                '.job-details-jobs-unified-top-card__bullet',
                '.location'
            ])
            
            # Description is often loaded dynamically, so we may not get it
            description = self._extract_text_by_selectors(soup, [
                '.description__text',
                '.job-description',
                '.jobs-description__content'
            ])
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description or 'Description not available - please copy manually from LinkedIn',
                'job_id': job_id,
                'source': 'linkedin'
            }
            
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {e}")
            return {
                'title': '',
                'company': '',
                'location': '',
                'description': f'LinkedIn scraping failed: {str(e)}. Please enter details manually.',
                'source': 'linkedin'
            }
    
    def _scrape_indeed(self, url: str) -> Dict[str, Any]:
        """Scrape Indeed job posting"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self._extract_text_by_selectors(soup, [
                '[data-testid="jobsearch-JobInfoHeader-title"]',
                '.jobsearch-JobInfoHeader-title',
                'h1.icl-u-xs-mb--xs'
            ])
            
            company = self._extract_text_by_selectors(soup, [
                '[data-testid="inlineHeader-companyName"]',
                '.icl-u-lg-mr--sm',
                '.companyName'
            ])
            
            location = self._extract_text_by_selectors(soup, [
                '[data-testid="job-location"]',
                '.icl-u-colorForeground--secondary',
                '.locationsContainer'
            ])
            
            # Indeed job descriptions
            description = self._extract_text_by_selectors(soup, [
                '#jobDescriptionText',
                '.jobsearch-jobDescriptionText',
                '.jobDescription'
            ])
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'source': 'indeed'
            }
            
        except Exception as e:
            logger.error(f"Indeed scraping failed: {e}")
            return {
                'title': '',
                'company': '',
                'location': '',
                'description': f'Indeed scraping failed: {str(e)}',
                'source': 'indeed'
            }
    
    def _scrape_generic(self, url: str) -> Dict[str, Any]:
        """Generic scraping for other job sites"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic selectors that might work on various sites
            title = self._extract_text_by_selectors(soup, [
                'h1',
                '.job-title',
                '.position-title',
                '[class*="title"]'
            ])
            
            company = self._extract_text_by_selectors(soup, [
                '.company',
                '.employer',
                '[class*="company"]',
                '[class*="employer"]'
            ])
            
            location = self._extract_text_by_selectors(soup, [
                '.location',
                '.job-location',
                '[class*="location"]'
            ])
            
            # Look for large text blocks that might be descriptions
            description_elem = soup.find(['div', 'section'], 
                                       class_=re.compile(r'description|content|details'))
            description = description_elem.get_text(strip=True) if description_elem else ''
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'source': 'generic'
            }
            
        except Exception as e:
            logger.error(f"Generic scraping failed for {url}: {e}")
            return {
                'title': '',
                'company': '',
                'location': '',
                'description': f'Scraping failed: {str(e)}',
                'source': 'generic'
            }
    
    def _extract_linkedin_job_id(self, url: str) -> str:
        """Extract LinkedIn job ID from URL"""
        try:
            if 'currentJobId=' in url:
                parsed = parse_qs(urlparse(url).query)
                return parsed.get('currentJobId', [''])[0]
            elif '/view/' in url:
                return url.split('/view/')[-1].split('?')[0]
            else:
                return ''
        except:
            return ''
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: list) -> str:
        """Try multiple CSS selectors to extract text"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except:
                continue
        return ''
    
    def scrape_with_jobspy(self, site: str = 'indeed', search_term: str = '', 
                         location: str = '', results_wanted: int = 10) -> Optional[list]:
        """
        Use JobSpy library for scraping (Indeed works best)
        
        Args:
            site: Job site to scrape ('indeed', 'linkedin', 'zip_recruiter', etc.)
            search_term: Job search term
            location: Location filter
            results_wanted: Number of results to fetch
            
        Returns:
            List of job dictionaries or None if failed
        """
        try:
            from jobspy import scrape_jobs
            
            jobs = scrape_jobs(
                site_name=site,
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=72,  # Jobs posted within last 72 hours
                country_indeed='USA'  # or 'UK' for UK Indeed
            )
            
            if jobs is not None and not jobs.empty:
                # Convert DataFrame to list of dictionaries
                job_list = []
                for _, row in jobs.iterrows():
                    job_dict = {
                        'title': row.get('title', ''),
                        'company': row.get('company', ''),
                        'location': row.get('location', ''),
                        'description': row.get('description', ''),
                        'url': row.get('job_url', ''),
                        'date_posted': row.get('date_posted', ''),
                        'salary': row.get('min_amount', ''),
                        'source': site
                    }
                    job_list.append(job_dict)
                
                logger.info(f"Successfully scraped {len(job_list)} jobs from {site}")
                return job_list
            else:
                logger.warning(f"No jobs found on {site} for '{search_term}' in '{location}'")
                return []
                
        except ImportError:
            logger.error("JobSpy library not installed. Run: pip install jobspy")
            return None
        except Exception as e:
            logger.error(f"JobSpy scraping failed: {e}")
            return None

# Global scraper instance
job_scraper = JobScraper()