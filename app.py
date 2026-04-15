import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF
from supabase import create_client, Client

# --- 1. SUPABASE CONNECTION SETUP ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error("Missing Supabase Secrets! Please ensure SUPABASE_URL and SUPABASE_KEY are in your secrets.")

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
    "PH": "Parker-Hannifin", "MCK": "McKessey", "F": "Ford", "GM": "GM", "DASH": "DoorDash", "EMR": "Emerson Electric",
    "NSC": "Norfolk Southern", "PCAR": "PACCAR", "ROST": "Ross Stores", "WELL": "Welltower", "MSI": "Motorola",
    "PSX": "Phillips 66", "MPC": "Marathon Petroleum", "CPRT": "Copart", "DXCM": "Dexcom", "AJG": "Arthur J. Gallagher",
    "HLT": "Hilton", "CSX": "CSX Corp", "IT": "Gartner", "CARR": "Carrier", "CTAS": "Cintas", "AON": "Aon",
    "TGT": "Target", "NOC": "Northrop Grumman", "ANET": "Arista Networks", "D": "Dominion Energy", "TT": "Trane",
    "ROP": "Roper", "TDG": "TransDigm", "EW": "Edwards Lifesciences", "CUM": "Cummins", "MET": "MetLife",
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
    "DXC": "DXC Tech", "TFX": "Teleflex", "MTD": "Mettler Toledo", "Zebra": "Zebra Tech", "HII": "Huntington Ingalls",
    "LNT": "Alliant Energy", "NI": "NiSource", "ATO": "Atmos Energy", "NRG": "NRG Energy", "VST": "Vistra Corp",
    "SRE": "Sempra", "WEC": "WEC Energy", "ES": "Eversource", "DTE": "DTE Energy", "ETR": "Entergy",
    "FE": "FirstEnergy", "AEE": "Ameren", "CMS": "CMS Energy", "EVRG": "Evergy", "AVB": "AvalonBay",
    "EQR": "Equity Residential", "PSA": "Public Storage", "BXP": "Boston Properties", "KIM": "Kimco Realty",
    "REG": "Regency Centers", "UDR": "UDR Inc.", "HST": "Host Hotels"
}

NIFTY_MAP = {f"{k} ({v})": k for k, v in NIFTY_50_DATA.items()}
SP_MAP = {f"{k} ({v})": k for k, v in SP_500_DATA.items()}

# --- 3. DATA ENGINE ---
@st.cache_data
def get_supabase_data(tickers, start, end):
    try:
        response = supabase.table("stock_history") \
            .select("date, ticker, price") \
            .in_("ticker", tickers) \
            .gte("date", start.strftime('%Y-%m-%d')) \
            .lte("date", end.strftime('%Y-%m-%d')) \
            .order("date") \
            .limit(30000) \
            .execute()
        
        full_df = pd.DataFrame(response.data)
        if full_df.empty:
            return pd.DataFrame()

        full_df['date'] = pd.to_datetime(full_df['date'])
        filtered_df = full_df.drop_duplicates(subset=['date', 'ticker'], keep='last')
        pivoted_df = filtered_df.pivot(index='date', columns='ticker', values='price')
        return pivoted_df.ffill().bfill()
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return pd.DataFrame()

# --- 4. PDF ENGINE ---
def create_pdf(market, stocks, weights, final_ret, start, end):
    pdf = FPDF() 
    pdf.add_page() 
    pdf.set_font("Arial", 'B', 16) 
    pdf.cell(0, 10, f'{market} Analysis Report', 0, 1, 'C') 
    pdf.ln(10) 
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Analysis Range: {start} to {end}", ln=True) 
    pdf.ln(5)
    for s, w in zip(stocks, weights):
        pdf.cell(0, 8, f"- {s}: {w*100:.2f}%", ln=True) 
    pdf.ln(10) 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Portfolio Growth: {final_ret:.2f}%", ln=True) 
    return pdf.output(dest='S').encode('latin-1')

# --- 5. PAGE SETUP ---
st.set_page_config(page_title="Portfolio Pro", layout="centered")

# --- 6. INPUTS (VERTICAL LAYOUT) ---
st.title("📂 Portfolio Pro")
st.markdown("---")

market_choice = st.selectbox("Select Market", ["Nifty 50 (India)", "S&P 500 (USA)"])

