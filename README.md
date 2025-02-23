# Hackalytics

## Inspiration
We were inspired by portfolios that go all in on one industry or one type of stock and lose it all in a sudden flash. Many investors, especially new ones, tend to chase trends rather than diversify, leaving them vulnerable to market volatility. We wanted to create a tool that actively helps investors mitigate risk through strategic diversification.

## What it does
Our platform analyzes a user’s stock portfolio and recommends uncorrelated stocks for better diversification. Users upload their portfolio file, and we apply covariance analysis to suggest stable investments from different sectors. 

## How we built it
- Financial Modeling Prep & Stock APIs – For real-time stock data and news.
- Streamlit – To build a simple, interactive dashboard.
- Matplotlib, Pandas, NumPy, nltk, fmp, etc – For data processing, visualization, and covariance calculations.

## Challenges we ran into
- Integrating multiple data sources and ensuring accuracy.
- Optimizing covariance analysis to recommend genuinely unrelated stocks.
- Handling API limits while keeping analysis real-time.

## Accomplishments that we're proud of
- Built an intuitive dashboard with real-time stock recommendations.
- Implemented covariance analysis for precise diversification.

## What we learned
- Small errors in data can impact financial models significantly.
- Optimizing covariance analysis improves recommendation quality.

## What's next for no-YOLO portfolio
- Enhancing covariance analysis with more time intervals.
- Expanding support for bonds and ETFs.
- Automating portfolio tracking with brokerage integration.
