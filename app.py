import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF
from supabase import create_client, Client

# set_page_config must be the first Streamlit command
st.set_page_config(page_title="Portfolio Pro", layout="centered")

# Hide the "Built with Streamlit" footer and main menu hamburger
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 1. SUPABASE CONNECTION (created once, reused across reruns/users) ---
@st.cache_resource
def get_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = get_client()
except Exception:
    st.error("Missing Supabase Secrets! Please ensure SUPABASE_URL and SUPABASE_KEY are in your secrets.")
    st.stop()  # without this the app would crash later with a confusing NameError

# --- 2. FULL COMPANY DATABASE ---
NIFTY_50_DATA = {
    "ADANIENT.NS": "Adani Enterprises", "ADANIPORTS.NS": "Adani Ports", "APOLLOHOSP.NS": "Apollo Hospitals",
    "ASIANPAINT.NS": "Asian Paints", "AXISBANK.NS": "Axis Bank", "BAJAJ-AUTO.NS": "Bajaj Auto",
    "BAJAJFINSV.NS": "Bajaj Finserv", "BAJFINANCE.NS": "Bajaj Finance", "BEL.NS": "Bharat Electronics",
    "BPCL.NS": "Bharat Petroleum", "BHARTIARTL.NS": "Bharti Airtel", "BRITANNIA.NS": "Britannia Industries",
    "CIPLA.NS": "Cipla", "COALINDIA.NS": "Coal India", "DIVISLAB.NS": "Divi's Laboratories",
    "DRREDDY.NS": "Dr. Reddy's", "EICHERMOT.NS": "Eicher Motors", "GRASIM.NS": "Grasim Industries",
    "HCLTECH.NS": "HCLTech", "HDFCBANK.NS": "HDFC Bank", "HDFCLIFE.NS": "HDFC Life",
    "HEROMOTOCO.NS": "Hero MotoCorp", "HINDALCO.NS": "Hindalco", "HINDUNILVR.NS": "Hindustan Unilever",
    "ICICIBANK.NS": "ICICI Bank", "ITC.NS": "ITC Ltd", "INDUSINDBK.NS": "IndusInd Bank",
    "INFY.NS": "Infosys", "JSWSTEEL.NS": "JSW Steel", "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "LTIM.NS": "LTIMindtree", "LT.NS": "Larsen & Toubro", "M&M.NS": "Mahindra & Mahindra",
    "MARUTI.NS": "Maruti Suzuki", "NTPC.NS": "NTPC", "NESTLEIND.NS": "Nestle India",
    "ONGC.NS": "ONGC", "POWERGRID.NS": "Power Grid", "RELIANCE.NS": "Reliance Industries",
    "SBILIFE.NS": "SBI Life", "SBIN.NS": "State Bank of India", "SUNPHARMA.NS": "Sun Pharma",
    "TATACONSUM.NS": "Tata Consumer", "TATASTEEL.NS": "Tata Steel",
    "TCS.NS": "TCS", "TECHM.NS": "Tech Mahindra", "TITAN.NS": "Titan Company",
    "ULTRACEMCO.NS": "UltraTech Cement", "WIPRO.NS": "Wipro"
}

