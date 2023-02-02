""" Le serveur de l'application RTS."""
# -*- coding: utf-8 -*-
from flask import Flask, request, json
from werkzeug.wrappers import Response
import random
import sqlite3

app: Flask = Flask(__name__)
""" Le serveur flask."""

app.secret_key = "qwerasdf1234"
"""" The flask server secret key."""

class Dbman():
    """Gère la base de données.

    :type conn: sqlite3.Connection
    :type curs: sqlite3.Cursor"""
    def __init__(self):
        """Initialise la base de donnée."""
        self.conn = sqlite3.connect("RTS_serveur_DB.db")
        """Représente la connexion à la base de données."""
        self.curs = self.conn.cursor()
        """Représente le curseur de la base de données."""

    def setpartiecourante(self, chose: str) -> None:
        """Choisis la partie courante.
        :param str chose: L'état choisis. todo: JM

        :rtype: None"""
        self.vidertable("partiecourante")
        self.curs.execute("Insert into partiecourante (etat) VALUES(?);",
                          (chose,))
        self.conn.commit()

    def setinitaleatoire(self, chose: str) -> None:
        """Initalise la partie avec une configuration aléatoire.
        :param str chose: L'état choisis todo: JM

        :rtype: None"""
        self.vidertable("initaleatoire")
        self.curs.execute(
            "Insert into initaleatoire (initaleatoire) VALUES(?);",
            (chose,))
        self.conn.commit()

    def setnbrIA(self, chose: str) -> None:
        """Choisis le nombre d'IA.
        :param str chose: Le nombre d'IA choisis

        :rtype: None"""
        self.vidertable("nbrIA")
        self.curs.execute("Insert into nbrIA (nbrIA) VALUES(?);", (chose,))
        self.conn.commit()

    def setcadrecourant(self, chose: str) -> None:
        """Choisis le cadre courant.
        :param str chose: Le cadre courant choisis

        :rtype: None"""
        self.vidertable("cadrecourant")
        self.curs.execute("Insert into cadrecourant (cadrecourant) VALUES(?);",
                          (chose,))
        self.conn.commit()

    def ajouterjoueur(self, nom: str) -> None:
        """Ajoute un joueur à la base de données.
        :param str nom: Le nom du joueur à ajouter todo: JM

        :rtype: None"""
        self.curs.execute("Insert into joueurs (nom) VALUES(?);", (nom,))
        self.conn.commit()

    def ajouteractionaujoueur(self, nom: str,
                              cadrejeu: str, action: str) -> None:
        """Ajoute une action à un joueur.
        :param str nom: Le nom du joueur.
        :param str cadrejeu: Le cadre de jeu.
        :param str action: L'action à ajouter.

        :rtype: None
        """
        self.curs.execute("Insert into actionsenattente "
                          "(nom,cadrejeu,action)"
                          " VALUES(?,?,?);", (nom, cadrejeu, action))
        self.conn.commit()

    def getinfo(self, table: str) -> list:
        """"Sert à récupérer les informations d'une table.

        :param str table: Le nom de la table.

        :return: Les informations de la table.
        :rtype: list"""
        sqlnom = "select * from '" + table + "'"
        self.curs.execute(sqlnom)
        info = self.curs.fetchall()
        return info

    def getinfoconditionel(self, table: str, champ: str,
                           valeur: str) -> list:
        """Sert à récupérer les informations d'une table en fonction
        d'un champ.

        :param str table: Le nom de la table.
        :param str champ: Le champ à vérifier.
        :param str valeur: La valeur à vérifier.

        :return: Les informations de la table.
        :rtype: list"""
        sqlnom = "select * from '" + table + "' WHERE nom=?"
        self.curs.execute(sqlnom, (valeur))
        info = self.curs.fetchall()
        return info

    def resetdb(self) -> None:
        """Réinitialise la base de données.

        :rtype: None"""
        tables = ["partiecourante", "joueurs", "cadrecourant",
                  "actionsenattente", "initaleatoire", "nbrIA"]

        for i in tables:
            self.vidertable(i)

        self.curs.execute("Insert into partiecourante (etat) VALUES(?);",
                          ("dispo",))
        self.curs.execute("Insert into cadrecourant (cadrecourant) VALUES(?);",
                          (0,))
        self.curs.execute(
            "Insert into initaleatoire (initaleatoire) VALUES(?);",
            (2020,))
        self.curs.execute("Insert into nbrIA (nbrIA) VALUES(?);", (0,))
        self.conn.commit()

    def effaceractionsjoueur(self, joueur: str)  -> None:
        """Efface les actions d'un joueur de la table.

        :param str joueur: Le nom du joueur.

        :rtype: None"""
        self.curs.execute("DELETE from actionsenattente WHERE  nom=?", (joueur,))
        self.conn.commit()

    def vidertable(self, table: str)  -> None:
        """Vide une table.

        :param str table: Le nom de la table.

        :rtype: None
        """
        self.curs.execute("DELETE from " + table)
        self.conn.commit()

    def fermerdb(self)  -> None:
        """Ferme la base de données.

        :rtype: None"""
        self.conn.close()

    def updatejoueur(self, nomjoueur: str, cadre: str) -> None:
        """Met à jour le dernier cadre de jeu d'un joueur.

        :param str nomjoueur: Le nom du joueur.
        :param str cadre: Le cadre de jeu.

        :rtype: None TODO: JM"""
        # Make it so PyCharm will not warm me for SQL Dialect not configured
        monsql = "UPDATE joueurs SET derniercadrejeu = ? WHERE nom = ? ;"
        self.curs.execute(monsql, (cadre, nomjoueur))
        self.conn.commit()

#################################################################################################


@app.route("/tester_jeu", methods=["GET", "POST"])
def tester_jeu() -> Response:
    """Sert à tester le jeu.

    :rtype: Response"""
    db = Dbman()
    info = db.getinfo("partiecourante")

    return Response(json.dumps(info), mimetype='application/json')


@app.route("/reset_jeu", methods=["GET", "POST"])
def reset_jeu() -> Response:
    """Sert à réinitialiser le jeu.

    :rtype: Response"""

    db = Dbman()
    db.resetdb()
    info = db.getinfo("partiecourante")

    return Response(json.dumps(info), mimetype='application/json')

@app.route("/creer_partie", methods=["GET", "POST"])
def creer_partie() -> Response | str:
    """Sert à créer une partie.

    :rtype: Response | str"""
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
def inscrire_joueur() -> Response | str:
    """Sert à inscrire un joueur au jeu et à la base de données.

    :rtype: Response | str"""
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
def boucler_sur_lobby() -> Response:
    """Sert à boucler sur le lobby lors de l'attente de joueurs.

    :rtype: Response"""
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
def lancer_partie() -> Response:
    """Sert à lancer la partie.

    :rtype: Response"""
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
def boucler_sur_jeu() -> Response:
    """Sert à boucler sur le jeu.

    :rtype: Response"""
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
