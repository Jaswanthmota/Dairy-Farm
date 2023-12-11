from flask import Flask,render_template,request,redirect,session,url_for
from mysql.connector import connect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os

con=connect(host='localhost',port=3306,database='products',user='root')


app=Flask(__name__)
app.secret_key='hghfgfchhfhfh'
bcrypt = Bcrypt(app)

app.config['IMAGE_UPLOADS']="C:/Users/Jaswanth/Projects/farmer-friendly-app/static/images"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def Login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('Sign_up.html')

@app.route('/admin')
def admin():
    return render_template('admin_login.html')

@app.route('/adminlogin_validation',methods=["GET","POST"])
def adminlogin_validation():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        session['admin']=password
        if (email=="admin123@gmail.com") and (password=='admin'):
            return render_template('Admin.html')
        else:
            return "Check ur credentials"
    else:
        return render_template('admin_login.html')

@app.route('/adminpanel')
def adminPanel():
    if session.get('admin'):
        return render_template('Admin.html')
    else:
        return redirect('/admin')

@app.route('/Signup_validation',methods=["POST","GET"])
def Signup_validation():
    if request.method=="POST":
        email=request.form['email']
        name=request.form['name']
        cur=con.cursor()
        cur.execute('select * from users where email=%s',(email,))
        x=cur.fetchone()
        if x==None:
            pass1=request.form['pass1']
            pass2=request.form['pass2']
            if pass1 == pass2:
                cur=con.cursor()
                password=bcrypt.generate_password_hash(pass1)
                cur.execute("insert into users values(%s,%s,%s)",(name,email,password))
                con.commit()
                return redirect('/login')
            else:
                return "Please Check ur Password,Password should Match!..."
        else:
            return redirect('/login')
    else:
        return redirect('/signup')

@app.route('/login_validate',methods=["POST","GET"])
def login_validate():
    if request.method=="POST":
        email=request.form['email']
        session['email']=email
        cur=con.cursor()
        cur.execute("select * from users where email=%s",(email,))
        x=cur.fetchone()
        if x!=None:
            return redirect('/prodetails')
        else:
            return redirect('/signup')
    else:
        return redirect('/login')

@app.route('/prodetails')
def prodetails():
    if session.get('email'):
        cur=con.cursor()
        cur.execute('select * from products')
        y=cur.fetchall()
        return render_template('viewproducts.html',productdetails=y)
    else:
        return render_template('login.html')


@app.route('/add_product')
def add_case():
    if session.get('admin'):
        return render_template('AddProduct_form.html')
    else:
        return render_template('admin_login.html')

@app.route('/AddingProductInDb',methods=["GET","POST"])
def AddingProductInDb():
    if request.method=="POST":
        fid=request.form['fid']
        pid=request.form['pid']
        if request.files:
            image=request.files['image']
            image.save(os.path.join(app.config['IMAGE_UPLOADS'],image.filename))
        quantity=request.form['quantity']
        price=request.form['price']
        cur=con.cursor()
        cur.execute("insert into products values(%s,%s,%s,%s,%s)",
        (fid,pid,image.filename,quantity,price))
        con.commit()
        return render_template('Admin.html')
    else:
        return render_template("admin_login.html")

@app.route('/editproduct')
def Editcase():
    if session.get('admin'):
        return render_template('editproductid.html')
    else:
        return render_template('admin_login.html')


@app.route('/EditingCaseInDb',methods=["GET","POST"])
def EditingCaseInDb():
    if request.method=="POST":
        pid=request.form['pid']
        cur=con.cursor()
        cur.execute("select * from products where pid=%s",(pid,))
        x=cur.fetchone()
        if x==None:
            return render_template('AddProduct_form.html')
        else:
            fid=request.form['fid']
            pid=request.form['pid']
            quantity=request.form['quantity']
            price=request.form['price']
            cur=con.cursor()
            cur.execute("update products SET fid=%s,pid=%s,quantity=%s,price=%s where pid=%s",(fid,pid,quantity,price,pid))
            con.commit()
            return render_template('Admin.html')
    else:
        return render_template("admin_login.html")

@app.route('/admineditproduct',methods=['GET','POST'])
def admineditcase():
    pid=request.form['pid']
    cur=con.cursor()
    cur.execute('select * from products where pid=%s',(pid,))
    x=cur.fetchone()
    if x!=None:
        return render_template('EditProduct_Form.html',x=x)
    else:
        return render_template("AddProduct_Form.html")

