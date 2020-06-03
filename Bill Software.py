#!python3

import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import date
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import io
from reportlab.lib.pagesizes import letter
import backend
import os


backend.connectsqlite()

def updatestock():
    def update():
        conn = sqlite3.connect("BillData.db")
        cur  = conn.cursor()
        cur.execute("SELECT * FROM inventory WHERE product = ?", (entryStock.get()))
        data = cur.fetchall()
        cur.execute("UPDATE inventory SET Stock = ? WHERE `product` = ?", (data[2]+entryStock.get(),product.get))
        conn.commit()
        conn.close()

    def delete():
        conn = sqlite3.connect("BillData.db")
        cur  = conn.cursor()
        cur.execute("DELETE FROM inventory WHERE `product` = ?", (product.get(),))
        conn.commit()
        conn.close()

    updatewindow = Tk()
    updatewindow.wm_title("update stock")
    product = StringVar()
    choices = [data[0] for data in backend.viewallinv()]
    product.set(choices[0])
    optionProduct = OptionMenu(updatewindow, product, *choices)
    optionProduct.grid(row = 0, column = 0, columnspan = 2 , sticky = W)

    stock = IntVar()
    entryStock = Entry(updatewindow, textvariable = stock)
    entryStock.grid(row = 1, column = 0)
    buttonupdate = Button(updatewindow, text = "update", width = 15, bg = 'light cyan', command = update)
    buttonDelete = Button(updatewindow, text = "Delete", width = 15, bg = 'tomato', command = delete)
    buttonupdate.grid(row = 2, column = 0)
    buttonDelete.grid(row = 2, column = 1)
    updatewindow.mainloop()

def editinventory():
    
    
    
    def updateGUI():
        def updateinventory():
            conn = sqlite3.connect("BillData.db")
            cur  = conn.cursor()
            try:
                cur.execute("INSERT INTO inventory VALUES (?, ?, ?)", (entryProduct.get(), entryPrice.get(), 0))
                conn.commit()
                conn.close()
                messagebox.askokcancel('Saved', "Data Saved {} : {}".format(entryProduct.get(), entryPrice.get()))
                windowUpdateGUI.destroy()
                return True
            except sqlite3.IntegrityError:
                conn.close()
                messagebox.showinfo('Not Saved', "Data Already present ")
                windowUpdateGUI.destroy()
                return False
        
        windowUpdateGUI = Tk()
        labelInventory = Label(windowUpdateGUI, text = "Name")
        labelPrice     = Label(windowUpdateGUI, text = "Price")
        labelInventory.grid(row = 0, column = 0)
        labelPrice.grid(row = 1, column = 0)
        product      = StringVar()
        price        = IntVar()
        entryProduct = Entry(windowUpdateGUI, textvariable = product)
        entryPrice   = Entry(windowUpdateGUI, textvariable = price)
        entryProduct.grid(row = 0 , column = 1)
        entryPrice.grid(row = 1, column = 1)
        buttonSaveedit  = Button(windowUpdateGUI, text = "Save", width = 15, bg = 'light cyan', command = updateinventory)
        buttonSaveedit.grid(row = 2, column = 0)
        windowUpdateGUI.mainloop()

    def deleteGUI():
        def deleteinventory():
            conn = sqlite3.connect("BillData.db")
            cur  = conn.cursor()
            cur.execute("DELETE FROM inventory WHERE `product` = ?", (product.get(),))
            conn.commit()
            conn.close()
            windowDeleteGUI.destroy()

        windowDeleteGUI = Tk()
        product = StringVar()
        try:
            choices = [data[0] for data in backend.viewallinv()]
            product.set(choices[0])
        except IndexError:
            choices = ["Please Add Product Before Proceeding!"]
            pass
        
        optionProduct = OptionMenu(windowDeleteGUI, product, *choices)
        optionProduct.config(width = 20)
        optionProduct.grid(row = 0, column = 1, columnspan = 2, sticky = W)
        buttonwindowDeleteGUIdelete = Button(windowDeleteGUI, text = 'Delete', width = 15, bg = 'orange', command = deleteinventory)
        buttonwindowDeleteGUIdelete.grid(row=1,column=0)
        windowDeleteGUI.mainloop()

    editwindow = Tk()
    editwindow.wm_title("Product List")
    buttonEditwindowAddNew = Button(editwindow, text = 'Add new', width = 15, bg = 'light cyan', command = updateGUI )
    buttonEditwindowDelete = Button(editwindow, text = 'Delete',  width = 15, bg = 'light cyan', command = deleteGUI )
    buttonEditwindowAddNew.grid(row = 0 ,column = 0)
    buttonEditwindowDelete.grid(row = 1 ,column = 0)
    
    editwindow.mainloop()

