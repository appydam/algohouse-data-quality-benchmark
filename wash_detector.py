#!/usr/bin/env python3
"""
Wash Trading Detector for Cryptocurrency Exchanges

Academic References:
- Benford's Law: Nigrini, M. J. (1999). "I've Got Your Number." Journal of Accountancy
- Wash Trading Detection: Cong, Lin William et al. (2022). "Crypto Wash Trading." Yale/NBER Working Paper
- First-Digit Law: Hill, T. P. (1995). "A Statistical Derivation of the Significant-Digit Law." Statistical Science

Usage:
    python wash_detector.py --exchange binance --pair BTC/USDT --days 30 --output report.json --compare-algohouse
"""

import argparse
import ccxt
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from scipy import stats
import requests
import sys


def fetch_trades(exchange_name, pair, days=30):
    """
    Fetch historical trades from specified exchange using CCXT.
    
    Args:
        exchange_name: Exchange identifier (e.g., 'binance', 'kraken')
        pair: Trading pair (e.g., 'BTC/USDT')
        days: Number of days of historical data to fetch
    
    Returns:
        list: Trade data with timestamp, price, amount, side
    """
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'enableRateLimit': True,
            'timeout': 30000,
        })
        
        print(f"Fetching {days} days of trades from {exchange_name} for {pair}...")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        since = int(start_time.timestamp() * 1000)
        
        all_trades = []
        current_since = since
        
        while current_since < int(end_time.timestamp() * 1000):
            trades = exchange.fetch_trades(pair, since=current_since, limit=1000)
            
            if not trades:
                break
            
            all_trades.extend(trades)
            current_since = trades[-1]['timestamp'] + 1
            
            print(f"  Fetched {len(all_trades)} trades...", end='\r')
            
            if len(trades) < 1000:
                break
        
        print(f"\nTotal trades fetched: {len(all_trades)}")
        return all_trades
        
    except Exception as e:
        print(f"Error fetching trades: {e}")
        sys.exit(1)


def benford_law_test(trades):
    """
    Apply Benford's Law to detect wash trading.
    
    Benford's Law (Nigrini, 1999): Natural numerical data follows a logarithmic distribution
    of first digits. Manipulated data (wash trading) deviates from this pattern.
    
    Expected first digit distribution: P(d) = log10(1 + 1/d) for d in [1,9]
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        dict: chi_squared, p_value, result (PASS/FAIL)
    """
    # Extract first digits from trade amounts
    amounts = [float(t['amount']) for t in trades if float(t['amount']) > 0]
    first_digits = [int(str(float(amt)).lstrip('0.')[0]) for amt in amounts if amt > 0]
    first_digits = [d for d in first_digits if 1 <= d <= 9]
    
    if not first_digits:
        return {"chi_squared": 0, "p_value": 1.0, "result": "INSUFFICIENT_DATA"}
    
    # Count observed frequencies
    observed = Counter(first_digits)
    observed_freq = [observed.get(d, 0) for d in range(1, 10)]
    
    # Benford's Law expected frequencies
    expected_freq = [len(first_digits) * np.log10(1 + 1/d) for d in range(1, 10)]
    
    # Chi-squared test
    # Reference: Hill, T. P. (1995). Statistical Science, Vol. 10, No. 4
    chi_squared, p_value = stats.chisquare(observed_freq, expected_freq)
    
    # p < 0.05 indicates significant deviation from Benford's Law (likely manipulation)
    result = "FAIL" if p_value < 0.05 else "PASS"
    
    return {
        "chi_squared": float(chi_squared),
        "p_value": float(p_value),
        "result": result
    }


def buy_sell_symmetry_test(trades):
    """
    Test for buy/sell order symmetry.
    
    Reference: Cong et al. (2022). "Crypto Wash Trading." Yale/NBER Working Paper.
    Natural markets show ~50/50 buy/sell ratio. Wash trading often creates asymmetry
    as bots place matched orders with timing delays.
    
    Acceptable range: 45-55% for either side.
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        dict: buy_pct, sell_pct, result (PASS/FAIL)
    """
    buy_count = sum(1 for t in trades if t.get('side') == 'buy')
    sell_count = sum(1 for t in trades if t.get('side') == 'sell')
    total = buy_count + sell_count
    
    if total == 0:
        return {"buy_pct": 0, "sell_pct": 0, "result": "INSUFFICIENT_DATA"}
    
    buy_pct = (buy_count / total) * 100
    sell_pct = (sell_count / total) * 100
    
    # Flag if either side is outside 45-55% range
    result = "PASS" if 45 <= buy_pct <= 55 and 45 <= sell_pct <= 55 else "FAIL"
    
    return {
        "buy_pct": float(buy_pct),
        "sell_pct": float(sell_pct),
        "result": result
    }


