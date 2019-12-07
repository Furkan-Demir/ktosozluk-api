import os
from flask import Flask, jsonify, make_response, request, abort, render_template, redirect, url_for, session
from flask_restful import reqparse, abort, Api, Resource
from flask_mysqldb import MySQL,MySQLdb
from flask_cors import CORS
import bcrypt
import datetime
import jwt

app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={r"/": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'Red!23412#'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ktosozluk'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/kayit', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        nick = request.form['nick']
        password = request.form['password']
        token = nick+password
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        say = curl.execute("SELECT user_nick FROM users WHERE user_nick=%s ",(nick,))
        curl.close()

        if say == 0:
            if len(nick) < 2:
                return render_template('kayit.html')
            else:
                
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (user_name, user_password, user_nick, user_token) VALUES (%s,%s,%s,%s)",(name,password,nick,token,))
                mysql.connection.commit()
                cur.close()
                return render_template('index.html')
        else:
            return render_template('kayit.html')
    else:
        return render_template("kayit.html")   


class Veritabani(Resource):
    def get(self):
        rehber = mysql.connection.cursor()
        rehber.execute("SELECT * from rehber")
        rehber_cek = rehber.fetchall()
        rehber.close()
        _rehber = jsonify({"rehber" : rehber_cek})
        _rehber.status_code = 200
        return _rehber

    def post(self):
        json_data = request.get_json(force=True)
        print(json_data['register'])
        token = "Başarılı"
        return jsonify({'datax': token})

class Login(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        print(json_data['login'])
        nick = json_data['login']['username']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        saydir = curl.execute("SELECT * FROM users WHERE user_nick=%s",(nick,))
        user = curl.fetchone()
        curl.close()
        if saydir == 1:
            if json_data['login']["password"] == user["user_password"]:
                session = user["user_token"]
                return jsonify({'token': session, 'kod':'truex','dataxx':'Dogggrruu'})
            else:
                return jsonify({'kod': 'falsex', 'dataxx':'Sifre Yanlis'})
        else:
            return jsonify({'kod': 'falseyok','dataxx':'Hesap Yok'})
        # json_data = request.get_json(force=True)
        # print(json_data['rehber'])
        # print(json_data['rehber']['firstName'])
        # return {'datax': 'Hello world'}, 201

class YeniBasliklar(Resource):
    def get(self):
        rehber = mysql.connection.cursor()
        rehber.execute("SELECT * from basliklar ORDER BY baslik_puan ASC")
        rehber_cek = rehber.fetchall()
        rehber.close()
        _rehber = jsonify({"baslik" : rehber_cek})
        _rehber.status_code = 200
        return _rehber

class GundemBasliklar(Resource):
    def get(self):
        rehber = mysql.connection.cursor()
        rehber.execute("SELECT * from basliklar ORDER BY baslik_puan DESC")
        rehber_cek = rehber.fetchall()
        rehber.close()
        _rehber = jsonify({"baslik" : rehber_cek})
        _rehber.status_code = 200
        return _rehber


class BaslikEkle(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        print(json_data['baslik'])
        title = json_data['baslik']['baslik_title']
        puan = json_data['baslik']['baslik_puan']
        from_token = json_data['baslik']['from_token']
        baslik_entry = json_data['baslik']['baslik_entry']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        saydir = curl.execute("SELECT * FROM basliklar WHERE baslik_title=%s",(title,))
        curl.close()
        if saydir == 1:
            return jsonify({'Mesaj': 'Böyle Bir Başlık Var', 'cood' : "0"})
        else:
            baslik_sahibi = mysql.connection.cursor()
            baslik_sahibi.execute("SELECT * from users WHERE user_token = %s",(from_token,))
            user_bilgisi = baslik_sahibi.fetchone()
            baslik_sahibi.close()
            from_id = user_bilgisi["user_id"]
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO basliklar (baslik_title, baslik_puan, baslik_from_id, baslik_entry) VALUES (%s,%s,%s,%s)",(title,puan,from_id,baslik_entry,))
            mysql.connection.commit()
            cur.close()            
            return jsonify({'Mesaj': 'Başarıyla Eklendi!', 'cood' : "1"})


api.add_resource(Veritabani, '/')
api.add_resource(Login, '/login')
api.add_resource(YeniBasliklar, '/basliklar/yeni')
api.add_resource(GundemBasliklar, '/basliklar/gundem')
api.add_resource(BaslikEkle, '/basliklar/ekle')



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

