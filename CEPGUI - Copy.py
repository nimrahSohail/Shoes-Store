# Libraries used is this code
from os import error
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image,ImageTk
import smtplib
from datetime import datetime
import os.path

# Username and password for entering in admin panel
admin_user='admin'
admin_pass='admin'

class Products:
    '''This class contains products with their respective attributes''' 
    def __init__(self):
        self.products={} 

    def load_product(self):
        '''Function for loading the products from file'''
        self.__init__()
        f=open('products.txt','r+')
        for i in f:
            i=i.split(";")
            self.products.update({i[0]:[i[1],i[2],i[3],i[4],i[5],i[6],i[7]]})   
        f.close()

    def save_product(self):
        '''Function for saving the products in file'''
        f=open("products.txt","w+")
        for i in self.products:
            f.write(str(i)+';')
            for j in self.products[i]:
                f.write(str(j)+';')
            f.write('\n')
        f.close()  

class RateButton(Button):
    '''This is not a main class, it is created to modify Button class functionality to get Entry labels value (Rating)'''
    def __init__(self,entry,rate_win,title,**k):
        Button.__init__(self,title,**k)
        self.rate_win=rate_win
        self.entry=entry
    def update_rating(self,products):
        '''This function updates the rating user gives in the file'''
        self.products=products
        try:
            user_rat=self.entry.get()
            if 0<=float(user_rat)<=5:
                for key in Cart.myCart:
                    self.key=key
                    self.values=self.products[self.key]
                    raters_now=int(self.values[6])+1
                    new_rating=round((float(user_rat)+(float(self.values[4])*float(self.values[6])))/float(raters_now),1)
                    self.products.update({self.key:[self.values[0],self.values[1],self.values[2],self.values[3],str(new_rating),self.values[5],str(raters_now)]})
                self.rate_win.destroy()
                return self.products
            else:
                raise ValueError
        except:
            messagebox.showerror('Invalid value','You were supposed to enter number between 0 and 5 only')
            self.rate_win.destroy() 
            return self.products 
     
class Cart():
    '''This class stores the information about customer cart, including his history, and the current cart he is shopping with'''
    def __init__(self,username):
        self.username=username
        Cart.myCart={}
        Cart.sales=[]
        Cart.myHistory=[]
        Cart.prod_list=Products()

    def add_to_cart(self):
        '''This function add the product using its key to user's cart'''
        prod_id=self.id
        prod_val=self.value
        if prod_id not in Cart.myCart:  
            Cart.myCart.update({prod_id:[prod_val[1],prod_val[2],1,prod_val[4]]})
        else: 
            Cart.myCart.update({prod_id:[prod_val[1],prod_val[2],Cart.myCart[prod_id][2]+1,prod_val[4]]})
        Cart.prod_list.load_product()
        for i in Cart.prod_list.products:
            if i==prod_id:
                other=Cart.prod_list.products[i]
                Cart.prod_list.products[i]=[other[0],other[1],other[2],int(other[3])-1,other[4],other[5],other[6]]
        Cart.prod_list.save_product()

    def remove_from_cart(self,id):
        '''This function removes the product using its key from user's cart'''
        try:
            prod_id=id
            prod_val=Cart.myCart[id]
            if Cart.myCart[prod_id][2]>1:  
                Cart.myCart.update({prod_id:[prod_val[0],prod_val[1],Cart.myCart[prod_id][2]-1,prod_val[3]]})
            else: 
                Cart.myCart.pop(prod_id)
            Cart.prod_list.load_product()
            for i in Cart.prod_list.products:
                if i==prod_id:
                    other=Cart.prod_list.products[i]
                    self.prod_list.products[i]=[other[0],other[1],other[2],int(other[3])+1,other[4],other[5],other[6]]
            Cart.prod_list.save_product()
        except:
            messagebox.showerror('Invalid key','No product with this Id is in your cart')

    def add_to_sales(self,username):
        '''When user checkout this function is called, it stores the current cart to sales list for record so that it can be fetched when user want to view his history'''
        Cart.sales=[]
        self.load_history()
        for item in Cart.myCart:
            data=Cart.myCart[item]
            Cart.sales.append([username,item,data[0],data[1],data[2],datetime.now().strftime("%H:%M:%S %d-%b-%y")])
        self.save_cart_history()

    def load_history(self):
        '''This functions loads the sales record from file'''
        f=open('sales.txt','r+')
        sale=f.readlines()
        for i in sale:
            i=i.split(";")
            Cart.sales.append([i[0],i[1],i[2],i[3],i[4],i[5]])
        f.close()

    def fetch_customer_history(self,username):
        '''This function fetches the user's record from sales data using his username'''
        Cart.sales=[]
        Cart.myHistory=[]
        self.load_history()
        for item in Cart.sales:
            if item[0]==username:
                Cart.myHistory.append([item[1],item[2],item[3],item[4],item[5]])

    def save_cart_history(self):
        '''This function saves sales list in file for future use'''
        f=open("sales.txt","w+")
        for i in self.sales:
            f.write(str(i[0])+';'+str(i[1])+';'+str(i[2])+';'+str(i[3])+';'+str(i[4])+';'+str(i[5]+';'))
            f.write('\n')
        f.close()

class buyButton(Button,Cart):
    '''This is not a main class, it is used to modify the Button class functionality to obtain the product id when its respective buy button is clicked'''
    
    def __init__(self,id,value,title, **k):
        Button.__init__(self,title, **k)
        self.id=id
        self.value = value
        self.max_items=int(value[3])

    def add_to_cart(self):
        'This function checks if the item is available in stock and then refer to add to cart function of cart to store the item in cart if its available, else inform user that its not available'
        try:
            if self.max_items>0:
                self.max_items-=1
                return super().add_to_cart()
            else: raise ValueError
        except:
            messagebox.showinfo("Out Of Stock", "Sorry this item is out of stock!")

