# AlgoHouse Data Quality Benchmark

**Comprehensive data quality analysis for crypto exchanges** — detect wash trading, validate order books, and score data reliability.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- No API keys required (all data sources are public)

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/appydam/algohouse-data-quality-benchmark.git
cd algohouse-data-quality-benchmark

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo (shows sample output in 4 seconds)
python3 demo_run.py

# 4. OR run the full benchmark with live data (5-8 minutes)
jupyter notebook benchmark.ipynb
```

### Running the Full Benchmark

1. **Open Jupyter:**
   ```bash
   jupyter notebook benchmark.ipynb
   ```

2. **Run all cells sequentially** (Cell → Run All)

3. **What it does:**
   - ✅ Fetches 1,000+ trades per exchange (10 exchanges)
   - ✅ Runs 5 quality measurements
   - ✅ Calculates composite trust scores (0-100)
   - ✅ Generates interactive visualizations

4. **Output files:**
   - `heatmap.html` - Quality metrics heatmap
   - `scatter.html` - Trust vs. volume scatter plot
   - `barchart.html` - Ranked trust scores bar chart

**Total runtime:** ~5-8 minutes (depending on exchange API latency)

### Quick Demo (No APIs, 4 seconds)

Want to see sample output instantly? Run the demo script:

```bash
python3 demo_run.py
```

This generates sample output showing how the benchmark works without hitting live APIs.

---

## 📊 Sample Results

Based on demo run (actual results will vary with live data):

### Top 3 Exchanges by Trust Score:
1. **Binance** - 94.2/100 (Grade: A+)
2. **Coinbase** - 92.1/100 (Grade: A+)
3. **Kraken** - 89.5/100 (Grade: A)

### Exchanges Flagged for Wash Trading (Benford's Law):
- ⚠️ **Huobi** - FAIL (p-value: 0.0300)
- ⚠️ **MEXC** - FAIL (p-value: 0.0100)

### Execution Time:
- **Demo:** 4 seconds
- **Live benchmark:** 5-8 minutes (depends on API latency)

See full demo output in [`demo_output.txt`](demo_output.txt)

---

## 📊 What It Measures

### 1. **Tick Completeness**
Detects data gaps > 1 second that corrupt backtests.

### 2. **Order Book Depth Accuracy**
Validates bid-ask spread reasonableness and depth at 0.1% price levels (institutional standard).

### 3. **Benford's Law Wash Trading Test** 🔬
Applies Benford's Law to detect artificial volume. 

**Academic Sources:**
- Nigrini, M. (1999). "I've Got Your Number." *Journal of Accountancy*
- Cong et al. (2022). "Crypto Wash Trading." *Yale/NBER Working Paper*

Natural trade distributions follow logarithmic first-digit patterns. Wash trading violates this.

- **p-value < 0.01:** FAIL (high manipulation risk)
- **p-value < 0.05:** SUSPICIOUS (moderate risk)
- **p-value ≥ 0.05:** PASS (natural distribution)

### 4. **Buy/Sell Symmetry**
Flags exchanges with >55% buy or sell imbalance (natural markets are ~50/50).

### 5. **Normalization Consistency**
Checks timestamp quality and precision (100ms alignment).

---

## 🎯 Composite Trust Score

Each exchange receives a **Data Trust Score (0-100)** based on weighted components:

| Component | Weight | Why It Matters |
|-----------|--------|----------------|
| **Benford's Law** | 30% | Wash trading is the #1 risk for quant backtests |
| **Order Book Accuracy** | 25% | Critical for execution quality |
| **Tick Completeness** | 20% | Data gaps destroy backtest validity |
| **Buy/Sell Symmetry** | 15% | Market balance indicator |
| **Normalization** | 10% | Timestamp quality for tick-level analysis |

**Grading:**
- **90-100:** A+ (institutional-grade)
- **80-89:** A (excellent)
- **70-79:** B (good)
- **60-69:** C (acceptable)
- **50-59:** D (poor)
- **<50:** F (unreliable)

---

## 📈 Exchanges Tested

Default configuration tests **10 major exchanges** for `BTC/USDT`:

1. Binance
2. Kraken
3. Coinbase
4. Bybit
5. KuCoin
6. Gate.io
7. OKX
8. Huobi
9. MEXC
10. Bitget

**Customize:** Edit `EXCHANGES_TO_TEST` in Section 1 of the notebook.

---

## 📊 Visualizations

The benchmark generates 3 interactive **Plotly dark-mode charts**:

1. **Heatmap** (`heatmap.html`) — Quality metrics per exchange
2. **Scatter Plot** (`scatter.html`) — Trust score vs. 24h volume
3. **Bar Chart** (`barchart.html`) — Ranked trust scores

All charts export as standalone HTML files (no internet required).

---

## 🏢 Dual-Use for Sales

This benchmark is designed for **two distinct use cases**:

### Use Case #1: Quant Traders (Public Repo)
- Clone and run to validate exchange data quality before backtesting
- Compare AlgoHouse scores with CCXT raw data
- Detect wash trading on unregulated exchanges

### Use Case #2: Enterprise Sales (Solidus Labs-Style Motion)
This same code powers a **compliance narrative** for institutional clients:

**Sales Pitch:**
> "We tested 10 exchanges using academic wash trading detection (Benford's Law). 3 exchanges FAILED. Are you trading on them?"

**GTM Strategy:**
- Publish public benchmark results on Reddit (r/algotrading)
- Position AlgoHouse as the "truth-teller" in a space full of fake volume
- Convert quant traders into enterprise leads (hedge funds, prop firms)

**Expected Flow:**
1. Quant sees benchmark results on r/algotrading (1,000+ upvotes)
2. Clones repo and runs against their exchanges
3. Discovers their current exchange has poor trust score
4. Upgrades to AlgoHouse for verified clean data
5. CTO at their fund requests enterprise demo

This is the **same playbook** Solidus Labs used to land Coinbase, Kraken, and Binance as clients.

---

## 📋 Tracking Issues

Development tracked via GitHub Issues (L1.1-L1.5):
- [#1 - L1.1: Setup & Dependencies](https://github.com/appydam/algohouse-data-quality-benchmark/issues/1) ✅
- [#2 - L1.2: Data Collection](https://github.com/appydam/algohouse-data-quality-benchmark/issues/2) ✅
- [#3 - L1.3: Five Quality Measurements](https://github.com/appydam/algohouse-data-quality-benchmark/issues/3) ✅
- [#4 - L1.4: Composite Trust Score](https://github.com/appydam/algohouse-data-quality-benchmark/issues/4) ✅
- [#5 - L1.5: Plotly Visualizations](https://github.com/appydam/algohouse-data-quality-benchmark/issues/5) ✅

---

## 🔧 Requirements

**Python:** 3.8+

**Dependencies:**
```
ccxt>=4.0.0
pandas>=1.3.0
scipy>=1.7.0
statsmodels>=0.13.0
plotly>=5.0.0
numpy>=1.21.0
requests>=2.26.0
jupyter>=1.0.0
notebook>=6.4.0
```

Install via:
```bash
pip install -r requirements.txt
```

**No API keys required** - all data sources (CCXT, AlgoHouse API, Coin Metrics Community API) are publicly accessible.

---

## 📚 Data Sources

1. **CCXT** — Real-time trade data, order books, OHLCV
2. **AlgoHouse API** — Exchange quality scores (`https://api.algohouse.com/v1/exchanges`)
3. **Coin Metrics Community API** — Reference market data (free tier)

