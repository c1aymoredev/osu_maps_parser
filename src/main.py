"""Main script for downloading and storing osu! beatmap data."""
import asyncio
from config import CLIENT_ID, CLIENT_SECRET, DB_DSN
from osu_api import OsuAPI
from database import Database
from stats import Stats
from utils import generate_date_ranges

async def process_date_range(api: OsuAPI, db: Database, stats: Stats, start_date: str, end_date: str):
    print(f"\nProcessing period: {start_date} to {end_date}")
    stats.current_date_range = f"{start_date} to {end_date}"
    
    cursor = None
    while True:
        response = await api.get_beatmaps(start_date, end_date, cursor=cursor)
        beatmapsets = response.get('beatmapsets', [])
        
        if not beatmapsets:
            await db.save_progress(start_date, end_date, cursor, completed=True)
            break
            
        print(f"Found {len(beatmapsets)} beatmapsets")
        for beatmapset in beatmapsets:
            for beatmap in beatmapset.get('beatmaps', []):
                if beatmap.get('mode') == 'osu':  # only osu! gamemode
                    stats.processed_beatmaps += 1
                    await db.insert_beatmap(beatmap, beatmapset, stats)
                    print(f"Saved: {beatmapset.get('title', 'Unknown')} [{beatmap.get('version', 'Unknown')}] by {beatmapset.get('creator', 'Unknown')}")
        
        cursor = response.get('cursor_string', '')
        await db.save_progress(start_date, end_date, cursor)
        
        if not cursor:
            await db.save_progress(start_date, end_date, cursor, completed=True)
            break
            
        stats.print_progress()
        await asyncio.sleep(0.5)

async def main():
    # init
    api = OsuAPI(CLIENT_ID, CLIENT_SECRET)
    db = Database()
    stats = Stats()
    
    await api.init_session()
    await db.init_pool(DB_DSN)
    await api.get_token()
    
    # generating all time periods
    date_ranges = generate_date_ranges()
    
    try:
        # processing each period
        for start_date, end_date in date_ranges:
            # checking if this period has already been processed
            if not await db.is_period_completed(start_date, end_date):
                try:
                    await process_date_range(api, db, stats, start_date, end_date)
                except Exception as e:
                    print(f"Error processing period {start_date} to {end_date}: {e}")
                    await asyncio.sleep(5)
                    continue
    finally:
        await api.close_session()
        print("\nFinished!")
        stats.print_progress()

if __name__ == "__main__":
    asyncio.run(main())