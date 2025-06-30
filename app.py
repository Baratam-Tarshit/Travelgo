from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory user database with a default user for testing
users = {
    "tar@gmail.com": "tar123"
}

# In-memory booking storage per user
user_bookings = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        if username in users:
            flash('Username already exists. Please login.')
            return redirect(url_for('login'))

        users[username] = password
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    user = session['user']
    bookings = user_bookings.get(user, [])

    return render_template('dashboard.html', name=user, bookings=bookings)

# ======== Booking Pages ========
@app.route('/flight')
def flight():
    return render_template('flight.html')

@app.route('/train')
def train():
    return render_template('train.html')

@app.route('/bus')
def bus():
    return render_template('bus.html')

@app.route('/hotel')
def hotel():
    return render_template('hotel.html')

@app.route('/hostel')
def hostel():
    return render_template('hostel.html')

# ======== Bus Booking Route ========
@app.route('/confirm_bus_booking', methods=['POST'])
def confirm_bus_booking():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    booking = {
        'name': request.form['name'],
        'source': request.form['source'],
        'destination': request.form['destination'],
        'time': request.form['time'],
        'type': 'bus',
        'travel_date': request.form['date'],
        'num_persons': int(request.form['persons']),
        'price_per_person': int(request.form['price']),
        'total_price': int(request.form['price']) * int(request.form['persons'])
    }

    session['pending_booking'] = booking

    return render_template('confirm.html', booking=booking)

# ======== Train Booking Route ========
@app.route('/confirm_train_booking', methods=['POST'])
def confirm_train_booking():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    booking = {
        'name': request.form['name'],
        'train_number': request.form['trainNumber'],
        'source': request.form['source'],
        'destination': request.form['destination'],
        'departure_time': request.form['departureTime'],
        'arrival_time': request.form['arrivalTime'],
        'type': 'train',
        'travel_date': request.form['date'],
        'num_persons': int(request.form['persons']),
        'price_per_person': int(request.form['price']),
        'total_price': int(request.form['price']) * int(request.form['persons'])
    }

    session['pending_booking'] = booking

    return render_template('confirm.html', booking=booking)

# ======== Flight Booking Route ========
@app.route('/confirm_flight_booking', methods=['POST'])
def confirm_flight_booking():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    booking = {
        'name': request.form['airline'],
        'flight_number': request.form['flightNumber'],
        'source': request.form['source'],
        'destination': request.form['destination'],
        'departure_time': request.form['departureTime'],
        'arrival_time': request.form['arrivalTime'],
        'type': 'flight',
        'travel_date': request.form['date'],
        'num_persons': int(request.form['persons']),
        'price_per_person': int(request.form['price']),
        'total_price': int(request.form['price']) * int(request.form['persons'])
    }

    session['pending_booking'] = booking

    return render_template('confirm.html', booking=booking)

# ======== Hotel Booking Route ========
@app.route('/confirm_hotel_booking', methods=['POST'])
def confirm_hotel_booking():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    booking = {
        'name': request.form['hotelName'],
        'location': request.form['location'],
        'check_in_date': request.form['checkInDate'],
        'check_out_date': request.form['checkOutDate'],
        'num_rooms': int(request.form['numRooms']),
        'num_guests': int(request.form['numGuests']),
        'price_per_night': float(request.form['pricePerNight']),
        'num_nights': int(request.form['numNights']),
        'total_price': float(request.form['pricePerNight']) * int(request.form['numRooms']) * int(request.form['numNights']),
        'type': 'hotel'
    }

    session['pending_booking'] = booking

    return render_template('confirm.html', booking=booking)

# ======== Final Confirmation Common Route ========
@app.route('/final_confirm_booking', methods=['POST'])
def final_confirm_booking():
    if 'user' not in session:
        return {"success": False, "message": "Please login first.", "redirect": url_for('login')}

    user = session['user']
    booking = session.pop('pending_booking', None)

    if booking:
        if user not in user_bookings:
            user_bookings[user] = []

        # Format booking details for dashboard
        if booking['type'] == 'flight':
            booking_details = f"{booking['name']} {booking['flight_number']} {booking['source']}→{booking['destination']} {booking['departure_time']} - {booking['arrival_time']} ({booking['num_persons']} persons)"
        elif booking['type'] == 'bus':
            booking_details = f"{booking['name']} {booking['source']}→{booking['destination']} {booking.get('time')} ({booking['num_persons']} persons)"
        elif booking['type'] == 'train':
            booking_details = f"{booking['name']} {booking['train_number']} {booking['source']}→{booking['destination']} {booking['departure_time']} - {booking['arrival_time']} ({booking['num_persons']} persons)"
        elif booking['type'] == 'hotel':
            booking_details = f"{booking['name']} in {booking['location']} ({booking['num_rooms']} rooms, {booking['num_guests']} guests, {booking['check_in_date']} to {booking['check_out_date']})"
        else:
            booking_details = "Unknown Booking"

        user_bookings[user].append({
            'type': booking['type'],
            'details': booking_details,
            'date': booking['check_in_date'] if booking['type'] == 'hotel' else booking['travel_date'],
            'booking_id': len(user_bookings[user]) + 1
        })

        return {"success": True, "message": "Booking confirmed successfully!", "redirect": url_for('dashboard')}
    else:
        return {"success": False, "message": "No booking found.", "redirect": url_for('dashboard')}

# ======== Cancel Booking Route ========
@app.route('/cancel', methods=['POST'])
def cancel_booking():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    user = session['user']
    booking_id = int(request.form['booking_id'])

    if user in user_bookings:
        user_bookings[user] = [b for b in user_bookings[user] if b['booking_id'] != booking_id]

    flash('Booking cancelled successfully.')
    return redirect(url_for('dashboard'))

# ======== Run the app ========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)