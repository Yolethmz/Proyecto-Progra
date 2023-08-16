from flask import Flask,jsonify
from flask_mail import Mail, Message
from flask import render_template,redirect, url_for, request , session
from datetime import datetime
import os
import socket 
from werkzeug.utils import secure_filename

#context={'now':int(time.time()),'strftime':time.strftime }

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

now = datetime.now()
now1 = now.strftime("%Y-%m-%d %H:%M:%S")
    
import pymysql
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'reds209ndsldssdsljdsldsdsljdsldksdksdsdfsfsfsfis'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.static_folder = 'static'

app.config["IMAGE_UPLOADS"] = "static/uploads/"
app.config["IMAGE_UPLOADS1"] = "static/profiles/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF",'png', 'jpg', 'jpeg', ]




mail_settings = {
    "MAIL_SERVER": 'manolito2562000@gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'xxxxxx@gmail.com',   
    "MAIL_PASSWORD": '1234xxxxx'           
}

app.config.update(mail_settings)
mail = Mail(app)
app.config.update(mail_settings)
mail = Mail(app)

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False
db = pymysql.connect("localhost", "root", "", "test")
counter = 1

@app.route('/home')
def home():
    now = datetime.now()
    now1 = now.strftime("%Y-%m-%d %H:%M:%S")
   # print(now)
    cursor = db.cursor()
    sql = "SELECT * FROM empname where statusflag = '1' order by id asc"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('people.html', results=results,now1=now1)

@app.route('/')
@app.route('/people')
def people():
    if session.get("user") != None:
        
  
        cursor = db.cursor()
        sql = "SELECT e.id,e.forname,	e.lastname,e.detail,	e.tags,	REPLACE (e.filename, '', '#') AS filename,e.ddttm,e.usernickname,e.active, Count(s.score) As _count, e.user_id FROM empname as e LEFT JOIN scores s  on s.post_id = e.id WHERE	e.active = '1' GROUP BY e.id  ORDER BY e.id desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        return render_template('people.html', results=results)
    else:
        return redirect(url_for('login'))


@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == "POST":
        textsearch = request.form
        wordtext = textsearch['mytext']
  
        cursor = db.cursor()
        sql = "SELECT e.id,e.forname,	e.lastname,e.detail,	e.tags,	REPLACE (e.filename, '', '#') AS filename,e.ddttm,e.usernickname,e.active, Count(s.score) As _count , e.user_id FROM empname as e LEFT JOIN scores s  on s.post_id = e.id WHERE	e.active = '1' and ( e.forname LIKE N'%" + wordtext + "%' or e.lastname Like N'%" + wordtext + "%' ) GROUP BY e.id  ORDER BY e.id desc"
        #print(sql)
       # exit
        cursor.execute(sql)
        results = cursor.fetchall()
        #return redirect(url_for('search', results1=results))
    
        return render_template('people_search.html', results1=results)


@app.route('/contact')
def contact():
   
    global counter
    counter += 1
    
    return render_template("contact.html", count=counter)


@app.route('/board/<int:id>' , methods=['GET','POST'])
def board(id):
    
    
    error = None
    if request.method == "POST":
        now1 = now.strftime("%Y-%m-%d %H:%M:%S")
        uselogin = request.form
        user = uselogin['comment']
        cursor = db.cursor()
        if user != '' :
            cursor = db.cursor()
            query_string = "SELECT e.id,e.forname,	e.lastname,e.detail,	e.tags,	REPLACE (e.filename, '', '#') AS filename,e.ddttm,e.usernickname,e.active, Count(s.score) As _count, e.user_id FROM empname as e LEFT JOIN scores s  on s.post_id = e.id WHERE	e.active = '1' and e.id = '"+ str(id) + "' GROUP BY e.id  ORDER BY e.id desc  limit 1; "
            cursor.execute(query_string)
            results = cursor.fetchall()
            if results:
                data = cursor.execute("INSERT INTO comments(board_text, user_id, emp_id ,  dttm, active) VALUES (%s,%s,%s,%s,%s)",
                (user, str(session.get("id")) ,str(id) ,now,1 ))
                
                
            else:
               
                
                return render_template("board.html", error='', results = results)
                
        else:
            return render_template("board.html", error='please fill data')

    # Commit to DB
        cursor.connection.commit()
        

    #Close connection
        cursor.close()
        return redirect(url_for('board', id=(id)))
   
    else:
        cursor = db.cursor()
        query_string = "SELECT e.id,e.forname,	e.lastname,e.detail,	e.tags,	REPLACE (e.filename, '', '#') AS filename,e.ddttm,e.usernickname,e.active, Count(s.score) As _count, e.user_id FROM empname as e LEFT JOIN scores s  on s.post_id = e.id WHERE	e.active = '1' and e.id = '"+ str(id) + "' GROUP BY e.id  ORDER BY e.id desc  limit 1; "
        cursor.execute(query_string)
        resultsx = cursor.fetchall()
        
        qlr = "SELECT * , (select nickname from  register where register.id =  comments.user_id and statusflag= '1' limit 1)  as 'user' FROM comments  WHERE emp_id = '"+ str((id))  +"' 	AND active = '1' GROUP BY id 	ORDER BY id DESC; "
        cursor.execute(qlr)
        boardsesult = cursor.fetchall()
    return render_template("board.html", resultsx = resultsx, boardsesult = boardsesult,id=str((id)))




