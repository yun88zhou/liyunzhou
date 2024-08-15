from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect


app = Flask(__name__)
app.static_url_path='/static'

dbconn = None
connection = None



def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'user' in request.form:
            return redirect(url_for('home'))
        elif 'admin' in request.form:
            return redirect(url_for('admin'))
    
    return render_template('login.html')

@app.route("/home")
def home():
    return render_template("base.html")

@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("SELECT driver_id, CONCAT(surname,' ',first_name) AS Name,date_of_birth,age,caregiver,car.model,car.drive_class\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num\
                       ORDER BY surname ASC, first_name ASC;")
    driverList = connection.fetchall()
    # print(driverList)
    return render_template("driverlist.html", driver_list = driverList)    


@app.route("/rundetails", methods=["GET"])
def rundetails():
    # Get parameter from url link
    drivername=request.args.get('drivername')
    connection = getCursor()
    connection.execute("SELECT * FROM (\
                       SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
                       round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
                       FROM run\
                       LEFT JOIN driver ON run.dr_id = driver.driver_id\
                       LEFT JOIN course ON run.crs_id = course.course_id\
                       LEFT JOIN car ON driver.car = car.car_num) AS subquery\
                       WHERE subquery.drivers = %s;", (drivername,))
    driver_result = connection.fetchall()
    # print(drivername)
    # print(driver_result)
    return render_template("rundetails.html",driver_name=drivername,driver_result=driver_result)    

