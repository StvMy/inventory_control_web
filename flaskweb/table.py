from flask import Blueprint, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import pool
import os

DB_PARAMS = {
    "minconn":1,
    "maxconn":10,
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
    
    cur.execute("SELECT * FROM type_list")
    types = cur.fetchall()
    
    cur.execute("SELECT * FROM mutasi ORDER BY date DESC")
    mutasi = cur.fetchall()
    
    cur.execute("SELECT * FROM asset_data")
    all_asset = cur.fetchall()
    
    cur.execute("SELECT * FROM pr ORDER BY status ASC")
    pr_list = cur.fetchall()
    
    cur.execute("SELECT * FROM service_history ORDER BY date DESC")
    services = cur.fetchall()
    
    cur.close()
    conn.close()

    return render_template("table.html",item_types = types, data_asset=all_asset, data_mutasi=mutasi, service_history = services, pr=pr_list)



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
            return redirect(url_for("tables.table_data", tab="pr"))
        except psycopg2.Error as e:
            print(e)
                      