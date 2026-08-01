import os
from dotenv import load_dotenv

load_dotenv(encoding='utf-16')
key = os.getenv('OPENROUTER_API_KEY')
print('Key loaded:', key[:15] + '...' if key else 'NOT FOUND')
