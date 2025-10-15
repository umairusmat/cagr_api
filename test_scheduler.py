"""
Test the background scheduler
"""

import asyncio
import logging
from scheduler_fixed import CAGRBackgroundScheduler, load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scheduler():
    """Test the scheduler"""
    print("Testing CAGR Background Scheduler")
    print("=" * 50)
    
    # Load config
    config = load_config()
    print(f"Config: {config}")
    
    # Create scheduler
    scheduler = CAGRBackgroundScheduler(config)
    
    try:
        # Start scheduler
        print("Starting scheduler...")
        await scheduler.start()
        
        # Wait a bit to see if it starts properly
        print("Scheduler started, waiting 10 seconds...")
        await asyncio.sleep(10)
        
        # Test manual scrape
        print("Testing manual scrape...")
        await scheduler.trigger_manual_scrape()
        
        print("Manual scrape completed")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Stop scheduler
        print("Stopping scheduler...")
        await scheduler.stop()
        print("Scheduler stopped")

if __name__ == "__main__":
    asyncio.run(test_scheduler())
