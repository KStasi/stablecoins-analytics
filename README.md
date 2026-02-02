# Stablecoins Analytics

Analytics dashboard for comparing price impact and volume for bridging USDT and USDC stablecoins between different chains using Near Intents API.

## Features

- Historical slippage analysis for USDT and USDC cross-chain bridging
- Interactive matrices showing slippage between different chains
- Color-coded visualization (green = low slippage, red = high slippage)
- PostgreSQL database for persistent data storage
- Automated data collection every 6 hours
- Support for multiple chains: Ethereum, Base, Arbitrum, BSC, Polygon, Optimism, Avalanche, Solana, NEAR

## Prerequisites

- Docker Desktop (must be running)
- Python 3.11+
- uv package manager

## Setup

### Quick Start (Automated)

```bash
./run.sh
```

This will:

1. Start PostgreSQL in Docker
2. Run initial data collection
3. Start background scheduler
4. Launch Streamlit app

### Manual Setup

1. **Install dependencies**

```bash
uv sync
```

2. **Start Docker Desktop** (make sure Docker is running)

3. **Start PostgreSQL database**

```bash
docker-compose up -d
```

4. **Run initial data collection** (This will fetch historical data and populate the database)

```bash
uv run python collector.py
```

5. **Start the scheduler** (Background process that collects data every 6 hours)

```bash
uv run python scheduler.py &
```

6. **Run the Streamlit app**

```bash
uv run streamlit run app.py
```

The app will be available at http://localhost:8501

## Project Structure

- `app.py` - Streamlit dashboard application
- `database.py` - SQLAlchemy models and database configuration
- `collector.py` - Data collection script that fetches from Near Intents API
- `scheduler.py` - Background scheduler that runs data collection every 6 hours
- `docker-compose.yml` - PostgreSQL database configuration
- `.env` - Environment variables (API key, database URL)

## Database

PostgreSQL runs in Docker on port 5432 with the following credentials:

- Host: localhost
- Port: 5432
- Database: stablecoins_analytics
- User: stablecoins
- Password: stablecoins123

## Data Collection

The collector fetches transaction data from Near Intents API and stores:

- Individual bridge transactions with slippage calculations
- Aggregated slippage cache for quick dashboard loading
- Automatic deduplication based on transaction hashes

## Configuration

Edit `.env` file to change:

- `API_KEY` - Your Near Intents API key
- `DATABASE_URL` - PostgreSQL connection string
- `API_URL` - Near Intents API endpoint

To change collection frequency, edit `scheduler.py` and modify the schedule interval.
