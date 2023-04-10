from flask import Flask,render_template,request, session, redirect, url_for
from flask_pymongo import PyMongo
import pickle
import numpy as np
import bcrypt
import pymongo





popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

sem6_df = pickle.load(open('new.pkl','rb'))
sem6_df_rom = pickle.load(open('rom.pkl','rb'))
sem6_df_ms_tr = pickle.load(open('mystery_triller.pkl','rb'))
sem6_lit_fic = pickle.load(open('literature_fiction.pkl','rb'))
sem6_eng =pickle.load(open('engineering.pkl','rb'))
sem6_manga = pickle.load(open('manga.pkl','rb'))

app = Flask(__name__)

app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://ruchirrao04:ruchir03@cluster0.coezmw7.mongodb.net/?retryWrites=true&w=majority")

db = client.get_database('total_records')

records = db.register

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )


@app.route('/new')
def neww():
    return render_template('new.html',
                           book_name = list(sem6_df['title'].values),
                           author=list(sem6_df['author'].values),
                           image=list(sem6_df['image_link'].values),
                           publisher=list(sem6_df['publisher'].values),
                           language=list(sem6_df['language'].values),
                           rating=list(sem6_df['rating'].values)
                           )

@app.route('/romance')
def romm():
    return render_template('romance.html',
                           book_name = list(sem6_df_rom['title'].values),
                           author=list(sem6_df_rom['author'].values),
                           image=list(sem6_df_rom['image_link'].values),
                           publisher=list(sem6_df_rom['publisher'].values),
                           language=list(sem6_df_rom['language'].values),
                           rating=list(sem6_df_rom['rating'].values)
                           )


@app.route('/mystery_triller')
def mystrs():
    return render_template('mys_tr.html',
                           book_name = list(sem6_df_ms_tr['title'].values),
                           author=list(sem6_df_ms_tr['author'].values),
                           image=list(sem6_df_ms_tr['image_link'].values),
                           publisher=list(sem6_df_ms_tr['publisher'].values),
                           language=list(sem6_df_ms_tr['language'].values),
                           rating=list(sem6_df_ms_tr['rating'].values)
                           )

@app.route('/literature_fiction')
def litfic():
    return render_template('lit_fic.html',
                           book_name = list(sem6_lit_fic['title'].values),
                           author=list(sem6_lit_fic['author'].values),
                           image=list(sem6_lit_fic['image_link'].values),
                           publisher=list(sem6_lit_fic['publisher'].values),
                           language=list(sem6_lit_fic['language'].values),
                           rating=list(sem6_lit_fic['rating'].values)
                           )

@app.route('/engineering')
def engg():
    return render_template('engine.html',
                           book_name = list(sem6_eng['title'].values),
                           author=list(sem6_eng['author'].values),
                           image=list(sem6_eng['image_link'].values),
                           publisher=list(sem6_eng['publisher'].values),
                           language=list(sem6_eng['language'].values),
                           rating=list(sem6_eng['rating'].values)
                           )


@app.route('/manga')
def mangg():
    return render_template('manga.html',
                           book_name = list(sem6_manga['title'].values),
                           author=list(sem6_manga['author'].values),
                           image=list(sem6_manga['image_link'].values),
                           publisher=list(sem6_manga['publisher'].values),
                           language=list(sem6_manga['language'].values),
                           rating=list(sem6_manga['rating'].values)
                           )

@app.route("/register", methods=['post', 'get'])
def register():
    message = ''
    
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            #insert it in the record collection
            records.insert_one(user_input)
            
            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data["email"]
            #if registered redirect to logged in as the registered user
            return redirect(url_for("logged_in"))
    return render_template('register.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in',methods=["POST", "GET"])
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email,
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))
   
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('signout.html')

@app.route('/category')
def categ():
    return render_template('category.html')


@app.route('/about_us')
def sigmas():
    return render_template('about_us.html')

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)