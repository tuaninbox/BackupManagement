import os, datetime
from flask import Flask, render_template, url_for, abort, send_file, redirect, request, session, flash
from functools import wraps
#from flask import *
#from functools import wraps
import mimetypes

app=Flask(__name__)
app.secret_key = 'modaiewkjlhdsa fhdsajkf ewuihk dddasdfha fad'

class User:
    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname

    def initials(self):
        return "{}.{}".format(self.firstname[0],self.lastname[0])



#@app.route('/')
@app.route('/cewabackup')
def index():
    return render_template('home.html', title="This is title", user=User("Tuan", "Hoang"))


@app.route('/ses')
def ses():
    return """<html><body>%s'<br>'%s</body></html>
    """ % (app.permanent_session_lifetime,session.modified)


@app.route('/')
@app.route('/ip')
def ipaddress():
    ipadd = request.remote_addr
#    ipadd = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return render_template('ip.html', title="Your IP Address",ipadd=ipadd)

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrap

@app.route('/view/<path:file>', methods = ['POST','GET'] )
@login_required
def viewfile(file):
    session.modified = True
    base_dir = os.path.normpath('/tftproot/ConfigurationArchive')
    abs_path=os.path.normpath(os.path.join(base_dir,file))
    #ftype, encoding = mimetypes.guess_type(abs_path,strict=False)
    #print(ftype, encoding)
    return send_file(abs_path,mimetype='text/plain')


@app.route('/configuration', defaults={'req_path': ''})
@app.route('/<path:req_path>')
@login_required
def listing(req_path=''):
    base_dir = os.path.normpath('/tftproot/ConfigurationArchive')

    # Joining the base and the requested path
    abs_path = os.path.normpath(os.path.join(base_dir, req_path))
    #print(abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    #if os.path.isfile(abs_path):
     #   ftype, encoding = mimetypes.guess_type(abs_path,strict=False)
       # print(ftype, encoding)
    #    return send_file(abs_path, as_attachment=False)

    # Show directory contents
    files=[]
    folders=[]
    items = sorted(os.listdir(abs_path),key=lambda f: os.path.getctime("{}/{}".format(abs_path, f)), reverse=True)
    for item in items:
        #print(os.path.join(abs_path,item))
        if os.path.isfile(os.path.join(abs_path, item)):
            files.append(item)
         #   print(files)
        else: #if os.path.isdir(os.path.join(abs_path, file)):
            folders.append(item)
          #  print(folders)

    parent = os.path.split(req_path)
    if abs_path == base_dir:
        req_path = ""
    elif req_path[-1:] != "/":
        req_path = req_path + "/"


    #print(files)
    #print(folders)
    return render_template('list.html', parent=parent, path=req_path, folders=folders, files=files, title="Configuration")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    session.modified = True


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'username' or request.form['password'] != 'password':
	    error = 'Invalid Credentials. Please try again'
        else:
            session['logged_in'] = True
            #session.permanent = True
            #app.permanent_session_lifetime = datetime.timedelta(minutes=3)
            #session.modified = True
            return redirect(url_for('listing'))
    return render_template('login.html', error=error)
if __name__ == "__main__":
    app.run("10.43.3.241",port=80,debug=False)