def viewrecords():
    reset()
    for data in backend.viewall():
        tempStr = data[0] + '    ' + data[1] + '    ' + data[2] + '    '  + data[3] + '    ' + data[4]  + '    ' + str(data[5]) + '    ' + str(data[6])
        listboxMain.insert(END, tempStr)

def searchrecords():
    listboxMain.delete(0,END)
    for data in backend.search(billNo.get(), name.get(), address.get()):
        tempStr = data[0] + '    ' + data[1] + '    ' + data[2] + '    '  + data[3] + '    ' + data[4]  + '    ' + str(data[5]) + '    ' + str(data[6])
        listboxMain.insert(END, tempStr)

def getselected(event):
    global selectedData
    try:
        index        = listboxMain.curselection()[0]
        selectedData = listboxMain.get(index)
        data         = backend.search(selectedData.split('    ',1)[0])
        entryName.delete(0,END)
        name.set(data[0][2])
        entryAddress.delete(0,END)
        address.set(data[0][3])
        quantity.set(data[0][-2])
        billNo.set(data[0][0])
        dateToday.set(data[0][1])
        product.set(data[0][4])
    except IndexError:
        selectedData = '-1'
    

def deleterecord():
    if messagebox.askyesno("Delete Record", "Do you Want to delete {}".format(selectedData)):
        backend.delete(selectedData.split('    ', 1)[0])
        reset()
        try:
            path = os.getcwd() + "/Bill Reciepts/"
            os.remove("{}/{}.pdf".format(path,selectedData.split('    ', 1)[0].replace('/','-')))
            listboxMain.insert(END, "Data Deleted Successfully!")
        except:
            pass
        return
    reset()
    listboxMain.insert(END, " Data Not Deleted")
    
def saverecord():
    if name.get() == '' or address.get() == '' or quantity.get == 0:
        messagebox.askokcancel("Warning", "Please Check name/ address/ qauntity")
        return
    if backend.insert(billNo.get(), dateToday.get(), name.get(), address.get(), product.get(), quantity.get(), backend.calculateprice(product.get()
    , quantity.get())) :
        generatebill(billNo.get())
        reset()
        billNo.set(backend.generatebillno())
        listboxMain.insert(END, "Data Added Successfully")
    else:
        reset()
        listboxMain.insert(END, "Bill no. Already Present!")

def exportrecord():
    backend.exportcsv()
    reset()
    listboxMain.insert(END, " Data has been exported as 'Bills.csv' successfully!")

def reset():
    entryName.delete(0,END)
    entryAddress.delete(0,END)
    quantity.set(0)
    billNo.set(backend.generatebillno())
    dateToday.set(date.today().strftime("%d/%m/%Y"))
    listboxMain.delete(0, END)

def generatebill(billNo):
    Data   = backend.search(billNo)
    packet = io.BytesIO()
    can    = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 550, str(Data[0][2]))
    can.drawString(50, 460, str(Data[0][4]))
    can.drawString(270, 460, str(Data[0][-2]))
    can.drawString(350, 460, str(Data[0][-1]/Data[0][-2]))
    can.drawString(480, 460, str(Data[0][-1]))
    can.drawString(480, 110, str(Data[0][-1]))
    can.drawString(100, 520, str(Data[0][3]))
    can.drawString(380, 610, str(Data[0][0]))
    can.drawString(380, 580, str(Data[0][1]))
    can.save()
    packet.seek(0)
    new_pdf      = PdfFileReader(packet)
    existing_pdf = PdfFileReader(open("Bill.pdf", "rb"))
    output       = PdfFileWriter()
    page         = existing_pdf.getPage(0)
    page2        = new_pdf.getPage(0)
    page.mergePage(page2)
    output.addPage(page)
    try:
        os.mkdir("{}/{}".format(os.getcwd(), "Bill Reciepts"))
    except FileExistsError:
        pass

    outputStream = open("Bill Reciepts\{}.pdf".format(Data[0][0]).replace('/','-'), "wb" )
    output.write(outputStream)
    outputStream.close()
    reset()
    listboxMain.insert(END, "Reciept Generated Successfully!")


