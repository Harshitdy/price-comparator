from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import errorcode


with open("F:\\internship\\to complete\\price comparator\\price comparator templates\\templates\\config.json", 'r') as j: # location of config.json file
   params = json.load(j)["params"]

local_server = True



try:
    cnx = mysql.connector.connect(user = params['user'], password = params['password'],
                              host='localhost',
                              database=params['user_datbase'])
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
cursor = cnx.cursor()


app = Flask(__name__)

app.secret_key = 'the-random-string'

app.config.update(
   MAIL_SERVER = 'smtp.gmail.com',
   MAIL_PORT = '465',
   MAIL_USE_SSL = 'True',
   MAIL_USERNAME = params['gmail_user'],
   MAIL_PASSWORD = params['gmail_password']
)
mail = Mail(app)
if (local_server):                              
   app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
   app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Signup_data(db.Model):
   S_NO = db.Column(db.Integer, primary_key=True)
   Full_name = db.Column(db.String(20), unique = False, nullable = False)
   Email = db.Column(db.String(20), unique=True, nullable=False)
   Password = db.Column(db.String(20), unique=True, nullable=False)
   Phone = db.Column(db.String(15), unique=True, nullable=False)
   Date = db.Column(db.String(10), unique=False, nullable=True)

@app.route('/')
def sign_in():
   return render_template("signin.html")

@app.route('/comp')
def comp():
   return render_template("price_comp.html")

@app.route('/sign_up', methods=['GET', 'POST'])
def Sign_up():
   if request.method == "POST":
      Full_Name = request.form.get('Username')
      email = request.form.get('email')
      password = request.form.get('password')
      Phone_num = request.form.get('Phone')
      entry = Signup_data(Full_name = Full_Name, Email = email, Password = password, Phone = Phone_num, Date = datetime.now())
      db.session.add(entry)
      db.session.commit()
      try:
         mail.send_message('Someone SignedUp',
                           sender = email,
                           recipients = [params['gmail_user']],
                           body = Full_Name+'\n' + Phone_num
                            )

      except Exception as e:
         print(e)
      return render_template('signin.html', params = params)
   else:
      return render_template('signup.html', params = params)

@app.route('/sign_validation', methods=["GET","POST"])
def sign_validation():
   email = request.form.get('email')
   password = request.form.get('pass')
   if ('user' in session and session['user'] == email):
      return render_template('searchpage.html')
   else:
      cursor.execute("""SELECT * FROM `signup_data` WHERE `Email` LIKE '{}' AND `Password` LIKE '{}'"""
                  .format(email, password))
      users = cursor.fetchall()
   
      if len(users)>0:
         return render_template('searchpage.html', data = users)
      else:
         return render_template('signin.html')

@app.route('/all_data', methods=["GET","POST"])
def Alldata():
   if request.method == "POST":
      flipkart = request.form.get('flipkart')
      amazon = request.form.get('amazon')
      grofers = request.form.get('grofers')
      headsupfortails = request.form.get('headsupfortails')
      twenty_kg = request.form.get('20kg')
      ten_kg = request.form.get('10kg')
      three_kg = request.form.get('3kg')
      one_kg = request.form.get('1kg')

      # PREPARED STATEMENT
      sql = """SELECT * FROM `all_data` WHERE `Data_source` IN (%s,%s,%s,%s) AND `Weight` IN (%s,%s,%s,%s) ORDER BY `Price`"""

      # EXECUTE WITH PARAMS
      cursor.execute(sql, (flipkart, amazon, grofers, headsupfortails, one_kg, three_kg, ten_kg, twenty_kg))

      all_data2 = cursor.fetchall()
   return render_template("searchpage.html", dataSrc = all_data2)



if __name__=="__main__":
    app.run(debug=True)