@app.route('/Product_details')
def Case_details():
    if session.get('admin'):
        cur=con.cursor()
        cur.execute('select * from products')
        y=cur.fetchall()
        return render_template('viewproduct.html',productdetails=y)
    else:
        return render_template('admin_login.html')


@app.route('/addtocart/<string:pid>')
def Savecase(pid):
    if not session.get('email'):
        return render_template('login.html')
    else:
        cur=con.cursor()
        cur.execute('select * from mycart where pid=%s',(pid,))
        x=cur.fetchone()
        con.commit()
        if x!=None and len(x)!=0:
            return redirect('/mycart')
        else:
            cur=con.cursor()
            cur.execute('select * from products where pid=%s',(pid,))
            x=cur.fetchone()
            cur.execute('insert into mycart values(%s,%s,%s,%s,%s,%s)',(session.get('email'),x[0],x[1],x[2],x[3],x[4]))
            con.commit()
            return redirect('/mycart')


@app.route('/mycart')
def Mycases():
    if session.get('email'):
        cur=con.cursor()
        cur.execute('select * from mycart where email=%s',(session.get('email'),))
        x=cur.fetchall()
        if x!=None and len(x)!=0:
            return render_template('myproducts.html',myproducts=x)
        else:
            return render_template('myproducts.html',myproducts="No products in your cart")
    else:
        return redirect('/login')


@app.route('/deletecart/<string:pid>/')
def DeleteCase(pid):
    if session.get('email'):
        cur=con.cursor()
        cur.execute('DELETE FROM mycart WHERE pid=%s' ,(pid,))
        con.commit()
        return redirect('/mycart')
    else:
        return redirect('/login')
    
@app.route('/deletecartandpayment/<string:pid>/')
def DeleteCase1(pid):
    if session.get('email'):
        cur=con.cursor()
        cur.execute('DELETE FROM mycart WHERE pid=%s' ,(pid,))
        # cur.execute('DELETE FROM products WHERE pid=%s' ,(pid,))
        con.commit()
        return redirect('/payment')
    else:
        return redirect('/login')
    
@app.route('/payment')
def payment():
    if session.get('email'):
        return render_template('payment.html')
    else:
        return redirect('/login')
    
@app.route('/password')
def Password():
    if session.get('email'):
        return render_template('password.html')
    else:
        return redirect('/login')


@app.route('/repeatnew', methods=['GET', 'POST'])
def RepeatNew():
    if request.method == "POST":
        old = request.form['old1']
        new = request.form['new']
        repeatn = request.form['repeat']

        print("Old:", old)
        print("New:", new)
        print("Repeat:", repeatn)

        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE email=%s', (session.get('email'),))
        x = cur.fetchone()
        print("Fetched user data:", x)

        if bcrypt.check_password_hash(x[2], old):
            if new == repeatn:
                new_hashed_password = generate_password_hash(new)
                cur = con.cursor()
                cur.execute("UPDATE users SET password=%s WHERE email=%s", (new_hashed_password, session.get('email')))
                con.commit()
                print("Password updated successfully.")
                return redirect('/logout')
            else:
                print("New passwords do not match.")
                return render_template('password.html')
        else:
            print("Old password doesn't match.")
            return render_template('password.html')
    else:
        return redirect('/login')
@app.route('/repeatnew',methods=['GET','POST'])
def RepeatNew():
    if request.method=="POST":
        old=request.form['old1']
        new=request.form['new']
        repeatn=request.form['repeat']
        cur=con.cursor()
        cur.execute('select * from users where email=%s',(session.get('email'),))
        x=cur.fetchone()
        if bcrypt.check_password_hash(x[2], old):
            if new==repeatn:
                cur=con.cursor()
                password=bcrypt.generate_password_hash(new)
                cur.execute("update users SET password=%s where email=%s",(password,session.get('email')))
                con.commit()
                return redirect('/logout')
            else:
                return render_template('password.html')
        else:
            return render_template('password.html')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session['email']=None
    return redirect('/')


@app.route('/logoutadmin')
def logoutadmin():
    session['admin']=None
    return redirect('/')

if __name__=="__main__":
     app.run(debug=True)