class Admin(Products):
    '''This admin class contains all the functionality of admin panel'''
    def destroy_frames(self):
        '''This function destroy previous frames to avoid overlapping'''
        if self.current_frame=='show':
            self.tree_frame.destroy()
        if self.current_frame=='add':
            self.add_frame.destroy()
        if self.current_frame=='search':
            self.tree_frame.destroy()
            self.search_frame.destroy()
        if self.current_frame=='restock':
            self.restock_frame.destroy()
        if self.current_frame=='lowStock':
            self.tree_frame.destroy()
        if self.current_frame=='remove':
            self.tree_frame.destroy()
            self.remove_frame.destroy()
   
    def create_admin_treeview(self):
        '''This function is created to avoid repitition of code for creating Treeview component'''
        self.style=ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Treeview',
            background='#E0CCE3',
            foreground='black',
            rowheight=20,
            fieldbackground='D3D3D3'
            )
        self.style.map('Treeview',
            background=[('selected','#8C5394')])

        #Frame for treeview
        self.tree_frame=Frame(self.root)
        self.tree_frame.place(x=450,y=130,height=520,width=700)
        self.tree_frame.config(bg='#C2C2AE')

        #Scrollbar
        self.tree_scroll=Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT,fill=Y)

        #Defining
        self.my_tree=ttk.Treeview(self.tree_frame,yscrollcommand=self.tree_scroll.set,selectmode='browse')
        self.my_tree['columns']=('Product Id','Name','Price','Quantity','Rating')
        self.tree_scroll.config(command=self.my_tree.yview)

        #Formatting
        self.my_tree.column('#0',width=0,stretch=NO)
        self.my_tree.column('Product Id',anchor=CENTER,width=80)
        self.my_tree.column('Name',anchor=CENTER,width=220)
        self.my_tree.column('Price',anchor=CENTER,width=100)
        self.my_tree.column('Quantity',anchor=CENTER,width=100)
        self.my_tree.column('Rating',anchor=CENTER,width=180)

        #Headings
        self.my_tree.heading('#0',text='',anchor=W)
        self.my_tree.heading('Product Id',text='Product Id',anchor=CENTER)
        self.my_tree.heading('Name',text='Name',anchor=CENTER)
        self.my_tree.heading('Price',text='Price',anchor=CENTER)
        self.my_tree.heading('Quantity',text='Quantity',anchor=CENTER)
        self.my_tree.heading('Rating',text='Rating',anchor=CENTER)
        self.my_tree.place(x=0,y=0,height=520,width=683)

        #For Striped Treeview
        self.my_tree.tag_configure('odd',background='#F5DCD0')
        self.my_tree.tag_configure('even',background='#F5F5C4')   

    def show_product(self):
        '''This function loads all the products from file to treeview'''
        self.destroy_frames()
        self.current_frame='show'
        self.create_admin_treeview()
        item_id=1
        f=open('products.txt','r')
        items=f.readlines()
        self.my_tree.delete(*self.my_tree.get_children())
        for i in items:
            item=i.split(';')
            if item_id%2==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+'✩')),tags=('even',))
            else:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+'✩')),tags=('odd',))
            item_id+=1

    def add(self):
        '''This function saves the product in file'''
        if os.path.exists('products.txt'):
            self.load_product()
        try:
            if len(self.entry_id.get())==0 or len(self.entry_image.get())==0 or len(self.entry_title.get())==0 or len(self.entry_price.get())==0 or len(self.entry_quantity.get())==0 or len(self.text.get("1.0",'end-1c'))==0:
                self.message='Please enter values in all entry fields'
                raise ValueError
            if self.entry_id.get() in self.products:
                self.message='Product with similar Id exist in records'
                raise KeyError
            if os.path.isfile(self.entry_image.get())==False:
                self.message='Image file does not exist'
                raise KeyError
            if True:
                self.message='Please enter an integer in price'
                if isinstance(int(self.entry_price.get()),int)==False:
                    raise ValueError
            if True:
                self.message='Please enter an integer in quantity'
                if isinstance(int(self.entry_quantity.get()),int)==False:
                    raise ValueError
            self.products.update({self.entry_id.get():[self.entry_image.get(),self.entry_title.get(),self.entry_price.get(),self.entry_quantity.get(),'0',self.text.get("1.0",'end-1c'),'0']})
            messagebox.showinfo('Success!','Product added to records')
        except:
            messagebox.showwarning('Invalid entry',self.message)
        self.save_product()

    def remove(self):
        '''This function removes the product from file'''
        self.load_product()
        try:
            if self.entry_id.get() in self.products:
                self.products.pop(self.entry_id.get())
            else: raise IndexError
        except:
            messagebox.showinfo('Wrong Id','Sorry this product does not exist in records')
        self.save_product()
        
    def update(self):
        '''This function updates quantity of product in records'''
        self.load_product()
        try:
            if self.entry_id.get() in self.products:
                for i in self.products:
                    if i==self.entry_id.get():
                        other=self.products[i]
                        self.products[i]=[other[0],other[1],other[2],int(other[3])+int(self.entry_id2.get()),other[4],other[5],other[6]]                
            else:
                raise IndexError
        except:
            messagebox.showinfo('Wrong Id','Sorry this product does not exist in records')

        self.save_product()

    def search(self):
        '''This function searches for product in records using its product Id'''
        self.destroy_frames()
        self.current_frame='search'
        self.create_admin_treeview()
        self.search_frame=Frame(self.root)
        self.search_frame.config(bg='#C4F5EF')
        self.search_frame.place(x=450,y=550,width=683,height=100)
        f=open('products.txt','r')
        items=f.readlines()
        self.my_tree.delete(*self.my_tree.get_children())
        def check():
            item_id=1
            found=0
            product_id=item_name.get()
            for i in items:
                item=i.split(';')
                if item[0]==product_id:
                    if item_id%2==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+' Stars')),tags=('even',))
                    else:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+' Stars')),tags=('odd',)) 
                    item_id+=1
                    found+=1
            if found==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=('Sorry item not found'))
            self.search_frame.destroy()
        label_head=Label(self.search_frame,text="Search Product",bg='#8C5394',fg='#FFFFFF',font=('Constantia',16))
        label_head.place(x=0,y=0,height=40,width=683)      
        item_name=Entry(self.search_frame)
        item_name.place(x=120,y=60)
        instruction=Label(self.search_frame,text='Enter id:',font=('#DCC4F5',11,'italic','bold'))
        instruction.place(x=10,y=60)
        search_btn=Button(self.search_frame,text='Search record',font=('#DCC4F5',11,'italic','bold'),relief='groove',command=check)
        search_btn.place(x=300,y=60)

    def LowStock(self):
        '''This function lists the products which needs to be restocked'''
        self.destroy_frames()
        self.current_frame='lowStock'
        self.create_admin_treeview()
        f=open('products.txt','r')
        item_id=1
        items=f.readlines()
        self.my_tree.delete(*self.my_tree.get_children())
        for i in items:
            item=i.split(';')
            if int(item[4])<30:
                if item_id%2==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+' Stars')),tags=('even',))
                else:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[2]),str(item[3]+'$'),str(item[4]),str(item[5]+' Stars')),tags=('odd',))
                item_id+=1

    def add_product(self):
        '''This function provides data for add function to add products in file'''
        self.destroy_frames()
        self.current_frame='add'
        self.add_frame=Frame(self.root)
        self.add_frame.config(bg='#E0CCE3')
        self.add_frame.place(x=450,y=130,width=700,height=520)
        label_head=Label(self.add_frame,text="Add Product",bg='#8C5394',fg='#FFFFFF',font=('Constantia',24))
        label_head.place(x=0,y=0,width=700,height=80)
        label_id=Label(self.add_frame,text="Enter Product ID:",bg='#FFF5CF',font=('Constantia',16))
        label_id.place(x=10,y=120,height=30)
        self.entry_id=Entry(self.add_frame)
        self.entry_id.place(x=200,y=120,height=30)
        label_image=Label(self.add_frame,text='Enter Image Name:',bg='#FFF5CF',font=('Constantia',16))
        label_image.place(x=10,y=170,height=30)
        self.entry_image=Entry(self.add_frame)
        self.entry_image.place(x=200,y=170,height=30)
        label_price=Label(self.add_frame,text="Enter price:",bg='#FFF5CF',font=('Constantia',16))
        label_price.place(x=10,y=220,height=30)
        self.entry_price=Entry(self.add_frame)
        self.entry_price.place(x=200,y=220,height=30)
        label_title=Label(self.add_frame,text="Enter Title:",bg='#FFF5CF',font=('Constantia',16))
        label_title.place(x=10,y=270,height=30)
        self.entry_title=Entry(self.add_frame)
        self.entry_title.place(x=200,y=270,height=30)
        label_quantity=Label(self.add_frame,text="Enter Quantity:",bg='#FFF5CF',font=('Constantia',16))
        label_quantity.place(x=10,y=320,height=30)
        self.entry_quantity=Entry(self.add_frame)
        self.entry_quantity.place(x=200,y=320,height=30)
        label_desc=Label(self.add_frame,text="Enter Description:",bg='#FFF5CF',font=('Constantia',16))
        label_desc.place(x=10,y=370,height=30)
        self.text =Text(self.add_frame, undo = True, height = 5, width = 50)
        self.text.place(x=200,y=370)
        b=Button(self.add_frame,text='Enter Record',bg='#FFF5CF',font=('Constantia',12),command=self.add)
        b.place(x=300,y=470)

    def remove_product(self):
        '''This function provides data for remove function'''
        self.destroy_frames
        self.create_admin_treeview()
        self.show_product()
        self.current_frame='remove'
        self.remove_frame=Frame(self.root)
        self.remove_frame.config(bg='#C4F5EF')
        self.remove_frame.place(x=450,y=550,width=683,height=100)
        label_head=Label(self.remove_frame,text="Remove Product",bg='#8C5394',fg='#FFFFFF',font=('Constantia',16))
        label_head.place(x=0,y=0,height=40,width=683)
        label_id=Label(self.remove_frame,text="Enter Product ID:",bg='#FFF5CF',font=('Constantia',12))
        label_id.place(x=50,y=60,height=30)
        self.entry_id=Entry(self.remove_frame)
        self.entry_id.place(x=250,y=60,height=30)
        b=Button(self.remove_frame,text='Enter',bg='#FFF5CF',font=('Constantia',12),command=self.remove)
        b.place(x=500,y=60)

    def restock_product(self):
        '''This function helps to restock products using thier id and quanitity'''
        self.destroy_frames()
        self.current_frame='restock'
        self.restock_frame=Frame(self.root)
        self.restock_frame.config(bg='#E0CCE3')
        self.restock_frame.place(x=450,y=130,width=700,height=520)
        label_head=Label(self.restock_frame,text="Restock Product",bg='#8C5394',fg='#FFFFFF',font=('Constantia',26))
        label_head.place(x=0,y=0,height=80,width=700)
        label_id=Label(self.restock_frame,text="Enter Product ID:",bg='#FFF5CF',font=('Constantia',16))
        label_id.place(x=20,y=200,height=30)
        self.entry_id=Entry(self.restock_frame)
        self.entry_id.place(x=200,y=200,height=30)
        label2_id=Label(self.restock_frame,text="Enter Quantity:",bg='#FFF5CF',font=('Constantia',16))
        label2_id.place(x=50,y=350,height=30)
        self.entry_id2=Entry(self.restock_frame)
        self.entry_id2.place(x=200,y=350,height=30)    
        b=Button(self.restock_frame,text='Enter',bg='#FFF5CF',font=('Constantia',12),command=self.update)
        b.place(x=300,y=430,height=30)

    def log_out(self):
        '''This function destroys the window and logout the admin'''
        self.destroy_frames()
        self.root.destroy()
        m.login_window()

    def loggedin_admin(self):
        '''This function initiates admin panel creating interface'''
        self.root.destroy() 
        self.current_frame=None
        self.root=Tk()
        self.root.title('Air It')
        self.root.geometry('1200x700')
        # self.root.iconbitmap('CS20098.ico')
        self.root.configure(bg='#F9F0FA')
        self.root.resizable(0,0)
        self.f=Frame(self.root,bg="#c5bec6") 
        self.f.place(x=0,y=0,width=1200,height=80)
        self.k=Frame(self.root,bg="#8C5394") 
        self.k.place(x=400,y=0,width=400,height=80)
        img = Image.open('images\shoe.jpg')
        img=img.resize((120,90),Image.ANTIALIAS)
        img=ImageTk.PhotoImage(img)
        label_img=Label(self.f,image=img)
        label_img.photo=img
        label_img.place(x=-2,y=-12)
        self.l=Label(self.root,text='AIR IT',font=('Eras Demi ITC',36),bg='#c5bec6',fg='#4e2f25')
        self.l.place(x=150,y=10)
        self.j=Label(self.root,text='Admin Interface',font=('Eras Demi ITC',32),fg='#c5bec6',bg='#8C5394')
        self.j.place(x=430,y=10)
        bkg=Frame(self.root,bg="#8C5394") 
        bkg.place(x=50,y=130,width=300,height=520)
        menu=Label(self.root,text='MENU',font=('Constantia',32),fg='#4e2f25',bg='#E0CCE3')
        menu.place(x=50,y=170,width=300,height=80)
        option1=Button(text='Show products',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.show_product)
        option1.place(x=50,y=290,width=300,height=40)
        option2=Button(text='Add product',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.add_product)
        option2.place(x=50,y=350,width=300,height=40)
        option3=Button(text='Search product',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.search)
        option3.place(x=50,y=410,width=300,height=40)
        option4=Button(text='Restock product',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.restock_product)
        option4.place(x=50,y=470,width=300,height=40)
        option5=Button(text='Low stock products',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.LowStock)
        option5.place(x=50,y=530,width=300,height=40)
        option7=Button(self.root,text='Remove Product',font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.remove_product)
        option7.place(x=50,y=590,width=300,height=40)
        option8=Button(self.root,text='Log Out',font=('Constantia',14,'italic'),fg='#c5bec6',bg='#4e2f25',command=self.log_out)
        option8.place(x=1100,y=25,width=80,height=30)
        self.show_product()

