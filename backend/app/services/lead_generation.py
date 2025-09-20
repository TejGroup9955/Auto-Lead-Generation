import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import spacy
from fake_useragent import UserAgent
import time
import random
from app.config import settings

class LeadGenerationService:
    def __init__(self):
        self.ua = UserAgent()
        # Load lightweight models for CPU processing
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.nlp = spacy.load('en_core_web_sm')
        except:
            self.sentence_model = None
            self.nlp = None
    
    def search_duckduckgo(self, query: str, region: str = "India") -> List[Dict[str, Any]]:
        """Search DuckDuckGo for companies matching the query"""
        try:
            search_query = f"{query} companies {region}"
            url = f"https://html.duckduckgo.com/html/?q={search_query}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parse DuckDuckGo results
            for result in soup.find_all('div', class_='result')[:10]:  # Limit to 10 results
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('div', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True)
                    
                    # Extract company info
                    company_data = self._extract_company_info(title, snippet, url)
                    if company_data:
                        results.append(company_data)
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def search_opencorporates(self, query: str, region: str = "India") -> List[Dict[str, Any]]:
        """Search OpenCorporates API for company data"""
        if not settings.opencorporates_api_key:
            return []
        
        try:
            url = "https://api.opencorporates.com/v0.4/companies/search"
            params = {
                'q': query,
                'jurisdiction_code': 'in' if region == 'India' else '',
                'api_token': settings.opencorporates_api_key,
                'per_page': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for company in data.get('results', {}).get('companies', []):
                company_info = company.get('company', {})
                results.append({
                    'company_name': company_info.get('name', ''),
                    'website': '',  # OpenCorporates doesn't provide website
                    'address': company_info.get('registered_address_in_full', ''),
                    'industry': company_info.get('company_type', ''),
                    'source': 'opencorporates',
                    'raw_data': company_info
                })
            
            return results
            
        except Exception as e:
            print(f"OpenCorporates search error: {e}")
            return []
    
    def search_google_places(self, query: str, region: str = "India") -> List[Dict[str, Any]]:
        """Search Google Places API for business data"""
        if not settings.google_maps_api_key:
            return []
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f"{query} {region}",
                'key': settings.google_maps_api_key,
                'type': 'establishment'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for place in data.get('results', [])[:10]:  # Limit to 10 results
                results.append({
                    'company_name': place.get('name', ''),
                    'website': '',  # Would need Place Details API for website
                    'address': place.get('formatted_address', ''),
                    'industry': ', '.join(place.get('types', [])),
                    'source': 'google_places',
                    'raw_data': place
                })
            
            return results
            
        except Exception as e:
            print(f"Google Places search error: {e}")
            return []
    
    def calculate_relevance_score(self, company_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate relevance score using keyword matching and semantic similarity"""
        if not keywords:
            return 0.0
        
        # Combine company text data
        text_fields = [
            company_data.get('company_name', ''),
            company_data.get('industry', ''),
            company_data.get('description', ''),
        ]
        company_text = ' '.join(filter(None, text_fields)).lower()
        
        if not company_text:
            return 0.0
        
        # Keyword matching score (0.0 to 0.6)
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in company_text:
                keyword_matches += 1
        
        keyword_score = min(keyword_matches / len(keywords), 1.0) * 0.6
        
        # Semantic similarity score (0.0 to 0.4)
        semantic_score = 0.0
        if self.sentence_model:
            try:
                keywords_text = ' '.join(keywords)
                embeddings = self.sentence_model.encode([company_text, keywords_text])
                similarity = float(embeddings[0] @ embeddings[1] / 
                                 (embeddings[0] @ embeddings[0] * embeddings[1] @ embeddings[1]) ** 0.5)
                semantic_score = max(0, similarity) * 0.4
            except:
                pass
        
        return min(keyword_score + semantic_score, 1.0)
    
    def _extract_company_info(self, title: str, snippet: str, url: str) -> Dict[str, Any]:
        """Extract company information from search results"""
        # Basic company name extraction
        company_name = title.split(' - ')[0].split(' | ')[0].strip()
        
        # Try to extract website from URL
        website = ''
        if url.startswith('http'):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                website = f"{parsed.scheme}://{parsed.netloc}"
            except:
                pass
        
        # Extract potential industry/business type from snippet
        industry = ''
        business_keywords = ['software', 'technology', 'consulting', 'services', 'solutions', 
                           'manufacturing', 'retail', 'healthcare', 'finance', 'education']
        
        snippet_lower = snippet.lower()
        for keyword in business_keywords:
            if keyword in snippet_lower:
                industry = keyword.title()
                break
        
        return {
            'company_name': company_name,
            'website': website,
            'industry': industry,
            'description': snippet,
            'source': 'duckduckgo',
            'raw_data': {
                'title': title,
                'snippet': snippet,
                'url': url
            }
        }
    
    def generate_leads(self, keywords: List[str], region: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Generate leads from multiple sources"""
        all_leads = []
        
        # Search query combining keywords
        query = ' '.join(keywords[:3])  # Use first 3 keywords to avoid too long queries
        
        # Search DuckDuckGo
        duckduckgo_leads = self.search_duckduckgo(query, region)
        all_leads.extend(duckduckgo_leads)
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Search OpenCorporates
        opencorporates_leads = self.search_opencorporates(query, region)
        all_leads.extend(opencorporates_leads)
        
        # Add delay
        time.sleep(random.uniform(1, 3))
        
        # Search Google Places
        google_leads = self.search_google_places(query, region)
        all_leads.extend(google_leads)
        
        # Remove duplicates based on company name
        seen_companies = set()
        unique_leads = []
        
        for lead in all_leads:
            company_name = lead.get('company_name', '').lower().strip()
            if company_name and company_name not in seen_companies:
                seen_companies.add(company_name)
                
                # Calculate relevance score
                lead['relevance_score'] = self.calculate_relevance_score(lead, keywords)
                lead['keywords_matched'] = self._find_matched_keywords(lead, keywords)
                
                unique_leads.append(lead)
        
        # Sort by relevance score and return top results
        unique_leads.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return unique_leads[:limit]
    
    def _find_matched_keywords(self, lead_data: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Find which keywords match the lead data"""
        text_fields = [
            lead_data.get('company_name', ''),
            lead_data.get('industry', ''),
            lead_data.get('description', ''),
        ]
        company_text = ' '.join(filter(None, text_fields)).lower()
        
        matched = []
        for keyword in keywords:
            if keyword.lower() in company_text:
                matched.append(keyword)
        
        return matched