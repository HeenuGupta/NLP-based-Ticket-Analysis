import os
from flask import *
from werkzeug import secure_filename
import csv
from py2neo import *
import time
import nltk

ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__)
app.secret_key = 'random string'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_files(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
	return render_template('homepage.html')


@app.route('/alreadyuploaded/',methods=['post'])
def alreadyuploaded():
	passwo = request.form['pass']
	gr = Graph(password=passwo)
	sq = gr.run("match (a:ListItem) return a.value").data()
	tempvalues1 = []
	for i in sq:
		for j, k in i.items():
			tempvalues1.append(k)
	return render_template('resultspage.html', contenttype=".csv", tm=0, passval=passwo , available=tempvalues1)


@app.route('/results/', methods=['post'])
def results():
	file = request.files['file']
	if file.filename == '':
		flash("No file was selected !!")
		flash("Choose your file again")
		return redirect(url_for("home"))
	elif not allowed_files(file.filename):
		flash("Invalid file (Only .csv (UTF-8) allowed)!!")
		flash("Choose your file again")
		return redirect(url_for("home"))
	else:
		st = time.time()
		adid=request.form['adid']
		passw = request.form['pass']
		UPLOAD_FOLDER = "C:\\Users\\"+adid+"\\Documents\\Neo4j\\CaseStudy/import/"
		gr = Graph(password=passw)
		securedfile = secure_filename(file.filename)

		if not os.path.exists(UPLOAD_FOLDER):
			os.makedirs(UPLOAD_FOLDER)
		lista=['ticket','ticket type',"request","issue",'severity',"unclassified","minor","normal","major","critical",'requester ID','requester seniority',"junior","regular","senior","management",'filed against',"systems","software","hardware","access","login",'priority',"unassigned","low","medium","high",'IT owner ID','days open','satisfaction',"unknown","unsatisfied","satisfied","highly satisfied"]
		tx=gr.begin()
		for item in lista:
			a=Node("ListItem",value=item)
			tx.merge(a)
		tx.commit()
		file.save(os.path.join(UPLOAD_FOLDER, securedfile))

		ctype = file.content_type

		rqidlist = set()
		itolist = set()
		dolist = set()


		with open(UPLOAD_FOLDER + securedfile) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				tt = row['Ticket_Type']
				sv = row['Severity']
				rqid = int(row['Requester_ID'])
				rs = row['Requester_Seniority']
				fa = row["Filed_Against"]
				pr = row["Priority"]
				ito = int(row["IT_Owner_ID"])
				do = int(row["Days_Open"])
				sat = row["Satisfaction"]
				tx = gr.begin()
				a = Node("tempdata", ticket_type=tt, severity=sv, request_id=rqid, requester_seniority=rs,
						 filed_against=fa, priority=pr, it_owner_id=ito, days_open=do, satisfaction=sat)
				tx.merge(a)
				a = Node("RequesterID", RequesterID=rqid)
				tx.merge(a)
				rqidlist.add(rqid)
				a = Node("IT_OWNER_ID", ITOWNERID=ito)
				tx.merge(a)
				itolist.add(ito)
				a = Node("DaysOpen", DaysOpen=do)
				tx.merge(a)
				dolist.add(do)
				tx.commit()

		tx = gr.begin()
		a = Node("TicketType", TicketType='Request')
		tx.merge(a)
		a = Node("TicketType", TicketType='Issue')
		tx.merge(a)
		a = Node("Severity", Severity='0 - Unclassified')
		tx.merge(a)
		a = Node("Severity", Severity='1 - Minor')
		tx.merge(a)
		a = Node("Severity", Severity='2 - Normal')
		tx.merge(a)
		a = Node("Severity", Severity='3 - Major')
		tx.merge(a)
		a = Node("Severity", Severity='4 - Critical')
		tx.merge(a)
		a = Node("RequesterSeniority", RequesterSeniority='1 - Junior')
		tx.merge(a)
		a = Node("RequesterSeniority", RequesterSeniority='2 - Regular')
		tx.merge(a)
		a = Node("RequesterSeniority", RequesterSeniority='3 - Senior')
		tx.merge(a)
		a = Node("RequesterSeniority", RequesterSeniority='4 - Manager')
		tx.merge(a)
		a = Node("FiledAgainst", FiledAgainst='Systems')
		tx.merge(a)
		a = Node("FiledAgainst", FiledAgainst='Software')
		tx.merge(a)
		a = Node("FiledAgainst", FiledAgainst='Access/Login')
		tx.merge(a)
		a = Node("FiledAgainst", FiledAgainst='Hardware')
		tx.merge(a)
		a = Node("Priority", Priority='0 - Unassigned')
		tx.merge(a)
		a = Node("Priority", Priority='1 - Low')
		tx.merge(a)
		a = Node("Priority", Priority='2 - Medium')
		tx.merge(a)
		a = Node("Priority", Priority='3 - High')
		tx.merge(a)
		a = Node("Satisfaction", Satisfaction='0 - Unknown')
		tx.merge(a)
		a = Node("Satisfaction", Satisfaction='1 - Unsatisfied')
		tx.merge(a)
		a = Node("Satisfaction", Satisfaction='2 - Satisfied')
		tx.merge(a)
		a = Node("Satisfaction", Satisfaction='3 - Highly satisfied')
		tx.merge(a)
		tx.commit()
		gr.run(
			"MATCH (a:tempdata),(b:Severity) WHERE a.severity = '0 - Unclassified' AND b.Severity = '0 - Unclassified' MERGE (a)-[r:Severity]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Severity) WHERE a.severity = '1 - Minor' AND b.Severity = '1 - Minor' MERGE (a)-[r:Severity]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Severity) WHERE a.severity = '2 - Normal' AND b.Severity = '2 - Normal' MERGE (a)-[r:Severity]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Severity) WHERE a.severity = '3 - Major' AND b.Severity = '3 - Major' MERGE (a)-[r:Severity]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Severity) WHERE a.severity = '4 - Critical' AND b.Severity = '4 - Critical' MERGE (a)-[r:Severity]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:TicketType) WHERE a.ticket_type = 'Issue' AND b.TicketType = 'Issue' MERGE (a)-[r:TicketType]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:TicketType) WHERE a.ticket_type = 'Request' AND b.TicketType = 'Request' MERGE (a)-[r:TicketType]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:RequesterSeniority) WHERE a.requester_seniority = '1 - Junior' AND b.RequesterSeniority = '1 - Junior' MERGE (a)-[r:RequesterSeniority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:RequesterSeniority) WHERE a.requester_seniority = '2 - Regular' AND b.RequesterSeniority = '2 - Regular' MERGE (a)-[r:RequesterSeniority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:RequesterSeniority) WHERE a.requester_seniority = '3 - Senior' AND b.RequesterSeniority = '3 - Senior' MERGE (a)-[r:RequesterSeniority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:RequesterSeniority) WHERE a.requester_seniority = '4 - Manager' AND b.RequesterSeniority = '4 - Manager' MERGE (a)-[r:RequesterSeniority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:FiledAgainst) WHERE a.filed_against = 'Systems' AND b.FiledAgainst = 'Systems' MERGE (a)-[r:FiledAgainst]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:FiledAgainst) WHERE a.filed_against = 'Software' AND b.FiledAgainst = 'Software' MERGE (a)-[r:FiledAgainst]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:FiledAgainst) WHERE a.filed_against = 'Hardware' AND b.FiledAgainst = 'Hardware' MERGE (a)-[r:FiledAgainst]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:FiledAgainst) WHERE a.filed_against = 'Access/Login' AND b.FiledAgainst = 'Access/Login' MERGE (a)-[r:FiledAgainst]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Priority) WHERE a.priority = '0 - Unassigned' AND b.Priority = '0 - Unassigned' MERGE (a)-[r:Priority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Priority) WHERE a.priority = '1 - Low' AND b.Priority = '1 - Low' MERGE (a)-[r:Priority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Priority) WHERE a.priority = '2 - Medium' AND b.Priority = '2 - Medium' MERGE (a)-[r:Priority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Priority) WHERE a.priority = '3 - High' AND b.Priority = '3 - High' MERGE (a)-[r:Priority]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Satisfaction) WHERE a.satisfaction = '0 - Unknown' AND b.Satisfaction = '0 - Unknown' MERGE (a)-[r:Satisfaction]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Satisfaction) WHERE a.satisfaction = '1 - Unsatisfied' AND b.Satisfaction = '1 - Unsatisfied' MERGE (a)-[r:Satisfaction]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Satisfaction) WHERE a.satisfaction = '2 - Satisfied' AND b.Satisfaction = '2 - Satisfied' MERGE (a)-[r:Satisfaction]->(b)")
		gr.run(
			"MATCH (a:tempdata),(b:Satisfaction) WHERE a.satisfaction = '3 - Highly satisfied' AND b.Satisfaction = '3 - Highly satisfied' MERGE (a)-[r:Satisfaction]->(b)")
		for i in rqidlist:
			gr.run("MATCH (a:tempdata),(b:RequesterID) WHERE a.request_id = " + str(i) + " AND b.RequesterID =" + str(
				i) + " MERGE (a)-[r:RequesterID]->(b)")
		for i in dolist:
			gr.run("MATCH (a:tempdata),(b:DaysOpen) WHERE a.days_open = " + str(i) + " AND b.DaysOpen =" + str(
				i) + " MERGE (a)-[r:Daysopen]->(b)")
		for i in itolist:
			gr.run("MATCH (a:tempdata),(b:IT_OWNER_ID) WHERE a.it_owner_id = " + str(i) + " AND b.ITOWNERID =" + str(
				i) + " MERGE (a)-[r:ITOWNERID]->(b)")

		sq = gr.run("match (a:ListItem) return a.value").data()
		tempvalues2 = []
		for i in sq:
			for j, k in i.items():
				tempvalues2.append(k)
		return render_template('resultspage.html', contenttype=ctype, tm=time.time() - st, passval=passw, available=tempvalues2)


@app.route('/analysis/', methods=['post'])
def analysis():
	passwo=request.form["pass"]
	gr=Graph(password=passwo)
	inputstr = request.form['inputstr']
	gr.run("Merge(a:ListItem{value:'"+inputstr+"'})")

	propdict_50 = {'type': ("request", "issue"), 'request_id':(list(range(1,2001))),'severity': ("unclassified", "minor", "normal", "major", "critical"),
				'seniority': ("junior", "regular", "senior", "management"),
				'against': ("systems", "software", "hardware", "access", "login"),
				'priority': ("unassigned", "low", "medium", "high"),'it_owner_id':(list(range(1,51))),'days_open':(list(range(1,21))),
				'satisfaction': ("unknown", "unsatisfied", "satisfied", "highly")}
	dict_50 = {"Request": "ticket_type", "Issue": "ticket_type", "0 - Unclassified": "severity", "1 - Minor": "severity",
			"2 - Normal": "severity", "3 - Major": "severity", "4 - Critical": "severity",
			"1 - Junior": "requester_seniority", "2 - Regular": "requester_seniority", "3 - Senior": "requester_seniority",
			"4 - Management": "requester_seniority", "Systems": "filed_against", "Software": "filed_against",
			"Hardware": "filed_against", "Access/Login": "filed_against", "0 - Unassigned": "priority",
			"1 - Low": "priority", "2 - Medium": "priority", "3 - High": "priority", "0 - Unknown": "satisfaction",
			"1 - Unsatisfied": "satisfaction", "2 - Satisfied": "satisfaction", "3 - Highly satisfied": "satisfaction"}
	dict_51 = {"request": "Request", "issue": "Issue", "unclassified": "0 - Unclassified", "minor": "1 - Minor",
			 "normal": "2 - Normal", "major": "3 - Major", "critical": "4 - Critical", "junior": "1 - Junior",
			 "regular": "2 - Regular", "senior": "3 - Senior", "management": "4 - Management", "systems": "Systems",
			 "software": "Software", "hardware": "Hardware", "login": "Access/Login", "access": "Access/Login",
			 "unassigned": "0 - Unassigned", "low": "1 - Low", "medium": "2 - Medium", "high": "3 - High",
			 "unknown": "0 - Unknown", "unsatisfied": "1 - Unsatisfied", "satisfied": "2 - Satisfied",
			 "highly": "3 - Highly satisfied"}
	list0 = []
	list1 = []
	list2 = []
	if inputstr!="":
		inputstr += "???"
		tokens = nltk.word_tokenize(inputstr)
		print(tokens)
		for token in tokens:
			token = str.lower(token)
			if token in propdict_50.keys():
				m = 0
				for props in propdict_50[token]:
					if props in tokens:
						m = 1
				if m == 0:
					list0.append(dict_50[dict_51[propdict_50[token][0]]])

		str1 = ""

		for word in tokens:
			ind = tokens.index(word)
			word = str.lower(word)
			tokens[ind]=word

			cword = ""
			dword=""
			if word.isdigit():
				if not tokens[ind + 1][0] == '-':
					list1.append(word)
				else:
					tokens[ind]='??'
			elif not word.isalpha():
				for i in word:
					if i.isalpha():
						cword += i
					if i.isdigit():
						dword+=i
				tokens[ind]=cword
				if len(dword)>0 and word[1]!='-':
					tokens.insert(ind + 1, dword)
				print(tokens)
			else:
				cword = word
		for word in tokens:
			ind = tokens.index(word)
			if word in dict_51.keys():
				str1 += dict_50[dict_51[word]] + ":'" + dict_51[word] + "'"
				str1 += ","
			if word == "requester" and tokens[ind + 1] == "id":
				list2.append("request_id")
			if word == "it" and tokens[ind + 1].lower() == "owner" and tokens[ind + 2].lower() == "id":
				list2.append("it_owner_id")
			if word == "open":
				list2.append("days_open")

		if len(list1) == len(list2):
			for i in list(range(len(list1))):
				str1 += list2[i] + ":" + list1[i] + ","
		elif len(list2)>len(list1) and len(list1)!=0:
			if (int(list1[0]) in propdict_50[list2[0]]) and (int(list1[len(list1)-1]) in propdict_50[list2[len(list1)-1]]):
				print("satisfied")
				list0.append(list2[len(list2)-1])
				for i in list(range(len(list1))):
					str1 += list2[i] + ":" + list1[i] + ","
			else:
				print("not satisfied")
				list0.append(list2[0])
				for i in list(range(len(list1))):
					str1 += list2[i+1] + ":" + list1[i] + ","
		elif len(list2)!=0:
			list0.append(list2[0])

		a = len(str1) - 1
		print(list0)
		print(list1)
		print(list2)
		valuessing = []
		valuesrqid = []
		labelsrqid = []
		tempvalues = []
		valuesprop = []
		labelsprop = []
		rqid = str1
		idval = ""
		prop = "Days Open"
		valtochart = ""
		temppropvalues = []
		txt = request.form["query"].strip()
		txtrqid = request.form["rqidquery"].strip()
		txtprop = request.form["propquery"].strip()
		if len(list0)==0:
			sq = gr.run("Match (a:tempdata{" + str1[0:a] + "}) return count(*)").data()
			for i in sq:
				valuessing.append(int(i['count(*)']))
			valtochart = valuessing[0]

			rqidq = gr.run("match (n:tempdata{" +str1[0:a]+ "}) return n.days_open,count(n)").data()
			print(rqid)


			for i in rqidq:
				for j, k in i.items():
					tempvalues.append(k)
			l = len(tempvalues)

			for i in range(0, l, 2):
				labelsrqid.append(tempvalues[i])
				valuesrqid.append(tempvalues[i + 1])
		if len(list0)!=0:
			sq = gr.run("Match (a:tempdata{" + str1[0:a] + "}) return count(*)").data()
			print(sq)

			for i in sq:
				valuessing.append(int(i['count(*)']))
			valtochart = valuessing[0]
			txtprop = list0[0].strip().lower()
			propq = gr.run("match (a:tempdata{"+str1[0:a]+"}) return a." + list0[0] + ",count(a)").data()
			for i in propq:
				for j, k in i.items():
					temppropvalues.append(k)
			l = len(temppropvalues)
			for i in range(0, l, 2):
				labelsprop.append(temppropvalues[i])
				valuesprop.append(temppropvalues[i + 1])

		if (inputstr==""):
			flash("No query detected !!")
			flash("Try Again !!")
			return redirect(url_for("alreadyuploaded"))

		return render_template('analysispage.html', valtochart=valtochart,propsstr=str1[0:a], valuesrqid=valuesrqid,
							   labelsrqid=labelsrqid, rqid=rqid, idval=idval, prop=prop, labelsprop=labelsprop,
							   valuesprop=valuesprop, txtprop=txtprop, )

	else:
		keys = []
		vals = []
		valuessing = []
		valuesrqid = []
		labelsrqid = []
		tempvalues = []
		valuesprop = []
		labelsprop = []
		rqid = ""
		propsstr=""
		idval = ""
		prop = ""
		txtprop = ""
		valtochart = ""
		temppropvalues = []
		txt = request.form["query"].strip()
		txtrqid = request.form["rqidquery"].strip()
		txtprop = request.form["propquery"].strip()
		if not txt == "":
			properties = list(txt.split(','))
			for i in properties:
				k, v = i.split(':')
				keys.append(k.strip().lower())
				vals.append(v.strip().title())
			props = dict(zip(keys, vals))
			# print(props)
			propsstr += "{"
			for i, j in props.items():
				propsstr += i + ":"
				propsstr += "'" + j + "',"
			l = len(propsstr)
			propsstr = propsstr[:l - 1]
			propsstr += "}"
			sq = gr.run("Match (a:tempdata" + propsstr + ") return count(*)").data()

			for i in sq:
				valuessing.append(int(i['count(*)']))
			valtochart = valuessing[0]
		# print(valuessing)

		if not txtrqid == "":
			rqid, prop = txtrqid.split(",")
			rqid, idval = rqid.split(":")
			rqid = rqid.strip().lower()
			idval = idval.strip()
			prop = prop.strip().capitalize()
			if prop == "Daysopen":
				prop = "DaysOpen"
			if prop == "Tickettype":
				prop = "TicketType"
			if prop == "Requesterseniority":
				prop = "RequesterSeniority"
			if prop == "Filedagainst":
				prop = "FiledAgainst"
			rqidq = gr.run("match (a:tempdata{" + rqid + ":" + idval + "})--(n:" + prop + ") return n." + prop + ",count(n)").data()

			for i in rqidq:
				for j, k in i.items():
					tempvalues.append(k)
			l = len(tempvalues)

			for i in range(0, l, 2):
				labelsrqid.append(tempvalues[i])
				valuesrqid.append(tempvalues[i + 1])
		# print(labelsrqid)
		# print(valuesrqid)
		if not txtprop == "":
			txtprop = txtprop.strip().lower()
			propq = gr.run("match (a:tempdata) return a." + txtprop + ",count(a)").data()
			for i in propq:
				for j, k in i.items():
					temppropvalues.append(k)
			l = len(temppropvalues)
			for i in range(0, l, 2):
				labelsprop.append(temppropvalues[i])
				valuesprop.append(temppropvalues[i + 1])
		# print(labelsprop)
		# print(valuesprop)

		if ((len(labelsrqid) == 0 and txtrqid != "") or (len(labelsprop) != 0 and labelsprop[0] == None and txtprop != "")):
			flash("Your one or more query didn't match database records !!")
			flash("Try Again !!")
			return redirect(url_for("alreadyuploaded"))
	#	if txt == "":
	#		propsstr = "NA"
	#		valtochart = "NA"

		return render_template('analysispage.html', valtochart=valtochart, propsstr=propsstr, valuesrqid=valuesrqid,
							   labelsrqid=labelsrqid, rqid=rqid, idval=idval, prop=prop, labelsprop=labelsprop,
							   valuesprop=valuesprop, txtprop=txtprop, )


if __name__ == '__main__':
	app.debug = True
	app.run(host="0.0.0.0", port=5050)  # specify port value