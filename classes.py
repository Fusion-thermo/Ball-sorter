class Plateau:
    def __init__(self,n_fioles_haut,n_fioles_bas):
        self.n_fioles_haut=n_fioles_haut
        self.n_fioles_bas=n_fioles_bas
        self.nb_fioles=n_fioles_bas+n_fioles_haut
        self.fioles=[]
    def ajouter_fiole(self,fiole):
        self.fioles.append(fiole)
        #self.nb_fioles+=1
    def affichage(self):
        for i in range(self.nb_fioles):
            self.fioles[i].affichage(i)
        print("\n")
    def copy(self):
        copie=Plateau(self.n_fioles_haut,self.n_fioles_bas)
        

class Fiole:
    def __init__(self,coos,taille):
        self.coos=coos
        self.taille=taille
        self.quantite=0
        self.nb_couleurs=0
        #fin de la liste = haut de la fiole
        self.balles=[]
    def ajouter(self,balles):
        if sum(balle.nombre for balle in self.balles) + balles.nombre> self.taille:
            raise ValueError("Déjà {} balles".format(self.taille))
        if self.quantite>0:
            self.quantite+=balles.nombre
            new=Balles(balles.couleur,balles.nombre+self.balles[-1].nombre)
            self.balles.pop()
            self.balles.append(new)
        else:
            self.balles.append(balles)
            self.quantite=balles.nombre
            self.nb_couleurs=1
    def retirer(self):
        self.quantite-=self.balles[-1].nombre
        self.nb_couleurs-=1
        self.balles.pop()
    def initialiser(self,balles):
        if self.quantite>0:
            if self.balles[-1].couleur==balles.couleur:
                new=Balles(balles.couleur,balles.nombre+self.balles[-1].nombre)
                self.balles.pop()
                self.balles.append(new)
            else:
                self.balles.append(balles)
                self.nb_couleurs+=1
        else:
            self.balles.append(balles)
            self.nb_couleurs=1
        self.quantite+=balles.nombre
        if self.quantite==self.taille:
            #parce qu'elles sont ajoutées du haut vers le bas
            self.balles.reverse()

    def affichage(self,numero=""):
        print(numero,[balles.affichage() for balles in self.balles])            

class Balles:
    def __init__(self,couleur,nombre):
        self.couleur=couleur
        self.nombre=nombre
    def affichage(self):
        return (self.couleur,self.nombre)

class Mouvement:
    def __init__(self,parent,numero_du_coup,action):
        self.parent=parent
        self.enfants=[]
        #si pas d'enfants : ou bien pas encore générés car mouv pas encore choisi, ou bien il mène à une défaite et peut être retiré.
        self.numero_du_coup=numero_du_coup
        self.action=action
        self.tried=False

def bonne_couleur(mesure, reference, ecart_admissible):
    correct=True
    for i in range(3):
        if abs(mesure[i]-reference[i]) > ecart_admissible*255:
            correct=False
    return correct

""" #Jeu de test simple : 
plateau=Plateau(5,0)
for i in range(5):
    plateau.fioles.append(Fiole((0,0),3))
plateau.fioles[0].balles=[Balles("vert",1),Balles("jaune",1),Balles("rouge",1)]
plateau.fioles[0].quantite,plateau.fioles[0].nb_couleurs = 3,3
plateau.fioles[1].balles=[Balles("vert",1),Balles("bleu",1),Balles("jaune",1)]
plateau.fioles[1].quantite,plateau.fioles[1].nb_couleurs = 3,3
plateau.fioles[2].balles=[Balles("bleu",1),Balles("rouge",1)]
plateau.fioles[2].quantite,plateau.fioles[2].nb_couleurs = 2,2
#les deux dernières sont vides """
#Jeu de test complexe : 
plateau=Plateau(6,5)
for i in range(11):
    plateau.fioles.append(Fiole((0,0),4))
plateau.fioles[0].balles=[Balles('magenta', 2), Balles('cyan', 1), Balles('orange', 1)]
plateau.fioles[0].quantite,plateau.fioles[0].nb_couleurs = 4,3
plateau.fioles[1].balles=[Balles('bleu', 1), Balles('rouge', 1), Balles('jaune', 2)]
plateau.fioles[1].quantite,plateau.fioles[1].nb_couleurs = 4,3
plateau.fioles[2].balles=[Balles('violet', 3), Balles('gris', 1)]
plateau.fioles[2].quantite,plateau.fioles[2].nb_couleurs = 4,2
plateau.fioles[3].balles=[Balles('jaune', 1), Balles('magenta', 1), Balles('gris', 1), Balles('bleu', 1)]
plateau.fioles[3].quantite,plateau.fioles[3].nb_couleurs = 4,4
plateau.fioles[4].balles=[Balles('gris', 1), Balles('bleu', 1), Balles('vert', 1), Balles('rouge', 1)]
plateau.fioles[4].quantite,plateau.fioles[4].nb_couleurs = 4,4
plateau.fioles[5].balles=[Balles('violet', 1), Balles('vert', 1), Balles('orange', 1), Balles('gris', 1)]
plateau.fioles[5].quantite,plateau.fioles[5].nb_couleurs = 4,4
plateau.fioles[6].balles=[Balles('cyan', 2), Balles('vert', 1), Balles('jaune', 1)]
plateau.fioles[6].quantite,plateau.fioles[6].nb_couleurs = 4,3
plateau.fioles[7].balles=[Balles('orange', 1), Balles('vert', 1), Balles('orange', 1), Balles('bleu', 1)]
plateau.fioles[7].quantite,plateau.fioles[7].nb_couleurs = 4,4
plateau.fioles[8].balles=[Balles('magenta', 1), Balles('rouge', 2), Balles('cyan', 1)]
plateau.fioles[8].quantite,plateau.fioles[8].nb_couleurs = 4,3
#les deux dernières sont vides