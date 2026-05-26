import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF
from supabase import create_client, Client

# Hide the "Built with Streamlit" footer and main menu hamburger
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. SUPABASE CONNECTION SETUP ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error("❌ App Initialization Error: Database connection could not be established.")
    st.stop()  # Safe execution halt prevents downstream NameErrors or stack exposures

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
    "A": "Agilent", "AAPL": "Apple Inc.", "ABBV": "AbbVie", "ABT": "Abbott Labs", "ACN": "Accenture",
    "ADBE": "Adobe", "ADI": "Analog Devices", "ADM": "Archer-Daniels-Midland", "ADP": "ADP",
    "ADSK": "Autodesk", "AEE": "Ameren", "AEP": "American Electric Power", "AES": "AES Corp",
    "AIG": "AIG", "AIZ": "Assurant", "AJG": "Arthur J. Gallagher", "ALB": "Albemarle",
    "ALGN": "Align Technology", "AMAT": "Applied Materials", "AMD": "AMD", "AMCR": "Amcor",
    "AMGN": "Amgen", "AMT": "American Tower", "AMZN": "Amazon", "ANET": "Arista Networks",
    "AON": "Aon", "APA": "APA Corp", "APH": "Amphenol", "APOLLOHOSP.NS": "Apollo Hospitals",
    "ARE": "Alexandria RE", "ATO": "Atmos Energy", "AVB": "AvalonBay", "AVGO": "Broadcom",
    "AWK": "American Water", "AXP": "American Express", "AZO": "AutoZone", "BA": "Boeing",
    "BAC": "Bank of America", "BALL": "Ball Corp", "BBWI": "Bath & Body Works", "BBY": "Best Buy",
    "BEN": "Franklin Resources", "BIO": "Bio-Rad", "BKR": "Baker Hughes", "BLK": "BlackRock",
    "BRK-B": "Berkshire Hathaway", "BRO": "Brown & Brown", "BSX": "Boston Scientific",
    "BXP": "Boston Properties", "C": "Citigroup", "CAH": "Cardinal Health", "CARR": "Carrier",
    "CAT": "Caterpillar", "CB": "Chubb", "CBRE": "CBRE Group", "CDNS": "Cadence Design",
    "CDW": "CDW Corp", "CHD": "Church & Dwight", "CHTR": "Charter Comm", "CI": "Cigna",
    "CIM": "Kimco Realty", "CIPLA.NS": "Cipla", "CLX": "Clorox", "CMCSA": "Comcast",
    "CMG": "Chipotle", "CMS": "CMS Energy", "CNC": "Centene", "CNP": "CenterPoint",
    "COALINDIA.NS": "Coal India", "COP": "ConocoPhillips", "COR": "Cencora", "COST": "Costco",
    "CPB": "Campbell Soup", "CPRT": "Copart", "CRL": "Charles River", "CRM": "Salesforce",
    "CSCO": "Cisco", "CSX": "CSX Corp", "CTAS": "Cintas", "CTSH": "Cognizant", "CUM": "Cummins",
    "CVS": "CVS Health", "CZR": "Caesars", "D": "Dominion Energy", "DAL": "Delta Air Lines",
    "DASH": "DoorDash", "DE": "Deere & Co", "DELL": "Dell", "DFS": "Discover", "DG": "Dollar General",
    "DHR": "Danaher", "DIS": "Disney", "DLR": "Digital Realty", "DLTR": "Dollar Tree",
    "DOV": "Dover Corp", "DPZ": "Domino's", "DRI": "Darden Restaurants", "DTE": "DTE Energy",
    "DVN": "Devon Energy", "DXC": "DXC Tech", "DXCM": "Dexcom", "EBAY": "eBay", "ECL": "Ecolab",
    "ED": "Consolidated Edison", "EFX": "Equifax", "EG": "Everest Group", "EMN": "Eastman Chemical",
    "EMR": "Emerson Electric", "ENPH": "Enphase Energy", "EOG": "EOG Resources", "EPAM": "EPAM Systems",
    "EQR": "Equity Residential", "ES": "Eversource", "ESS": "Essex Property", "ETN": "Eaton",
    "ETR": "Entergy", "EVRG": "Evergy", "EW": "Edwards Lifesciences", "EXC": "Exelon",
    "EXPE": "Expedia", "F": "Ford", "FAST": "Fastenal", "FDX": "FedEx", "FE": "FirstEnergy",
    "FICO": "Fair Isaac", "FI": "Fiserv", "FIS": "Fidelity National", "FITB": "Fifth Third",
    "FMC": "FMC Corp", "FRT": "Federal Realty", "FSLR": "First Solar", "FTNT": "Fortinet",
    "GD": "General Dynamics", "GE": "General Electric", "GEN": "Gen Digital", "GEV": "GE Vernova",
    "GILD": "Gilead Sciences", "GLW": "Corning", "GM": "GM", "GNRC": "Generac", "GOOG": "Alphabet (C)",
    "GOOGL": "Alphabet (A)", "GPN": "Global Payments", "GS": "Goldman Sachs", "GWW": "Grainger",
    "HAS": "Hasbro", "HCA": "HCA Healthcare", "HD": "Home Depot", "HES": "Hess Corp",
    "HII": "Huntington Ingalls", "HLT": "Hilton", "HON": "Honeywell", "HRL": "Hormel",
    "HSIC": "Henry Schein", "HST": "Host Hotels", "HWM": "Howmet", "IBM": "IBM",
    "ICE": "Intercontinental Exchange", "IDXX": "IDEXX Labs", "ILV": "Elevance Health",
    "INTC": "Intel", "INTU": "Intuit", "INVH": "Invitation Homes", "IP": "International Paper",
    "IQV": "IQVIA", "IR": "Ingersoll Rand", "ISRG": "Intuitive Surgical", "IT": "Gartner",
    "ITW": "Illinois Tool Works", "IVZ": "Invesco", "JBHT": "JB Hunt", "JCI": "Johnson Controls",
    "JKHY": "Jack Henry", "JNJ": "Johnson & Johnson", "JNPR": "Juniper Networks", "JPM": "JPMorgan Chase",
    "KDP": "Keurig Dr Pepper", "KEY": "KeyCorp", "KEYS": "Keysight", "KIM": "Kimco Realty",
    "KLAC": "KLA Corp", "KMB": "Kimberly-Clark", "KMX": "CarMax", "KO": "Coca-Cola", "KR": "Kroger",
    "KVUE": "Kenvue", "L": "Loews Corp", "LHX": "L3Harris", "LIN": "Linde", "LLY": "Eli Lilly",
    "LMT": "Lockheed Martin", "LNT": "Alliant Energy", "LOW": "Lowe's", "LRCX": "Lam Research",
    "LULU": "Lululemon", "LUV": "Southwest Airlines", "LYB": "LyondellBasell", "MA": "Mastercard",
    "MAA": "Mid-America Apartment", "MAR": "Marriott", "MCHP": "Microchip", "MCK": "McKessey",
    "MCO": "Moody's", "MDT": "Medtronic", "MDLZ": "Mondelez", "MET": "MetLife", "META": "Meta Platforms",
    "MGM": "MGM Resorts", "MHK": "Mohawk Industries", "MKC": "McCormick", "MMC": "Marsh McLennan",
    "MOS": "Mosaic", "MPC": "Marathon Petroleum", "MRO": "Marathon Oil", "MS": "Morgan Stanley",
    "MSCI": "MSCI", "MSFT": "Microsoft", "MSI": "Motorola", "MTB": "M&T Bank", "MTCH": "Match Group",
    "MTD": "Mettler Toledo", "MU": "Micron", "NEE": "NextEra Energy", "NFLX": "Netflix", "NI": "NiSource",
    "NOC": "Northrop Grumman", "NOW": "ServiceNow", "NRG": "NRG Energy", "NSC": "Norfolk Southern",
    "NWS": "News Corp (B)", "NWSA": "News Corp (A)", "NVDA": "Nvidia", "O": "Realty Income",
    "ODFL": "Old Dominion", "OKE": "ONEOK", "ORCL": "Oracle", "ORLY": "O'Reilly", "OTIS": "Otis Worldwide",
    "PANW": "Palo Alto Networks", "PARA": "Paramount", "PAYC": "Paycom", "PAYX": "Paychex",
    "PCAR": "PACCAR", "PEP": "PepsiCo", "PFE": "Pfizer", "PG": "Procter & Gamble", "PGR": "Progressive",
    "PH": "Parker-Hannifin", "PKG": "Packaging Corp", "PLD": "Prologis", "PM": "Philip Morris",
    "PNW": "Pinnacle West", "POOL": "Pool Corp", "PPL": "PPL Corp", "PRU": "Prudential",
    "PSA": "Public Storage", "PSX": "Phillips 66", "QRVO": "Qorvo", "REG": "Regency Centers",
    "REGN": "Regeneron", "RF": "Regions Financial", "RL": "Ralph Lauren", "ROP": "Roper",
    "ROST": "Ross Stores", "RTX": "Raytheon", "RVTY": "Revvity", "SJM": "JM Smucker",
    "SLB": "Schlumberger", "SNPS": "Synopsys", "SPGI": "S&P Global", "SRE": "Sempra", "STE": "STERIS",
    "STLD": "Steel Dynamics", "STT": "State Street", "STX": "Seagate", "SWK": "Stanley Black & Decker",
    "SWKS": "Skyworks", "SYK": "Stryker", "SYY": "Sysco", "T": "AT&T", "TDG": "TransDigm",
    "TECH": "Bio-Techne", "TEL": "TE Connectivity", "TER": "Teradyne", "TFX": "Teleflex",
    "TGT": "Target", "TMO": "Thermo Fisher", "TPR": "Tapestry", "TROW": "T. Rowe Price",
    "TRV": "Travelers", "TSLA": "Tesla", "TSN": "Tyson Foods", "TT": "Trane", "TXN": "Texas Instruments",
    "TYL": "Tyler Tech", "UBER": "Uber", "UDR": "UDR Inc.", "UHS": "Universal Health", "ULTA": "Ulta Beauty",
    "UNH": "UnitedHealth", "UNP": "Union Pacific", "USB": "US Bancorp", "V": "Visa", "VICI": "VICI Properties",
    "VLO": "Valero", "VMC": "Vulcan Materials", "VNO": "Vornado", "VRTX": "Vertex Pharma",
    "VST": "Vistra Corp", "VTR": "Ventas", "WBA": "Walgreens", "WBD": "Warner Bros. Discovery",
    "WDC": "Western Digital", "WEC": "WEC Energy", "WELL": "Welltower", "WFC": "Wells Fargo",
    "WES": "Western Midstream", "WHR": "Whirlpool", "WM": "Waste Management", "WMB": "Williams Cos",
    "WMT": "Walmart", "WY": "Weyerhaeuser", "XEL": "Xcel Energy", "XOM": "Exxon Mobil",
    "XRAY": "Dentsply Sirona", "ZBH": "Zimmer Biomet", "Zebra": "Zebra Tech", "ZTS": "Zoetis"
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

