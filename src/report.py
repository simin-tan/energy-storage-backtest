import plotly.graph_objects as go

def generate_report(df):
    # Create an interactive plot showing the market prices
    fig = go.Figure()
    
    # Add the base market electricity price line
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['electricity_price_eur_mwh'],
        mode='lines',
        name='Electricity Price (EUR/MWh)',
        line=dict(color='gray', width=1)
    ))
    
    # Highlight Charge points
    charge_events = df[df['action'] == 'CHARGE']
    fig.add_trace(go.Scatter(
        x=charge_events.index, 
        y=charge_events['electricity_price_eur_mwh'],
        mode='markers',
        name='Battery Charging (Buying)',
        marker=dict(color='green', size=7)
    ))
    
    # Highlight Discharge points
    discharge_events = df[df['action'] == 'DISCHARGE']
    fig.add_trace(go.Scatter(
        x=discharge_events.index, 
        y=discharge_events['electricity_price_eur_mwh'],
        mode='markers',
        name='Battery Discharging (Selling)',
        marker=dict(color='red', size=7)
    ))
    
    fig.update_layout(
        title="Automated Battery Storage Asset Backtest Simulation",
        xaxis_title="Timestamp (UTC)",
        yaxis_title="EUR / MWh",
        template="plotly_dark"
    )
    
    # Automatically export it as a clean HTML file
    fig.write_html("battery_performance_report.html")
    print("Interactive HTML report generated successfully!")
