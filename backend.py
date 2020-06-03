#!python3
import csv
import sqlite3
from datetime import *


def connectsqlite():
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS bills ( `Bill no` TEXT PRIMARY KEY, `Date` TEXT, `Name` TEXT, `Address` TEXT, Product TEXT, Qauntity INTEGER , Price INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS inventory ( `product` TEXT PRIMARY KEY, Price INTEGER , Stock INTEGER)")
    conn.commit()
    conn.close()

def insert(billNo, date, name, address, product, Qauntity, price):
    conn = sqlite3.connect("BillData.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?)", (billNo, date, name, address, product, Qauntity, price))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    

def viewall():
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM bills")
    data = cur.fetchall()
    conn.close()
    return data

def viewallinv():
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    data = cur.fetchall()
    conn.close()
    return data

def search(billNo = "", name = "", address = ""):
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM bills WHERE `Bill no` = ? OR `Name` = ? OR `Address` = ?", (billNo, name, address))
    data = cur.fetchall()
    conn.close()
    return data

def delete(BillNo):
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("DELETE FROM bills WHERE `Bill no` = ?", (BillNo,))
    conn.commit()
    conn.close()

def generatebillno():
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM bills")
    try:
        data = cur.fetchall()[-1]
    except IndexError:
        data = ('CH/0000/0000', 0)
    conn.close()
    billno = "CH/" + str(date.today().year) +"/" +str(int(data[0][8:])+1)
    return billno

def calculateprice(product, qauntity):
    conn = sqlite3.connect("BillData.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM inventory WHERE `product` = ?", (product,))
    data = cur.fetchall()
    return data[0][1]*qauntity

def exportcsv():
    data = viewall()
    with open('Bills.csv', 'w', newline = '') as file:
        openfile = csv.writer(file)
        openfile.writerow(['Bill No', 'Date', 'Name', 'Address', 'Product', 'Qauntity', 'Price'])
        openfile.writerows(data)
