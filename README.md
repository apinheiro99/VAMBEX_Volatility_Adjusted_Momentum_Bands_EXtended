# VAMBEX — Volatility-Adjusted Momentum Bands eXtended
## Multi-Timeframe Deterministic Trading Model (1H + 4H + 1D)

VAMBEX is a **deterministic**, **multi-timeframe**, **practically oriented** quantitative model designed for short 7–10 day cycles.
It uses a combination of volatility, momentum, market regime, and cost-average (CA) adjustments to generate **5 operational levels**:

- **3 sell levels (Sell 1, Sell 2, Sell 3)**
- **2 buy levels (Buy 1, Buy 2)**

With dynamic recommended percentages for each level.

---

## 📌 Model Objectives

- **Maximize profit** in short cycles.
- **Minimize risk** by avoiding bad entry/exit zones.
- **Prevent capital from getting stuck** for weeks or months.
- **Quickly follow market shifts.**
- **Allow manual operation or future automation via API.**
- **Keep everything 100% mathematical and reproducible.**

---

## 🧠 How the model works

### Timeframes used

- **1H** → momentum, acceleration, normalized force  
- **4H** → volatility (ATR), anchor price, and structure of movement  
- **1D** → smoothing, regime confirmation, and macro stability

This fusion makes the model:

- responsive like scalping  
- stable like swing  
- and precise like an institutional bot

---

## 🔍 Mathematical Structure (Summary)

### Composite Volatility
Daily volatility is estimated as:

```
Vol = 0.5·ATR_4H + 0.3·σ1H + 0.2·σ1D
```

### Momentum (1H)
Fast component that adjusts the aggressiveness of the bands.

### Regime (4H/1D)
Automatic classification:

- bull  
- bear  
- sideways  

### Operational Levels

#### SELL:
```
Sell 1 = P0 + 0.6·Vol·K
Sell 2 = P0 + 1.0·Vol·K
Sell 3 = P0 + 1.5·Vol·K·(1 + 0.1·(2·ForceNorm - 1))
```
Where **K** is the correction based on cost average (CA).

#### BUY:
```
Buy 1 = P0 - 0.8·Vol
Buy 2 = P0 - 1.4·Vol
(if bear → Buy2 adjusted deeper)
```

---

## 📊 Dynamic Allocations (%)

### SELL (3 levels)
Depends on normalized momentum:
- strong momentum → more weight on Sell 3  
- weak momentum → more weight on Sell 1  

Always totals **100%**.

### BUY (2 levels)
Depends on the regime:
- bear → heavier weight on Buy 2  
- bull → heavier weight on Buy 1  

Always totals **100%**.

---

## 🏗 Project Structure

```
VAMBEX/
│── main.py
│── requirements.txt
│
└── core/
    ├── data_loader.py     ← reads Binance K-lines JSON
    ├── indicators.py      ← ATR, EMA, StdDev
    ├── momentum.py        ← momentum & acceleration
    ├── regime.py          ← regime & EMA20 slope
    ├── allocations.py     ← dynamic percentages
    └── model_vamb.py      ← mathematical core
```

---

## ▶ How to use

1. Download Binance K-line JSON files (1H, 4H, 1D)  
2. Edit `main.py`:
```
CA = 81.15846
PATH_1H = "LTCUSDT_1h_raw.txt"
PATH_4H = "LTCUSDT_4h_raw.txt"
PATH_1D = "LTCUSDT_1d_raw.txt"
```
3. Run:
```
python main.py
```

---

## 🖨 Example output

```
==============================
 VAMBEX Trading Levels
==============================
Regime: bull (EMA20 slope: 5.23%)
ATR 4H: 0.842135
Volatility: 1.945321
------------------------------
SELL LEVELS:
 Sell 1: 83.51   | 32%
 Sell 2: 85.10   | 30%
 Sell 3: 87.90   | 38%
------------------------------
BUY LEVELS:
 Buy 1: 79.45   | 64%
 Buy 2: 77.98   | 36%
==============================
```

---

## 🛠 Requirements

```
pandas>=2.0
numpy>=1.24
```

---

## 📜 License

Open Software License ("OSL") v 3.0

---

## 🧑‍💻 Author

Volatility Adjusted Momentum Bands EXtended.<br>
Andre Pinheiro

```
If you want to improve it, submit a PR or open Issues freely.
```