@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == "POST":
        uselogin = request.form
        user = uselogin['exampleInputEmail1']
        lname = uselogin['password']
        nname = uselogin['nickname']
        lasname = uselogin['lastname']
        cursor = db.cursor()
        if user != '' and lname != '' and nname != '':
            cursor = db.cursor()
            query_string = "SELECT * FROM register where user = '"+ user + "' and statusflag= '1' "
            cursor.execute(query_string)
            results = cursor.fetchall()
            if results:
                return render_template("register.html", error='This email is already registered ')
            else:
                data = cursor.execute("INSERT INTO register(user, pass, nickname, lastname, statusflag) VALUES (%s,%s, %s,%s, %s)",
                                     (user, lname, nname, lasname, 1 ))
                if data:
                    # Remove email sending code

                    # Commit to DB
                    cursor.connection.commit()
                    
                    # Close connection
                    cursor.close()
                    
                    return redirect(url_for('login', success='success'))  # Redirect to the login page after successful registration
        else:
            return render_template("register.html", error='please fill data')

        cursor.connection.commit()
        cursor.close()

    return render_template("register.html", error=error)



@app.route('/post', methods=['GET','POST'])

def insert():
    if session.get("user") != None:
        
        st = str(session.get("user"))
        now = datetime.now()
        now1 = now.strftime("%Y-%m-%d %H:%M:%S")
        error = None
        if request.method == "POST":
      
            savedata = request.form
            user = savedata['forename']
            lname = savedata['lastname']
            detail = savedata['detail']
            dttm = savedata['dtime']
            tag = savedata['tag']
        #image = savedata['image']
            files = request.files['image']
            image = files.filename
            cursor = db.cursor()
            if user != '' and lname != '':
            
                cursor.execute("INSERT INTO empname(forname, lastname,detail,tags,filename, ddttm ,usernickname, mailname,user_id,active) VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s, %s)",(user,lname,detail,tag,image,now,str(session.get("nickname")),str(session.get("user")),str(session.get("id")),1))
            file = request.files['image']
            #return redirect(request.url)
        # if user does not select file, browser also
        # submit an empty part without filename
            if file.filename == '':
            #flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
            else:
                return render_template("home.html", error='please fill data',now1=now1)

    # Commit to DB
            cursor.connection.commit()

    #Close connection
            cursor.close()
       # cursor.close()
       # return render_template("upload_image", error=error)
            return redirect(url_for('people', error=error))
        
        #return render_template("people.html", error=error)  
        
       # return redirect(url_for('insert', error=error))
        else:
            return render_template("home.html", error=error)  
    else:
        return redirect(url_for('login'))
    
    

@app.route('/login', methods=['GET','POST'])
def login():
    #print(request.args.get('success'))
    error = None
    if request.method == "POST":
        uselogin = request.form
        user = uselogin['username']
        password = uselogin['pass']
       # print(user,password)
       # exit
        cursor = db.cursor() 
        #    return redirect(url_for('home'))
        Query_str = "SELECT user , id , nickname , lastname FROM register where statusflag='1'  and user = '"+ user +"' and pass ='"+ password +"';"
       
        
        cursor.execute(Query_str)
       # cursor.execute("SELECT * FROM register where statusflag = 1 and user = '"+ user +"' and pass ='"+ password +"';")
       
        results = cursor.fetchone()
        #print(results)
        if results:
            session.clear()
            session["user"] = results[0]
            session["id"] = results[1]
            session["nickname"] = results[2]
            session["lastname"] = results[3]
            return redirect(url_for('people', error=error))
            
        else:  
               
            return render_template('login.html',error=error, sk="", logins='user,pass not correct')
    
    return render_template('login.html', error=error, sk="",success=request.args.get('success'))