window = Tk()
window.wm_title("Maharashtra Agrovett")

labelName     = Label(window, text = "Name :")
labelAddress  = Label(window, text = "Address :")
labelProduct  = Label(window, text = "Product :")
labelDate     = Label(window, text = "Date :")
labelQuantity = Label(window, text = "Quantity :")
labelBillno   = Label(window, text = "Bill No. :")

labelName.grid(row = 0, column = 0)
labelAddress.grid(row = 1, column = 0)
labelProduct.grid(row = 2, column = 0)
labelQuantity.grid(row = 3, column = 0)
labelDate.grid(row = 0, column = 4)
labelBillno.grid(row = 1, column = 4)

name      = StringVar()
address   = StringVar()
quantity  = IntVar()
dateToday = StringVar()
billNo    = StringVar()
billNo.set(backend.generatebillno())
dateToday.set(date.today().strftime("%d/%m/%Y"))
entryName     = Entry(window, textvariable = name, width = 60)
entryAddress  = Entry(window, textvariable = address, width = 60)
entryQuantity = Entry(window, textvariable = quantity)
entryDate     = Entry(window, textvariable = dateToday)
entryBillno   = Entry(window, textvariable = billNo)

entryName.grid(row = 0, column = 1, columnspan = 3)
entryAddress.grid(row = 1, column = 1,columnspan = 3)
entryQuantity.grid(row = 3, column =1)
entryDate.grid(row = 0, column = 5)
entryBillno.grid(row = 1, column = 5)

product = StringVar()
try:
    choices = [data[0] for data in backend.viewallinv()]
    product.set(choices[0])
except IndexError:
    choices = ["Please Add Product Before Proceeding!"]
    pass

optionProduct = OptionMenu(window, product, *choices)
optionProduct.config(width = 45)
optionProduct.grid(row = 2, column = 1, columnspan = 2, sticky = W)

listboxMain = Listbox(window, height = 7, width = 60)
listboxMain.bind('<<ListboxSelect>>', getselected)
listboxMain.grid(row = 4, column = 1, columnspan = 3)

yscrollListbox = Scrollbar(window)
xscrollListbox = Scrollbar(window, orient = HORIZONTAL)

yscrollListbox.grid(row = 4, column = 4, rowspan = 6)
xscrollListbox.grid(row = 10, column = 1, columnspan = 3)

listboxMain.configure(   yscrollcommand = yscrollListbox.set)
yscrollListbox.configure(command = listboxMain.yview())
listboxMain.configure(   xscrollcommand = xscrollListbox.set)
xscrollListbox.configure(command = listboxMain.xview())

buttonSave    = Button(window, text = "Save",          width = 15, bg = 'light cyan', command = saverecord)
buttonViewall = Button(window, text = "View All",      width = 15, bg = 'deep sky blue', command = viewrecords)
buttonPrint   = Button(window, text = "To Excel",      width = 15, bg = 'medium spring green', command = exportrecord)
buttonDelete  = Button(window, text = "Delete",        width = 15, bg = 'coral', command = deleterecord)
buttonSearch  = Button(window, text = "Search Entry",  width = 15, bg = 'misty rose', command = searchrecords)
buttonClose   = Button(window, text = "Close",         width = 15, bg = 'tomato2', command = window.destroy)
buttonReset   = Button(window, text = "Reset",         width = 15, bg = 'bisque', command = reset)
buttonEdit    = Button(window, text = "Edit",          width = 15, bg = 'lemon chiffon', command = editinventory)
buttonStock   = Button(window, text = "update Stock",  width = 15, command = updatestock)

buttonViewall.grid(row = 11, column = 0)
buttonSearch.grid(row = 11, column = 1)
buttonPrint.grid(row = 11, column = 2)
buttonDelete.grid(row = 11, column = 3)
buttonSave.grid(row = 11, column = 4)
buttonClose.grid(row = 11, column = 5)
buttonReset.grid(row = 10, column  = 5)
buttonEdit.grid(row = 4, column = 5)
buttonStock.grid(row = 5, column  = 5)


window.mainloop()