def extract_text_from_url(url: str) -> str:
    """Extracts clean text from a news URL with enhanced anti-bot headers."""
    # Engine A: Try specialized Newspaper3k extraction
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text
    except Exception:
        pass 

    # Engine B: Advanced Human-Mimic HTML parsing fallback
    try:
        # High-fidelity header stack to bypass standard anti-scraping firewalls
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1' # Do Not Track request indicator
        }
        
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strip out non-content elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Extract paragraphs from the main content body
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 20]
            text_content = " ".join(paragraphs)
            
            if text_content.strip():
                return text_content
                
        raise ValueError(f"Target URL returned a non-200 status code: {response.status_code}")
    except Exception as e:
        raise ValueError(f"Resilient Extraction Failure: {str(e)}")