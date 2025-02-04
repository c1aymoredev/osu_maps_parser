"""Module for interacting with the osu! API v2."""
import asyncio
from typing import Dict
import aiohttp
import time

class OsuAPI:
    """Handles authentication and requests to the osu! API."""
    def __init__(self, client_id: int, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.base_url = "https://osu.ppy.sh/api/v2"
        self.session = None
        self.last_request_time = 0
        self.rate_limit = 1/10  # 10 queries per second max
        
    async def init_session(self):
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def wait_for_rate_limit(self):
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
        
    async def get_token(self) -> str:
        await self.wait_for_rate_limit()
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'public'
        }
        async with self.session.post('https://osu.ppy.sh/oauth/token', data=data) as response:
            result = await response.json()
            self.token = result['access_token']
            return self.token

    async def get_beatmaps(self, start_date: str, end_date: str, mode: str = 'osu', limit: int = 100, cursor: str = None) -> Dict:
        await self.wait_for_rate_limit()
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {
            'sort': 'ranked_date',
            's': mode,
            'limit': limit,
            'status': 'ranked',
            'q': f'ranked>={start_date} ranked<={end_date}'
        }
        if cursor:
            params['cursor_string'] = cursor
            
        async with self.session.get(f"{self.base_url}/beatmapsets/search", headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 401:  # token expired
                await self.get_token()
                return await self.get_beatmaps(start_date, end_date, mode, limit, cursor)
            else:
                print(f"API Error: {response.status}")
                print("Response:", await response.text())
                await asyncio.sleep(5)  # pause on error
                return {"beatmapsets": []}