SP_500_DATA = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta Platforms",
    "GOOGL": "Alphabet (A)", "GOOG": "Alphabet (C)", "BRK-B": "Berkshire Hathaway", "LLY": "Eli Lilly",
    "AVGO": "Broadcom", "JPM": "JPMorgan Chase", "TSLA": "Tesla", "WMT": "Walmart", "XOM": "Exxon Mobil",
    "UNH": "UnitedHealth", "MA": "Mastercard", "PG": "Procter & Gamble", "V": "Visa", "ORCL": "Oracle",
    "COST": "Costco", "HD": "Home Depot", "ABBV": "AbbVie", "JNJ": "Johnson & Johnson", "MRK": "Merck",
    "AMD": "AMD", "NFLX": "Netflix", "CRM": "Salesforce", "BAC": "Bank of America", "ADBE": "Adobe",
    "KO": "Coca-Cola", "PEP": "PepsiCo", "LIN": "Linde", "TMO": "Thermo Fisher", "WFC": "Wells Fargo",
    "CSCO": "Cisco", "ACN": "Accenture", "DIS": "Disney", "PM": "Philip Morris", "ABT": "Abbott Labs",
    "INTU": "Intuit", "DHR": "Danaher", "CAT": "Caterpillar", "GE": "General Electric", "VZ": "Verizon",
    "AMAT": "Applied Materials", "INTC": "Intel", "IBM": "IBM", "UBER": "Uber", "PFE": "Pfizer",
    "AMGN": "Amgen", "NOW": "ServiceNow", "TXN": "Texas Instruments", "NEE": "NextEra Energy", "GS": "Goldman Sachs",
    "ISRG": "Intuitive Surgical", "LOW": "Lowe's", "CMCSA": "Comcast", "AXP": "American Express", "MS": "Morgan Stanley",
    "SPGI": "S&P Global", "HON": "Honeywell", "ELV": "Elevance Health", "RTX": "Raytheon", "COP": "ConocoPhillips",
    "BKNG": "Booking Holdings", "PLD": "Prologis", "SYK": "Stryker", "TJX": "TJX Companies", "VRTX": "Vertex Pharma",
    "ETN": "Eaton", "C": "Citigroup", "REGN": "Regeneron", "LRCX": "Lam Research", "BLK": "BlackRock",
    "ADI": "Analog Devices", "MDLZ": "Mondelez", "BA": "Boeing", "CB": "Chubb", "BSX": "Boston Scientific",
    "DE": "Deere & Co", "CI": "Cigna", "MU": "Micron", "T": "AT&T", "MMC": "Marsh McLennan",
    "AMT": "American Tower", "LMT": "Lockheed Martin", "PANW": "Palo Alto Networks", "UNP": "Union Pacific",
    "GILD": "Gilead Sciences", "ADP": "ADP", "SCHW": "Charles Schwab", "FI": "Fiserv", "PGR": "Progressive",
    "MDT": "Medtronic", "CDNS": "Cadence Design", "VLO": "Valero", "CVS": "CVS Health", "MAR": "Marriott",
    "HCA": "HCA Healthcare", "ORLY": "O'Reilly", "SNPS": "Synopsys", "EOG": "EOG Resources", "AIG": "AIG",
    "ZTS": "Zoetis", "KLAC": "KLA Corp", "SLB": "Schlumberger", "MCO": "Moody's", "FDX": "FedEx",
    "APH": "Amphenol", "ECL": "Ecolab", "WM": "Waste Management", "ADSK": "Autodesk", "GD": "General Dynamics",
    "ITW": "Illinois Tool Works", "USB": "US Bancorp", "ICE": "Intercontinental Exchange", "CMG": "Chipotle",
    "PH": "Parker-Hannifin", "MCK": "McKesson", "F": "Ford", "GM": "GM", "DASH": "DoorDash", "EMR": "Emerson Electric",
    "NSC": "Norfolk Southern", "PCAR": "PACCAR", "ROST": "Ross Stores", "WELL": "Welltower", "MSI": "Motorola",
    "PSX": "Phillips 66", "MPC": "Marathon Petroleum", "CPRT": "Copart", "DXCM": "Dexcom", "AJG": "Arthur J. Gallagher",
    "HLT": "Hilton", "CSX": "CSX Corp", "IT": "Gartner", "CARR": "Carrier", "CTAS": "Cintas", "AON": "Aon",
    "TGT": "Target", "NOC": "Northrop Grumman", "ANET": "Arista Networks", "D": "Dominion Energy", "TT": "Trane",
    "ROP": "Roper", "TDG": "TransDigm", "EW": "Edwards Lifesciences", "CMI": "Cummins", "MET": "MetLife",
    "WMB": "Williams Cos", "ADM": "Archer-Daniels-Midland", "DELL": "Dell", "O": "Realty Income", "BKR": "Baker Hughes",
    "KMB": "Kimberly-Clark", "OKE": "ONEOK", "DLR": "Digital Realty", "COR": "Cencora", "A": "Agilent",
    "GWW": "Grainger", "PAYX": "Paychex", "TEL": "TE Connectivity", "JCI": "Johnson Controls", "IDXX": "IDEXX Labs",
    "MSCI": "MSCI", "IQV": "IQVIA", "LULU": "Lululemon", "KVUE": "Kenvue", "TRV": "Travelers", "STX": "Seagate",
    "FTNT": "Fortinet", "KDP": "Keurig Dr Pepper", "MCHP": "Microchip", "PRU": "Prudential", "CTSH": "Cognizant",
    "AEP": "American Electric Power", "GEV": "GE Vernova", "SYY": "Sysco", "CNC": "Centene", "KR": "Kroger",
    "OTIS": "Otis Worldwide", "FICO": "Fair Isaac", "FIS": "Fidelity National", "HWM": "Howmet", "EXC": "Exelon",
    "EFX": "Equifax", "BBY": "Best Buy", "AZO": "AutoZone", "XEL": "Xcel Energy", "ED": "Consolidated Edison",
    "FAST": "Fastenal", "DFS": "Discover", "STT": "State Street", "CDW": "CDW Corp", "LHX": "L3Harris",
    "KEYS": "Keysight", "MTB": "M&T Bank", "GLW": "Corning", "WBD": "Warner Bros. Discovery", "WES": "Western Midstream",
    "VICI": "VICI Properties", "GPN": "Global Payments", "WY": "Weyerhaeuser", "DLTR": "Dollar Tree",
    "HPQ": "HP Inc.", "CHD": "Church & Dwight", "WTW": "WTW", "CBRE": "CBRE Group", "ULTA": "Ulta Beauty",
    "VMC": "Vulcan Materials", "ODFL": "Old Dominion", "DAL": "Delta Air Lines", "EBAY": "eBay",
    "TROW": "T. Rowe Price", "AWK": "American Water", "LYB": "LyondellBasell", "ARE": "Alexandria RE",
    "IR": "Ingersoll Rand", "TSN": "Tyson Foods", "GEN": "Gen Digital", "ZBH": "Zimmer Biomet",
    "ALGN": "Align Technology", "FITB": "Fifth Third", "BRO": "Brown & Brown", "MGM": "MGM Resorts",
    "LUV": "Southwest Airlines", "HBAN": "Huntington", "ESS": "Essex Property", "MAA": "Mid-America Apartment",
    "RVTY": "Revvity", "SWK": "Stanley Black & Decker", "EXPE": "Expedia", "STLD": "Steel Dynamics",
    "TER": "Teradyne", "WDC": "Western Digital", "RF": "Regions Financial", "INVH": "Invitation Homes",
    "VTR": "Ventas", "PKG": "Packaging Corp", "CNP": "CenterPoint", "CLX": "Clorox", "DG": "Dollar General",
    "POOL": "Pool Corp", "DPZ": "Domino's", "DRI": "Darden Restaurants", "MKC": "McCormick", "STE": "STERIS",
    "WAT": "Waters Corp", "KEY": "KeyCorp", "CAH": "Cardinal Health", "EG": "Everest Group", "HES": "Hess Corp",
    "DVN": "Devon Energy", "DOV": "Dover Corp", "MTCH": "Match Group", "MRO": "Marathon Oil", "JBHT": "JB Hunt",
    "BALL": "Ball Corp", "AMCR": "Amcor", "TYL": "Tyler Tech", "EPAM": "EPAM Systems", "FSLR": "First Solar",
    "FMC": "FMC Corp", "PARA": "Paramount", "QRVO": "Qorvo", "ENPH": "Enphase Energy", "HAS": "Hasbro",
    "CHTR": "Charter Comm", "BBWI": "Bath & Body Works", "MHK": "Mohawk Industries", "GNRC": "Generac",
    "AIZ": "Assurant", "L": "Loews Corp", "IVZ": "Invesco", "KMX": "CarMax", "MOS": "Mosaic", "APA": "APA Corp",
    "AES": "AES Corp", "CPB": "Campbell Soup", "HRL": "Hormel", "BEN": "Franklin Resources", "TPR": "Tapestry",
    "NWS": "News Corp (B)", "NWSA": "News Corp (A)", "VNO": "Vornado", "WBA": "Walgreens", "CZR": "Caesars",
    "RL": "Ralph Lauren", "PPL": "PPL Corp", "PAYC": "Paycom", "JKHY": "Jack Henry", "JNPR": "Juniper Networks",
    "SJM": "JM Smucker", "ALB": "Albemarle", "PNW": "Pinnacle West", "FRT": "Federal Realty", "XRAY": "Dentsply Sirona",
    "EMN": "Eastman Chemical", "IP": "International Paper", "SWKS": "Skyworks", "WHR": "Whirlpool",
    "TECH": "Bio-Techne", "BIO": "Bio-Rad", "UHS": "Universal Health", "HSIC": "Henry Schein", "CRL": "Charles River",
    "DXC": "DXC Tech", "TFX": "Teleflex", "MTD": "Mettler Toledo", "ZBRA": "Zebra Tech", "HII": "Huntington Ingalls",
    "LNT": "Alliant Energy", "NI": "NiSource", "ATO": "Atmos Energy", "NRG": "NRG Energy", "VST": "Vistra",
    "SRE": "Sempra", "WEC": "WEC Energy", "ES": "Eversource", "DTE": "DTE Energy", "ETR": "Entergy",
    "FE": "FirstEnergy", "AEE": "Ameren", "CMS": "CMS Energy", "EVRG": "Evergy", "AVB": "AvalonBay",
    "EQR": "Equity Residential", "PSA": "Public Storage", "BXP": "Boston Properties", "KIM": "Kimco Realty",
    "REG": "Regency Centers", "UDR": "UDR Inc.", "HST": "Host Hotels"
}

