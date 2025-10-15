"""
Update tickers file for Railway deployment
"""

def create_new_tickers_file():
    """Create a new tickers.csv file with AAPL, MSFT, TSLA, META"""
    
    # New tickers to scrape
    new_tickers = ["AAPL", "MSFT", "TSLA", "META"]
    
    # Create tickers.csv content
    csv_content = "ticker\n"
    for ticker in new_tickers:
        csv_content += f"{ticker}\n"
    
    # Write to file
    with open("input/tickers.csv", "w") as f:
        f.write(csv_content)
    
    print("SUCCESS: Created new tickers.csv with:")
    for ticker in new_tickers:
        print(f"  - {ticker}")
    
    print("\nTo deploy these tickers to Railway:")
    print("1. git add input/tickers.csv")
    print("2. git commit -m 'Update tickers to AAPL, MSFT, TSLA, META'")
    print("3. git push origin main")
    print("4. Wait for Railway to redeploy and scrape new tickers")

if __name__ == "__main__":
    create_new_tickers_file()