@app.route("/listalldetails", methods=["GET","POST"])
def listalldetails():
    if request.method == "GET":
        connection = getCursor()
        connection.execute("SELECT * FROM driver;")
        driver_result = connection.fetchall()


        connection = getCursor()
        connection.execute("SELECT * FROM (\
            SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
            round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
            FROM run\
            LEFT JOIN driver ON run.dr_id = driver.driver_id\
            LEFT JOIN course ON run.crs_id = course.course_id\
            LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
        run_result = connection.fetchall()
        return render_template("allrundetails.html", driver_result=driver_result, run_result=run_result)
    else:
        driverid = request.form.get('driver')
        try:
            driverid = int(driverid)

            # 查询所有驾驶员
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            # 查询指定驾驶员的详细信息
            connection = getCursor()
            connection.execute("SELECT * FROM (\
                SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class, \
                round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals \
                FROM run \
                LEFT JOIN driver ON run.dr_id = driver.driver_id \
                LEFT JOIN course ON run.crs_id = course.course_id \
                LEFT JOIN car ON driver.car = car.car_num) AS subquery \
                WHERE dr_id=%s;", (driverid,))
            run_result = connection.fetchall()
            return render_template("allrundetails.html", driverid=driverid, run_result=run_result, driver_result=driver_result)
        
        except ValueError:
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            connection = getCursor()
            connection.execute("SELECT * FROM (\
                SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class, \
                round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals \
                FROM run \
                LEFT JOIN driver ON run.dr_id = driver.driver_id \
                LEFT JOIN course ON run.crs_id = course.course_id \
                LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
            run_result = connection.fetchall()

            return render_template("allrundetails.html", driverid=driverid, run_result=run_result,driver_result=driver_result)
        

@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)

@app.route("/listoverall")
def listoverall():
    connection = getCursor()
    connection.execute("SELECT A.ID, A.DriverName, A.Car, \
                       COALESCE(B.courseA,'dnf') AS courseA, \
                       COALESCE(B.courseB,'dnf') AS courseB,\
                       COALESCE(B.courseC,'dnf') AS courseC,\
                       COALESCE(B.courseD,'dnf') AS courseD,\
                       COALESCE(B.courseE,'dnf') AS courseE,\
                       COALESCE(B.courseF,'dnf') AS courseF,\
                       COALESCE(B.Overall, 'NQ') AS Overall\
                       FROM (\
                       SELECT driver_id AS ID, CONCAT(first_name,' ', surname, \
                       CASE \
                       WHEN 12< age < 25 THEN ' (J)'\
                       ELSE ''\
                       END) AS DriverName, car.model AS Car\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num) AS A\
                       JOIN \
                       (SELECT dr_id AS ID,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                       round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                       round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                       round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                       round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                       round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                       FROM ( \
                       SELECT dr_id, \
                       crs_id,\
                       round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                       FROM run\
                       WHERE seconds IS NOT NULL\
                       GROUP BY dr_id, crs_id) AS subquery\
                       GROUP BY dr_id) AS B ON A.ID=B.ID\
                       ORDER BY Overall;")
    overallList = connection.fetchall()
    print(overallList)
    return render_template("overallresults.html", overallList = overallList)    

@app.route("/showgraph")
def showgraph():
    connection = getCursor()
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '
    connection.execute("SELECT CONCAT(A.ID,' ', A.DriverName) AS Dnames\
                       FROM (SELECT driver_id AS ID, CONCAT(first_name,' ', surname,\
                       CASE \
                       WHEN 12< age < 25 THEN ' (J)'\
                       ELSE ''\
                       END) AS DriverName, car.model AS Car\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num) AS A\
                       JOIN \
                       (SELECT dr_id AS ID,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                       round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                       round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                       round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                       round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                       round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                       FROM ( \
                       SELECT dr_id, crs_id,\
                       round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                       FROM run\
                       WHERE seconds IS NOT NULL\
                       GROUP BY dr_id, crs_id\
                       ) AS subquery\
                       GROUP BY dr_id) AS B ON A.ID=B.ID\
                       ORDER BY Overall IS NULL, Overall DESC LIMIT 5;")
    bestDriverList=connection.fetchall()
    print(bestDriverList)
    name_list=[]
    for i in bestDriverList:
        name_list.append(i[0])
    # print(name_list)
    connection.execute("SELECT Overall\
                    FROM (SELECT driver_id AS ID, CONCAT(first_name,' ', surname,\
                    CASE \
                    WHEN 12< age < 25 THEN ' (J)'\
                    ELSE ''\
                    END) AS DriverName, car.model AS Car\
                    FROM driver\
                    LEFT JOIN car ON driver.car=car.car_num) AS A\
                    JOIN \
                    (SELECT dr_id AS ID,\
                    round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                    round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                    round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                    round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                    round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                    round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                    round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                    MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                    MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                    FROM ( \
                    SELECT dr_id, crs_id,\
                    round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                    FROM run\
                    WHERE seconds IS NOT NULL\
                    GROUP BY dr_id, crs_id\
                    ) AS subquery\
                    GROUP BY dr_id) AS B ON A.ID=B.ID\
                    ORDER BY Overall IS NULL, Overall DESC LIMIT 5;")
    resultsList=connection.fetchall() 
    value_list=[]
    for i in resultsList:
        value_list.append(i[0])
    # print(value_list)
    return render_template("top5graph.html",name_list=name_list,value_list = value_list)

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/admin/listjuniordriver')
def listjuniordriver():
    connection = getCursor()
    connection.execute("SELECT\
                       o.driver_id, \
                       IFNULL(CONCAT(n.first_name, ' ', n.surname), o.first_name) AS Name,\
                       o.date_of_birth,o.age,\
                       IFNULL(CONCAT(n2.first_name, ' ', n2.surname), ' ') AS Caregiver,\
                       o.car\
                       FROM driver AS o\
                       LEFT JOIN driver AS n ON o.driver_id = n.driver_id\
                       LEFT JOIN driver AS n2 ON o.caregiver = n2.driver_id\
                       WHERE o.age >=12 AND o.age<25\
                       ORDER BY \
                       CASE WHEN o.age IS NULL THEN 0 ELSE 1 END, \
                       o.age DESC,  \
                       IFNULL(n.surname, o.surname), \
                       IFNULL(n.first_name, o.first_name);")
    junior_driver_list = connection.fetchall()
    # print(junior_driver_list)
    return render_template("juniordriverlist.html",junior_driver_list=junior_driver_list)

@app.route('/admin/searchdriverlist')
def searchdriverlist():
    connection = getCursor()
    connection.execute("SELECT driver_id,surname,first_name,date_of_birth,age,caregiver,car FROM driver\
                       order by surname, first_name")
    driver_list = connection.fetchall()
    return render_template("searchdriverlist.html", driver_list = driver_list)

@app.route('/admin/searchrunlist')
def searchrunlist():
    connection = getCursor()
    connection.execute("SELECT * FROM (\
        SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
        round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
        FROM run\
        LEFT JOIN driver ON run.dr_id = driver.driver_id\
        LEFT JOIN course ON run.crs_id = course.course_id\
        LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
    driverRun_list = connection.fetchall()
    return render_template("searchrunlist.html", driverRun_list = driverRun_list)

@app.route('/admin/searchdriverlist/filter', methods=["POST"])
def searchdriverlistfilter():
    drivers=request.form.get('driver') #  Get the search query for drivers from the form data.
    connection = getCursor()
    connection.execute("SELECT driver_id,surname,first_name,date_of_birth,age,caregiver,car FROM driver\
                        WHERE surname  Like  %s or first_name Like  %s\
                       order by surname, first_name;", (f'%{drivers}%',f'%{drivers}%',))
    driver_list = connection.fetchall()
    return render_template("searchdriverlist.html", driver_list = driver_list,drivers=drivers)

@app.route('/admin/searchrunlist/filter', methods=["POST"])
def searchrunlistfilter():
    drivers=request.form.get('driver') #  Get the search query for drivers from the form data.
    connection = getCursor()
    connection.execute("SELECT * FROM (\
        SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
        round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
        FROM run\
        LEFT JOIN driver ON run.dr_id = driver.driver_id\
        LEFT JOIN course ON run.crs_id = course.course_id\
        LEFT JOIN car ON driver.car = car.car_num) AS subquery\
        WHERE drivers LIKE %s;", (f'%{drivers}%',))
    driverRun_list = connection.fetchall()
    return render_template("searchrunlist.html", driverRun_list = driverRun_list,drivers=drivers)

@app.route('/admin/editruns', methods=['GET', 'POST'])
def editruns():
    if request.method == "GET":
        connection = getCursor()
        connection.execute("SELECT * FROM driver;")
        driver_result = connection.fetchall()


        connection = getCursor()
        connection.execute("SELECT * FROM run;")
        run_result = connection.fetchall()

        return render_template("editruns.html", driver_result=driver_result, run_result=run_result)


    else:
        driverid = request.form.get('selected_driver')
        session['driverid'] = driverid
        try:
            driverid = int(driverid)

            # 查询所有驾驶员
            try:
                connection = getCursor()
                connection.execute("SELECT * FROM driver;")
                driver_result = connection.fetchall()

                # 查询指定驾驶员的详细信息
                connection = getCursor()
                connection.execute("SELECT * FROM run\
                                    WHERE dr_id=%s;", (driverid,))
                run_result = connection.fetchall()
                return render_template("editruns.html", driverid=driverid, run_result=run_result, driver_result=driver_result)
            
            except:
                new_driver_id=driverid
        
                return render_template('adddriverrun.html', new_driver_id=new_driver_id)

        
        except ValueError:
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            connection = getCursor()
            connection.execute("SELECT * FROM run;")
            run_result = connection.fetchall()
            return render_template("editruns.html", driverid=driverid,driver_result=driver_result, run_result=run_result)

@app.route('/admin/editruns2', methods=['GET', 'POST'])
def editruns2():
    if request.method == "GET":
        # get all the course table from database for select option 
        connection = getCursor()
        connection.execute("SELECT * FROM motorkhana.course;")
        courseList = connection.fetchall()

        print(courseList)
        connection = getCursor()
        connection.execute("SELECT * FROM run;")
        course_result = connection.fetchall()
        return render_template("editruns2.html",courseList=courseList,course_result=course_result)
    
    else:
       
        # get courseid from select bar
        courseid = request.form.get('selected_course')
        print(type(courseid))
        try:
            connection = getCursor()
            connection.execute("SELECT * FROM course;")
            courseList = connection.fetchall()

            connection = getCursor()
            connection.execute("SELECT * FROM run where crs_id = %s;",(courseid,))
            course_result = connection.fetchall()
           
        
            return render_template("editruns2.html",courseid=courseid, course_result=course_result)

        except:
            connection = getCursor()
            connection.execute("SELECT * FROM run;")
            course_result = connection.fetchall()

            return render_template("editruns2.html",courseid=courseid, course_result=course_result)
            

@app.route('/editrun_name', methods=["GET","POST"])
def editrun_name():
    if request.method == "GET":
        driverid = session.get('driverid')
        
        try:
            connection = getCursor()
            connection.execute("SELECT * FROM run where dr_id=%s;", (driverid,))
            run_result = connection.fetchall()
            return render_template("editrunbyname.html",driverid=driverid,run_result=run_result)
        except:
            new_driver_id=driverid
            new_driver_id=new_driver_id
            flash('Please add new runs for this driver first', 'error')
            return redirect('/admin/adddriverrun/{}'.format(new_driver_id))

    else:
        driverid = session.get('driverid')
        connection = getCursor()
        connection.execute("SELECT * FROM run where dr_id=%s;", (driverid,))
        run_result = connection.fetchall()


        Driverid=request.form.getlist("driverid")
        courseID=request.form.getlist("courseid")
        runNum=request.form.getlist("run_num")
        seconds=request.form.getlist("seconds")
        cones=request.form.getlist("cones")
        wd=request.form.getlist("wd")
        

       #get all the values from Driverid list by for loop
        current_Driverid=[]
        for i in range(len(Driverid)):
            current_Driverid.append(Driverid[i])

        #get all the values from courseID list by for loop
        current_courseID=[]
        for i in range(len(courseID)):
            current_courseID.append(courseID[i])

        #get all the values from runNum list by for loop
        current_runNum=[]
        for i in range(len(runNum)):
            current_runNum.append(runNum[i])
             
        #get all the values from seconds list by for loop
        current_seconds=[]
        for i in range(len(seconds)):
            if seconds[i]:
                try:
                    seconds[i] = float(seconds[i])
                except ValueError:
                    seconds[i] = None
            else:
                seconds[i] = None       
            current_seconds.append(seconds[i])
        
        #get all the values from cones list by for loop
        current_cones=[]
        for i in range(len(cones)):
            if cones[i]:
                try:
                    cones[i] = int(cones[i])
                except ValueError:
                    cones[i] = None
            else:
                cones[i] = None
            current_cones.append(cones[i])
        
        #get all the values from wd list by for loop
        current_wd=[]
        for i in range(len(wd)):
            if not wd[i]:
                wd[i]=0    
            current_wd.append(wd[i])

        
        connection = getCursor()
        sql = "UPDATE motorkhana.run SET seconds = %s, cones = %s, wd = %s WHERE (dr_id = %s) and (crs_id = %s) and (run_num = %s)"
        data = [(current_seconds[0], current_cones[0], current_wd[0], current_Driverid[0], current_courseID[0], current_runNum[0]),
                (current_seconds[1], current_cones[1], current_wd[1], current_Driverid[1], current_courseID[1], current_runNum[1]),
                (current_seconds[2], current_cones[2], current_wd[2], current_Driverid[2], current_courseID[2], current_runNum[2]),
                (current_seconds[3], current_cones[3], current_wd[3], current_Driverid[3], current_courseID[3], current_runNum[3]),
                (current_seconds[4], current_cones[4], current_wd[4], current_Driverid[4], current_courseID[4], current_runNum[4]),
                (current_seconds[5], current_cones[5], current_wd[5], current_Driverid[5], current_courseID[5], current_runNum[5]),
                (current_seconds[6], current_cones[6], current_wd[6], current_Driverid[6], current_courseID[6], current_runNum[6]),
                (current_seconds[7], current_cones[7], current_wd[7], current_Driverid[7], current_courseID[7], current_runNum[7]),
                (current_seconds[8], current_cones[8], current_wd[8], current_Driverid[8], current_courseID[8], current_runNum[8]),
                (current_seconds[9], current_cones[9], current_wd[9], current_Driverid[9], current_courseID[9], current_runNum[9]),
                (current_seconds[10], current_cones[10], current_wd[10], current_Driverid[10], current_courseID[10], current_runNum[10]),
                (current_seconds[11], current_cones[11], current_wd[11], current_Driverid[11], current_courseID[11], current_runNum[11])
                ]
        for item in data:
            connection.execute(sql, item)
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (current_Driverid[0],))
        new_run_list = connection.fetchall()

        return render_template("editrunbynamelist.html",run_result=run_result,new_run_list=new_run_list)

@app.route('/editrun_course', methods=["GET","POST"])
def editrun_course():
    if  request.method == "GET":
        # need get three parameters from the get url 
        drivertID=request.args.get('driverID')
        drivertID=int(drivertID)
        courseID=request.args.get('courseID')
        runNumber=request.args.get('runNumber')
        runNumber=int(runNumber)
        # put the three parameter to sql to grab the data of these three specific filed data 

        connection = getCursor()
        connection.execute("SELECT * FROM run where dr_id=%s and crs_id=%s and run_num=%s ;",(drivertID,courseID,runNumber,))
        course_result = connection.fetchall()
        return render_template("editrunbycourse.html",course_result=course_result)
    else:
        driverID=request.form.get('driverid')
        driverID=int(driverID)
        courseID=request.form.get('courseid')
        runNumber=request.form.get('run_number')
        Seconds=request.form.get('Seconds')
        Cones=request.form.get('Cones')
        WD=request.form.get('WD')
        
        connection = getCursor()
        connection.execute("UPDATE `run` SET `seconds` = %s, `cones` = %s, `wd` = %s  WHERE (`dr_id` = %s) and (`crs_id` = %s) and (`run_num` = %s);",(Seconds,Cones,WD,driverID,courseID,runNumber,))
        return redirect('/admin/editruns2')
        
        
         
    
   





@app.route('/admin/adddriver', methods=['GET', 'POST'])
def adddriver():
    if  request.method == "GET":
        connection = getCursor()
        connection.execute("SELECT * FROM driver;")  # Execute a SQL query to select all drivers from the databa
        driverList = connection.fetchall() # Fetch all the records (drivers) from the database.

        connection = getCursor()
        connection.execute("SELECT * FROM driver where age is null;")  # Execute a SQL query to select all drivers from the databa
        caregiverList = connection.fetchall()      
        return render_template("adddriver.html",driverList=driverList,caregiverList=caregiverList) #passing the driverList for display after rendering template


    else: # This is [POST] mode, user click Yes or No button in the dialog after clicking "Add New Driver" button.
        connection = getCursor()
        connection.execute("SELECT * FROM driver;")  # Execute a SQL query to select all drivers from the databa
        driverList = connection.fetchall()

        connection = getCursor()
        connection.execute("SELECT * FROM driver where age is null;")  # Execute a SQL query to select all caregivers from the database
        caregiverList = connection.fetchall()        

        
        age_confirmation = request.form.get('age_confirmation')
        if age_confirmation == "young": 
            # If the user clicks "12-16 yrs" in the dialog, it sets the age_confirmation variable to "young".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",caregiverList=caregiverList,age_confirmation=age_confirmation)  
        
        elif age_confirmation == "youngadult":  
            
            # If the user clicks "17-25 yrs" in the dialog, it sets the age_confirmation variable to "youngadult".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",age_confirmation=age_confirmation)
        
        elif age_confirmation == "adult":  
            
            # If the user clicks "Over 25 yrs" in the dialog, it sets the age_confirmation variable to "youngadult".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",age_confirmation=age_confirmation)  

        else:
            # This part is executed when the user has provided the necessary driver information in the add new driverform from(adddriverform.html).
            driverID =request.form.get('driver_id')
            driverID=int(driverID)

            # Checking for empty values and replacing them with "None" as needed.
            firstName = request.form.get('first_name')
            if firstName == "":
                firstName = "None"
            surname = request.form.get('surname')
            if surname == "":
                surname = "None"

            dobget = request.form.get('dob')
            print(dobget)
            if  dobget is not None and dobget != "None":
                dob = datetime.strptime(dobget, '%Y-%m-%d')
                current_date = datetime.now()
                age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

            else:
                dob=dobget
                dob = None
                age=request.form.get('age')
                if age == "" or "None":
                    age = None  
             
    
            caregiver = request.form.get('caregiver')
            if caregiver == "" or "None":
                    caregiver = None  

            car = request.form.get('car')
        
            
            connection = getCursor()
            connection.execute("SELECT driver_id FROM driver;")
            sql_driver_id = connection.fetchall()
            sql_driver_id=list(sql_driver_id)
            driver_id_list = [row[0] for row in sql_driver_id]

            if driverID not in driver_id_list:
                # Inserting the driver's information into the database
                connection = getCursor()
                connection.execute("INSERT INTO driver\
                                (driver_id, first_name, surname, date_of_birth, age, caregiver, car) \
                                VALUES (%s, %s, %s, %s, %s, %s, %s);", (driverID, firstName, surname, dob, age, caregiver, car,))
                new_driver_id=driverID
                connection.execute("SELECT * FROM driver WHERE driver_id = %s;", (new_driver_id,))
                new_driver_list=connection.fetchall()
                return render_template("adddriverlist.html",age=age,new_driver_id=new_driver_id,new_driver_list=new_driver_list,sql_driver_id=sql_driver_id)
            
            else:
                flash('This ID already exists', 'error')
                return redirect('/admin/adddriver')
            
@app.route('/admin/adddriverrun/<new_driver_id>', methods=['GET', 'POST'])
def adddriverrun(new_driver_id):
    if  request.method == "GET":
        driverid=new_driver_id

        return render_template("adddriverrun.html",driverid=driverid)

    else:  
        driverid=new_driver_id
        
        Driverid=request.form.getlist("driverid")
        courseID=request.form.getlist("courseid")
        runNum=request.form.getlist("run_num")
        seconds=request.form.getlist("seconds")
        cones=request.form.getlist("cones")
        wd=request.form.getlist("wd")


        #get all the values from Driverid list by for loop
        current_Driverid=[]
        for i in range(len(Driverid)):
            current_Driverid.append(Driverid[i])
        print(current_Driverid[0])
        #get all the values from courseID list by for loop
        current_courseID=[]
        for i in range(len(courseID)):
            current_courseID.append(courseID[i])

        #get all the values from runNum list by for loop
        current_runNum=[]
        for i in range(len(runNum)):
            current_runNum.append(runNum[i])
             
        #get all the values from seconds list by for loop
        current_seconds=[]
        for i in range(len(seconds)):
            if seconds[i]:
                try:
                    seconds[i] = float(seconds[i])
                except ValueError:
                    seconds[i] = None
            else:
                seconds[i] = None       
            current_seconds.append(seconds[i])
        print(current_seconds[0])
        #get all the values from cones list by for loop
        current_cones=[]
        for i in range(len(cones)):
            if cones[i]:
                try:
                    cones[i] = int(cones[i])
                except ValueError:
                    cones[i] = None
            else:
                cones[i] = None
            current_cones.append(cones[i])
        print(current_cones[0])

        #get all the values from wd list by for loop
        current_wd=[]
        for i in range(len(wd)):
            if not wd[i]:
                wd[i]=0    
            current_wd.append(wd[i])
        print(current_wd[0])


        connection = getCursor()
        sql = "INSERT INTO motorkhana.run (dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, %s, %s, %s, %s, %s);"
        data = [(current_Driverid[0], current_courseID[0], current_runNum[0], current_seconds[0], current_cones[0], current_wd[0]),
                (current_Driverid[1], current_courseID[1], current_runNum[1], current_seconds[1], current_cones[1], current_wd[1]),
                (current_Driverid[2], current_courseID[2], current_runNum[2], current_seconds[2], current_cones[2], current_wd[2]),
                (current_Driverid[3], current_courseID[3], current_runNum[3], current_seconds[3], current_cones[3], current_wd[3]),
                (current_Driverid[4], current_courseID[4], current_runNum[4], current_seconds[4], current_cones[4], current_wd[4]),
                (current_Driverid[5], current_courseID[5], current_runNum[5], current_seconds[5], current_cones[5], current_wd[5]),
                (current_Driverid[6], current_courseID[6], current_runNum[6], current_seconds[6], current_cones[6], current_wd[6]),
                (current_Driverid[7], current_courseID[7], current_runNum[7], current_seconds[7], current_cones[7], current_wd[7]),
                (current_Driverid[8], current_courseID[8], current_runNum[8], current_seconds[8], current_cones[8], current_wd[8]),
                (current_Driverid[9], current_courseID[9], current_runNum[9], current_seconds[9], current_cones[9], current_wd[9]),
                (current_Driverid[10], current_courseID[10], current_runNum[10], current_seconds[10], current_cones[10], current_wd[10]),
                (current_Driverid[11], current_courseID[11], current_runNum[11], current_seconds[11], current_cones[11], current_wd[11])]
        print(data)
        for item in data:
            connection.execute(sql, item)
        
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (driverid,))
        new_run_list = connection.fetchall()
        return render_template("adddriverrunlist.html",driverid=driverid,new_driver_id=new_driver_id,new_run_list=new_run_list)


if __name__ == '__main__':
    app.run(debug=True)
