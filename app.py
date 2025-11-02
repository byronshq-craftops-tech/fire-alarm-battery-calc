from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Standard battery sizes in Ah
STANDARD_BATTERY_SIZES = [1.2, 2.1, 3.2, 4, 7, 12, 18, 20, 24, 38]

def calculate_standby_capacity(quiescent_load, standby_period):
    """Calculate standby capacity in mAh"""
    return quiescent_load * standby_period

def calculate_operational_capacity(alarm_load):
    """Calculate operational capacity in mAh - operational duration fixed at 0.5 hrs"""
    operational_duration = 0.5
    return alarm_load * operational_duration

def calculate_minimum_required_capacity(standby_capacity, operational_capacity):
    """Calculate minimum required capacity in Ah with 25% safety factor"""
    return (standby_capacity + operational_capacity) / 1000 * 1.25

def find_required_battery_size(minimum_capacity_ah):
    """Find the smallest standard battery size that meets requirements"""
    for size in STANDARD_BATTERY_SIZES:
        if size >= minimum_capacity_ah:
            return size
    # If none of the standard sizes are big enough, return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get input values
        quiescent_load = float(request.form['quiescent_load'])
        alarm_load = float(request.form['alarm_load'])
        standby_period = float(request.form['standby_period'])

        # Perform calculations
        standby_capacity = calculate_standby_capacity(quiescent_load, standby_period)
        operational_capacity = calculate_operational_capacity(alarm_load)
        minimum_required_capacity = calculate_minimum_required_capacity(standby_capacity, operational_capacity)
        battery_size_required = find_required_battery_size(minimum_required_capacity)

        # Check if a suitable battery exists
        if battery_size_required is None:
            return jsonify({
                'standby_capacity': round(standby_capacity, 2),
                'operational_capacity': round(operational_capacity, 2),
                'operational_duration': 0.5,
                'minimum_required_capacity': round(minimum_required_capacity, 2),
                'battery_size_required': None,
                'error_message': 'No standard battery available for this requirement'
            })

        # Return results
        return jsonify({
            'standby_capacity': round(standby_capacity, 2),
            'operational_capacity': round(operational_capacity, 2),
            'operational_duration': 0.5,
            'minimum_required_capacity': round(minimum_required_capacity, 2),
            'battery_size_required': battery_size_required
        })

    except (ValueError, KeyError) as e:
        return jsonify({'error': 'Invalid input values'}), 400


if __name__ == '__main__':
    app.run(debug=True)