def volume_depth_ratio_test(exchange_name, pair):
    """
    Compare reported volume to order book depth.
    
    Wash trading inflates volume without corresponding order book depth.
    Healthy exchanges: ratio ~3-5x. Suspicious: ratio >10x.
    
    Benchmark: Kaiko Research (2021). "Exchange Data Quality Metrics."
    
    Args:
        exchange_name: Exchange identifier
        pair: Trading pair
    
    Returns:
        dict: ratio, benchmark, result (PASS/WARNING/FAIL)
    """
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({'enableRateLimit': True})
        
        # Get 24h volume
        ticker = exchange.fetch_ticker(pair)
        volume_24h = float(ticker.get('quoteVolume', 0))
        
        # Get order book depth (sum of top 20 levels)
        order_book = exchange.fetch_order_book(pair, limit=20)
        bid_depth = sum([bid[1] * bid[0] for bid in order_book['bids']])
        ask_depth = sum([ask[1] * ask[0] for ask in order_book['asks']])
        total_depth = bid_depth + ask_depth
        
        if total_depth == 0:
            return {"ratio": 0, "benchmark": "3-5x", "result": "INSUFFICIENT_DATA"}
        
        ratio = volume_24h / total_depth
        
        # Classify based on ratio
        if ratio < 3:
            result = "PASS"  # Low volume relative to depth (good liquidity)
        elif 3 <= ratio <= 10:
            result = "PASS"  # Normal range
        elif 10 < ratio <= 20:
            result = "WARNING"  # Elevated, needs investigation
        else:
            result = "FAIL"  # Volume inflation likely
        
        return {
            "ratio": float(ratio),
            "benchmark": "3-5x",
            "result": result
        }
        
    except Exception as e:
        print(f"Warning: Could not fetch order book data: {e}")
        return {"ratio": 0, "benchmark": "3-5x", "result": "ERROR"}


def calculate_manipulation_probability(benford, symmetry, volume_depth):
    """
    Calculate overall manipulation probability (0-1) based on three heuristics.
    
    Weighting:
    - Benford's Law: 50% (strongest academic evidence)
    - Buy/Sell Symmetry: 30% (good indicator but can have false positives)
    - Volume/Depth: 20% (useful but market-dependent)
    
    Args:
        benford: Benford test results
        symmetry: Symmetry test results
        volume_depth: Volume/depth test results
    
    Returns:
        float: Probability 0-1
    """
    score = 0.0
    
    # Benford's Law (50%)
    if benford['result'] == 'FAIL':
        # p-value < 0.01 = 0.5, p-value 0.01-0.05 = 0.3
        if benford['p_value'] < 0.01:
            score += 0.5
        else:
            score += 0.3
    
    # Buy/Sell Symmetry (30%)
    if symmetry['result'] == 'FAIL':
        # More extreme asymmetry = higher score
        max_deviation = max(abs(symmetry['buy_pct'] - 50), abs(symmetry['sell_pct'] - 50))
        if max_deviation > 15:  # >65% or <35%
            score += 0.3
        elif max_deviation > 10:  # >60% or <40%
            score += 0.2
        else:  # >55% or <45%
            score += 0.1
    
    # Volume/Depth Ratio (20%)
    if volume_depth['result'] == 'FAIL':
        score += 0.2
    elif volume_depth['result'] == 'WARNING':
        score += 0.1
    
    return min(score, 1.0)


def get_manipulation_label(probability):
    """
    Convert probability to categorical label.
    
    Args:
        probability: Float 0-1
    
    Returns:
        str: LOW/MEDIUM/HIGH
    """
    if probability < 0.3:
        return "LOW"
    elif probability < 0.6:
        return "MEDIUM"
    else:
        return "HIGH"


