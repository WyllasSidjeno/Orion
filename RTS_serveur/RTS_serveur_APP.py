# -*- coding: utf-8 -*-


from flask import Flask, request, json
from werkzeug.wrappers import Response
import random
import sqlite3

app = Flask(__name__)

app.secret_key = "qwerasdf1234"

class Dbman():
    def __init__(self):
        self.conn = sqlite3.connect("RTS_serveur_DB.db")
        self.curs = self.conn.cursor()

    def setpartiecourante(self, chose):
        self.vidertable("partiecourante")
        self.curs.execute("Insert into partiecourante (etat) VALUES(?);", (chose,))
        self.conn.commit()

    def setinitaleatoire(self, chose):
        self.vidertable("initaleatoire")
        self.curs.execute("Insert into initaleatoire (initaleatoire) VALUES(?);", (chose,))
        self.conn.commit()

    def setnbrIA(self, chose):
        self.vidertable("nbrIA")
        self.curs.execute("Insert into nbrIA (nbrIA) VALUES(?);", (chose,))
        self.conn.commit()

    def setcadrecourant(self, chose):
        self.vidertable("cadrecourant")
        self.curs.execute("Insert into cadrecourant (cadrecourant) VALUES(?);", (chose,))
        self.conn.commit()

    def ajouterjoueur(self, nom):
        self.curs.execute("Insert into joueurs (nom) VALUES(?);", (nom,))
        self.conn.commit()

    def ajouteractionaujoueur(self, nom, cadrejeu, action):
        self.curs.execute("Insert into actionsenattente (nom,cadrejeu,action) VALUES(?,?,?);", (nom, cadrejeu, action))
        self.conn.commit()

    def getinfo(self, table):
        sqlnom = "select * from '" + table + "'"
        self.curs.execute(sqlnom)
        info = self.curs.fetchall()
        return info

    def getinfoconditionel(self, table, champ, valeur):
        sqlnom = "select * from '" + table + "' WHERE nom=?"
        self.curs.execute(sqlnom, (valeur))
        info = self.curs.fetchall()
        return info

    def resetdb(self):
        tables = ["partiecourante", "joueurs", "cadrecourant", "actionsenattente", "initaleatoire", "nbrIA"]
        for i in tables:
            self.vidertable(i)

        self.curs.execute("Insert into partiecourante (etat) VALUES(?);", ("dispo",))
        self.curs.execute("Insert into cadrecourant (cadrecourant) VALUES(?);", (0,))
        self.curs.execute("Insert into initaleatoire (initaleatoire) VALUES(?);", (2020,))
        self.curs.execute("Insert into nbrIA (nbrIA) VALUES(?);", (0,))
        self.conn.commit()

    def effaceractionsjoueur(self, joueur):
        self.curs.execute("DELETE from actionsenattente WHERE  nom=?", (joueur,))
        self.conn.commit()

    def vidertable(self, table):
        self.curs.execute("DELETE from " + table)
        self.conn.commit()

    def fermerdb(self):
        self.conn.close()

    def updatejoueur(self, nomjoueur, cadre):
        monsql = "UPDATE joueurs SET derniercadrejeu = ? WHERE nom = ? ;"
        self.curs.execute(monsql, (cadre, nomjoueur))
        self.conn.commit()

#################################################################################################


@app.route("/tester_jeu", methods=["GET", "POST"])
def tester_jeu():
    db = Dbman()
    info = db.getinfo("partiecourante")

    return Response(json.dumps(info), mimetype='application/json')


@app.route("/reset_jeu", methods=["GET", "POST"])
def reset_jeu():
    db = Dbman()
    db.resetdb()
    info = db.getinfo("partiecourante")

    return Response(json.dumps(info), mimetype='application/json')

@app.route("/creer_partie", methods=["GET", "POST"])
def creer_partie():
    db = Dbman()
    info = db.getinfo("partiecourante")
    if "dispo" in info[0]:
        if request.method == "POST":
            nom = request.form["nom"]
            db.ajouterjoueur(nom)
            db.setpartiecourante("attente")

            joueurs = db.getinfo("joueurs")
            reponse = [joueurs]
            return Response(json.dumps(reponse), mimetype='application/json')
            # return repr([joueurs,valoptions])
    else:
        return str("banane")

@app.route("/inscrire_joueur", methods=["GET", "POST"])
def inscrire_joueur():
    db = Dbman()
    info = db.getinfo("partiecourante")
    if "attente" in info[0]:
        if request.method == "POST":
            nom = request.form["nom"]
            db.ajouterjoueur(nom)

            joueurs = db.getinfo("joueurs")
            reponse = [joueurs]
            return Response(json.dumps(reponse), mimetype='application/json')
            # return repr([joueurs,valoptions])
    else:
        return "Erreur d'inscription"


@app.route("/boucler_sur_lobby", methods=["POST"])
def boucler_sur_lobby():
    db = Dbman()
    info = db.getinfo("partiecourante")
    if "courante" in info[0]:
        # nbrIA=db.getinfo("nbrIA")
        initaleatoire = db.getinfo("initaleatoire")
        reponse = ["courante", initaleatoire]
        return Response(json.dumps(reponse), mimetype='application/json')
        # return str(["courante",initaleatoire,nbrIA])
    else:
        info = db.getinfo("joueurs")
        # maliste=[]
        # for i in info:
        #    maliste.append(i)

        return Response(json.dumps(info), mimetype='application/json')
        # return repr(info)

@app.route("/lancer_partie", methods=["GET", "POST"])
def lancer_partie():
    db = Dbman()
    if request.method == "POST":
        nom = request.form["nom"]

        initrand = random.randrange(1000, 10000)
        # db.setnbrIA(nbrIA)
        db.setinitaleatoire(initrand)
        db.setpartiecourante("courante")
        info = "courante"
        return Response(json.dumps(info), mimetype='application/json')
        # return "courante"


@app.route("/boucler_sur_jeu", methods=["POST"])
def boucler_sur_jeu():
    db = Dbman()
    # cadreactuel=db.getinfo("cadrecourant")[0]
    nom = request.form["nom"]
    cadrejeu = int(request.form["cadrejeu"])
    actionsrequises = request.form["actionsrequises"]
    ####################################################################
    ## test pour attendre les joueurs retardataires

    db.updatejoueur(nom, cadrejeu)

    joueurscadrejeu = db.getinfo("joueurs")
    _min = min(joueurscadrejeu, key=lambda t: t[1])
    _max = max(joueurscadrejeu, key=lambda t: t[1])
    # on joue le coup ordinaire
    # ON CALCULE LE CADRE DE L'ACTION REQUISE
    sautdecadre = _max[1] + 5
    # ON AJOUTE LES ACTIONS À TOUS LES JOUEURS
    if actionsrequises != "None":
        info = db.getinfo("joueurs")
        for i in info:
            db.ajouteractionaujoueur(i[0], sautdecadre, actionsrequises)

    if (cadrejeu - _min[1]) > 10:
        # on envoi attention
        maliste = ["ATTENTION"]
    else:
        # ON CHERCHE S'IL Y A DES ACTIONS QUE NOUS DEVRONS RECEPTIONNER
        info = db.getinfo("actionsenattente")

        maliste = []
        for i in info:
            if i[0] == nom:
                maliste.append([i[1], i[2]])
        db.effaceractionsjoueur(nom)
    db.fermerdb()

    return Response(json.dumps(maliste), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
