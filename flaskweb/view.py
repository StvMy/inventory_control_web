from flask import Blueprint, render_template,request,redirect,url_for,flash
from datetime import datetime
import psycopg2
import os

DB_PARAMS = {
    "database":"asset_list",
    "user" : "postgres",
    "password" : "postgreadmin",
    "host" : os.getenv("DB_HOST"),
    "port" : "5432"
}

views = Blueprint('views',__name__)


print(DB_PARAMS)

def get_db_connection():
    """ Establish connection and return database connection"""
    return psycopg2.connect(**DB_PARAMS) # ** -> unpack dictionary

        
@views.route('/home')
def home():
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try: 
        conn = get_db_connection()
    except psycopg2.Error:
        return render_template("404.html")
    
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM type_list"
    )
    all_asset = cur.fetchall()
    cur.execute(
        "SELECT * FROM asset_data"
    )
    table = cur.fetchall()
    cur.execute(
        "SELECT * FROM mutasi"
    )
    mutasi = cur.fetchall()
    cur.execute(
    "SELECT * FROM service_history"
    )
    services = cur.fetchall()
    
    cur.close()
    conn.close()
    print(f"data tabel: {table}")
    print(f"type list: {all_asset}")
    print(f"mutasi list: {mutasi}")
    print(f"service: {services}")
    return render_template("page_mutasi.html",data_asset=all_asset) 


@views.route('/submit', methods=["POST"])
def submission():
    """ CONNECT TO DATABASE """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Submission
    if request.method == "POST":
        
        # 2. Declare Variable
        username = request.form.get("usernamein")
        serial = request.form.get("serialin")
        store = request.form.get("storein")
        info = request.form.get("commentin")
        type_item = request.form.get("item")
        date = datetime.now()
        try:
            cur.execute(
                "SELECT * FROM asset_data WHERE Serial_Number = %s",
                (serial.upper(),)
            )
            if (cur.fetchall()):
                print("FLASSHH-----------------------------///////")
                flash("Nomor Serial sudah terdaftar","error")
            else:
                # 3. Execute SQL
                cur.execute(
                    "INSERT INTO asset_data (Type,Serial_Number,store, Information) Values(%s,%s,%s,%s);",
                    (type_item.upper(),serial.upper(),store.upper(),info.upper(),)
                )
                conn.commit()
                cur.execute(
                    "INSERT INTO mutasi (date, serial, initial, destination, info, name, item, item_store_name) Values(%s,%s,%s,%s,%s,%s,%s,%s);",
                    (date.strftime("%Y-%m-%d %H:%M:%S"),serial.upper(),"VENDOR","IT",info.upper(),username.upper(),type_item.upper(), store.upper())
                )
                # 3. Commit changes and close connections
                conn.commit()
                cur.close()
                conn.close()
            
        except psycopg2.Error as e:
            print (e)
            conn.rollback()  # important: clear failed transaction
            cur.close()
            conn.close()
        return redirect(url_for("views.home"))
       
    
@views.route('/add_type', methods=["POST"])
def submission_type():
    """ CONNECT TO DATABASE """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Submission
    if request.method == "POST":
        type_add =request.form.get("add_type")
        if type_add:
            try:
                cur.execute(
                    "SELECT * FROM type_list WHERE types = %s",
                    (type_add.upper(),)
                )
                if(cur.fetchall()):
                    flash("Nomor Serial sudah terdaftar","error")
                else:              
                    cur.execute(
                        "INSERT INTO type_list (types) values(%s);",
                        (type_add.upper(),)
                    )
                    
                    # 3. Commit changes and close connections
                    conn.commit()
                    cur.close()
                    conn.close()
                
            except psycopg2.Error:
                conn.rollback()  # important: clear failed transaction
                cur.close()
                conn.close()
        return redirect(request.referrer)
    
