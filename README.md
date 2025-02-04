# osu! Maps Parser 

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![osu!api v2](https://img.shields.io/badge/osu!api-v2-pink.svg)](https://osu.ppy.sh/docs/index.html)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)](https://www.postgresql.org/)

Asynchronous Python script for collecting data about all ranked beatmaps in osu! using the official API v2. The data is stored in a PostgreSQL database for further analysis.

## Features

- Downloads all ranked beatmaps information
- Stores detailed map data (AR, OD, CS, HP, BPM, etc.)
- Handles API rate limits
- Supports resuming from last position
- Shows progress statistics during execution

## Requirements

- Python 3.8+
- PostgreSQL
- osu! API v2 credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/c1aymoredev/osu_maps_parser.git
cd osu_maps_parser
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```sql
CREATE DATABASE osu_maps;
```

4. Configure the program:
- Get your osu! API credentials from https://osu.ppy.sh/home/account/edit#oauth
- Update `config.py` with your credentials:
```python
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
DB_DSN = "postgresql://postgres:your_password@localhost/osu_maps"
```

## Usage

Run the program:
```bash
python src/main.py
```

The program will:
1. Connect to the osu! API
2. Create necessary database tables
3. Start downloading beatmap data chronologically from 2007
4. Show progress and statistics during execution
5. Save all beatmap information to the database

## 📊 Database Structure

The program creates two tables:
- `beatmaps` - stores beatmap information
- `scraping_progress` - tracks download progress

Main beatmap fields:
- `id` - beatmap ID
- `title` - song title
- `artist` - song artist
- `creator` - mapper name
- `difficulty_rating` - star rating
- `bpm` - beats per minute
- `ar` - approach rate
- `od` - overall difficulty
- `cs` - circle size
- `hp` - drain rate
- `ranked_date` - when the map was ranked
- `raw_data` - full JSON data from API

## Contributing

Pull requests are welcome! Feel free to contribute to improve the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
