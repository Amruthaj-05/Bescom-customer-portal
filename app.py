from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"
DB = "users.db"

# ---------- DATABASE SETUP ----------
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Meter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                meter_id TEXT UNIQUE NOT NULL,
                Installation_date TEXT NOT NULL,
                Meter_type TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES users(customer_id)
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PowerConsumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meter_id TEXT NOT NULL,
                Consumption_id TEXT UNIQUE NOT NULL, 
                Consumption_date TEXT NOT NULL,    
                Units_Consumed TEXT NOT NULL,                
                FOREIGN KEY (meter_id) REFERENCES Meter(meter_id)
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                Consumption_id TEXT NOT NULL,
                Bill_Id TEXT UNIQUE NOT NULL,
                Amount TEXT NOT NULL,
                Due_date TEXT NOT NULL,
                Status TEXT NOT NULL, 
                FOREIGN KEY (customer_id) REFERENCES users(customer_id)
                FOREIGN KEY (Consumption_id) REFERENCES PowerConsumption(Consumption_id)
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Payment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Bill_Id TEXT NOT NULL,
                Payment_id TEXT UNIQUE,
                Payment_date TEXT,
                Payment_mode TEXT,
                Transaction_id TEXT, 
                FOREIGN KEY (Bill_Id) REFERENCES bills(Bill_Id)
            );
        """)

# ---------- ROUTES ----------

@app.route("/")
def root():
    return redirect("/home")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/help")
def help_page():
    return render_template("help.html")

@app.route("/aboutus")
def about_us():
    return render_template("aboutus.html")

@app.route("/login", methods=["POST"])
def login():
    customer_id = request.form["customer_id"]
    with sqlite3.connect(DB) as conn:
        user = conn.execute("SELECT * FROM users WHERE customer_id = ?", (customer_id,)).fetchone()
    if user:
        session["customer_id"] = customer_id
        return redirect("/dashboard")
    return render_template("customernotfound.html")


@app.route("/entry")
def entry():
    return render_template("entry.html")

@app.route("/Submit", methods=["POST"])
def Submit():
    Officer_id = request.form["Officer_id"]
    valid_officer_ids = ["OFFICER001", "OFFICER002", "ADMIN123"]
    if Officer_id in valid_officer_ids:
        session["Officer_id"] = Officer_id
        return redirect(url_for('option'))
    return render_template("invalidofficerid.html")

@app.route("/option")
def option():
    if "Officer_id" not in session:
        return redirect("/entry")
    return render_template("option.html")

@app.route("/update", methods=["GET", "POST"])
def update():
    if "Officer_id" not in session:
        return redirect("/entry")

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]
        meter_id = request.form["meter_id"]
        Installation_date = request.form["Installation_date"]
        Meter_type = request.form["Meter_type"]
        Consumption_id = request.form["Consumption_id"]
        Consumption_date = request.form["Consumption_date"]
        Units_Consumed = request.form["Units_Consumed"]
        Bill_Id = request.form["Bill_Id"]
        Amount = request.form["Amount"]
        Due_date = request.form["Due_date"]
        Status = request.form["Status"]
        Payment_id = request.form["Payment_id"] or ""
        Payment_date = request.form["Payment_date"] or ""
        Payment_mode = request.form["Payment_mode"] or ""
        Transaction_id = request.form["Transaction_id"] or ""
        with sqlite3.connect(DB) as conn:
            conn.execute("""
                UPDATE users
                SET name = ?, address = ?, phone = ?, email = ?
                WHERE customer_id = ?
            """, (name, address, phone, email, customer_id))

            conn.execute("""
                UPDATE Meter
                SET meter_id = ?, Installation_date = ?, Meter_type = ?
                WHERE customer_id = ?
            """, (meter_id,Installation_date,  Meter_type, customer_id))

            conn.execute("""
                UPDATE PowerConsumption
                SET Consumption_id = ?, Consumption_date = ?,Units_Consumed = ?
                WHERE meter_id = ?
            """, (Consumption_id,Consumption_date, Units_Consumed,meter_id))
   
            conn.execute("""
                UPDATE bills
                SET Bill_Id = ?, Amount = ?,Due_date = ?, Status = ?
                WHERE customer_id = ? and Consumption_id = ?
            """, (Bill_Id,  Amount,Due_date, Status, customer_id,Consumption_id))

            conn.execute("""
                UPDATE Payment
                SET Payment_id = ?, Payment_date  = ?,Payment_mode = ?, Transaction_id = ?
                WHERE Bill_Id = ?
            """, (Payment_id,Payment_date, Payment_mode, Transaction_id ,Bill_Id))


        return render_template("success.html", customer_id=customer_id)

    return render_template("update.html")

@app.route("/edit", methods=["POST"])
def edit():
    customer_id = request.form["customer_id"]
    with sqlite3.connect(DB) as conn:
      users = conn.execute("SELECT * FROM users WHERE customer_id = ?", (customer_id,)).fetchone()
      Meter = conn.execute("SELECT * FROM Meter WHERE customer_id = ?", (customer_id,)).fetchone()
      meter_id = Meter[2]  # assuming meter_id is the third column
      PowerConsumption = conn.execute("SELECT * FROM PowerConsumption WHERE meter_id = ?", (meter_id,)).fetchone()
      Consumption_id = PowerConsumption[2]  # assuming Consumption_id is the third column
      bills = conn.execute("SELECT * FROM bills WHERE customer_id = ? AND Consumption_id = ?", (customer_id, Consumption_id)).fetchone()
      Bill_Id = bills[3]  # assuming Bill_Id is the fourth column
      Payment = conn.execute("SELECT * FROM Payment WHERE Bill_Id = ?", (Bill_Id,)).fetchone()


    if not users or not Meter or not PowerConsumption or not bills or not Payment :
        return render_template("customernotfoundsearch.html")
    return render_template("edit.html", customer=users, Meter=Meter,PowerConsumption=PowerConsumption,bills=bills,Payment=Payment)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]
        meter_id = request.form["meter_id"]
        Installation_date = request.form["Installation_date"]
        Meter_type = request.form["Meter_type"]
        Consumption_id = request.form["Consumption_id"]
        Consumption_date = request.form["Consumption_date"]
        Units_Consumed = request.form["Units_Consumed"]
        Bill_Id = request.form["Bill_Id"]
        Amount = request.form["Amount"]
        Due_date = request.form["Due_date"]
        Status = request.form["Status"]
        Payment_id = request.form["Payment_id"] or ""
        Payment_date = request.form["Payment_date"] or ""
        Payment_mode = request.form["Payment_mode"]  or ""
        Transaction_id = request.form["Transaction_id"] or ""
        

        print(f"Creating customer: {customer_id}, Meter ID:{meter_id},Consumption ID:{Consumption_id},Bill ID: {Bill_Id},Payment ID:{Payment_id}")  # DEBUG

        with sqlite3.connect(DB) as conn:
            try:  
                conn.execute("""
                INSERT INTO users (name, address, phone, email, customer_id)
                VALUES(?,?,?,?,?)
            """, (name, address, phone, email, customer_id))

                conn.execute("""
                INSERT INTO Meter (meter_id,Installation_date,  Meter_type, customer_id)
                VALUES(?,?,?,?)
            """, (meter_id,Installation_date,  Meter_type, customer_id))

                conn.execute("""
                INSERT INTO PowerConsumption (Consumption_id,Consumption_date, Units_Consumed,meter_id)
                VALUES(?,?,?,?)
            """, (Consumption_id,Consumption_date, Units_Consumed,meter_id))
   
                conn.execute("""
                INSERT INTO bills (Bill_Id,  Amount,Due_date, Status, customer_id,Consumption_id)
                VALUES(?,?,?,?,?,?)
            """, (Bill_Id,  Amount,Due_date, Status, customer_id,Consumption_id))

                conn.execute("""
                INSERT INTO Payment (Payment_id,Payment_date, Payment_mode, Transaction_id ,Bill_Id)
                VALUES(?,?,?,?,?)
            """, (Payment_id,Payment_date, Payment_mode, Transaction_id ,Bill_Id))
                

                return redirect("/option")
            except sqlite3.IntegrityError as e:
              print("DB IntegrityError:", e)
              return render_template("alreadyexists.html")

    return render_template("create.html")

@app.route("/dashboard")
def dashboard():
    if "customer_id" not in session:
        return redirect("/index")

    customer_id = session["customer_id"]
    with sqlite3.connect(DB) as conn:
        user = conn.execute("SELECT * FROM users WHERE customer_id = ?", (customer_id,)).fetchone()

        Meter = conn.execute("SELECT * FROM Meter WHERE customer_id = ?", (customer_id,)).fetchone()

        meter_id = Meter[2]  # assuming meter_id is at index 2
        PowerConsumption = conn.execute("SELECT * FROM PowerConsumption WHERE meter_id = ?", (meter_id,)).fetchone()

        Consumption_id = PowerConsumption[2]  # assuming Consumption_id is at index 2
        bills = conn.execute("SELECT * FROM bills WHERE customer_id = ? AND Consumption_id = ?", (customer_id, Consumption_id)).fetchone()

        Bill_Id = bills[3]  # assuming Bill_Id is at index 3
        Payment = conn.execute("SELECT * FROM Payment WHERE Bill_Id = ?", (Bill_Id,)).fetchone()

         # Unpack the retrieved data (adjust indices carefully!)
        name, address, phone, email = user[2], user[3], user[4], user[5]
        meter_id, Installation_date, Meter_type = Meter[2], Meter[3], Meter[4]
        Consumption_id, Consumption_date, Units_Consumed = PowerConsumption[2], PowerConsumption[3], PowerConsumption[4]
        Bill_Id, Amount, Due_date, Status = bills[3], bills[4], bills[5], bills[6]
        Payment_id, Payment_date, Payment_mode, Transaction_id = Payment[2], Payment[3], Payment[4], Payment[5]
        return render_template("dashboard.html",
                           customer_id=customer_id,
                           name=name,
                           address=address,
                           phone=phone,
                           email=email,
                           meter_id=meter_id,
                           Installation_date=Installation_date,
                           Meter_type=Meter_type,
                           Consumption_id=Consumption_id,
                           Consumption_date=Consumption_date,
                           Units_Consumed=Units_Consumed,
                           Bill_Id=Bill_Id,
                           Amount=Amount,
                           Due_date=Due_date,
                           Status=Status,
                           Payment_id=Payment_id,
                           Payment_date=Payment_date,
                           Payment_mode=Payment_mode,
                           Transaction_id=Transaction_id)
    return "Data not found."

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("customer_id", None)
    session.pop("Officer_id", None)
    return redirect("/index")



# ---------- MAIN ----------
import webbrowser
import threading
if __name__ == "__main__":
    init_db()
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True,use_reloader=False)