class Customer(Cart):  
    '''This class contains all the customer related attributes'''
    def __init__(self):
        self.customer={}

    def destroy_frames(self):
        '''This function destroy previous frames to avoid overlapping'''
        if self.current_frame=='viewCart':
            self.my_tree.destroy()
            self.tree_scroll.destroy()
            # self.tree_frame.destroy()
            self.remove_frame.destroy()
        if self.current_frame=='showProducts':
            self.products_frame.destroy()

    def load_account(self):
        '''This function loads customer accounts from file'''
        if os.path.exists('customer.txt')==True:
            self.f=open('customer.txt','r+')
            for i in self.f:
                i=i.split(";")
                self.customer.update({i[0]:[i[1],i[2],i[3],i[4]]})   
            self.f.close()

    def create_treeview(self):
        '''This function is created to create treeview'''
        self.style=ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Treeview',
            background='#C2C2AE',
            foreground='black',
            rowheight=20,
            fieldbackground='#E0CCE3'
            )
        self.style.map('Treeview',
            background=[('selected','#DCC4F5')])

        #Frame for treeview
        self.tree_frame=Frame(self.root)
        self.tree_frame.place(x=450,y=130,height=520,width=700)
        self.tree_frame.config(bg='#C2C2AE')

        #Scrollbar
        self.tree_scroll=Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT,fill=Y)

        #Defining
        self.my_tree=ttk.Treeview(self.tree_frame,yscrollcommand=self.tree_scroll.set,selectmode='browse')
        self.my_tree['columns']=('Product Id','Name','Price','Quantity','Rating')
        self.tree_scroll.config(command=self.my_tree.yview)

        #Formatting
        self.my_tree.column('#0',width=0,stretch=NO)
        self.my_tree.column('Product Id',anchor=CENTER,width=100)
        self.my_tree.column('Name',anchor=CENTER,width=200)
        self.my_tree.column('Price',anchor=CENTER,width=120)
        self.my_tree.column('Quantity',anchor=CENTER,width=120)
        self.my_tree.column('Rating',anchor=CENTER,width=120)

        #Headings
        self.my_tree.heading('#0',text='',anchor=W)
        self.my_tree.heading('Product Id',text='Product Id',anchor=CENTER)
        self.my_tree.heading('Name',text='Name',anchor=CENTER)
        self.my_tree.heading('Price',text='Price',anchor=CENTER)
        self.my_tree.heading('Quantity',text='Quantity',anchor=CENTER)
        self.my_tree.heading('Rating',text='Rating',anchor=CENTER)
        self.my_tree.place(x=0,y=0,height=460,width=683)

        #For Striped Treeview
        self.my_tree.tag_configure('odd',background='#F5DCD0')
        self.my_tree.tag_configure('even',background='#F5F5C4')   

    def show_cart(self):
        '''This function shows customer his current cart with all the products and their quantity'''
        self.destroy_frames()
        self.current_frame='viewCart'
        self.create_treeview()
        item_id=1
        self.my_tree.delete(*self.my_tree.get_children())
        for item in Cart.myCart:
            data=Cart.myCart[item]
            if item_id%2==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item),str(data[0]),str(data[1]+'$'),str(data[2]),str(data[3]+'✩')),tags=('even',))
            else:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item),str(data[0]),str(data[1]+'$'),str(data[2]),str(data[3]+'✩')),tags=('odd',))
            item_id+=1

    def view_products(self):
        '''This function shows customer the items we are selling'''
        self.destroy_frames()
        self.load_product()
        self.current_frame='showProducts'

        # Frame for Products
        self.products_frame=Frame(self.root)
        self.products_frame.place(x=450,y=130,width=700,height=520)
        self.products_frame.config(bg='#C2C2AE',highlightbackground='#8C5394',highlightthickness=2)

        #Canvas
        product_canvas=Canvas(self.products_frame)
        product_canvas.pack(side=LEFT,fill="both",expand="yes")

        #Scrollbar
        product_scroll=ttk.Scrollbar(self.products_frame,orient="vertical", command=product_canvas.yview)
        product_scroll.pack(side=RIGHT,fill="y")

        product_canvas.configure(yscrollcommand=product_scroll.set)
        product_canvas.bind('<Configure>',lambda e: product_canvas.configure(scrollregion=product_canvas.bbox('all')))
        
        #CanvasFrame
        canvas_frame=Frame(product_canvas)
        product_canvas.create_window((0,0),window=canvas_frame,anchor="nw")

        x=0
        for i in self.products:
            shoe_frame=Frame(canvas_frame)
            shoe_frame.config(bg='#E0CCE3',height=240,width=700,padx=10,pady=20,highlightbackground='#B08D95',highlightthickness=2)
            shoe_frame.grid(row=x,column=0)
            img = Image.open(self.products[i][0])
            img=img.resize((200,200),Image.ANTIALIAS)
            img=ImageTk.PhotoImage(img)
            label_img=Label(shoe_frame,image=img)
            label_img.photo=img
            label_img.place(x=10,y=0)

            name=Label(shoe_frame,text=str(self.products[i][1]),bg='#E0CCE3',font=('Poppins SemiBold',18))
            name.place(x=240,y=10)
            price=Label(shoe_frame,text="$"+str(self.products[i][2]),bg='#E0CCE3',font=('Poppins Medium',16))
            price.place(x=490,y=12)
            desc_head=Label(shoe_frame,text="Description:",bg='#E0CCE3',font=('Poppins Medium',12))
            desc_head.place(x=240,y=50)
            desc=Message(shoe_frame,text=str(self.products[i][5]),bg='#E0CCE3',font=('Poppins Light',9),width=400)
            desc.place(x=240,y=94,height=120)
            rating=Label(shoe_frame,text=str(self.products[i][4])+'✩',bg='#E0CCE3',font=('Poppins Medium',14))
            rating.place(x=490,y=44)
            buy_button=buyButton(i,self.products[i],shoe_frame,text="Buy",bg='#8C5394',fg='#ffffff',font=('Constantia',12),activebackground='#78d6ff', bd=0, highlightthickness=0)
            buy_button.config(command=buy_button.add_to_cart)
            buy_button.place(x=560,y=14,height=30,width=80)
            x+=1

    def show_customer_history(self):
        '''This function shows customer his purchase history'''
        self.fetch_customer_history(self.username)
        self.style=ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Treeview',
            background='#E0CCE3',
            foreground='black',
            rowheight=20,
            fieldbackground='#E0CCE3'
            )
        self.style.map('Treeview',
            background=[('selected','#8C5394')])

        #Frame for treeview
        self.tree_frame=Frame(self.root)
        self.tree_frame.place(x=450,y=130,height=520,width=700)
        self.tree_frame.config(bg='#E0CCE3')

        #Scrollbar
        self.tree_scroll=Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT,fill=Y)

        #Defining
        self.my_tree=ttk.Treeview(self.tree_frame,yscrollcommand=self.tree_scroll.set,selectmode='browse')
        self.my_tree['columns']=('Product Id','Name','Price','Quantity','Purchasing Time')
        self.tree_scroll.config(command=self.my_tree.yview)

        #Formatting
        self.my_tree.column('#0',width=0,stretch=NO)
        # self.my_tree.column('#0',width=10)
        self.my_tree.column('Product Id',anchor=CENTER,width=83)
        self.my_tree.column('Name',anchor=CENTER,width=200)
        self.my_tree.column('Price',anchor=CENTER,width=100)
        self.my_tree.column('Quantity',anchor=CENTER,width=100)
        self.my_tree.column('Purchasing Time',anchor=CENTER,width=200)

        #Headings
        self.my_tree.heading('#0',text='',anchor=W)
        self.my_tree.heading('Product Id',text='Product Id',anchor=CENTER)
        self.my_tree.heading('Name',text='Name',anchor=CENTER)
        self.my_tree.heading('Price',text='Price',anchor=CENTER)
        self.my_tree.heading('Quantity',text='Quantity',anchor=CENTER)
        self.my_tree.heading('Purchasing Time',text='Purchasing Time',anchor=CENTER)
        self.my_tree.place(x=0,y=0,height=520,width=683)

        #For Striped Treeview
        self.my_tree.tag_configure('odd',background='#F5DCD0')
        self.my_tree.tag_configure('even',background='#F5F5C4')   

        item_id=1
        self.my_tree.delete(*self.my_tree.get_children())
        for item in Cart.myHistory:
            if item_id%2==0:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[1]),(str(item[2])+'$'),str(item[3]),str(item[4])),tags=('even',))
            else:self.my_tree.insert(parent='',index='end',iid=item_id,text='',values=(str(item[0]),str(item[1]),(str(item[2])+'$'),str(item[3]),str(item[4])),tags=('odd',))
            item_id+=1

    def remove_and_reload(self):
        '''this function reloads the frame when a product is removed by customer from his cart'''
        self.remove_from_cart(self.entry_id.get())
        self.view_cart()

    def view_cart(self):
        '''This function provides graphical interface for show cart function's data'''
        self.destroy_frames()
        self.create_treeview()
        self.show_cart()
        self.current_frame='viewCart'
        self.remove_frame=Frame(self.root)
        self.remove_frame.config(bg='#C4F5EF')
        self.remove_frame.place(x=450,y=530,width=683,height=120)
        self.total=0
        for item in Cart.myCart:
            values=Cart.myCart[item]
            bill=int(values[1])*int(values[2])
            self.total+=bill
        self.total=f'Bill is {self.total}$'
        label_head=Label(self.remove_frame,text="Review Cart",bg='#8C5394',fg='#FFFFFF',font=('Constantia',16))
        label_head.place(x=0,y=0,height=40,width=683)
        label_id=Label(self.remove_frame,text="Enter Product ID remove:",bg='#FFF5CF',font=('Constantia',12))
        label_id.place(x=20,y=50)
        self.total_bill=Label(self.remove_frame,text=self.total,bg='#FFF5CF',font=('Constantia',12))
        self.total_bill.place(x=0,y=80,width=683)
        self.entry_id=Entry(self.remove_frame)
        self.entry_id.place(x=250,y=50)
        b=Button(self.remove_frame,text='Enter',bg='#8C5394',fg='#ffffff',font=('Constantia',12),activebackground='#78d6ff',command=self.remove_and_reload)
        b.place(x=550,y=46,height=26,width=80)

    def generate_bill(self):
        '''This function generates invoice kind of screen when customer finishes the transaction'''
        self.root=Tk()
        self.root.geometry('500x700')
        self.root.resizable(0,0)
        self.root.title('Bill')
        self.root.configure(bg='#E0CCE3')
        self.f=Frame(self.root,bg="#c5bec6") 
        self.f.place(x=0,y=0,width=500,height=100)
        img = Image.open('images\shoe.jpg')
        img=img.resize((100,75),Image.ANTIALIAS)
        img=ImageTk.PhotoImage(img)
        label_img=Label(self.f,image=img)
        label_img.photo=img
        label_img.place(x=-2,y=-12)
        self.l=Label(self.root,text='AIR IT',font=('Eras Demi ITC',18),bg='#c5bec6',fg='#4e2f25')
        self.l.place(x=150,y=10)
        self.j=Label(self.root,text='Thankyou for shopping',font=('Constantia',14),fg='#c5bec6',bg='#8C5394')
        self.j.place(x=200,y=50)
        content_frame=Frame(self.root,bg="white")
        content_frame.place(x=0,y=100,width=500,height=600)
        columns=Label(content_frame,text='Product Id\tName\t\t\tPrice\t\tQuantity')
        columns.place(x=0,y=40)
        dashes1=Label(content_frame,text=str('*'*400))
        dashes1.place(x=0,y=70)
        c_y=100
        for i in Cart.myCart:
            values=Cart.myCart[i]
            line=f'{i:24}{values[0]:50}{values[1]:10}{values[2]:10}'
            line_lab=Label(content_frame,text=line)
            line_lab.place(x=0,y=c_y)
            c_y+=30
        dashes2=Label(content_frame,text=str('*'*400))
        dashes2.place(x=0,y=c_y)
        c_y+=30
        self.total=0
        for item in Cart.myCart:
            values=Cart.myCart[item]
            bill=int(values[1])*int(values[2])
            self.total+=bill
        self.total=f'Bill is {self.total}$ paid via {self.payment_via}'
        total_bill=Label(content_frame,text=self.total)
        total_bill.place(x=50,y=c_y)
        c_y+=30
        dateTime=Label(content_frame,text=f'Time:{datetime.now().strftime("%H:%M:%S"):16} Date:{datetime.now().strftime("%d-%b-%y"):20}')
        dateTime.place(x=50,y=c_y)
        Cart.myCart={}
        ~self

    def update_rating(self):
        '''This function rates the product using customer input and do further procedures'''
        self.products=self.button.update_rating(self.products)
        self.save_product()
        self.generate_bill()

    def rate_product(self):
        '''This function creates graphical window to let the customer rate the products'''
        self.root.destroy()
        self.load_product() 
        ratewin=Tk()
        ratewin.geometry('500x500') 
        ratewin.config(bg='#E0CCE3')
        columns=Label(ratewin,text='Product Name')
        columns.place(x=10,y=40)
        c_y=100
        for i in Cart.myCart:
            values=Cart.myCart[i]
            if i in self.products:
                label=Label(ratewin,text=values[0])
                label.place(x=10,y=c_y)
                c_y+=30
        lab1=Label(ratewin,text='Enter rating (0-5):')
        lab1.place(x=10,y=c_y+20)
        entry_name=Entry(ratewin)
        entry_name.place(x=200,y=c_y+60,width=100,height=30)
        self.button=RateButton(entry_name,ratewin,ratewin,text='Rate',bg='#8C5394',fg='#ffffff',font=('Constantia',12),activebackground='#78d6ff', bd=0, highlightthickness=0)
        self.button.configure(command=self.update_rating)
        self.button.place(x=200,y=c_y+100)

    def __invert__(self):
        '''This function sends the transaction summary to customer account if valid email is entered!
            Unary operator(~) is overloaded to execute send email functionality'''
        try:
            self.body=f'Thank You {self.customer_name} for shopping from Ait It, your total {self.total}. We hope that you like our products and shop again.\nRegards: AirIt'
            message = 'Subject: {}\n\n{}'.format('ThankYou For Shopping', self.body)
            server=smtplib.SMTP('smtp.gmail.com',587)
            server.ehlo()
            server.starttls()
            server.login('airitshoes@gmail.com','airitshoes')
            server.sendmail('airitshoes@gmail.com',self.customer_mail,message)
            server.close()
            messagebox.showinfo('ThankYou','Confirmation email has been sent, if you entered valid email.')
        except:
            pass

    def save_number_and_proceed(self):
        '''If customer choose to pay with card, this function takes his credit card number for dummy transaction'''
        self.credit_card=self.entry.get()
        self.newwin.destroy()
        self.add_to_sales(self.username)
        self.rate_product()

    def checkout(self):
        '''This function finalizes the transaction with taking the payment details from user and producing the invoice'''
        user_input=messagebox.askyesno("Checkout", "Are you sure you want to checkout?")
        if user_input==YES:
            if len(Cart.myCart)==0:
                self.root.destroy()
            else:
                payment_method=messagebox.askyesno('Payment via Card', 'Select Yes for payment via credit card and no for cash')
                if payment_method==YES:
                    self.payment_via='Credit Card'
                    self.newwin=Tk()
                    self.newwin.geometry('200x200')
                    self.newwin.config(bg='#E0CCE3')
                    label=Label(self.newwin,text='Please enter Credit Card number')
                    label.place(x=10,y=40)
                    self.entry=Entry(self.newwin)
                    self.entry.place(x=40,y=80,width=120)
                    button=Button(self.newwin,text='Enter Card Number',bg='#8C5394',fg='#ffffff',font=('Constantia',12),activebackground='#78d6ff', bd=0, highlightthickness=0,command=self.save_number_and_proceed)
                    button.place(x=30,y=140,width=140)
                else:
                    self.payment_via='Cash'
                    self.add_to_sales(self.username)
                    self.rate_product()
        if user_input==NO:
            pass

    def check_cart(self):
        '''This is a very special function which restricts the customer from destroying the window while 
        there is something in his cart, it is our digital security guard'''
        if len(self.myCart)>0:
            messagebox.showerror('Empty Cart','You can\'t close the app while your cart is not empty! ')
        else:
            self.root.destroy()        

    def logged_in(self):
        '''This function checks whether to open admin or customer panel and then opens the panel according to given credentials'''
        self.load_account()
        self.keys=list(self.customer.keys())
        if (self.entry_user.get() =='admin') and (self.entry_pass.get()=='admin'):Admin.loggedin_admin(self)    
        elif (self.entry_user.get() in self.keys) and (self.entry_pass.get()==self.customer[self.entry_user.get()][-1]):
            customer_data=self.customer[self.entry_user.get()]
            self.customer_mail=customer_data[1]
            self.customer_name=customer_data[0]
            self.username=self.entry_user.get()
            Cart.__init__(self,self.username)
            self.root.destroy()
            self.root=Tk()
            self.root.title('Air It')
            self.root.geometry('1200x700')
            self.root.protocol('WM_DELETE_WINDOW', self.check_cart)
            self.root.configure(bg='#F9F0FA')
            self.root.resizable(0,0)
            self.f1=Frame(self.root,bg="#c5bec6") 
            self.f1.place(x=0,y=0,width=1200,height=80)
            img = Image.open('images\shoe.jpg')
            img=img.resize((120,90),Image.ANTIALIAS)
            img=ImageTk.PhotoImage(img)
            label_img=Label(self.f1,image=img)
            label_img.photo=img
            label_img.place(x=-2,y=-12)
            l=Label(self.root,text='AIR IT',font=('Eras Demi ITC',36),bg='#c5bec6',fg='#4e2f25')
            l.place(x=150,y=10)
            self.current_frame=None
            bkg=Frame(self.root,bg="#8C5394") 
            bkg.place(x=50,y=130,width=300,height=520)
            menu=Label(self.root,text='MENU',font=('Constantia',28),fg='#4e2f25',bg='#E0CCE3')
            menu.place(x=50,y=180,width=300,height=80)
            b1=Button(text="View All Products",font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.view_products)
            b1.place(x=50,y=320,width=300,height=40)
            b2=Button(self.root,text="My Cart",font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.view_cart)
            b2.place(x=50,y=400,width=300,height=40)
            b3=Button(self.root,text="Prevoius Purchases",font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.show_customer_history)
            b3.place(x=50,y=480,width=300,height=40)
            b4=Button(self.root,text="Check out",font=('Constantia',14,'italic'),fg='#4e2f25',bg='#E0CCE3',command=self.checkout)
            b4.place(x=50,y=560,width=300,height=40)
            self.view_products()
        else:messagebox.showerror('User not exist','Any user with such credentials do not exist!')
       
