"""
AOIE STRATEGIC PRINCIPLES:
1. LEGALITY FIRST: Only public, accessible data.
2. CORRELATION OVER COLLECTION: Power comes from connecting dots.
3. REAL-TIME INTELLIGENCE: Speed as a competitive advantage.
4. EXPLAINABLE DECISIONS: Transparent credibility scoring.
5. ETHICAL OPERATION: Privacy by design, no tracking.
"""

class AOIEPrinciples:
    """Advanced OSINT Intelligence Engine Core Principles and Boundaries"""
    
    LEGAL_DATA_SOURCES = {
        'social_platforms': [
            'X (Twitter) - API & public scraping',
            'Reddit - API & public forums', 
            'YouTube - Public videos & comments',
            'LinkedIn - Public profiles & posts',
            'Instagram - Public posts & stories'
        ],
        'news_media': [
            'GDELT Project - Global event database',
            'NewsAPI - 70,000+ sources',
            'RSS Feeds - Thousands of publishers',
            'Government releases - Official channels'
        ],
        'web_intelligence': [
            'Public forums & discussion boards',
            'Blogs & independent media',
            'Academic publications',
            'Open data repositories'
        ],
        'financial_signals': [
            'Stock market feeds - Real-time',
            'Cryptocurrency trends',
            'Commodity prices',
            'Economic indicators'
        ],
        'multimedia_content': [
            'Public livestreams',
            'Podcasts & audio content',
            'Satellite imagery (public)',
            'Public webcams & traffic cams'
        ]
    }
    
    PROHIBITED_ACTIVITIES = {
        'mobile_surveillance': 'No device tracking or app data',
        'private_communications': 'No DMs, private messages, or restricted content',
        'signal_interception': 'No radio frequency monitoring',
        'credential_abuse': 'No unauthorized API access',
        'deceptive_practices': 'No fake accounts or misrepresentation'
    }
    
    ETHICAL_GUIDELINES = {
        'privacy': 'Minimize data collection, anonymize where possible',
        'transparency': 'Clear scoring systems, explainable AI',
        'accountability': 'Audit trails, responsible disclosure',
        'beneficial_use': 'Focus on public good applications'
    }

    @classmethod
    def validate_source(cls, source_name: str) -> bool:
        """Verify if a data source is within the permitted AOIE boundaries"""
        for category in cls.LEGAL_DATA_SOURCES.values():
            if any(source_name.lower() in s.lower() for s in category):
                return True
        return False
