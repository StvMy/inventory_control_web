from flask import Blueprint, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import pool
import os
from datetime import datetime, timezone, timedelta

DB_PARAMS = {
    "minconn":1,
    "maxconn":5,
    "database":"asset_list",
    "user" : "postgres",
    "password" : "postgreadmin",
    "host" : os.getenv("DB_HOST"),
    "port" : "5432"
}

tables = Blueprint("tables",__name__)


def get_db_connection():
    """ Establish connection and return database connection"""
    
    return pool.ThreadedConnectionPool(**DB_PARAMS) # ** -> unpack dictionary

        
@tables.route("/tables")
def table_data():

    conn = get_db_connection().getconn()
    cur = conn.cursor()


    tab = request.args.get('tab')
    if tab is None:
        tab = "data"
    
    cur.execute("SELECT * FROM type_list")
    types = cur.fetchall()
    print("fetch")
    
    cur.execute("SELECT * FROM mutasi ORDER BY date DESC")
    mutasi = cur.fetchall()
    print("fetch")
    
    cur.execute("SELECT * FROM asset_data")
    all_asset = cur.fetchall()
    print("fetch")
    
    cur.execute("SELECT * FROM pr ORDER BY status ASC")
    pr_list = cur.fetchall()
    print("fetch")
    
    cur.execute("SELECT * FROM service_history ORDER BY date DESC")
    services = cur.fetchall()
    print("fetch")
    
    pr_sn = []
    for sn in pr_list:
        pr_sn.append(sn[1])
    print(pr_sn)
    

       
    cur.close()
    conn.close()
    print("close connection")
    
    print(tab)
    return render_template("table.html",pr_sn_list=pr_sn, item_types = types, data_asset=all_asset, data_mutasi=mutasi, service_history = services, pr=pr_list, tab=tab)



@tables.route("/delete_row_mut",methods=["POST"])
def del_row_mut():
    if request.method == "POST":    
        conn = get_db_connection().getconn()
        cur = conn.cursor()
        try:   
            sn = request.form.get("sn")
            idunique = request.form.get("id")
            
            #  1.Fetch data to display on the page
            cur.execute(
                "DELETE FROM mutasi WHERE serial = %s AND ID=%s ;",
                (sn, idunique,)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(e)

        cur.close()
        conn.close()
        
        return redirect(url_for("tables.table_data", tab="mutasi"))
    

@tables.route("/edit_row_mut",methods=["POST"])
def ed_row_mut():
    if request.method == "POST":    
        name = request.form.get("name")
        tokotertulis = request.form.get("tokotertulis")
        jenisbarang = request.form.get("jenisbarang")
        sn = request.form.get("sn")
        lokasiawal = request.form.get("lokasiawal")
        lokasitujuan = request.form.get("lokasitujuan")
        info = request.form.get("info")
        idunique = request.form.get("id")

        try:   
            conn = get_db_connection().getconn()
            cur = conn.cursor()
            
            print(f"{sn}----//----")
                
            cur.execute(  
                "UPDATE mutasi SET name=%s, item_store_name=%s, item=%s, initial=%s, destination=%s, info=%s WHERE serial=%s AND id=%s ;",
                (name, tokotertulis, jenisbarang, lokasiawal, lokasitujuan, info, sn, idunique, )
            )
            conn.commit()
            print(name, tokotertulis, jenisbarang, lokasiawal, lokasitujuan, info, sn, idunique)
            print("UPDATED")

        except psycopg2.Error as e:
            print(e)


        cur.close()
        conn.close()
        
        return redirect(url_for("tables.table_data", tab="mutasi"))


@tables.route("/delete_row_data",methods=["POST"])
def del_row_data():
    if request.method == "POST":    
        conn = get_db_connection().getconn()
        cur = conn.cursor()
        try:   
            sn = request.form.get("sn")
            
            #  1.Fetch data to display on the page
            cur.execute(
                "DELETE FROM asset_data WHERE serial_number = %s;",
                (sn.upper(),)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(e)

        cur.close()
        conn.close()
        
        return redirect(url_for("tables.table_data", tab="data"))
    
@tables.route("/edit_row_data",methods=["POST"])
def ed_row_data():
    if request.method == "POST":    
        type_item = request.form.get("type")
        sn = request.form.get("sn")
        info = request.form.get("info")
        store = request.form.get("store")  
        
        
        try:   
            conn = get_db_connection().getconn()
            cur = conn.cursor()
            
            print(f"{sn}----//----")
                
            cur.execute(  
                "UPDATE asset_data SET type = %s, information = %s, store = %s WHERE serial_number=%s;",
                (type_item, info, store, sn)
            )
            conn.commit()
            
            print("UPDATED")
        except psycopg2.Error as e:
            print(e)


        cur.close()
        conn.close()
        
        return redirect(url_for("tables.table_data", tab="data"))
    
    

@tables.route("/complete_pr",methods=["POST"])
def pr_done():
    if request.method == "POST":
        sn = request.form.get("sn")
        
        try:
            conn = get_db_connection().getconn()
            cur = conn.cursor()
            
            cur.execute(
                "UPDATE pr SET status = %s WHERE serial_number =%s;",
                ("DONE",sn.upper())
            )  
            conn.commit()    
        except psycopg2.Error as e:
            print(e)
        
        return redirect(url_for("tables.table_data", tab="pr"))

@tables.route("/delete_PR",methods=["POST"])
def pr_delete():
    if request.method == "POST":
        sn = request.form.get("sn")
        
        try:
            conn = get_db_connection().getconn()
            cur = conn.cursor()
            
            cur.execute(
                "DELETE FROM pr WHERE serial_number =%s;",
                (sn.upper(),)
            )  
            conn.commit()    
            print(f"delete PR: {sn}")
        except psycopg2.Error as e:
            print(e)
        
        return redirect(url_for("tables.table_data", tab="pr"))

@tables.route("/addPR",methods=["POST"])
def add_to_PR():
    date = datetime.now(timezone(timedelta(hours=8)))
    if request.method == "POST":
        sn = request.form.get("sn")
        try:
            print("IN FUNCTION!")
            conn = get_db_connection().getconn()
            cur = conn.cursor() 
            
            cur.execute(
                "SELECT * FROM asset_data WHERE serial_number = %s;",
                (sn,)
            )
            data_to_add = cur.fetchall()[0]
            print(data_to_add[0])
            cur.execute(
                "INSERT INTO pr (type,serial_number,information,store,status,date) values (%s,%s,%s,%s,%s,%s);",
                (data_to_add[0],data_to_add[1],data_to_add[2],data_to_add[3],"PENDING",date.strftime("%Y-%m-%d %H:%M:%S"),)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(e)
        
        return redirect(url_for("tables.table_data", tab="data"))