---

## 🧪 Run Tests

The notebook is self-contained. Simply run all cells in sequence:

1. **Section 1:** Setup (install dependencies)
2. **Section 2:** Data collection (CCXT + APIs)
3. **Section 3:** Run 5 quality measurements
4. **Section 4:** Calculate composite trust scores
5. **Section 5:** Generate visualizations

**No API keys required** — all data sources are public.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! To add a new quality metric:

1. Add measurement function in Section 3
2. Update trust score calculation in Section 4 with new weight
3. Add visualization if needed in Section 5
4. Submit PR with academic source citation

---

## 🎓 Academic References

1. **Benford's Law:**
   - Nigrini, M. J. (1999). "I've Got Your Number." *Journal of Accountancy*, 187(5), 79-83.
   - Hill, T. P. (1995). "A Statistical Derivation of the Significant-Digit Law." *Statistical Science*, 10(4), 354-363.

2. **Crypto Wash Trading:**
   - Cong, L. W., et al. (2022). "Crypto Wash Trading." *NBER Working Paper No. 30783*.
   - Victor, F., & Hagemann, T. (2019). "Cryptocurrency Pump-and-Dump Schemes." *arXiv:2102.07001*.

3. **Market Microstructure:**
   - Hasbrouck, J. (2007). *Empirical Market Microstructure*. Oxford University Press.

---

## 🚨 Disclaimer

This benchmark is for **research and educational purposes only**. 

- **Not financial advice:** Do not use as the sole basis for trading decisions.
- **Accuracy:** Results depend on API availability and may vary over time.
- **Exchange risks:** Past data quality does not guarantee future quality.

Always perform independent due diligence before selecting an exchange.

---

## 🔗 Links

- **AlgoHouse:** https://algohouse.com
- **GitHub Issues:** https://github.com/appydam/algohouse-data-quality-benchmark/issues
- **CCXT Documentation:** https://docs.ccxt.com

---

**Built by:** Forge (AI Engineering Agent)  
**For:** AlgoHouse Data Quality Initiative  
**Contact:** [@arpitdhamija](https://github.com/arpitdhamija)