NIFTY_MAP = {f"{k} ({v})": k for k, v in NIFTY_50_DATA.items()}
SP_MAP = {f"{k} ({v})": k for k, v in SP_500_DATA.items()}

# --- 3. DATA ENGINE ---
PAGE_SIZE = 1000          # Supabase returns at most ~1000 rows per request by default
N_PORTFOLIOS = 20_000     # vectorised, so far more paths than before at a fraction of the time


@st.cache_data(ttl=3600, show_spinner="Loading prices...")
def _fetch_prices(tickers: tuple, start: str, end: str) -> pd.DataFrame:
    """Download price rows page by page, then pivot to date x ticker.
    Exceptions are NOT caught here so a temporary failure is never cached."""
    rows, offset = [], 0
    while True:
        resp = (
            supabase.table("stock_history")
            .select("date, ticker, price")
            .in_("ticker", list(tickers))
            .gte("date", start)
            .lte("date", end)
            .order("date")
            .order("ticker")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        rows.extend(resp.data)
        if len(resp.data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame()
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset=["date", "ticker"], keep="last")
    return df.pivot(index="date", columns="ticker", values="price").ffill().bfill()


def get_supabase_data(tickers, start, end) -> pd.DataFrame:
    try:
        return _fetch_prices(tuple(sorted(tickers)), start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return pd.DataFrame()


# --- 3b. MONTE CARLO (fully vectorised) ---
def best_sharpe_weights(log_ret: pd.DataFrame, n: int = N_PORTFOLIOS) -> np.ndarray:
    mu = log_ret.mean().values * 252            # computed ONCE, not 2,000 times
    cov = log_ret.cov().values * 252
    w = np.random.default_rng().dirichlet(np.ones(len(mu)), n)   # n random portfolios, rows sum to 1
    rets = w @ mu
    vols = np.sqrt(np.einsum("ij,jk,ik->i", w, cov, w))
    return w[(rets / vols).argmax()]


def growth_vs_benchmark(prices: pd.DataFrame, tickers, weights, benchmark):
    """Cumulative growth of the weighted portfolio and of the benchmark."""
    if benchmark not in prices.columns:
        return None
    tickers = [t for t in tickers if t in prices.columns]
    if len(tickers) < 2:
        return None
    stocks = prices[tickers].dropna()
    if len(stocks) < 2:
        return None
    port = (1 + stocks.pct_change().dropna().dot(weights)).cumprod()
    bench = (1 + prices[benchmark].dropna().pct_change().dropna()).cumprod()
    return port, bench


def growth_chart(port, bench, bench_name, height, port_style, bench_style, port_name="Portfolio"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=port.index, y=port, name=port_name, line=port_style))
    fig.add_trace(go.Scatter(x=bench.index, y=bench, name=bench_name, line=bench_style))
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
    )
    return fig