@app.route('/deleted/<int:id>',methods=['GET','POST'])
def deleted(id):
    if session.get("user") != None:
         
        cursor = db.cursor()
        bid= request.args.get('boar_id', None)
       
        cursor.execute("UPDATE comments set active = '0'  WHERE id = %s",(id))

    # Commit to DB
    
        cursor.connection.commit()
        
        return redirect(url_for('board',id=bid))
         
         
    else:
        return redirect(url_for('login'))
         
         
      # print
    #Close connection
        #cursor.close()
#app.debug = True

@app.route('/deleted_post/<int:id>',methods=['GET','POST'])
def deleted_post(id):
    
    if session.get("user") != None:
      # print
        cursor = db.cursor()
        
        filen= request.args.get('filename')
        eid= request.args.get('emp_id', None)
        cursor.execute("UPDATE empname set active = '0'  WHERE id = %s",(id))

    # Commit to DB
        cursor.connection.commit()
        
        os.remove(os.path.join(app.config['IMAGE_UPLOADS'], filen))
        return redirect(url_for('people',id=eid))
    else:
         return redirect(url_for('login'))
        


@app.route('/logout/')
def logout():
    session.pop('user', None)
    session.pop('id', None)
    session.pop('nickname', None)
    return redirect(url_for('login'))


@app.route('/report/<int:id>')
def report(id):
    if session.get("user") != None:
        
        mailname = str(session.get("user"))
        nickname =  str(session.get("nickname"))
        msg = Message( 'Violaciones de la comunidad denunciadas',  sender ='manolito2562000@gmail.com', recipients = [mailname, 'manolito2562000@gmail.com']  ) 
        text = "<h3>support-service </h3><br>manolito2562000@gmail.com" 
        msg.html  = "Hola " + nickname + "<h4>Hemos recibido tu informe correctamente <b>ID de trabajo " + str(id) + "</b><br>Estamos en proceso de revisión</h4>" + text
        mail.body= msg.html
        mail.send(msg)
        return render_template('report.html',error='Somos conscientes del problema y estamos investigando.!')
    else:
        
        
        #return render_template('login.html',error='กรุณาเข้าสู่ระบบ!')
        return redirect(url_for('login'))

@app.route('/pump/<string:id>')
def pump(id):
    if session.get("user") != None:
        cursor = db.cursor()
        #print(str(session.get("user")) + id)
        query_string = " SELECT * FROM scores where userid = '" + str(session.get("id")) + "' and post_id = '"+(id)+"' and active = '1' "
        cursor.execute(query_string)
        results = cursor.fetchall()
        if results:
            #return render_template("pump.html", error='คุณได้กดให้กำลังใจแล้ว')
            return redirect(url_for('people'))
                
        else:
               
            data = cursor.execute("INSERT INTO scores(post_id, score, userid, active) VALUES (%s,%s, %s,%s)", ((id), 1 ,str(session.get("id")),1 ))  
             # Commit to DB
            cursor.connection.commit()

    #Close connection
            cursor.close()
            #return render_template('pump.html',error='คุณได้กดให้กำลังใจ!')
            
            return redirect(url_for('people'))
    else:
            
            
        #return render_template('login.html',error='กรุณาเข้าสู่ระบบ!')
        return redirect(url_for('login'))
            
@app.route('/profile/<string:id>',methods=['GET','POST'])
def profile(id):
    if session.get("user") != None:
        if request.method == "POST":
      
            savedata = request.form
            user = savedata['forename']
            lname = savedata['lastname']
            detail = savedata['about']
            dttm = savedata['dob']
            values = savedata['exampleRadios']
        #image = savedata['image']
            files = request.files['image']
            image = files.filename
            cursor = db.cursor()
            if user != '' and lname != '':
            
                cursor.execute("INSERT INTO profiles(img_file, aboutme,dob,gender,user_id,active) VALUES(%s,%s,%s,%s,%s, %s)",(image,detail,dttm,values,str(session.get("user")),1))
                return render_template("profile.html", success='สำเร็จ',now1=now1)
            file = request.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename
            if file.filename == '':
            #flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOADS1'], filename))
            else:
                return render_template("profile.html", error='please fill data',now1=now1)

    # Commit to DB
            cursor.connection.commit()

    #Close connection
            cursor.close()
        else:
                
            return render_template("profile.html")
        
    else:
        return redirect(url_for('login'))        

if __name__ == '__main__':
    #app.run(host="https://0ee22b64.ngrok.io", debug=True)
    app.run(host='127.0.0.1', port=5000 , debug=True)
#hhttp://e571645f.ngrok.io 
    app.run()
