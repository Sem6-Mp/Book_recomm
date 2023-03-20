from flask import Flask,render_template,request, session, redirect, url_for
from flask_pymongo import PyMongo
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/signup_bend'
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/SignUp', methods= ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data= request.form
        mongo.db.record.insert_one(dict(Name = data['name'],Email= data['email'], Password= data['password']))
    return render_template('signup.html')

@app.route('/LogIn', methods= ['POST','GET'])
def login():
    # users = mongo.db.users
    # login_user = users.find_one({'email': request.form['email']})
    # bcrypt = {}
    # if login_user:
    #     if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
    #         session['email'] = request.form['email']
    #         return redirect(url_for('index'))
    return render_template('signup.html')

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