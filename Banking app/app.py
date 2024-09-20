from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import yaml

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

def load_users():
    with open('users.yaml', 'r') as file:
        return yaml.safe_load(file)

def save_users(users_data):
    with open('users.yaml', 'w') as file:
        yaml.dump(users_data, file)

@app.route('/')
def home_redirect():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Handle login form submission
        name = request.form['name']
        password = request.form['password']
        users = load_users()['people']
        user = next((u for u in users if u['name'] == name and u['password'] == password), None)
        
        if user:
            session['name'] = user['name']
            return redirect('/dashboard')
        else:
            return render_template('home.html', error="Invalid credentials.")  # Show error if login fails

    # For GET requests, show the home page
    return render_template('home.html')

import yaml

def add_user_to_database(new_user):
    with open('users.yaml', 'r') as file:
        data = yaml.safe_load(file)
    data['people'].append(new_user)
    with open('users.yaml', 'w') as file:
        yaml.safe_dump(data, file)
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        print(request.form)  # This will show the incoming form data
        new_user = {
            'age': request.form['age'],
            'balance': 0.0,
            'gender': request.form['gender'],
            'id': request.form['id'],  # Ensure this matches your form
            'mobile_no.': request.form['mobile_no.'],
            'name': request.form['name'],
            'password': request.form['password']
        }
        add_user_to_database(new_user)
        flash("Account created successfully!")
        return redirect(url_for('login'))

    return render_template('create_account.html')

with open('users.yaml') as f:
    users_data = yaml.safe_load(f)
    users = {user['name']: user for user in users_data['people']}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        
        # Check if the user exists and the password is correct
        if name in users and users[name]['password'] == password:
            session['name'] = name  # Store the user's name in the session
            return redirect(url_for('user_dashboard'))  # Redirect to the dashboard
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)  # Render login page with error

    return render_template('login.html')  # Render login page for GET requests
import yaml
import yaml

def get_user_by_id(user_id):
    with open('users.yaml', 'r') as file:
        data = yaml.safe_load(file)
        for user in data['people']:
            if user['id'] == user_id:
                return user
    return None

def get_user_by_name(name):
    with open('users.yaml', 'r') as file:
        data = yaml.safe_load(file)

    # Search for the user by name in the YAML data
    for person in data['people']:
        if person['name'] == name:
            return person
    
    # If no user is found, return None
    return None
import yaml

def update_user_in_database(updated_user):
    with open('users.yaml', 'r') as file:
        data = yaml.safe_load(file)

    # Update the user's information in the YAML data
    for person in data['people']:
        if person['name'] == updated_user['name']:
            person.update(updated_user)
            break

    # Write the updated data back to the YAML file
    with open('users.yaml', 'w') as file:
        yaml.safe_dump(data, file)

@app.route('/dashboard')
def user_dashboard():
    if 'name' in session:
        logged_in_user = users[session['name']]  # Fetch user info
        return render_template('dashboard.html', user=logged_in_user)
    return redirect(url_for('login'))
@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if 'name' not in session:
        return redirect(url_for('login'))

    logged_in_user = get_user_by_name(session['name'])

    if request.method == 'POST':
        recipient_id = request.form['recipient_id']
        amount = float(request.form['amount'])

        recipient = get_user_by_id(recipient_id)

        if not recipient:
            flash("Recipient not found.")
            return render_template('pay.html')

        if logged_in_user['balance'] >= amount:
            logged_in_user['balance'] -= amount
            recipient['balance'] += amount

            update_user_in_database(logged_in_user)
            update_user_in_database(recipient)

            flash("Payment successful.")
        else:
            flash("Insufficient balance.")

    return render_template('pay.html', user=logged_in_user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'name' in session:
        users_data = load_users()  # Load users data here

        if request.method == 'POST':
            name = session['name']  # Get the user name from session
            amount = request.form.get('amount')

            if name and amount:
                try:
                    amount = float(amount)
                    
                    # Update user balance
                    user_found = False
                    for person in users_data['people']:
                        if person['name'] == name:
                            person['balance'] += amount
                            user_found = True
                            break
                    
                    if user_found:
                        # Save changes back to YAML
                        save_users(users_data)
                        
                        # Pop-up message
                        return '''
                            <script>
                                alert('Deposit successful! Your new balance is: ''' + str(person['balance']) + '''');
                                window.location.href = '/dashboard';  // Redirect to dashboard after alert
                            </script>
                        '''
                    else:
                        return render_template('deposit.html', error="User not found.")

                except ValueError:
                    return render_template('deposit.html', error="Please enter a valid amount.")
            else:
                return render_template('deposit.html', error="Please provide a valid amount.")
        
        return render_template('deposit.html')
    else:
        return redirect(url_for('login'))

@app.route('/check_balance', methods=['GET'])
def check_balance():
    if 'name' in session:
        users = load_users()
        
        logged_in_user = next((user for user in users['people'] if user['name'] == session['name']), None)
        
        if logged_in_user:
            return render_template('check_balance.html', balance=logged_in_user['balance'])
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('dashboard'))
    else:
        flash('You must be logged in to check your balance.', 'danger')
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.pop('name', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to home after logout

if __name__ == '__main__':
    app.run(debug=True)