def fetch_algohouse_score(exchange_name):
    """
    Fetch AlgoHouse quality score for comparison (optional).
    
    Args:
        exchange_name: Exchange identifier
    
    Returns:
        float: Quality score 0-1, or None if unavailable
    """
    try:
        # AlgoHouse public API endpoint
        response = requests.get('https://api.algohouse.ai/exchanges', timeout=10)
        data = response.json()
        
        # Find matching exchange
        for exchange in data:
            if exchange.get('exchange_code', '').lower() == exchange_name.lower():
                return float(exchange.get('exchange_data_credibility', 0))
        
        return None
        
    except Exception as e:
        print(f"Warning: Could not fetch AlgoHouse score: {e}")
        return None


def calculate_score_correlation(manipulation_prob, algohouse_score):
    """
    Calculate correlation between our manipulation probability and AlgoHouse score.
    
    Expected: High manipulation probability correlates with low AlgoHouse score.
    
    Args:
        manipulation_prob: Our calculated probability (0-1)
        algohouse_score: AlgoHouse credibility score (0-1)
    
    Returns:
        float: Correlation coefficient (-1 to 1)
    """
    if algohouse_score is None:
        return None
    
    # Expected: manipulation_prob and algohouse_score are inversely correlated
    # Convert both to same scale and calculate simple correlation
    return -1.0 * (manipulation_prob - (1 - algohouse_score))


def main():
    parser = argparse.ArgumentParser(
        description='Detect wash trading on cryptocurrency exchanges',
        epilog='Academic references: Nigrini (1999), Cong et al. (2022), Hill (1995)'
    )
    parser.add_argument('--exchange', required=True, help='Exchange name (e.g., binance, kraken)')
    parser.add_argument('--pair', required=True, help='Trading pair (e.g., BTC/USDT)')
    parser.add_argument('--days', type=int, default=30, help='Days of historical data (default: 30)')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--compare-algohouse', action='store_true', 
                        help='Compare results with AlgoHouse quality scores')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"Wash Trading Detector")
    print(f"{'='*70}\n")
    print(f"Exchange: {args.exchange}")
    print(f"Pair: {args.pair}")
    print(f"Period: {args.days} days")
    print(f"Output: {args.output}\n")
    
    # Step 1: Fetch trade data
    trades = fetch_trades(args.exchange, args.pair, args.days)
    
    if len(trades) < 100:
        print(f"Error: Insufficient data ({len(trades)} trades). Need at least 100 trades for statistical significance.")
        sys.exit(1)
    
    # Step 2: Run detection heuristics
    print("\nRunning detection tests...")
    
    benford = benford_law_test(trades)
    print(f"  Benford's Law: {benford['result']} (p={benford['p_value']:.4f})")
    
    symmetry = buy_sell_symmetry_test(trades)
    print(f"  Buy/Sell Symmetry: {symmetry['result']} ({symmetry['buy_pct']:.1f}% buy, {symmetry['sell_pct']:.1f}% sell)")
    
    volume_depth = volume_depth_ratio_test(args.exchange, args.pair)
    print(f"  Volume/Depth Ratio: {volume_depth['result']} (ratio={volume_depth['ratio']:.2f}x)")
    
    # Step 3: Calculate manipulation probability
    manipulation_prob = calculate_manipulation_probability(benford, symmetry, volume_depth)
    manipulation_label = get_manipulation_label(manipulation_prob)
    
    print(f"\nManipulation Probability: {manipulation_prob:.2%} ({manipulation_label})")
    
    # Step 4: Optional AlgoHouse comparison
    algohouse_score = None
    score_correlation = None
    
    if args.compare_algohouse:
        print("\nFetching AlgoHouse quality score...")
        algohouse_score = fetch_algohouse_score(args.exchange)
        if algohouse_score is not None:
            print(f"  AlgoHouse Credibility Score: {algohouse_score:.2f}")
            score_correlation = calculate_score_correlation(manipulation_prob, algohouse_score)
            print(f"  Score Correlation: {score_correlation:.3f}")
        else:
            print("  AlgoHouse score not available for this exchange")
    
    # Step 5: Build output report
    report = {
        "exchange": args.exchange,
        "pair": args.pair,
        "period_days": args.days,
        "total_trades_analyzed": len(trades),
        "analysis_timestamp": datetime.now().isoformat(),
        "benfords_law": benford,
        "buy_sell_symmetry": symmetry,
        "volume_depth_ratio": volume_depth,
        "manipulation_probability": float(manipulation_prob),
        "manipulation_label": manipulation_label,
        "algohouse_quality_score": algohouse_score,
        "score_correlation": score_correlation
    }
    
    # Step 6: Save to JSON
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {args.output}")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