# --- 4. PDF ENGINE ---
def create_pdf(market, stocks, weights, final_ret, start, end):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f'{market} Analysis Report'.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Analysis Range: {start} to {end}", ln=True)
    pdf.ln(5)
    for s, w in zip(stocks, weights):
        clean_s = s.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 8, f"- {clean_s}: {w*100:.2f}%", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Portfolio Growth: {final_ret:.2f}%", ln=True)
    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)   # works with fpdf and fpdf2


# --- 6. INPUTS ---
st.title("📂 Portfolio Pro")
st.markdown("---")

market_choice = st.selectbox("Select Market", ["Nifty 50 (India)", "S&P 500 (USA)"])

if "Nifty" in market_choice:
    current_map, market_name, benchmark_ticker = NIFTY_MAP, "Nifty 50", "^NSEI"
else:
    current_map, market_name, benchmark_ticker = SP_MAP, "S&P 500", "^GSPC"

selected_labels = st.multiselect(
    "Select 5-10 Stocks",
    options=list(current_map.keys()),
    placeholder="Search tickers...",
)
selected_tickers = [current_map[label] for label in selected_labels]

col_date1, col_date2 = st.columns(2)
with col_date1:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365))
with col_date2:
    end_date = st.date_input("End Date", datetime.today())

st.markdown("---")

