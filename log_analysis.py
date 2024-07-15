from pymavlink import mavutil
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points using Haversine formula."""
    R = 6371000.0  # Radius of the Earth in meters

    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def detect_flight_phases(bin_file_path):
    """Detect flight phases based on NTUN.TAT and print the results including energy consumption, altitude, and distance."""
    mavlog = mavutil.mavlink_connection(bin_file_path)

    previous_altitude = None
    previous_position = None
    total_distance = 0.0
    energy = 0.0  # Default value for energy
    previous_phase = None
    phase_start_energy = 0.0
    phase_start_distance = 0.0
    phase_start_altitude = 0.0
    phases = []

    while True:
        msg = mavlog.recv_match(type=['NTUN', 'GPS', 'BAT'], blocking=True)
        if msg is None:
            break

        if msg.get_type() == 'BAT':
            energy = msg.EnrgTot  # Extract total energy consumed in Wh

        elif msg.get_type() == 'NTUN':
            current_altitude = msg.TAT

        elif msg.get_type() == 'GPS':
            try:
                current_latitude = msg.Lat   # Convert from degrees * 1e7 to degrees
                current_longitude = msg.Lng   # Convert from degrees * 1e7 to degrees
            except AttributeError as e:
                print(f"Error accessing GPS data: {e}")
                continue  # Skip this iteration if GPS data cannot be accessed

            if previous_position is not None:
                # Calculate distance traveled since last position
                distance = calculate_distance(previous_position[0], previous_position[1],
                                              current_latitude, current_longitude)
                total_distance += distance

            if current_altitude == 0:
                phase = 'On Ground'
            elif previous_altitude is not None:
                altitude_change = current_altitude - previous_altitude
                if altitude_change > 0.0:
                    phase = 'climb'  # Change 'climb' to 'VTOL Climb'
                elif altitude_change < 0.0:
                    phase = 'descent'  # Change 'descent' to 'VTOL Descent'
                else:
                    phase = 'cruise'
            else:
                phase = 'unknown'  # For the first data point

            # Check for phase change before appending to flight_phases
            if phase != previous_phase:
                if previous_phase is not None:
                    energy_used = energy - phase_start_energy
                    distance_traveled = total_distance - phase_start_distance
                    if distance_traveled >= 100:  # Filter to ignore printing if distance is less than 100 meters
                        wh_per_km = (energy_used / (distance_traveled / 1000)) if distance_traveled != 0 else 0
                        phases.append((previous_phase, energy_used, distance_traveled, phase_start_altitude, wh_per_km))
                previous_phase = phase
                phase_start_energy = energy
                phase_start_distance = total_distance
                phase_start_altitude = current_altitude

            previous_altitude = current_altitude
            previous_position = (current_latitude, current_longitude)

    # Add the last phase to flight_phases if it has not been added yet
    if previous_phase is not None:
        energy_used = energy - phase_start_energy
        distance_traveled = total_distance - phase_start_distance
        if distance_traveled >= 100:  # Filter to ignore printing if distance is less than 100 meters
            wh_per_km = (energy_used / (distance_traveled / 1000)) if distance_traveled != 0 else 0
            phases.append((previous_phase, energy_used, distance_traveled, phase_start_altitude, wh_per_km))

    return phases
