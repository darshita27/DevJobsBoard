"""Role classification, ported from dev-jobs-blog's config/roles.json."""

ROLE_BUCKETS = [
    {'id': 'fullstack', 'label': 'Full Stack Developer', 'match': ['full stack', 'fullstack', 'full-stack']},
    {'id': 'mern', 'label': 'MERN Stack Developer', 'match': ['mern']},
    {'id': 'frontend', 'label': 'Frontend Developer', 'match': ['frontend', 'front end', 'front-end', 'ui engineer', 'ui developer']},
    {'id': 'backend', 'label': 'Backend Developer', 'match': ['backend', 'back end', 'back-end']},
    {'id': 'web', 'label': 'Web Developer', 'match': ['web developer', 'web development', 'web engineer']},
    {'id': 'react', 'label': 'React Developer', 'match': ['react']},
    {'id': 'node', 'label': 'Node.js Developer', 'match': ['node.js', 'nodejs', 'node js']},
    {'id': 'swe-intern', 'label': 'Software Engineer Intern', 'all': [['software', 'engineer'], ['intern']]},
    {'id': 'swd-intern', 'label': 'Software Developer Intern', 'all': [['software', 'developer'], ['intern']]},
    {'id': 'ai-intern', 'label': 'AI Intern', 'all': [['ai', 'artificial intelligence'], ['intern']]},
    {'id': 'ml-intern', 'label': 'Machine Learning Intern', 'all': [['machine learning', 'ml '], ['intern']]},
    {'id': 'genai-intern', 'label': 'Generative AI Intern', 'all': [['generative ai', 'gen ai', 'genai'], ['intern']]},
    {'id': 'llm-intern', 'label': 'LLM Engineer Intern', 'all': [['llm', 'large language model'], ['intern']]},
    {'id': 'prompt-intern', 'label': 'Prompt Engineer Intern', 'all': [['prompt'], ['intern']]},
]

EXCLUDE_TITLE_TERMS = [
    'principal', 'staff engineer', 'director', 'vice president', ' vp ', 'head of',
    'engineering manager', 'manager,', 'sales', 'recruiter', 'marketing', 'accountant',
    'technical program manager', 'product manager', 'solutions architect',
]

LOCATIONS_INCLUDE = [
    'india', 'bangalore', 'bengaluru', 'hyderabad', 'pune', 'chennai', 'mumbai',
    'delhi', 'new delhi', 'gurgaon', 'gurugram', 'noida', 'kolkata', 'ahmedabad',
    'jaipur', 'indore', 'chandigarh', 'coimbatore', 'kochi', 'trivandrum',
    'thiruvananthapuram', 'bhubaneswar', 'nagpur', 'vadodara', 'visakhapatnam', 'mysore',
]

MAX_AGE_DAYS = 45


def match_bucket(title: str):
    t = f' {(title or "").lower()} '

    for term in EXCLUDE_TITLE_TERMS:
        if term in t:
            return None

    for bucket in ROLE_BUCKETS:
        if 'match' in bucket and any(m in t for m in bucket['match']):
            return bucket
        if 'all' in bucket and all(any(term in t for term in group) for group in bucket['all']):
            return bucket
    return None


def matches_location(location: str) -> bool:
    loc = (location or '').lower()
    if any(term in loc for term in ('remote', 'anywhere', 'work from home', 'wfh')):
        return True
    return any(term in loc for term in LOCATIONS_INCLUDE)
