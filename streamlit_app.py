import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="FUB Building Energy Management",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .room-tile {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def get_building_structure():
    """Return the building structure with floors and rooms"""
    return {
        "Ground": ["Room 101", "Room 102", "Room 103"],
        "1": ["Room 201", "Room 202", "Room 203", "Room 204"],
        "2": ["Room 301", "Room 302", "Room 303"],
        "3": ["Room 401", "Room 402", "Room 403", "Room 404"],
        "4": ["Room 501", "Room 502"],
        "5": ["Room 601", "Room 602", "Room 603"]
    }

def generate_synthetic_data():
    """Generate synthetic data for all rooms in the building"""
    building_structure = get_building_structure()
    data = {}
    
    for floor, rooms in building_structure.items():
        for room in rooms:
            room_id = room.replace(" ", "")
            power = random.randint(800, 2000)
            voltage = 220
            current = power / voltage
            energy_kwh = random.uniform(5, 25)
            cost_taka = energy_kwh * 8.5
            carbon_emissions = energy_kwh * 500
            
            data[room_id] = {
                'room_id': room_id,
                'room_name': room,
                'floor': floor,
                'ac_status': random.choice([True, False]),
                'power': power,
                'voltage': voltage,
                'current': round(current, 2),
                'energy_kwh': round(energy_kwh, 2),
                'cost_taka': round(cost_taka, 2),
                'carbon_emissions': round(carbon_emissions, 2)
            }
    
    return data

def update_device_status(device_id, status):
    """Update device status in session state"""
    if device_id in st.session_state.building_data:
        st.session_state.building_data[device_id]['ac_status'] = status
        return True
    return False

# Initialize session state
if 'building_data' not in st.session_state:
    st.session_state.building_data = generate_synthetic_data()

def main():
    st.markdown('<h1 class="main-header">🏢 FUB Building Energy Management System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Building Overview", "Room Details", "Device Management"])
    
    if page == "Building Overview":
        show_building_overview()
    elif page == "Room Details":
        show_room_details()
    elif page == "Device Management":
        show_device_management()

def show_building_overview():
    st.header("Building Overview")
    
    # Building summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_energy = sum(room['energy_kwh'] for room in st.session_state.building_data.values())
    total_cost = sum(room['cost_taka'] for room in st.session_state.building_data.values())
    total_carbon = sum(room['carbon_emissions'] for room in st.session_state.building_data.values())
    
    with col1:
        st.metric("Total Energy Today", f"{total_energy:.2f} kWh")
    with col2:
        st.metric("Total Cost Today", f"৳{total_cost:.2f}")
    with col3:
        st.metric("Carbon Emissions", f"{total_carbon:.2f} gCO₂")
    with col4:
        active_devices = sum(1 for room in st.session_state.building_data.values() if room['ac_status'])
        st.metric("Active Devices", f"{active_devices}/{len(st.session_state.building_data)}")
    
    # Floor selection
    floors = get_building_structure()
    selected_floor = st.selectbox("Select Floor", list(floors.keys()))
    
    # Display room tiles for selected floor
    st.subheader(f"Floor {selected_floor} - Rooms")
    
    cols = st.columns(3)
    room_count = 0
    
    for room_id, room_data in st.session_state.building_data.items():
        if room_data['floor'] == selected_floor:
            with cols[room_count % 3]:
                status_color = "🟢" if room_data['ac_status'] else "🔴"
                
                st.markdown(f"""
                <div class="room-tile">
                    <h3>{room_id} - {room_data['room_name']}</h3>
                    <p>Status: {status_color} {'ON' if room_data['ac_status'] else 'OFF'}</p>
                    <p>Energy Today: {room_data['energy_kwh']:.2f} kWh</p>
                    <p>Cost: ৳{room_data['cost_taka']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Control buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Turn ON", key=f"on_{room_id}"):
                        update_device_status(room_id, True)
                        st.rerun()
                with col2:
                    if st.button(f"Turn OFF", key=f"off_{room_id}"):
                        update_device_status(room_id, False)
                        st.rerun()
            
            room_count += 1
    
    # Energy consumption trends
    st.subheader("Energy Consumption Trends")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2025, 11, 1))
    with col2:
        end_date = st.date_input("End Date", value=datetime(2025, 11, 15))
    
    # Create energy consumption chart
    room_names = [data['room_name'] for data in st.session_state.building_data.values()]
    energy_values = [data['energy_kwh'] for data in st.session_state.building_data.values()]
    
    fig = px.bar(
        x=room_names, 
        y=energy_values,
        title="Energy Consumption by Room",
        labels={'x': 'Room', 'y': 'Energy (kWh)'}
    )
    st.plotly_chart(fig, use_container_width=True)

def show_room_details():
    st.header("Room Details")
    
    # Room selection
    room_options = [f"{room_id} - {data['room_name']}" for room_id, data in st.session_state.building_data.items()]
    selected_room_option = st.selectbox("Select Room", room_options)
    selected_room = selected_room_option.split(" - ")[0]
    
    if selected_room in st.session_state.building_data:
        room_data = st.session_state.building_data[selected_room]
        
        # Room header with controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"{selected_room} - {room_data['room_name']}")
            status = "ON 🟢" if room_data['ac_status'] else "OFF 🔴"
            st.write(f"AC Status: {status}")
        
        with col2:
            if st.button("Turn ON AC" if not room_data['ac_status'] else "Turn OFF AC"):
                update_device_status(selected_room, not room_data['ac_status'])
                st.rerun()
        
        with col3:
            # Schedule control
            with st.expander("Schedule Settings"):
                schedule_on = st.time_input("Turn ON at", value=datetime.strptime("08:00", "%H:%M").time())
                schedule_off = st.time_input("Turn OFF at", value=datetime.strptime("17:00", "%H:%M").time())
                if st.button("Set Schedule"):
                    st.success(f"Schedule set: ON at {schedule_on}, OFF at {schedule_off}")
        
        # Current readings
        st.subheader("Current Readings")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Voltage", f"{room_data['voltage']} V")
        with col2:
            st.metric("Current", f"{room_data['current']} A")
        with col3:
            st.metric("Power", f"{room_data['power']} W")
        with col4:
            st.metric("Energy Today", f"{room_data['energy_kwh']} kWh")
        with col5:
            st.metric("Cost", f"৳{room_data['cost_taka']}")
        
        # Real-time graphs
        st.subheader("Real-time Monitoring")
        
        # Create sample time series data
        time_points = pd.date_range(start=datetime(2025, 11, 1, 0, 0, 0), 
                                   end=datetime(2025, 11, 1, 23, 59, 0), 
                                   freq='H')
        
        # Simulate data with some variation
        base_power = room_data['power']
        power_data = [base_power * (0.7 + 0.6 * (i % 24) / 24) for i in range(len(time_points))]
        voltage_data = [220 + 10 * (i % 12) / 12 for i in range(len(time_points))]
        current_data = [power_data[i] / voltage_data[i] for i in range(len(time_points))]
        
        # Create tabs for different graphs
        tab1, tab2, tab3 = st.tabs(["Power Consumption", "Voltage", "Current"])
        
        with tab1:
            fig_power = go.Figure()
            fig_power.add_trace(go.Scatter(x=time_points, y=power_data, mode='lines', name='Power (W)'))
            fig_power.update_layout(title="Power Consumption Over Time", xaxis_title="Time", yaxis_title="Power (W)")
            st.plotly_chart(fig_power, use_container_width=True)
        
        with tab2:
            fig_voltage = go.Figure()
            fig_voltage.add_trace(go.Scatter(x=time_points, y=voltage_data, mode='lines', name='Voltage (V)'))
            fig_voltage.update_layout(title="Voltage Over Time", xaxis_title="Time", yaxis_title="Voltage (V)")
            st.plotly_chart(fig_voltage, use_container_width=True)
        
        with tab3:
            fig_current = go.Figure()
            fig_current.add_trace(go.Scatter(x=time_points, y=current_data, mode='lines', name='Current (A)'))
            fig_current.update_layout(title="Current Over Time", xaxis_title="Time", yaxis_title="Current (A)")
            st.plotly_chart(fig_current, use_container_width=True)
        
        # Energy and cost analysis
        st.subheader("Energy Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily energy consumption
            days = [f"Nov {i}" for i in range(1, 16)]
            daily_energy = [room_data['energy_kwh'] * (0.8 + 0.4 * (i % 7) / 7) for i in range(15)]
            
            fig_daily = px.line(x=days, y=daily_energy, title="Daily Energy Consumption")
            fig_daily.update_layout(xaxis_title="Date", yaxis_title="Energy (kWh)")
            st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            # Cost analysis
            daily_cost = [energy * 8.5 for energy in daily_energy]
            
            fig_cost = px.bar(x=days, y=daily_cost, title="Daily Electricity Cost")
            fig_cost.update_layout(xaxis_title="Date", yaxis_title="Cost (Taka)")
            st.plotly_chart(fig_cost, use_container_width=True)
        
        # Carbon emissions
        st.metric("Carbon Emissions Today", f"{room_data['carbon_emissions']} gCO₂")

def show_device_management():
    st.header("Device Management")
    
    # Add new device form
    st.subheader("Add New Device")
    
    with st.form("add_device_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            device_id = st.text_input("Device ID")
            room_name = st.text_input("Room Name")
            floor = st.selectbox("Floor", ["Ground", "1", "2", "3", "4", "5"])
        
        with col2:
            device_type = st.selectbox("Device Type", ["AC", "Light", "Computer", "Other"])
            initial_status = st.radio("Initial Status", ["ON", "OFF"])
            power_rating = st.number_input("Power Rating (W)", min_value=0, value=1500)
        
        submitted = st.form_submit_button("Add Device")
        
        if submitted:
            if device_id and room_name:
                new_device = {
                    'room_id': device_id,
                    'room_name': room_name,
                    'floor': floor,
                    'device_type': device_type,
                    'ac_status': initial_status == "ON",
                    'power': power_rating,
                    'voltage': 220,
                    'current': power_rating / 220,
                    'energy_kwh': 0,
                    'cost_taka': 0,
                    'carbon_emissions': 0
                }
                
                st.session_state.building_data[device_id] = new_device
                st.success(f"Device {device_id} added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields")
    
    # Device list with controls
    st.subheader("Manage Existing Devices")
    
    for device_id, device_data in st.session_state.building_data.items():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{device_id}** - {device_data['room_name']} (Floor {device_data['floor']})")
            status = "ON 🟢" if device_data['ac_status'] else "OFF 🔴"
            st.write(f"Status: {status} | Power: {device_data['power']}W")
        
        with col2:
            if st.button("ON", key=f"on_{device_id}"):
                update_device_status(device_id, True)
                st.rerun()
        
        with col3:
            if st.button("OFF", key=f"off_{device_id}"):
                update_device_status(device_id, False)
                st.rerun()
        
        with col4:
            if st.button("Edit", key=f"edit_{device_id}"):
                st.info(f"Edit functionality for {device_id} - In a real app, this would open an edit form")
        
        with col5:
            if st.button("Delete", key=f"delete_{device_id}"):
                if st.session_state.building_data.get(device_id):
                    del st.session_state.building_data[device_id]
                    st.rerun()
        
        st.divider()

if __name__ == "__main__":
    main()