"""AI summarization layer for SynapseScanner."""
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Summary:
    """AI-generated summary of a paper."""
    tldr: str                       # 2-sentence summary
    insights: List[str]            # 3 key insights
    tags: List[str]                # Suggested tags
    raw_response: str = ""         # Full raw response for debugging


class AISummarizer:
    """AI summarization with Ollama and OpenAI support."""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None,
                 ollama_url: str = "http://localhost:11434"):
        """Initialize AI summarizer.
        
        Args:
            provider: "ollama", "openai", or None (auto-detect)
            model: Model name (provider-specific)
            ollama_url: URL for Ollama server
        """
        self.provider = provider
        self.model = model
        self.ollama_url = ollama_url
        self._ollama_available: Optional[bool] = None
        self._openai_available: Optional[bool] = None
    
    def is_available(self) -> bool:
        """Check if any AI provider is available."""
        return self._check_ollama() or self._check_openai()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        if self._ollama_available is not None:
            return self._ollama_available
        
        try:
            import requests
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            self._ollama_available = resp.status_code == 200
        except Exception:
            self._ollama_available = False
        
        return self._ollama_available
    
    def _check_openai(self) -> bool:
        """Check if OpenAI API key is available."""
        if self._openai_available is not None:
            return self._openai_available
        
        self._openai_available = bool(os.getenv("OPENAI_API_KEY"))
        return self._openai_available
    
    def _detect_provider(self) -> Optional[str]:
        """Auto-detect available provider."""
        if self._check_ollama():
            return "ollama"
        if self._check_openai():
            return "openai"
        return None
    
    def summarize(self, text: str, title: str = "", 
                  provider: Optional[str] = None) -> Optional[Summary]:
        """Summarize text using AI.
        
        Args:
            text: Text to summarize (typically abstract)
            title: Paper title for context
            provider: Override provider ("ollama", "openai", or None for auto)
            
        Returns:
            Summary object or None if AI unavailable
        """
        # Determine provider
        use_provider = provider or self.provider or self._detect_provider()
        
        if use_provider == "ollama" and self._check_ollama():
            return self._summarize_ollama(text, title)
        elif use_provider == "openai" and self._check_openai():
            return self._summarize_openai(text, title)
        
        return None
    
    def _summarize_ollama(self, text: str, title: str) -> Optional[Summary]:
        """Summarize using Ollama."""
        try:
            import requests
            
            model = self.model or "llama3.2"
            
            prompt = self._build_prompt(text, title)
            
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 300
                    }
                },
                timeout=60
            )
            
            if resp.status_code != 200:
                return None
            
            data = resp.json()
            response = data.get("response", "")
            
            return self._parse_response(response)
            
        except Exception:
            return None
    
    def _summarize_openai(self, text: str, title: str) -> Optional[Summary]:
        """Summarize using OpenAI API."""
        try:
            # Import here to avoid mandatory dependency
            try:
                import openai
            except ImportError:
                return None
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            
            client = openai.OpenAI(api_key=api_key)
            model = self.model or "gpt-3.5-turbo"
            
            prompt = self._build_prompt(text, title, for_chat=True)
            
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a research assistant. Summarize academic papers concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            response = resp.choices[0].message.content
            return self._parse_response(response)
            
        except Exception:
            return None
    
    def _build_prompt(self, text: str, title: str, for_chat: bool = False) -> str:
        """Build summarization prompt."""
        context = f"Title: {title}\n\n" if title else ""
        context += f"Abstract: {text[:2000]}"  # Limit text length
        
        prompt = f"""Please summarize the following research paper:

{context}

Provide:
1. TL;DR (2 sentences max)
2. 3 key insights (bullet points)
3. 3-5 suggested tags (comma-separated)

Format your response exactly like this:
TL;DR: <your 2-sentence summary>
Insights:
- <insight 1>
- <insight 2>
- <insight 3>
Tags: <tag1>, <tag2>, <tag3>, <tag4>, <tag5>"""
        
        return prompt
    
    def _parse_response(self, response: str) -> Summary:
        """Parse AI response into structured summary."""
        tldr = ""
        insights = []
        tags = []
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse TL;DR
            if line.lower().startswith("tldr:") or line.lower().startswith("tl;dr:"):
                tldr = line.split(":", 1)[1].strip()
                current_section = "tldr"
            
            # Parse Insights section
            elif line.lower().startswith("insight") or line.lower().startswith("key insight"):
                current_section = "insights"
            elif line.startswith("-") or line.startswith("•"):
                if current_section == "insights" or current_section is None:
                    insight = line[1:].strip()
                    if insight:
                        insights.append(insight)
                    current_section = "insights"
            
            # Parse Tags
            elif line.lower().startswith("tags:"):
                tags_text = line.split(":", 1)[1].strip()
                tags = [t.strip() for t in tags_text.split(",") if t.strip()]
                current_section = "tags"
            
            # Continue TL;DR on next lines if needed
            elif current_section == "tldr" and tldr and not insights:
                tldr += " " + line
        
        # Ensure we have at least something
        if not tldr:
            tldr = response[:200] + "..." if len(response) > 200 else response
        
        # Limit insights to 3
        insights = insights[:3]
        
        # Fallback tags if none extracted
        if not tags:
            tags = self._extract_basic_tags(tldr + " " + " ".join(insights))
        
        return Summary(
            tldr=tldr,
            insights=insights,
            tags=tags[:5],
            raw_response=response
        )
    
    def _extract_basic_tags(self, text: str) -> List[str]:
        """Extract basic tags from text when AI doesn't provide them."""
        # Simple keyword extraction for fallback
        common_research_terms = [
            "machine learning", "deep learning", "neural network", "artificial intelligence",
            "quantum", "physics", "chemistry", "biology", "medicine", "health",
            "climate", "environment", "energy", "materials", "nanotechnology",
            "genetics", "genomics", "protein", "cell", "molecular",
            "algorithm", "optimization", "simulation", "modeling",
            "theory", "experiment", "review", "meta-analysis"
        ]
        
        text_lower = text.lower()
        tags = []
        
        for term in common_research_terms:
            if term in text_lower:
                tags.append(term.replace(" ", "-"))
                if len(tags) >= 5:
                    break
        
        return tags if tags else ["research"]


def summarize_abstract(text: str, model: str = "ollama/llama3.2",
                       title: str = "") -> Optional[Dict]:
    """Convenience function for summarizing an abstract.
    
    Args:
        text: Abstract text
        model: Model specification (e.g., "ollama/llama3.2" or "openai/gpt-3.5-turbo")
        title: Paper title for context
        
    Returns:
        Dict with "tldr", "insights", "tags" or None if unavailable
    """
    # Parse model string
    if "/" in model:
        provider, model_name = model.split("/", 1)
    else:
        provider = None
        model_name = model
    
    summarizer = AISummarizer(provider=provider, model=model_name)
    summary = summarizer.summarize(text, title, provider=provider)
    
    if summary:
        return {
            "tldr": summary.tldr,
            "insights": summary.insights,
            "tags": summary.tags
        }
    
    return None