# Define variables based on selection BEFORE they are used
if "Nifty" in market_choice:
    current_map = NIFTY_MAP
    market_name = "Nifty 50"
    benchmark_ticker = "^NSEI"
else:
    current_map = SP_MAP
    market_name = "S&P 500"
    benchmark_ticker = "^GSPC"

# Now current_map is defined and safe to use
selected_labels = st.multiselect(
    "Select 5-10 Stocks", 
    options=list(current_map.keys()),
    placeholder="Search tickers..."
)
selected_tickers = [current_map[label] for label in selected_labels]

col_date1, col_date2 = st.columns(2)
with col_date1:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365))
with col_date2:
    end_date = st.date_input("End Date", datetime.today())

st.markdown("---")

# --- 7. ANALYSIS & DISPLAY ---
if 5 <= len(selected_tickers) <= 10:
    with st.spinner('⏳ Calculating Optimization...'):
        all_required = selected_tickers + [benchmark_ticker]
        data_combined = get_supabase_data(all_required, start_date, end_date)

        if not data_combined.empty and benchmark_ticker in data_combined.columns:
            available_tickers = [t for t in selected_tickers if t in data_combined.columns]
            
            if len(available_tickers) >= 2:
                # Math Logic
                data = data_combined[available_tickers].dropna()
                bench_data = data_combined[benchmark_ticker].dropna()
                
                returns_pct = data.pct_change().dropna()
                log_ret = np.log(data/data.shift(1)).dropna()
                
                num_portfolios = 2000
                all_weights = np.zeros((num_portfolios, len(available_tickers)))
                sharpe_arr = np.zeros(num_portfolios)

                for i in range(num_portfolios):
                    w = np.random.random(len(available_tickers))
                    w /= np.sum(w)
                    all_weights[i,:] = w
                    ret = np.sum((log_ret.mean() * w) * 252)
                    vol = np.sqrt(np.dot(w.T, np.dot(log_ret.cov() * 252, w)))
                    sharpe_arr[i] = ret / vol

                best_idx = sharpe_arr.argmax() 
                opt_weights = all_weights[best_idx,:] 
                
                opt_cum = (1 + returns_pct.dot(opt_weights)).cumprod()
                bench_cum = (1 + bench_data.pct_change().dropna()).cumprod()
                
                final_ret = float((opt_cum.iloc[-1] - 1) * 100) 
                bench_ret = float((bench_cum.iloc[-1] - 1) * 100) 
                alpha = final_ret - bench_ret 

                # --- MOBILE-FIRST VERTICAL DISPLAY ---
                st.subheader("📊 Performance Summary")
                m1, m2 = st.columns(2)
                m1.metric("Portfolio", f"{final_ret:.1f}%")
                m2.metric(f"{market_name}", f"{bench_ret:.1f}%")
                st.metric("Alpha (Your Edge)", f"{alpha:.1f}%", delta=f"{alpha:.1f}%")

                st.markdown("---")

                # Line Chart first
                st.subheader("📉 Market Comparison")
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=opt_cum.index, y=opt_cum, name="Portfolio", line=dict(color='#2ecc71', width=3)))
                fig_line.add_trace(go.Scatter(x=bench_cum.index, y=bench_cum, name=market_name, line=dict(color='#3498db', width=2, dash='dot')))
                fig_line.update_layout(
                    height=400, 
                    margin=dict(l=0, r=0, t=20, b=0), 
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white"
                )
                st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

                st.markdown("---")

                # Pie Chart second
                st.subheader("🍕 Optimal Allocation")
                available_labels_final = [l for l in selected_labels if current_map[l] in available_tickers]
                fig_pie = px.pie(values=opt_weights, names=available_labels_final, hole=0.4)
                fig_pie.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h"))
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

                st.markdown("---")

                # PDF Export at the bottom
                pdf_bytes = create_pdf(market_name, available_labels_final, opt_weights, final_ret, start_date, end_date)
                st.download_button("📩 Download PDF Report", data=pdf_bytes, file_name="Portfolio_Report.pdf", use_container_width=True)

            else:
                st.error("Not enough historical data found for these stocks.")
else:
    st.info("💡 Select 5 to 10 stocks above to begin the calculation.")
