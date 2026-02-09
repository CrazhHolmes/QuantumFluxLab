"""AutoDocs - Self-documenting breakthrough documentation for SynapseScanner v1.4.0"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class BreakthroughDocumenter:
    """
    Automatically documents research breakthroughs discovered by SynapseScanner.
    Generates markdown files, updates README, maintains breakthrough log.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize documenter with repository path."""
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.docs_dir = self.repo_path / "docs"
        self.readme_path = self.repo_path / "README.md"
        self.breakthrough_log_path = self.docs_dir / "BREAKTHROUGHS.md"
        
        # Ensure docs directory exists
        self.docs_dir.mkdir(exist_ok=True)
    
    def generate_breakthrough_doc(
        self,
        pattern: Dict[str, Any],
        papers: List[Any],
        connections: List[Any],
        ai_summary: Optional[Dict] = None,
        query: str = ""
    ) -> str:
        """
        Creates comprehensive markdown documentation for a breakthrough.
        
        Args:
            pattern: The detected pattern dict (type, hint, cost, difficulty)
            papers: List of Paper objects supporting this breakthrough
            connections: List of cross-source connections
            ai_summary: Optional AI-generated summary dict
            query: Original search query
            
        Returns:
            Markdown string with full documentation
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_slug = datetime.now().strftime("%Y-%m-%d")
        
        pattern_name = pattern.get("pattern", "Unknown Breakthrough")
        pattern_slug = self._slugify(pattern_name)
        
        # Build document
        lines = [
            f"# Breakthrough: {pattern_name}",
            "",
            f"**Discovered:** {timestamp}",
            f"**Query:** {query or 'N/A'}",
            f"**Sources:** {self._get_sources_list(papers)}",
            f"**Confidence:** {self._calculate_confidence(connections)}",
            "",
            "## The Breakthrough",
            "",
            f"{pattern.get('hint', 'No description available.')}",
            "",
        ]
        
        # Why It Matters section
        lines.extend([
            "## Why It Matters",
            "",
        ])
        
        if ai_summary and ai_summary.get("tldr"):
            lines.append(f"{ai_summary['tldr']}")
            lines.append("")
            if ai_summary.get("insights"):
                lines.append("### Key Insights")
                lines.append("")
                for insight in ai_summary["insights"][:3]:
                    lines.append(f"- {insight}")
                lines.append("")
        else:
            lines.append(self._get_pattern_explanation(pattern_name))
            lines.append("")
        
        # Supporting Evidence
        if papers:
            lines.extend([
                "## Supporting Evidence",
                "",
                "| Paper | Source | Key Insight | Link |",
                "|-------|--------|-------------|------|",
            ])
            
            for paper in papers[:5]:  # Top 5 papers
                title = paper.title[:50] + "..." if len(paper.title) > 50 else paper.title
                source = paper.source
                abstract = paper.abstract[:60] + "..." if len(paper.abstract) > 60 else paper.abstract
                url = paper.url or "N/A"
                lines.append(f"| {title} | {source} | {abstract} | [Link]({url}) |")
            
            lines.append("")
        
        # Cross-Source Connections
        if connections:
            lines.extend([
                "## Cross-Source Connections",
                "",
            ])
            
            for conn in connections[:5]:
                strength_emoji = "⭐" * (conn.strength // 2) + "☆" * (5 - conn.strength // 2)
                lines.append(f"- **{conn.paper_a.source} ↔ {conn.paper_b.source}** ({strength_emoji})")
                lines.append(f"  - {conn.reason}")
                lines.append("")
        
        # Implementation
        lines.extend([
            "## Implementation",
            "",
            f"**Cost:** {pattern.get('cost', 'Unknown')}",
            f"**Difficulty:** {pattern.get('difficulty', 'Unknown')}",
            f"**Estimated Time:** {self._estimate_time(pattern.get('difficulty', 'Unknown'))}",
            "",
        ])
        
        # Shopping list based on pattern type
        shopping_list = self._get_shopping_list(pattern_name)
        if shopping_list:
            lines.extend([
                "### Shopping List",
                "",
            ])
            for item, cost in shopping_list:
                lines.append(f"- [ ] {item} ({cost})")
            lines.append("")
        
        # Step-by-step
        steps = self._get_implementation_steps(pattern_name)
        if steps:
            lines.extend([
                "### Step-by-Step",
                "",
            ])
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        # Tags
        tags = self._generate_tags(pattern_name, papers)
        lines.extend([
            "## Tags",
            "",
            " ".join([f"#{tag}" for tag in tags]),
            "",
            "---",
            "",
            f"*Generated by SynapseScanner v1.4.0*",
            "",
        ])
        
        return "\n".join(lines)
    
    def update_readme(self, pattern: Dict[str, Any], doc_content: str) -> bool:
        """
        Updates README.md with latest breakthrough section.
        Inserts after "## Latest Discoveries" header.
        Maintains rolling log (keep last 5 discoveries).
        """
        if not self.readme_path.exists():
            print(f"[!] README.md not found at {self.readme_path}")
            return False
        
        try:
            content = self.readme_path.read_text(encoding='utf-8')
            
            # Find or create the Latest Discoveries section
            section_start = "## Latest Discoveries"
            section_marker_start = "<!-- SYNAPSESCANNER-BREAKTHROUGHS-START -->"
            section_marker_end = "<!-- SYNAPSESCANNER-BREAKTHROUGHS-END -->"
            
            # Create new entry
            new_entry = self._format_readme_entry(pattern, doc_content)
            
            if section_marker_start in content and section_marker_end in content:
                # Update existing section
                start_idx = content.find(section_marker_start) + len(section_marker_start)
                end_idx = content.find(section_marker_end)
                
                existing_entries = content[start_idx:end_idx]
                
                # Parse existing entries and keep only last 4 (plus new = 5)
                entries = self._parse_existing_entries(existing_entries)
                entries.insert(0, new_entry)  # Add new at top
                entries = entries[:5]  # Keep only 5
                
                # Rebuild section
                new_section_content = "\n\n---\n\n".join(entries)
                
                # Replace in content
                new_content = (
                    content[:start_idx] + 
                    "\n\n" + new_section_content + "\n\n" +
                    content[end_idx:]
                )
            else:
                # Create new section
                section_content = f"\n{section_start}\n\n{section_marker_start}\n\n{new_entry}\n\n{section_marker_end}\n\n"
                
                # Insert before first ## section or at end
                first_header = re.search(r'\n## ', content)
                if first_header:
                    insert_pos = first_header.start()
                    new_content = content[:insert_pos] + section_content + content[insert_pos:]
                else:
                    new_content = content + "\n" + section_content
            
            self.readme_path.write_text(new_content, encoding='utf-8')
            print(f"[OK] Updated README.md with new breakthrough")
            return True
            
        except Exception as e:
            print(f"[!] Failed to update README: {e}")
            return False
    
    def maintain_breakthrough_log(self, pattern: Dict[str, Any], doc_content: str) -> bool:
        """
        Appends to docs/BREAKTHROUGHS.md (chronological log of all discoveries).
        """
        try:
            # Create header if file doesn't exist
            if not self.breakthrough_log_path.exists():
                header = "# SynapseScanner Breakthrough Log\n\n"
                header += "Chronological record of all research breakthroughs discovered.\n\n"
                header += "---\n\n"
                self.breakthrough_log_path.write_text(header, encoding='utf-8')
            
            # Append new entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            pattern_name = pattern.get("pattern", "Unknown")
            
            entry = f"\n## {timestamp} - {pattern_name}\n\n"
            entry += f"**Cost:** {pattern.get('cost', 'Unknown')} | "
            entry += f"**Difficulty:** {pattern.get('difficulty', 'Unknown')}\n\n"
            entry += f"{pattern.get('hint', '')}\n\n"
            entry += f"[Full Documentation](./{self._slugify(pattern_name)}.md)\n\n"
            entry += "---\n"
            
            with open(self.breakthrough_log_path, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            print(f"[OK] Appended to {self.breakthrough_log_path}")
            return True
            
        except Exception as e:
            print(f"[!] Failed to update breakthrough log: {e}")
            return False
    
    def save_breakthrough_doc(self, pattern: Dict[str, Any], doc_content: str) -> Optional[Path]:
        """Save full breakthrough documentation to docs/ directory."""
        try:
            date_slug = datetime.now().strftime("%Y-%m-%d")
            pattern_slug = self._slugify(pattern.get("pattern", "breakthrough"))
            filename = f"{date_slug}-{pattern_slug}.md"
            filepath = self.docs_dir / filename
            
            # Handle collision by adding counter
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                filename = f"{date_slug}-{pattern_slug}-{counter}.md"
                filepath = self.docs_dir / filename
                counter += 1
            
            filepath.write_text(doc_content, encoding='utf-8')
            print(f"[OK] Saved breakthrough doc: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[!] Failed to save breakthrough doc: {e}")
            return None
    
    def generate_research_report(self, query: str, all_papers: List[Any],
                                 patterns: List[Dict], output_path: str) -> bool:
        """Generates full research report for a query."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            lines = [
                f"# Research Report: {query}",
                "",
                f"**Generated:** {timestamp}",
                f"**Papers Found:** {len(all_papers)}",
                f"**Breakthroughs Detected:** {len(patterns)}",
                "",
                "## Summary",
                "",
            ]
            
            if patterns:
                lines.append("### Detected Breakthroughs")
                lines.append("")
                for p in patterns:
                    lines.append(f"- **{p.get('pattern')}** ({p.get('cost')}, {p.get('difficulty')})")
                lines.append("")
            
            lines.extend([
                "## All Papers",
                "",
                "| Title | Source | Year | Citations |",
                "|-------|--------|------|-----------|",
            ])
            
            for paper in all_papers:
                year = paper.published[:4] if paper.published else "N/A"
                citations = paper.citations or "N/A"
                title = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title
                lines.append(f"| {title} | {paper.source} | {year} | {citations} |")
            
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("*Generated by SynapseScanner v1.4.0*")
            
            Path(output_path).write_text("\n".join(lines), encoding='utf-8')
            print(f"[OK] Saved research report: {output_path}")
            return True
            
        except Exception as e:
            print(f"[!] Failed to generate research report: {e}")
            return False
    
    # Helper methods
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text[:50]
    
    def _get_sources_list(self, papers: List[Any]) -> str:
        """Get comma-separated list of sources."""
        sources = list(set(p.source for p in papers if hasattr(p, 'source')))
        return ", ".join(sources) if sources else "N/A"
    
    def _calculate_confidence(self, connections: List[Any]) -> str:
        """Calculate confidence rating based on connections."""
        if not connections:
            return "⭐⭐⭐☆☆ (Medium)"
        
        avg_strength = sum(c.strength for c in connections) / len(connections)
        if avg_strength >= 7:
            return "⭐⭐⭐⭐⭐ (Very High)"
        elif avg_strength >= 5:
            return "⭐⭐⭐⭐☆ (High)"
        elif avg_strength >= 3:
            return "⭐⭐⭐☆☆ (Medium)"
        else:
            return "⭐⭐☆☆☆ (Low)"
    
    def _format_readme_entry(self, pattern: Dict[str, Any], doc_content: str) -> str:
        """Format a breakthrough entry for README."""
        pattern_name = pattern.get("pattern", "Unknown")
        cost = pattern.get("cost", "Unknown")
        difficulty = pattern.get("difficulty", "Unknown")
        hint = pattern.get("hint", "")
        
        date_str = datetime.now().strftime("%b %d, %Y")
        doc_filename = f"./docs/{self._slugify(pattern_name)}.md"
        
        entry = f"""### 🧪 {pattern_name} ({date_str})
**Cost:** {cost} | **Difficulty:** {difficulty} | **Confidence:** {self._calculate_confidence([])}

{hint}

<details>
<summary>🔬 Supporting Evidence</summary>

See full documentation for paper links and implementation details.

</details>

[📖 Full Documentation]({doc_filename})"""
        
        return entry
    
    def _parse_existing_entries(self, content: str) -> List[str]:
        """Parse existing README entries."""
        entries = []
        current_entry = []
        
        for line in content.split('\n'):
            if line.startswith('### ') and current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = [line]
            elif line.strip() or current_entry:
                current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        return [e.strip() for e in entries if e.strip()]
    
    def _get_pattern_explanation(self, pattern_name: str) -> str:
        """Get explanation for a pattern type."""
        explanations = {
            "Quantum breakthrough": (
                "This breakthrough leverages quantum mechanical phenomena that were previously "
                "only accessible in specialized laboratories. The suggested experiment makes "
                "quantum effects visible using inexpensive, readily available components."
            ),
            "Metamaterial lens": (
                "Negative-index metamaterials were once theoretical constructs. This approach "
                "demonstrates the effect using everyday materials, bridging the gap between "
                "theoretical physics and hands-on experimentation."
            ),
            "Temporal periodicity": (
                "Time crystals represent a new phase of matter. This simple analog demonstrates "
                "the core concept of discrete time-translation symmetry breaking in an accessible way."
            ),
            "AI physics": (
                "Machine learning is revolutionizing how we discover physical laws. This approach "
                "shows how neural networks can rediscover classical mechanics from raw data."
            ),
        }
        return explanations.get(pattern_name, "This breakthrough represents a significant finding in cross-disciplinary research.")
    
    def _get_shopping_list(self, pattern_name: str) -> List[tuple]:
        """Get shopping list for a pattern."""
        lists = {
            "Quantum breakthrough": [
                ("Polarizing filters (2x)", "$10"),
                ("Laser pointer (red)", "$15"),
                ("Cardboard/3D printed mounts", "$5"),
            ],
            "Metamaterial lens": [
                ("Microscope slides (pack of 10)", "$8"),
                ("Index matching oil", "$10"),
                ("Laser pointer", "$15"),
            ],
            "Temporal periodicity": [
                ("555 timer IC", "$0.50"),
                ("LED (any color)", "$0.20"),
                ("Resistors & capacitors", "$2"),
                ("Breadboard", "$5"),
            ],
            "AI physics": [
                ("Laptop with Python", "$0 (existing)"),
                ("Webcam (optional)", "$0 (phone works)"),
            ],
        }
        return lists.get(pattern_name, [])
    
    def _get_implementation_steps(self, pattern_name: str) -> List[str]:
        """Get implementation steps for a pattern."""
        steps = {
            "Quantum breakthrough": [
                "Set up laser pointer on stable surface",
                "Place first polarizer in beam path",
                "Add second polarizer and rotate 90° (beam should extinguish)",
                "Insert third polarizer at 45° between them (beam reappears!)",
                "Document results and compare with theoretical predictions",
            ],
            "Metamaterial lens": [
                "Stack microscope slides with index-matching oil between layers",
                "Shine laser through the stack at various angles",
                "Observe negative refraction (beam bends 'wrong' way)",
                "Measure angles and calculate effective refractive index",
            ],
            "Temporal periodicity": [
                "Build 555 timer circuit in astable mode (1 Hz)",
                "Connect LED output",
                "Observe the discrete time-symmetry breaking",
                "Compare with theoretical time-crystal models",
            ],
            "AI physics": [
                "Set up pendulum with position tracking (webcam or sensor)",
                "Collect motion data for 100+ swings",
                "Train small neural network (3-layer MLP)",
                "Compare network predictions with Newtonian physics",
                "Analyze what the network 'learned' about mechanics",
            ],
        }
        return steps.get(pattern_name, ["See full documentation for detailed steps."])
    
    def _estimate_time(self, difficulty: str) -> str:
        """Estimate implementation time."""
        times = {
            "Easy": "1-2 hours",
            "Medium": "Half day",
            "Research": "1-2 days",
        }
        return times.get(difficulty, "Variable")
    
    def _generate_tags(self, pattern_name: str, papers: List[Any]) -> List[str]:
        """Generate tags for a breakthrough."""
        tags = []
        
        # Base tags from pattern
        if "quantum" in pattern_name.lower():
            tags.extend(["quantum", "physics", "optics"])
        elif "material" in pattern_name.lower():
            tags.extend(["metamaterials", "optics", "physics"])
        elif "temporal" in pattern_name.lower() or "time" in pattern_name.lower():
            tags.extend(["time-crystals", "condensed-matter", "physics"])
        elif "AI" in pattern_name or "neural" in pattern_name:
            tags.extend(["machine-learning", "physics", "AI"])
        
        # Difficulty tag
        tags.append("breakthrough")
        tags.append("experiment")
        
        return list(set(tags))
