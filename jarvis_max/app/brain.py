import os
import logging
import aiohttp
import json
logger = logging.getLogger("jarvis.brain")

class AIBrain:
    def __init__(self):
        self.providers = {
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'xai': os.getenv('XAI_API_KEY')
        }
        self.current_provider = 'deepseek'
        
    async def process_query(self, query, use_consensus=False):
        logger.info(f"Processing query: {query}, consensus: {use_consensus}")
        
        if use_consensus:
            return await self._meta_consensus(query)
        else:
            return await self._single_provider(query)
            
    async def _single_provider(self, query):
        # Use DeepSeek API
        api_key = self.providers.get(self.current_provider)
        if not api_key:
            return f"Error: No API key found for {self.current_provider}"
            
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'user', 'content': query}
            ],
            'stream': False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.deepseek.com/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        return f"API Error: {response.status} - {error_text}"
        except Exception as e:
            return f"Error calling DeepSeek API: {str(e)}"
        
    async def _meta_consensus(self, query):
        # For now, just use single provider
        logger.info("Using meta-consensus for query")
        return await self._single_provider(query)