# --- 7. ANALYSIS & DISPLAY ---
if not (5 <= len(selected_tickers) <= 10):
    st.session_state.pop("results", None)
    st.info("💡 Select 5 to 10 stocks above to begin the calculation.")
    st.stop()

if start_date >= end_date:
    st.error("Start Date must be before End Date.")
    st.stop()

all_required = selected_tickers + [benchmark_ticker]
data_combined = get_supabase_data(all_required, start_date, end_date)

if data_combined.empty or benchmark_ticker not in data_combined.columns:
    st.error("Not enough historical data found for these stocks.")
    st.stop()

available_tickers = [t for t in selected_tickers if t in data_combined.columns]
if len(available_tickers) < 2:
    st.error("Not enough historical data found for these stocks.")
    st.stop()

missing = [t for t in selected_tickers if t not in available_tickers]
if missing:
    st.warning(f"No price data found for: {', '.join(missing)}. They were skipped.")

data = data_combined[available_tickers].dropna()
returns_pct = data.pct_change().dropna()
log_ret = np.log(data / data.shift(1)).dropna()

# --- Risk metrics ---
st.subheader("🧮 Asset Risk Metrics Matrix")
variance_series = log_ret.var() * 252
st.markdown("**Annualized Asset Variance Summary:**")
var_cols = st.columns(len(available_tickers))
for col, ticker in zip(var_cols, available_tickers):
    col.metric(label=ticker.replace(".NS", ""), value=f"{variance_series[ticker]:.4f}")

fig_corr = px.imshow(
    returns_pct.corr(),
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="RdBu_r",
    range_color=[-1, 1],
    labels=dict(color="Correlation"),
)
fig_corr.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Tickers", yaxis_title="Tickers")
st.plotly_chart(fig_corr, width="stretch", config={'displayModeBar': False})

st.markdown("---")

# --- Simulation ---
st.subheader("🚀 Run Allocation Engine")
st.markdown("Click below to pass these correlation and variance parameters through the Monte Carlo pipeline.")

# Identifies the current inputs, so old results are never shown against new selections
signature = (market_name, tuple(available_tickers), start_date, end_date)

