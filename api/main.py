from flask import Flask, jsonify,request,render_template
from datetime import datetime
import json
import threading,time
import pytz

app = Flask(__name__)

started = False


#/home/ahmadraza1907r2/mysite/pt.json
class Calander():
    def __init__(self) -> None:
        self.big = True
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

obj = None
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
            sm = int(request.form.get('mon'))
            sy = int(request.form.get('year'))
            
            obj = Calander() 
            if not sd or not sm or not sy:
                return jsonify({"Code":"Err","msg":"Invalid Data"})
            print(sd,sm,sy)
            obj.sd = sd
            obj.sm = sm
            obj.sy = sy
            threading.Thread(target=obj.run).start()
            started= True
            return jsonify({"Code":"Success","msg":"Started"})
        except: return jsonify({"Code":"Err","msg":"Invalid Data"})
    else:
        if started:
            return jsonify({"Code":"Success","msg":"Already Started"})
        else:
            return render_template('startdate.html')

@app.route('/set',methods=['GET','POST'])
def set():
    if started:
        if request.method == "POST":
            if request.form.get('check')=="on":
                obj.big = True
            else:
                obj.big = False

            return render_template('setdate.html',value = {"month":obj.big})
        else:
            return render_template('setdate.html',value = {"month":obj.big})
    else: return jsonify({"Code":"Success","msg":"Calander not started yet"})



if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0")
