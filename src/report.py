import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_report(df):
    # Create an interactive plot showing the market prices
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    
    # Add the base market electricity price line
    fig.add_trace(
        go.Scatter(
            x = df.index, 
            y = df['electricity_price_eur_mwh'],
            mode = 'lines',
            name = 'Electricity Price (EUR/MWh)',
            line = dict(color='gray', width=1)
        ),
        secondary_y = False
    )

    # Add battery state of charge over time
    fig.add_trace(
        go.Scatter(
            x = df.index,
            y = df['state_of_charge_mwh'],
            mode = 'lines',
            name = 'Battery State of Charge (MWh)',
            line = dict(color='blue', width=2)
        ),
        secondary_y = True
    )

    # Highlight Charge points
    charge_events = df[df['action'] == 'CHARGE']
    fig.add_trace(go.Scatter(
        x = charge_events.index, 
        y = charge_events['electricity_price_eur_mwh'],
        mode = 'markers',
        name = 'Battery Charging (Buying)',
        marker = dict(color='green', size=7)
    ))
    
    # Highlight Discharge points
    discharge_events = df[df['action'] == 'DISCHARGE']
    fig.add_trace(go.Scatter(
        x = discharge_events.index, 
        y = discharge_events['electricity_price_eur_mwh'],
        mode = 'markers',
        name = 'Battery Discharging (Selling)',
        marker = dict(color='red', size=7)
    ))
    
    fig.update_layout(
        title = "Automated Battery Storage Asset Backtest Simulation",
        xaxis_title = "Timestamp (UTC)",
        template = "plotly_dark"
    )

    fig.update_yaxes(
        title_text = 'Electricity Price (EUR/MWh)',
        secondary_y = False
    )

    fig.update_yaxes(
        title_text = 'State of Charge (MWh)',
        secondary_y = True
    )
    
    # Automatically export it as a clean HTML file
    fig.write_html("outputs/battery_performance_report.html")
    print("Interactive HTML report generated successfully!")