class Account(Customer,Admin):
    '''This account class inherits from customer and admin class, it instantiate the initial login/signup window'''
    def __init__(self):
        Customer.__init__(self)
        Products.__init__(self)
    def save_account(self):
        '''Save accounts in file'''
        self.load_account()
        try:
            if len(self.entry_user.get())==0 or len(self.entry_name.get())==0 or len(self.entry_email.get())==0 or len(self.entry_phone.get())==0 or len(self.entry_pass.get())==0:
                self.error_title='Invalid Value'
                self.error_message='Please enter values in all entry fields'
                raise ValueError
            if self.entry_user.get() in self.customer:
                self.error_title='Username exist'
                self.error_message='Username already exists, please consider using a different one!'
                raise KeyError
            if True:
                self.error_title='Invalid phone number'
                self.error_message='Please enter a valid phone number!'
                if isinstance(int(self.entry_phone.get()),int)==False:
                    raise ValueError
            if  '@' and '.' not in self.entry_email.get():
                self.error_title='Invalid email address'
                self.error_message='Please enter a valid email address'
                raise ValueError

            self.customer.update({self.entry_user.get():[self.entry_name.get(),self.entry_email.get(),self.entry_phone.get(),self.entry_pass.get()]})
            self.f=open("customer.txt","w+")
            for i in self.customer:
                self.f.write(str(i)+';')
                for j in self.customer[i]:
                    self.f.write(str(j)+';')
                self.f.write('\n')
            self.f.close()
            self.logged_in()
        except:
            messagebox.showerror(self.error_title,self.error_message)

    def create_account(self):
        '''Allows the customer to create an account if he does not have one'''
        self.root.destroy()
        self.root=Tk()
        self.root.geometry('450x500')
        self.root.title('Air It')
        self.root.configure(bg='#F9F0FA')
        self.root.resizable(0,0)
        self.f=Frame(self.root,bg="#c5bec6") 
        self.f.place(x=0,y=0,width=450,height=80)
        img = Image.open('images\shoe.jpg')
        img=img.resize((120,90),Image.ANTIALIAS)
        img=ImageTk.PhotoImage(img)
        label_img=Label(self.f,image=img)
        label_img.photo=img
        label_img.place(x=-2,y=-12)
        self.l=Label(self.root,text='AIR IT',font=('Eras Demi ITC',24),bg='#c5bec6',fg='#4e2f25')
        self.l.place(x=150,y=10)
        label_name=Label(self.root,text="Enter Full Name:",bg='#FFF5CF',font=('Constantia',14))
        label_name.place(x=10,y=120)
        self.entry_name=Entry(self.root)
        self.entry_name.place(x=200,y=128)
        label_email=Label(self.root,text="Enter Email Address:",bg='#FFF5CF',font=('Constantia',14))
        label_email.place(x=10,y=150)
        self.entry_email=Entry(self.root)
        self.entry_email.place(x=230,y=158)
        label_phone=Label(self.root,text="Enter Phone Number:",bg='#FFF5CF',font=('Constantia',14))
        label_phone.place(x=10,y=180)
        self.entry_phone=Entry(self.root)
        self.entry_phone.place(x=230,y=188)
        label_user=Label(self.root,text="Enter Username:",bg='#FFF5CF',font=('Constantia',14))
        label_user.place(x=10,y=210)
        self.entry_user=Entry(self.root)
        self.entry_user.place(x=200,y=218)
        label_pass=Label(self.root,text="Enter Password:",bg='#FFF5CF',font=('Constantia',14))
        label_pass.place(x=10,y=240)
        self.entry_pass=Entry(self.root)
        self.entry_pass.place(x=200,y=248)
        b_create=Button(self.root,text="Create Account",font=('Constantia',16),bg='#523A28',fg='#FFFFFF',command=self.save_account)
        b_create.place(x=110,y=300)

    def login_window(self):
        '''Allows the customer/admin to login if they have an account, otherwisw allowing to create one'''
        self.root = Tk()
        self.root.title("Air It")
        self.root.geometry('450x400')
        self.root.resizable(0,0)
        self.root.configure(bg='#F9F0FA')
        self.f=Frame(self.root,bg="#c5bec6") 
        self.f.place(x=0,y=0,width=1200,height=80)
        img = Image.open('images\shoe.jpg')
        img=img.resize((120,90),Image.ANTIALIAS)
        img=ImageTk.PhotoImage(img)
        label_img=Label(self.f,image=img)
        label_img.photo=img
        label_img.place(x=-2,y=-12)
        self.l=Label(self.root,text='AIR IT',font=('Eras Demi ITC',24),bg='#c5bec6',fg='#4e2f25')
        self.l.place(x=150,y=10)
        label_user=Label(self.root,text="Username:",bg='#FFF5CF',font=('Constantia',16))
        label_user.place(x=80,y=100)
        self.entry_user=Entry(self.root)
        self.entry_user.place(x=210,y=110)
        label_pass=Label(self.root,text="Password:",bg='#FFF5CF',font=('Constantia',16))
        label_pass.place(x=80,y=150)
        self.entry_pass=Entry(self.root)
        self.entry_pass.place(x=210,y=160)
        b_log=Button(self.root,text="Log in",font=('Constantia',16),bg='#523A28',fg='#FFFFFF',command=self.logged_in)
        b_log.place(x=160,y=200)
        b_create=Button(self.root,text="Create Account",font=('Constantia',16),bg='#523A28',fg='#FFFFFF',command=self.create_account)
        b_create.place(x=120,y=250)
        self.root.mainloop()

#Initiating the code
m=Account()
m.login_window()

# Coded by
#Muhammad Faizan
#CS-20098

#Muhammad Hamdan
#CS-20086

#Umer Khalil
#CS-20135
