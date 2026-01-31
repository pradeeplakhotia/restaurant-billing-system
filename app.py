from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from fpdf import FPDF
import os
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Change this in production
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'Billing.db')

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Admin':
            return "Access Denied: Admin Rights Required", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user'] = user['Username']
            session['role'] = user['Role']
            
            # Redirect based on role
            if user['Role'] == 'Waiter':
                return redirect(url_for('kot'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match!')
            return redirect(url_for('change_password'))
            
        conn = get_db_connection()
        # Verify current password
        user = conn.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', 
                          (session['user'], current_password)).fetchone()
        
        if user:
            # Update password
            conn.execute('UPDATE Users SET Password = ? WHERE Username = ?', 
                       (new_password, session['user']))
            conn.commit()
            flash('Password updated successfully!')
            conn.close()
            return redirect(url_for('index'))
        else:
            conn.close()
            flash('Incorrect current password!')
            return redirect(url_for('change_password'))
            
    return render_template('change_password.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add_item', methods=('GET', 'POST'))
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        item = request.form['item']
        rate = request.form['rate']

        if not item or not rate:
            flash('Item and Rate are required!')
        else:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO Menu (item, rate) VALUES (?, ?)', (item, rate))
                conn.commit()
                flash('Item added successfully!')
            except sqlite3.IntegrityError:
                flash('Item already exists!')
            finally:
                conn.close()
            return redirect(url_for('add_item'))
            
    # Fetch existing items to show list
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Menu ORDER BY item COLLATE NOCASE ASC').fetchall()
    conn.close()

    return render_template('add_item.html', items=items)

@app.route('/update_item', methods=['POST'])
def update_item():
    item = request.form['item']
    rate = request.form['rate']
    
    if item and rate:
        conn = get_db_connection()
        conn.execute('UPDATE Menu SET rate = ? WHERE item = ?', (rate, item))
        conn.commit()
        conn.close()
        flash('Item rate updated successfully!')
        
    return redirect(url_for('add_item'))

@app.route('/delete_item', methods=['POST'])
def delete_item():
    item = request.form['item']
    if item:
        conn = get_db_connection()
        conn.execute('DELETE FROM Menu WHERE item = ?', (item,))
        conn.commit()
        conn.close()
        flash('Item deleted successfully!')
    return redirect(url_for('add_item'))

@app.route('/add_waiter', methods=('GET', 'POST'))
@login_required
@admin_required
def add_waiter():
    if request.method == 'POST':
        waiter = request.form['waiter']

        if not waiter:
            flash('Waiter name is required!')
        else:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO Headwaiter (waiter) VALUES (?)', (waiter,))
                conn.commit()
                flash('Waiter added successfully!')
            except sqlite3.IntegrityError:
                flash('Waiter already exists!')
            finally:
                conn.close()
            return redirect(url_for('add_waiter'))
            
    # Fetch existing waiters to show list
    conn = get_db_connection()
    waiters = conn.execute('SELECT * FROM Headwaiter ORDER BY waiter COLLATE NOCASE ASC').fetchall()
    conn.close()

    return render_template('add_waiter.html', waiters=waiters)

@app.route('/delete_waiter', methods=['POST'])
def delete_waiter():
    waiter = request.form['waiter']
    if waiter:
        conn = get_db_connection()
        conn.execute('DELETE FROM Headwaiter WHERE waiter = ?', (waiter,))
        conn.commit()
        conn.close()
        flash('Waiter deleted successfully!')
    return redirect(url_for('add_waiter'))

@app.route('/billing')
@login_required
@admin_required
def billing():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Menu ORDER BY item COLLATE NOCASE ASC').fetchall()
    waiters = conn.execute('SELECT * FROM Headwaiter ORDER BY waiter COLLATE NOCASE ASC').fetchall()
    
    # Get next invoice number
    last_inv = conn.execute('SELECT MAX(InvNo) FROM SaleInvMaster').fetchone()[0]
    next_inv = (last_inv or 0) + 1
    
    conn.close()
    return render_template('billing.html', items=items, waiters=waiters, next_inv=next_inv)

@app.route('/get_item_rate/<item_name>')
def get_item_rate(item_name):
    conn = get_db_connection()
    item = conn.execute('SELECT rate FROM Menu WHERE item = ?', (item_name,)).fetchone()
    conn.close()
    if item:
        return {'rate': item['rate']}
    return {'rate': 0}

@app.route('/get_invoice_details/<int:inv_no>')
def get_invoice_details(inv_no):
    try:
        conn = get_db_connection()
        master = conn.execute('SELECT * FROM SaleInvMaster WHERE InvNo = ?', (inv_no,)).fetchone()
        
        if not master:
            conn.close()
            return {'status': 'error', 'message': 'Invoice not found'}
            
        details = conn.execute('SELECT * FROM SaleInvDetails WHERE InvNo = ?', (inv_no,)).fetchall()
        conn.close()
        
        return {
            'status': 'success',
            'master': dict(master),
            'details': [dict(d) for d in details]
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/save_invoice', methods=['POST'])
def save_invoice():
    try:
        data = request.json
        master = data['master']
        details = data['details']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if Invoice Exists
        existing = cursor.execute('SELECT 1 FROM SaleInvMaster WHERE InvNo = ?', (master['InvNo'],)).fetchone()
        
        if existing:
            # UPDATE Master
            cursor.execute('''
                UPDATE SaleInvMaster SET
                    InvDate = ?, InvTime = ?, Amount = ?, CGSTPer = ?, CGST = ?, 
                    SGSTPer = ?, SGST = ?, Adjustment = ?, NetAmount = ?, Remark = ?, 
                    AmtInWords = ?, TableNo = ?, Waiter = ?
                WHERE InvNo = ?
            ''', (
                master['InvDate'], master['InvTime'], master['Amount'], master['CGSTPer'], master['CGST'], 
                master['SGSTPer'], master['SGST'], master['Adjustment'], master['NetAmount'], master['Remark'], 
                master['AmtInWords'], master['TableNo'], master['Waiter'], master['InvNo']
            ))
            
            # Delete old details to replace (simplest update strategy)
            cursor.execute('DELETE FROM SaleInvDetails WHERE InvNo = ?', (master['InvNo'],))
            
        else:
            # INSERT New Master
            cursor.execute('''
                INSERT INTO SaleInvMaster (
                    InvNo, InvDate, InvTime, Amount, CGSTPer, CGST, 
                    SGSTPer, SGST, Adjustment, NetAmount, Remark, 
                    AmtInWords, TableNo, Waiter
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                master['InvNo'], master['InvDate'], master['InvTime'], 
                master['Amount'], master['CGSTPer'], master['CGST'], 
                master['SGSTPer'], master['SGST'], master['Adjustment'], 
                master['NetAmount'], master['Remark'], master['AmtInWords'], 
                master['TableNo'], master['Waiter']
            ))
        
        # Save Details (New or Replaced)
        for item in details:
            cursor.execute('''
                INSERT INTO SaleInvDetails (InvNo, Item, Rate, Qty, Amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (master['InvNo'], item['Item'], item['Rate'], item['Qty'], item['Amount']))
            
        # Update KOT: Mark as Billed
        if master['TableNo']:
            cursor.execute('''
                UPDATE KOT 
                SET BillMade = 'Yes' 
                WHERE TableNo = ? AND BillMade = 'No'
            ''', (master['TableNo'],))
        
        conn.commit()
        conn.close()
        
        # Generate PDF
        pdf_path = generate_pdf(master, details)
        
        return {'status': 'success', 'message': 'Invoice saved successfully!', 'pdf_url': pdf_path}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/delete_invoice/<int:inv_no>', methods=['POST'])
def delete_invoice(inv_no):
    try:
        conn = get_db_connection()
        
        # Check if exists
        exists = conn.execute('SELECT 1 FROM SaleInvMaster WHERE InvNo = ?', (inv_no,)).fetchone()
        if not exists:
            conn.close()
            return {'status': 'error', 'message': 'Invoice not found'}
            
        # Delete
        conn.execute('DELETE FROM SaleInvDetails WHERE InvNo = ?', (inv_no,))
        conn.execute('DELETE FROM SaleInvMaster WHERE InvNo = ?', (inv_no,))
        
        conn.commit()
        conn.close()
        
        return {'status': 'success', 'message': 'Invoice deleted successfully'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# --- KOT Routes ---

@app.route('/kot')
@login_required
def kot():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Menu ORDER BY item COLLATE NOCASE ASC').fetchall()
    conn.close()
    return render_template('kot.html', items=items)

@app.route('/get_next_kot_no')
def get_next_kot_no():
    conn = get_db_connection()
    last_no = conn.execute('SELECT MAX(EntryNo) FROM KOT').fetchone()[0]
    conn.close()
    next_no = (last_no or 0) + 1
    return {'next_no': next_no}

@app.route('/kot_action', methods=['POST'])
def kot_action():
    try:
        data = request.json
        action = data.get('action')
        conn = get_db_connection()
        
        if action == 'save':
            conn.execute('''
                INSERT INTO KOT (EntryDate, EntryTime, TableNo, Item, Qty, BillMade, KOTPrinted)
                VALUES (?, ?, ?, ?, ?, 'No', 'No')
            ''', (data['date'], data['time'], data['tableNo'], data['item'], data['qty']))
            
        elif action == 'update':
            conn.execute('''
                UPDATE KOT 
                SET Item = ?, Qty = ?, TableNo = ? 
                WHERE EntryNo = ?
            ''', (data['item'], data['qty'], data['tableNo'], data['entryNo']))
            
        elif action == 'delete':
            conn.execute('DELETE FROM KOT WHERE EntryNo = ?', (data['entryNo'],))
        
        conn.commit()
        conn.close()
        return {'status': 'success', 'message': f'KOT {action}d successfully'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/get_pending_kot_items/<table_no>')
def get_pending_kot_items(table_no):
    try:
        conn = get_db_connection()
        # Aggregate items by name, summing quantity
        rows = conn.execute('''
            SELECT Item, SUM(Qty) as TotalQty 
            FROM KOT 
            WHERE TableNo = ? AND BillMade = 'No' 
            GROUP BY Item
        ''', (table_no,)).fetchall()
        
        items = []
        for row in rows:
            item_name = row['Item']
            qty = row['TotalQty']
            
            # Fetch rate from Menu
            menu_item = conn.execute('SELECT rate FROM Menu WHERE item = ?', (item_name,)).fetchone()
            rate = menu_item['rate'] if menu_item else 0
            
            items.append({
                'item': item_name,
                'qty': qty,
                'rate': rate,
                'amount': qty * rate
            })
            
        conn.close()
        return {'status': 'success', 'items': items}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/get_kot_data')
def get_kot_data():
    conn = get_db_connection()
    # Get recent entries (last 50 for example, or all if not too many)
    entries = conn.execute('SELECT * FROM KOT ORDER BY EntryNo DESC LIMIT 100').fetchall()
    
    # Get running tables (Distinct tables where BillMade is 'No')
    running_tables = conn.execute('''
        SELECT DISTINCT TableNo FROM KOT 
        WHERE BillMade = 'No' 
        ORDER BY TableNo
    ''').fetchall()
    
    conn.close()
    
    return {
        'entries': [dict(row) for row in entries],
        'running_tables': [row['TableNo'] for row in running_tables]
    }

# --- Sales Report Routes ---

@app.route('/sales_report')
@login_required
@admin_required
def sales_report():
    conn = get_db_connection()
    # Table name is Headwaiter
    waiters = conn.execute('SELECT * FROM Headwaiter ORDER BY waiter').fetchall()
    conn.close()
    return render_template('sales_report.html', waiters=waiters)

@app.route('/generate_sales_report', methods=['POST'])
def generate_sales_report():
    try:
        data = request.json
        report_type = data.get('type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        waiter = data.get('waiter')
        
        conn = get_db_connection()
        query = "SELECT InvNo, InvDate, InvTime, Waiter, NetAmount FROM SaleInvMaster WHERE 1=1"
        params = []
        
        if report_type == 'datewise':
            query += " AND InvDate BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif report_type == 'waiterwise':
            query += " AND InvDate BETWEEN ? AND ? AND Waiter = ?"
            params.extend([start_date, end_date, waiter])
            
        rows = conn.execute(query, params).fetchall()
        conn.close()
        
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "Sales Report", ln=True, align='C')
        
        # Subheader
        pdf.set_font("Arial", size=10)
        subtitle = f"Type: {report_type.capitalize().replace('_', ' ')}"
        
        if report_type != 'complete' and start_date and end_date:
            # Reformat header dates too if valid
            try:
                s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                subtitle += f" | From: {s_date} To: {e_date}"
            except:
                subtitle += f" | From: {start_date} To: {end_date}"
                
        if report_type == 'waiterwise' and waiter:
            subtitle += f" | Waiter: {waiter}"
            
        pdf.cell(190, 8, subtitle, ln=True, align='C')
        pdf.ln(5)
        
        # Table Header
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(30, 10, "Inv No", 1, 0, 'C', 1)
        pdf.cell(40, 10, "Date", 1, 0, 'C', 1)
        pdf.cell(30, 10, "Time", 1, 0, 'C', 1)
        pdf.cell(50, 10, "Waiter", 1, 0, 'L', 1)
        pdf.cell(40, 10, "Net Amt", 1, 1, 'R', 1)
        
        # Rows
        pdf.set_font("Arial", size=10)
        total_net_amt = 0
        for row in rows:
            # Format Date dd-mm-yyyy
            try:
                date_obj = datetime.datetime.strptime(row['InvDate'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d-%m-%Y')
            except:
                formatted_date = str(row['InvDate']) # Fallback

            pdf.cell(30, 10, str(row['InvNo']), 1, 0, 'C')
            pdf.cell(40, 10, formatted_date, 1, 0, 'C')
            pdf.cell(30, 10, str(row['InvTime']), 1, 0, 'C')
            pdf.cell(50, 10, str(row['Waiter']), 1, 0, 'L')
            pdf.cell(40, 10, str(row['NetAmount']), 1, 1, 'R')
            total_net_amt += row['NetAmount']
            
        # Total Row
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(150, 10, "Total Net Amount:", 1, 0, 'R')
        pdf.cell(40, 10, f"{total_net_amt:.2f}", 1, 1, 'R')
        
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        filename = f"sales_report_{report_type}.pdf"
        filepath = os.path.join(reports_dir, filename)
        pdf.output(filepath)
        
        # Check if email is requested
        if data.get('send_email') and data.get('recipient_email'):
            recipient = data.get('recipient_email')
            subject = f"Sales Report - {report_type.capitalize()}"
            body = "Please find attached the generated sales report."
            
            email_result = send_email_with_attachment(recipient, subject, body, filepath, filename)
            if email_result['status'] == 'error':
                 return email_result # Return error if email failed
                 
            return {'status': 'success', 'message': 'Email sent successfully'}

        return {'status': 'success', 'pdf_url': f"/static/reports/{filename}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

@app.route('/reprint_invoice/<int:inv_no>')
def reprint_invoice(inv_no):
    filename = f"inv_{inv_no}.pdf"
    filepath = os.path.join(BASE_DIR, 'static', 'invoices', filename)
    
    # 1. Check if file exists
    if os.path.exists(filepath):
        return {'status': 'success', 'pdf_url': f"/static/invoices/{filename}"}
        
    # 2. If not, regenerate from DB
    try:
        conn = get_db_connection()
        master = conn.execute('SELECT * FROM SaleInvMaster WHERE InvNo = ?', (inv_no,)).fetchone()
        
        if not master:
            conn.close()
            return {'status': 'error', 'message': 'Invoice not found'}
            
        details_rows = conn.execute('SELECT * FROM SaleInvDetails WHERE InvNo = ?', (inv_no,)).fetchall()
        conn.close()
        
        # Convert rows to dicts for generate_pdf
        master_dict = dict(master)
        details_list = [dict(row) for row in details_rows]
        
        # generate_pdf expects details keys as Item, Rate, Qty, Amount (Capitals) or whatever matches DB cols
        # DB cols are capitalized in Create Table? Let's check init_db.
        # SaleInvDetails: InvNo, Item, Rate, Qty, Amount. Yes capitalized.
        # Row factory returns matches column names.
        
        pdf_path = generate_pdf(master_dict, details_list)
        return {'status': 'success', 'pdf_url': pdf_path}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

# --- Bulk Rate Update ---

@app.route('/bulk_update')
@login_required
@admin_required
def bulk_update():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Menu ORDER BY item COLLATE NOCASE ASC').fetchall()
    conn.close()
    return render_template('bulk_update.html', items=items)

@app.route('/update_rate_fast', methods=['POST'])
def update_rate_fast():
    try:
        data = request.json
        item = data.get('item')
        rate = data.get('rate')
        
        conn = get_db_connection()
        conn.execute('UPDATE Menu SET rate = ? WHERE item = ?', (rate, item))
        conn.commit()
        conn.close()
        
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# --- Summary Report ---

@app.route('/summary_report')
@login_required
@admin_required
def summary_report():
    return render_template('summary_report.html')

@app.route('/generate_summary_report', methods=['POST'])
def generate_summary_report():
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        conn = get_db_connection()
        # Aggregate logic
        rows = conn.execute('''
            SELECT InvDate, SUM(NetAmount) as DailyTotal
            FROM SaleInvMaster
            WHERE InvDate BETWEEN ? AND ?
            GROUP BY InvDate
            ORDER BY InvDate
        ''', (start_date, end_date)).fetchall()
        conn.close()
        
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "Daily Summary Report", ln=True, align='C')
        
        # Subheader
        pdf.set_font("Arial", size=10)
        try:
            s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            subtitle = f"From: {s_date} To: {e_date}"
        except:
            subtitle = f"From: {start_date} To: {end_date}"
        
        pdf.cell(190, 8, subtitle, ln=True, align='C')
        pdf.ln(5)
        
        # Table Header
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(220, 255, 220) # Light green
        pdf.cell(45, 10, "", 0, 0) # Indent
        pdf.cell(50, 10, "Date", 1, 0, 'C', 1)
        pdf.cell(50, 10, "Total Amount", 1, 1, 'R', 1)
        
        # Rows
        pdf.set_font("Arial", size=11)
        grand_total = 0
        for row in rows:
            try:
                d_str = datetime.datetime.strptime(row['InvDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
            except:
                d_str = row['InvDate']
                
            pdf.cell(45, 10, "", 0, 0) # Indent
            pdf.cell(50, 10, d_str, 1, 0, 'C')
            pdf.cell(50, 10, f"{row['DailyTotal']:.2f}", 1, 1, 'R')
            grand_total += row['DailyTotal']
            
        pdf.ln(2)
        
        # Grand Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(45, 10, "", 0, 0) # Indent
        pdf.cell(50, 10, "Grand Total:", 1, 0, 'R')
        pdf.cell(50, 10, f"{grand_total:.2f}", 1, 1, 'R')
        
        reports_dir = os.path.join(BASE_DIR, 'static', 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        filename = f"summary_{start_date}_{end_date}.pdf"
        filepath = os.path.join(reports_dir, filename)
        pdf.output(filepath)
        
        return {'status': 'success', 'pdf_url': f"/static/reports/{filename}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

# --- Sale Details Report Routes ---

@app.route('/sale_details_report')
@login_required
@admin_required
def sale_details_report():
    return render_template('sale_details_report.html')

@app.route('/generate_sale_details_report', methods=['POST'])
def generate_sale_details_report():
    try:
        data = request.json
        report_type = data.get('type') # 'summary' or 'details'
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        conn = get_db_connection()
        
        if report_type == 'summary':
            # Aggregate Qty by Item
            rows = conn.execute('''
                SELECT 
                    D.Item, 
                    SUM(D.Qty) as TotalQty, 
                    SUM(D.Amount) as TotalAmount
                FROM SaleInvDetails D
                JOIN SaleInvMaster M ON D.InvNo = M.InvNo
                WHERE M.InvDate BETWEEN ? AND ?
                GROUP BY D.Item
                ORDER BY TotalQty DESC
            ''', (start_date, end_date)).fetchall()
            
            headers = ["Item Name", "Total Qty", "Total Amount"]
            col_widths = [80, 40, 50]
            aligns = ['L', 'C', 'R']
            
            data_rows = []
            grand_qty = 0
            grand_amt = 0
            for row in rows:
                data_rows.append([
                    row['Item'],
                    str(row['TotalQty']),
                    f"{row['TotalAmount']:.2f}"
                ])
                grand_qty += row['TotalQty']
                grand_amt += row['TotalAmount']
                
            # Add Total Row
            data_rows.append(["TOTAL", str(grand_qty), f"{grand_amt:.2f}"])
            
        elif report_type == 'details':
            # Detailed list
            rows = conn.execute('''
                SELECT 
                    M.InvNo, M.InvDate, M.Waiter, 
                    D.Item, D.Qty, D.Amount
                FROM SaleInvDetails D
                JOIN SaleInvMaster M ON D.InvNo = M.InvNo
                WHERE M.InvDate BETWEEN ? AND ?
                ORDER BY D.Item, M.InvDate
            ''', (start_date, end_date)).fetchall()
            
            headers = ["InvNo", "Date", "Waiter", "Item", "Qty", "Amount"]
            col_widths = [20, 30, 40, 60, 20, 20]
            aligns = ['C', 'C', 'L', 'L', 'C', 'R']
            
            data_rows = []
            current_item = None
            item_qty = 0
            item_amt = 0
            
            for row in rows:
                # Add a separator or header for new item group if desired, 
                # or just list them. The user said "grouped by item" potentially implied by "same details of the next item".
                # Let's list everything sorted by Item as realized in Query.
                
                # To make it readable, maybe print Item name only when it changes?
                # Or just print simple table. 
                # "in the details it may opeen a new report in which it will display invno, invdate, waiter, item and qty and subtotal"
                
                try:
                    d_str = datetime.datetime.strptime(row['InvDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
                except:
                    d_str = row['InvDate']
                    
                data_rows.append([
                    str(row['InvNo']),
                    d_str,
                    row['Waiter'],
                    row['Item'],
                    str(row['Qty']),
                    f"{row['Amount']:.2f}"
                ])
        
        conn.close()
        
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        title = "Item Sale Summary" if report_type == 'summary' else "Item Sale Details"
        pdf.cell(190, 10, title, ln=True, align='C')
        
        pdf.set_font("Arial", size=10)
        try:
             s_d = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d-%m-%Y')
             e_d = datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%m-%Y')
             subtitle = f"From: {s_d} To: {e_d}"
        except:
             subtitle = f"From: {start_date} To: {end_date}"
             
        pdf.cell(190, 8, subtitle, ln=True, align='C')
        pdf.ln(5)
        
        # Table Header
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, 1, 0, aligns[i], 1)
        pdf.ln()
        
        # Rows
        pdf.set_font("Arial", size=10)
        for row in data_rows:
            is_total_row = (row[0] == "TOTAL")
            if is_total_row:
                 pdf.set_font("Arial", 'B', 10)
                 
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 10, str(val), 1, 0, aligns[i])
            pdf.ln()
            
        reports_dir = os.path.join(BASE_DIR, 'static', 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        filename = f"sale_details_{report_type}_{start_date}_{end_date}.pdf"
        filepath = os.path.join(reports_dir, filename)
        pdf.output(filepath)
        
        return {'status': 'success', 'pdf_url': f"/static/reports/{filename}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

def generate_pdf(master, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Restaurant Billing System", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="123 Food Street, Tasty City", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Invoice Details
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, f"Invoice No: {master['InvNo']}", 0, 0)
    pdf.cell(100, 10, f"", 0, 0) # Spacer
    pdf.cell(60, 10, f"Date: {master['InvDate']} {master['InvTime']}", 0, 1)
    
    pdf.cell(30, 10, f"Table No: {master['TableNo']}", 0, 0)
    pdf.cell(100, 10, f"", 0, 0) # Spacer
    pdf.cell(60, 10, f"Waiter: {master['Waiter']}", 0, 1)
    pdf.ln(5)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(80, 10, "Item", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Rate", 1, 0, 'R', 1)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Amount", 1, 1, 'R', 1)
    
    # Table Rows
    pdf.set_font("Arial", size=10)
    for item in details:
        pdf.cell(80, 10, str(item['Item']), 1, 0, 'L')
        pdf.cell(30, 10, str(item['Rate']), 1, 0, 'R')
        pdf.cell(20, 10, str(item['Qty']), 1, 0, 'C')
        pdf.cell(40, 10, str(item['Amount']), 1, 1, 'R')
        
    pdf.ln(5)
    
    # Totals
    def add_total_row(label, value, bold=False):
        pdf.set_font("Arial", 'B' if bold else '', 10)
        pdf.cell(130, 8, label, 0, 0, 'R')
        pdf.cell(40, 8, str(value), 1, 1, 'R')

    add_total_row("Total Amount:", master['Amount'])
    if master['CGST'] > 0:
        add_total_row(f"CGST ({master['CGSTPer']}%) :", master['CGST'])
    if master['SGST'] > 0:
        add_total_row(f"SGST ({master['SGSTPer']}%) :", master['SGST'])
    if master['Adjustment'] != 0:
        add_total_row("Adjustment:", master['Adjustment'])
    add_total_row("Net Amount:", master['NetAmount'], bold=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Amount in Words: {master['AmtInWords']}", 0, 1)
    
    if master['Remark']:
        pdf.cell(0, 10, f"Remark: {master['Remark']}", 0, 1)
        
    pdf.ln(10)
    pdf.cell(0, 10, "Thank you for visiting!", 0, 1, 'C')
    
    invoices_dir = os.path.join(BASE_DIR, 'static', 'invoices')
    if not os.path.exists(invoices_dir):
        os.makedirs(invoices_dir)
        
    filename = f"inv_{master['InvNo']}.pdf"
    filepath = os.path.join(invoices_dir, filename)
    pdf.output(filepath)
    return f"/static/invoices/{filename}"

# --- Email Configuration ---
# REPLACE THESE WITH YOUR ACTUAL DETAILS
SENDER_EMAIL = "pradeeplakhotia63@gmail.com" 
APP_PASSWORD = "your_16_char_app_password"

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Helper function for sending email
def send_email_with_attachment(recipient_email, subject, body, attachment_path, attachment_name):
    try:
        if not os.path.exists(attachment_path):
            return {'status': 'error', 'message': 'Attachment file not found.'}

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="pdf")
            attach.add_header('Content-Disposition','attachment',filename=attachment_name)
            msg.attach(attach)

        # Send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return {'status': 'success'}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

@app.route('/send_email_invoice', methods=['POST'])
def send_email_invoice():
    data = request.json
    inv_no = data.get('inv_no')
    recipient_email = data.get('email')
    
    if not inv_no or not recipient_email:
        return {'status': 'error', 'message': 'Invoice No and Email are required'}
        
    filename = f"inv_{inv_no}.pdf"
    filepath = os.path.join(BASE_DIR, 'static', 'invoices', filename)
    
    subject = f"Invoice #{inv_no} from Restaurant Billing System"
    body = f"Dear Customer,\n\nPlease find attached the invoice #{inv_no} for your recent visit.\n\nThank you for dining with us!\n\nRegards,\nRestaurant Team"
    
    result = send_email_with_attachment(recipient_email, subject, body, filepath, filename)
    if result['status'] == 'success':
         return {'status': 'success', 'message': f'Email sent successfully to {recipient_email}'}
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
