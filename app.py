from flask import Flask, jsonify,request,render_template
from datetime import datetime
import base64
import threading,time
import json
import pytz
app = Flask(__name__)

started = False

class Calander():
    def __init__(self) -> None:
        self.big = False
        self.a = 0
        self.sd=29
        self.sm = 1
        self.sy = 1444
        with open('pt.json') as f:
            self.pt = json.loads(f.read())
    def current_date(self):
        utc_plus_4 = pytz.timezone("Etc/GMT-4")
        current_datetime = datetime.now(utc_plus_4)

        return  current_datetime
    def set_month(self,v):
        self.big = v
    def today_prayer_time(self):
        cd = self.current_date()
        sp = self.pt['Dates'][cd.strftime("%d-%m-2022")].split(":")
        return sp
    def change_date(self,sp):
        cd = self.current_date()
        if cd.hour == int(sp[0]) and cd.minute == int(sp[1]):
            if self.sd < 29 or (self.sd==29 and self.big):
                self.sd+=1
            elif self.sd == 30 or (self.sd==29 and not self.big):
                self.sd = 1
                if self.sm<12: self.sm+=1
                else: 
                    self.sy += 1
                    self.sm = 1
                    self.big = True
            time.sleep(90)
    def get_CMD(self):
        return {"Code":"Success","msg":self.a,"Islamic Date":f"{self.sd} {self.pt['Names'][f'{self.sm}']} {self.sy}"}
    def run(self):
        while True:
            self.a+=1
            self.change_date(self.today_prayer_time())
            time.sleep(1)

obj = Calander()

def backgroundFun():
    obj.a+=1
    obj.change_date(obj.today_prayer_time())

def base64_encode(data):
    encoded_bytes = base64.b64encode(data.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def base64_decode(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data.encode('utf-8'))
    return decoded_bytes.decode('utf-8')
def check_pass(password:str):
    c = None
    with open('credential') as f:
        j = json.loads(f.read())
        if base64_encode(password) == j['pass']:
            c = True
        else:
            c = False
    return c

@app.route('/')
def index():
    if started == False:
        return jsonify({"Code":"Success","msg":"Calander not started yet"})
    else:
        return jsonify(obj.get_CMD())

@app.route('/start', methods=['GET','POST'])
def start():
    global started,obj
    if request.method == "POST":
        try:
            sd = int(request.form.get("day"))
            sm = int(request.form.get('mselect'))
            sy = int(request.form.get('year'))
            # obj = Calander() 
            if not sd or not sm or not sy:
                return jsonify({"Code":"Err","msg":"Invalid Data"})
            obj.sd = sd
            obj.sm = sm
            obj.sy = sy
            t1 = threading.Thread(target=obj.run)
            t1.start()
            
            started= True
            return jsonify({"Code":"Success","msg":"Started"})
        except: return jsonify({"Code":"Err","msg":"Invalid Data"})
    else:
        if started:
            return jsonify({"Code":"Success","msg":"Already Started"})
        else:
            return render_template('startdate.html',data=[[i,obj.pt['Names'][i]] for i in obj.pt['Names'].keys()])

@app.route('/update',methods=['GET','POST'])
def update():
    if not started:
        return jsonify({"Code":"Success","msg":"Calander not started yet"})
    if request.method == "GET":
        return render_template('update.html',date = {"d":obj.sd,'m':obj.sm,'y':obj.sy,'months':[[int(i),obj.pt['Names'][i]] for i in obj.pt['Names'].keys()]})
    if request.method == "POST":
        try:
            password = request.form.get('pass')
            if not check_pass(password):
                return jsonify({"Code":"Not Updated","msg":"Invalid Password"})
            sd = int(request.form.get("day"))
            sm = int(request.form.get('mselect'))
            sy = int(request.form.get('year'))
            if not sd or not sm or not sy:
                return jsonify({"Code":"Not Updated","msg":"Invalid Data"})
            obj.sd = sd
            obj.sm = sm
            obj.sy = sy            
            return jsonify({"Code":"Success","msg":"Updated"})
        except: return jsonify({"Code":"Err","msg":"Invalid Data"})
@app.route('/admin',methods=["GET"])
def admin():
    return render_template('admin.html')


@app.route('/changepassword',methods=["GET","POST"])
def changePassword():
    if request.method == "POST":
        current = request.form.get('current')
        if not check_pass(current):
            return jsonify({"Code":"Not Changed","msg":"Invalid Current Password"})
        else:
            npass = request.form.get('new')
            cpass = request.form.get('confirm')
            if npass != cpass:
                return jsonify({"Code":"Not Changed","msg":"New Passwords not matched"})
            elif len(npass)<6:
                return jsonify({"Code":"Not Changed","msg":"Enter password of atleast 6 digits"})
            else:
                with open('credential','w') as f:
                    f.write(json.dumps({"pass":base64_encode(npass)}))
                return jsonify({"Code":"Successfully Changed","msg":""})

    else:
        return render_template('changepass.html')


@app.route('/set',methods=['GET','POST'])
def set():
    if started:
        if request.method == "POST":
            password = request.form.get('pass')
            if not check_pass(password):
                return jsonify({"Code":"Not Set","msg":"Invalid Password"})
            if request.form.get('check')=="on":
                obj.big = True
            else:
                obj.big = False

            return render_template('setdate.html',value = {"month":obj.big})
        else:
            return render_template('setdate.html',value = {"month":obj.big})
    else: return jsonify({"Code":"Success","msg":"Calander not started yet"})



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
