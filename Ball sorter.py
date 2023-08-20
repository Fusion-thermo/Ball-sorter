from PIL import Image, ImageGrab
import numpy as np
from time import sleep,time
import pyautogui #for absolutely no apparent reason removing this breaks the program, the positioning doesn't go where it is supposed to go.
from pynput.mouse import Button, Controller
from classes import *

def affiche_mouvements(mouvs):
    total=[]
    print("mouvements :\n")
    for mouv in mouvs:
        total.append((mouv[0].affichage(),mouv[1].affichage()))
    print("mouvs fin\n")
    return total

def priorite_mouvements(mouve):
    depart=mouve[0]
    arrivee=mouve[1]
    score=0
    if arrivee.quantite>0:
        #règle 1 : se rejoindre dans le tube avec le moins de balles d'une autre couleur
        score+=len(arrivee.balles)
    else:
        #règle 2 : arrivée vide
        score+=100
    
    return score

def solveur():
    victoire=False
    defaite=False
    numero_coup=0
    mouvements_possibles=Mouvement(None,0,None)
    mouvement_actuel=mouvements_possibles
    #le niveau des coups que l'on essaie : d'abord tous les premiers coups possibles, puis les 2è etc
    numero_actuel=1
    while not victoire:
        numero_coup+=1
        #mouvements possibles
        mouvements=[]
        for i in range(plateau.nb_fioles-1):
            for j in range(i+1,plateau.nb_fioles):
                #print(i,j)
                #vers la droite : si fiole de départ non vide et si même couleur et si nombre de balles pas plus grand que la capacité de la fiole d'arrivée et si (départ a plus d'une seule couleur ou l'arrivée n'est pas vide)
                for sens in range(2):
                    if sens==0:
                        a,b=i,j
                    else:
                        a,b=j,i
                    if a==1 and b==9:
                        c=9
                    if plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite > 0:
                        if plateau.fioles[a].balles[-1].couleur == plateau.fioles[b].balles[-1].couleur and plateau.fioles[a].balles[-1].nombre + plateau.fioles[b].quantite <= plateau.fioles[b].taille:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
                    elif plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite == 0:
                        if plateau.fioles[a].nb_couleurs>1:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
        plateau.affichage()
        if mouvements==[]:
            for fiole in plateau.fioles:
                if fiole.nb_couleurs>1:
                    defaite=True
            victoire=True
        else:
            mouvements.sort(key=priorite_mouvements)
            for mouve in mouvements:
                mouvement_actuel.enfants.append(Mouvement(mouvement_actuel,numero_coup,mouve))
            #affiche_mouvements(mouvements)
            #action
            choisi=mouvements[0]
            choisi[1].ajouter(choisi[0].balles[-1])
            choisi[0].retirer()
            mouvement_actuel=mouvement_actuel.enfants[0]
        if defaite:
            #1) marquer le parent de cette série de coups du niveau actuel comme "tried"
            #2) chercher un autre mouvement du même niveau non tried
            #2.1) s'il n'y en a pas le niveau augmente de 1
            #3) chercher un mouvement du nouveau niveau et reprendre à partir de là,
            #ce qui veut dire refaire les coups qui mènent à ce niveau
            


    if victoire:
        print('gagné')
    else:
        print('perdu')

def initialisation_plateau():
        dico_couleurs={"orange":(215, 111, 0),"cyan":(7, 162, 124),"magenta":(131, 3, 156),"jaune":(208, 187, 0),"rouge":(174, 0, 0),"bleu":(1, 90, 174),"gris":(140, 140, 140),"violet":(90, 12, 164),"vert":(3, 142, 0)}
        sleep(2)
        im = ImageGrab.grab(bbox =(968,441,1768,1464))
        #im.show()
        px=im.load()
        #haut avec 6 fioles
        x0,y0=69,130
        x02,y02=1038,568
        decalage_x=130
        decalage_y=89
        for x in range(6):
            #img= ImageGrab.grab(bbox =(x02+x*decalage_x,y02,x02+(x+1)*decalage_x,y02+3*decalage_y))
            plateau.ajouter_fiole(Fiole((x0+x*decalage_x,y0),4))
            for y in range(4):
                couleur=px[x0+x*decalage_x,y0+y*decalage_y]
                for color in dico_couleurs.keys():
                    if bonne_couleur(couleur,dico_couleurs[color],0.1):
                        #print(x,y,color)
                        plateau.fioles[x].initialiser(Balles(color,1))
        #bas avec 5 fioles
        x0,y0=96,648
        x02,y02=1038,568
        decalage_x=151.75
        for x in range(5):
            #img= ImageGrab.grab(bbox =(x02+x*decalage_x,y02,x02+(x+1)*decalage_x,y02+3*decalage_y))
            plateau.ajouter_fiole(Fiole((x0+x*decalage_x,y0),4))
            for y in range(4):
                couleur=px[x0+x*decalage_x,y0+y*decalage_y]
                for color in dico_couleurs.keys():
                    if bonne_couleur(couleur,dico_couleurs[color],0.1):
                        #print(x,y,color)
                        plateau.fioles[6+x].initialiser(Balles(color,1))
                    

# plateau=Plateau(6,5)
# initialisation_plateau()
# plateau.affichage()
plateau_original=plateau.copy()
solveur()