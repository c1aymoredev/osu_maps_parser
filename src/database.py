"""Database module for storing and managing beatmap data."""
import asyncpg
import json
from datetime import datetime
from typing import Dict, List

class Database:
    def __init__(self):
        self.pool = None
        
    async def init_pool(self, dsn: str):
        self.pool = await asyncpg.create_pool(dsn)
        await self.create_tables()
        
    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS beatmaps (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    artist TEXT,
                    creator TEXT,
                    difficulty_rating REAL,
                    bpm REAL,
                    total_length INTEGER,
                    star_rating REAL,
                    created_at TEXT,
                    ranked_date TEXT,
                    last_updated TEXT,
                    ar REAL,
                    od REAL,
                    cs REAL,
                    hp REAL,
                    version TEXT,
                    mode TEXT,
                    status TEXT,
                    raw_data JSONB
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS scraping_progress (
                    id SERIAL PRIMARY KEY,
                    start_date TEXT,
                    end_date TEXT,
                    cursor_string TEXT,
                    completed BOOLEAN DEFAULT false,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
    async def save_progress(self, start_date: str, end_date: str, cursor: str = None, completed: bool = False):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO scraping_progress (start_date, end_date, cursor_string, completed)
                VALUES ($1, $2, $3, $4)
            ''', start_date, end_date, cursor, completed)
            
    async def get_uncompleted_periods(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            records = await conn.fetch('''
                SELECT DISTINCT start_date, end_date
                FROM scraping_progress
                WHERE NOT completed
                ORDER BY start_date ASC
            ''')
            return [dict(r) for r in records]
        
    async def is_period_completed(self, start_date: str, end_date: str) -> bool:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow('''
                SELECT completed FROM scraping_progress
                WHERE start_date = $1 AND end_date = $2 AND completed = true
            ''', start_date, end_date)
            return bool(record)
        
    async def insert_beatmap(self, beatmap: Dict, beatmapset: Dict, stats):
        try:
            async with self.pool.acquire() as conn:
                data = self.prepare_beatmap_data(beatmap, beatmapset)
                await conn.execute('''
                    INSERT INTO beatmaps 
                    (id, title, artist, creator, difficulty_rating, bpm, 
                    total_length, star_rating, created_at, ranked_date, last_updated,
                    ar, od, cs, hp, version, mode, status, raw_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 
                            $14, $15, $16, $17, $18, $19)
                    ON CONFLICT (id) DO UPDATE SET
                    last_updated = EXCLUDED.last_updated,
                    raw_data = EXCLUDED.raw_data
                ''', 
                    data['id'], data['title'], data['artist'], data['creator'],
                    data['difficulty_rating'], data['bpm'], data['total_length'],
                    data['star_rating'], data['created_at'], data['ranked_date'], 
                    data['last_updated'], data['ar'], data['od'], data['cs'], 
                    data['hp'], data['version'], data['mode'], data['status'],
                    data['raw_data']
                )
                stats.successful_saves += 1
        except Exception as e:
            print(f"Error saving beatmap {beatmap.get('id')}: {str(e)}")
            stats.failed_saves += 1

    def prepare_beatmap_data(self, beatmap: Dict, beatmapset: Dict) -> Dict:
        return {
            'id': beatmap.get('id'),  
            'title': beatmapset.get('title'),
            'artist': beatmapset.get('artist'),
            'creator': beatmapset.get('creator'),
            'difficulty_rating': beatmap.get('difficulty_rating'),
            'bpm': beatmapset.get('bpm'),
            'total_length': beatmap.get('total_length'),
            'star_rating': beatmap.get('difficulty_rating'),
            'created_at': beatmap.get('created_at'),
            'ranked_date': beatmapset.get('ranked_date'),
            'last_updated': datetime.now().isoformat(),
            'ar': beatmap.get('ar'),
            'od': beatmap.get('accuracy'),
            'cs': beatmap.get('cs'),
            'hp': beatmap.get('drain'),
            'version': beatmap.get('version'),
            'mode': beatmap.get('mode'),
            'status': beatmapset.get('status'),
            'raw_data': json.dumps({
                'beatmap': {k: v for k, v in beatmap.items() if k != 'beatmapset'},
                'beatmapset': {k: v for k, v in beatmapset.items() if k != 'beatmaps'}
            })
        }