if st.button("Run Portfolio Simulation", type="primary", width="stretch"):
    with st.spinner(f"⏳ Running {N_PORTFOLIOS:,} Monte Carlo paths..."):
        opt_weights = best_sharpe_weights(log_ret)
        port = growth_vs_benchmark(data_combined, available_tickers, opt_weights, benchmark_ticker)
        port_cum, bench_cum = port
        final_ret = float((port_cum.iloc[-1] - 1) * 100)
        bench_ret = float((bench_cum.iloc[-1] - 1) * 100)
        st.session_state["results"] = dict(
            signature=signature,
            weights=opt_weights,
            labels=[l for l in selected_labels if current_map[l] in available_tickers],
            port_cum=port_cum,
            bench_cum=bench_cum,
            final_ret=final_ret,
            bench_ret=bench_ret,
        )

res = st.session_state.get("results")
if res and res["signature"] == signature:
    alpha = res["final_ret"] - res["bench_ret"]

    st.markdown("---")
    st.subheader("📊 Performance Summary (Selected Period)")
    m1, m2 = st.columns(2)
    m1.metric("Portfolio", f"{res['final_ret']:.1f}%")
    m2.metric(market_name, f"{res['bench_ret']:.1f}%")
    st.metric("Alpha (Your Edge)", f"{alpha:.1f}%", delta=f"{alpha:.1f}%")

    st.markdown("---")
    st.subheader("📉 Market Comparison")
    st.plotly_chart(
        growth_chart(res["port_cum"], res["bench_cum"], market_name, 400,
                     dict(color="#2ecc71", width=3), dict(color="#3498db", width=2, dash="dot")),
        width="stretch", config={'displayModeBar': False},
    )

    st.markdown("---")
    st.subheader("🍕 Optimal Allocation")
    fig_pie = px.pie(values=res["weights"], names=res["labels"], hole=0.4)
    fig_pie.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h"))
    st.plotly_chart(fig_pie, width="stretch", config={'displayModeBar': False})

    # --- 8. Out-of-sample: end date -> today ---
    today_date = datetime.today().date()
    if (today_date - end_date).days >= 30:
        st.markdown("---")
        st.subheader("📈 Out-of-Sample Performance (End Date to Today)")
        st.caption(f"Tracking performance from **{end_date}** to **{today_date}** based on optimized allocations.")

        post_data = get_supabase_data(all_required, end_date, today_date)
        post = growth_vs_benchmark(post_data, available_tickers, res["weights"], benchmark_ticker) if not post_data.empty else None

        if post is None:
            st.info("No recent market data available in database for this period.")
        else:
            post_cum, post_bench_cum = post
            post_ret = float((post_cum.iloc[-1] - 1) * 100)
            post_bench_ret = float((post_bench_cum.iloc[-1] - 1) * 100)
            post_alpha = post_ret - post_bench_ret

            pm1, pm2, pm3 = st.columns(3)
            pm1.metric("Post-Portfolio Return", f"{post_ret:.1f}%")
            pm2.metric(f"Post-{market_name} Return", f"{post_bench_ret:.1f}%")
            pm3.metric("Post-Alpha", f"{post_alpha:.1f}%", delta=f"{post_alpha:.1f}%")

            st.plotly_chart(
                growth_chart(post_cum, post_bench_cum, f"{market_name} (Post-Analysis)", 350,
                             dict(color="#e74c3c", width=3), dict(color="#34495e", width=2, dash="dot"),
                             port_name="Portfolio (Post-Analysis)"),
                width="stretch", config={'displayModeBar': False},
            )

    st.markdown("---")
    st.download_button(
        "📩 Download PDF Report",
        data=create_pdf(market_name, res["labels"], res["weights"], res["final_ret"], start_date, end_date),
        file_name="Portfolio_Report.pdf",
        width="stretch",
    )

st.caption(
    "**Disclaimer & Disclosure** This application is strictly for **educational and research purposes**. "
    "It is not a commercial financial product and does not constitute professional investment advice."
)