@views.route('/remove_type', methods=["POST"])
def submission_remove_type():
    """ CONNECT TO DATABASE """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Submission
    if request.method == "POST":
        data = request.get_json()
        type_remove = data["type"]
        print(type_remove)
        try:
            cur.execute(
                "SELECT types FROM type_list WHERE types = %s ",
                (type_remove.upper(),)
            )
            if(cur.fetchall()):
                cur.execute(
                    "DELETE FROM type_list WHERE types = %s ",
                    (type_remove.upper(),)
                )
                
                # 3. Commit changes and close connections
                conn.commit()
                cur.close()
                conn.close()
                print("OK")
            else:
                flash("Nomor Serial tidak terdaftar","error")
        except psycopg2.Error as e:
            print(e)
            conn.rollback()  # important: clear failed transaction
            cur.close()
            conn.close()

    return redirect(request.referrer)
   
    
@views.route('/out_item', methods=["POST"])
def submission_out():
    """ CONNECT TO DATABASE """
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Submission
    if request.method == "POST":
        username = request.form.get("usernameout")
        serial = request.form.get("serialout")
        store = request.form.get("storeout")
        info = request.form.get("commentout")
        date = datetime.now()
        try:

            cur.execute(
                "SELECT type,store FROM asset_data WHERE serial_number = %s ;",
                (serial.upper(),)
            )
            data = cur.fetchall() 
            if data:
                print(f"data: ----------{data[0][0]}-----------")
                cur.execute(
                    "INSERT INTO mutasi (date,serial, initial, destination, info, name, item, item_store_name) Values(%s,%s,%s,%s,%s,%s,%s,%s);",
                    (date.strftime("%Y-%m-%d %H:%M:%S"),serial.upper(),"IT",store.upper(),info.upper(),username.upper(),data[0][0].upper(), data[0][1].upper(),)
                )
                # Commit changes
                conn.commit()
                
                cur.execute( 
                    "DELETE FROM asset_data WHERE serial_number = %s ;",
                    (serial.upper(),)
                )
                conn.commit()
                cur.close()
                conn.close()
                return redirect(request.referrer)
            else:
                flash("Nomor Serial tidak terdaftar","error")
                return(redirect(url_for("views.home")))
        except psycopg2.Error as e:
            print(e)
            conn.rollback()  # important: clear failed transaction
            cur.close()
            conn.close()
            return redirect(request.referrer)

  
    
@views.route('/service', methods=["POST"])
def submission_service():    
    """ CONNECT TO DATABASE """
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        username = request.form.get("usernameservice")
        serial = request.form.get("serialservice")
        info = request.form.get("commentservice")
        date = datetime.now()
        try:
            cur.execute(
                "SELECT type FROM asset_data WHERE serial_number = %s",
                (serial.upper(),)
            )
            data_serial = cur.fetchall()
            if data_serial:
                print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%{data_serial[0]}")
                cur.execute(
                    "INSERT INTO service_history (username,serial,info,item,date) Values(%s,%s,%s,%s,%s); ",
                    (username.upper(),serial.upper(),info.upper(),data_serial[0],date.strftime("%Y-%m-%d %H:%M:%S"),)
                )
                conn.commit()
                
                cur.execute(
                    "SELECT information FROM asset_data WHERE serial_number = %s ",
                    (serial.upper(),)
                )
                current_info = cur.fetchall()
                cur.execute(
                    "UPDATE asset_data set information = %s WHERE serial_number = %s ",
                    (f"{current_info[0]},SUDAH DIPERBAIKI",serial.upper(),)
                )
                conn.commit()
                cur.close()
                conn.close()
                return redirect(request.referrer)
            else:
                flash("Nomor Serial tidak terdaftar","error")
                return redirect(url_for("views.home"))
        except psycopg2.Error as e:
            print(e)
            conn.rollback()  # important: clear failed transaction
            cur.close()
            conn.close() 
            return redirect(request.referrer) 
    
    
    

# @views.route('/mutasi', methods=["POST"])
# def submission_mutasi():    
#     """ CONNECT TO DATABASE """
#     conn = get_db_connection()
#     cur = conn.cursor()
#     if request.method == "POST":
#         username = request.form.get("usernamemutasi")
#         serial = request.form.get("serialmutasi")
#         store = request.form.get("storemutasi")
#         info = request.form.get("commentmutasi")
        
#         try:
#             cur.execute(
#                 "SELECT "
#             )
#         except psycopg2.Error as e:
#             print(e)
#             conn.rollback()  # important: clear failed transaction
#             cur.close()
#             conn.close()
            