if "Nifty" in market_choice:
    current_map = NIFTY_MAP
    market_name = "Nifty 50"
    benchmark_ticker = "^NSEI"
else:
    current_map = SP_MAP
    market_name = "S&P 500"
    benchmark_ticker = "^GSPC"

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

# --- 7. ANALYSIS & DISPLAY CONTROL ---
if 5 <= len(selected_tickers) <= 10:
    
    all_required = selected_tickers + [benchmark_ticker]
    data_combined = get_supabase_data(all_required, start_date, end_date)

    if not data_combined.empty and benchmark_ticker in data_combined.columns:
        available_tickers = [t for t in selected_tickers if t in data_combined.columns]
        
        if len(available_tickers) >= 2:
            data = data_combined[available_tickers].dropna()
            bench_data = data_combined[benchmark_ticker].dropna()
            
            returns_pct = data.pct_change().dropna()
            log_ret = np.log(data/data.shift(1)).dropna()
            
            # --- PRE-RUN ASSET METRICS GRID ---
            st.subheader("🧮 Asset Risk & Return Metrics")
            
            # Calculate Independent Total Returns ((Last Price / First Price) - 1) * 100
            independent_returns = {}
            for ticker in available_tickers:
                first_price = data[ticker].iloc[0]
                last_price = data[ticker].iloc[-1]
                independent_returns[ticker] = ((last_price / first_price) - 1) * 100

            # Calculate Annualized Variance
            variance_series = log_ret.var() * 252
            
            # Render independent data parameters cleanly into summary columns
            st.markdown("**Independent Asset Breakdown (Over Date Range):**")
            for ticker in available_tickers:
                clean_name = ticker.replace(".NS", "")
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.markdown(f"**{clean_name}**")
                with c2:
                    st.markdown(f"Return: `{independent_returns[ticker]:+.2f}%` | Variance: `{variance_series[ticker]:.4f}`")
            
            st.markdown(" ")
            
            # Calculate and display Correlation Matrix
            st.markdown("**Asset Correlation Matrix Heatmap:**")
            corr_matrix = returns_pct.corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                range_color=[-1, 1],
                labels=dict(color="Correlation")
            )
            fig_corr.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Tickers",
                yaxis_title="Tickers"
            )
            st.plotly_chart(fig_corr, width='stretch', config={'displayModeBar': False})
            
            st.markdown("---")
            
            # --- THE SIMULATION ACTION BUTTON ---
            st.subheader("🚀 Run Allocation Engine")
            st.markdown("Click below to pass these parameters through the Monte Carlo optimization framework.")
            
            if st.button("Run Portfolio Simulation", type="primary", width='stretch'):
                with st.spinner('⏳ Running 2,000 Monte Carlo Paths...'):
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

                    st.session_state['calculated'] = True
                    st.session_state['final_ret'] = final_ret
                    st.session_state['bench_ret'] = bench_ret
                    st.session_state['alpha'] = alpha
                    st.session_state['opt_cum'] = opt_cum
                    st.session_state['bench_cum'] = bench_cum
                    st.session_state['opt_weights'] = opt_weights
                    st.session_state['available_labels_final'] = [l for l in selected_labels if current_map[l] in available_tickers]

            # --- RENDER SIMULATION RESULTS ---
            if 'calculated' in st.session_state and st.session_state['calculated']:
                st.markdown("---")
                st.subheader("📊 Performance Summary")
                m1, m2 = st.columns(2)
                m1.metric("Portfolio", f"{st.session_state['final_ret']:.1f}%")
                m2.metric(f"{market_name}", f"{st.session_state['bench_ret']:.1f}%")
                st.metric("Alpha (Your Edge)", f"{st.session_state['alpha']:.1f}%", delta=f"{st.session_state['alpha']:.1f}%")

                st.markdown("---")

                # Line Chart
                st.subheader("📉 Market Comparison")
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=st.session_state['opt_cum'].index, y=st.session_state['opt_cum'], name="Portfolio", line=dict(color='#2ecc71', width=3)))
                fig_line.add_trace(go.Scatter(x=st.session_state['bench_cum'].index, y=st.session_state['bench_cum'], name=market_name, line=dict(color='#3498db', width=2, dash='dot')))
                fig_line.update_layout(
                    height=400, 
                    margin=dict(l=0, r=0, t=20, b=0), 
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white"
                )
                st.plotly_chart(fig_line, width='stretch', config={'displayModeBar': False})

                st.markdown("---")

                # Pie Chart
                st.subheader("🍕 Optimal Allocation")
                fig_pie = px.pie(values=st.session_state['opt_weights'], names=st.session_state['available_labels_final'], hole=0.4)
                fig_pie.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h"))
                st.plotly_chart(fig_pie, width='stretch', config={'displayModeBar': False})

                st.markdown("---")
                
                pdf_bytes = create_pdf(market_name, st.session_state['available_labels_final'], st.session_state['opt_weights'], st.session_state['final_ret'], start_date, end_date)
                st.download_button("📩 Download PDF Report", data=pdf_bytes, file_name="Portfolio_Report.pdf", width='stretch')

            # Footer disclosures stay static at the base
            st.caption("""
            **Disclaimer & Disclosure** This application is strictly for **educational and research purposes**. It is not a commercial financial 
            product and does not constitute professional investment advice. 
            """)
            
        else:
            st.error("Not enough historical data found for these stocks.")
else:
    if 'calculated' in st.session_state:
        st.session_state['calculated'] = False
    st.info("💡 Select 5 to 10 stocks above to begin the calculation.")
