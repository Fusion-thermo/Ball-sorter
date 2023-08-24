from PIL import Image, ImageGrab
from classes import *
from statistics import mean

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
        score+=10 * arrivee.nb_couleurs
        #règle esthétique : les balles de 1 rejoignent les balles de 3 et pas l'inverse
        score+=depart.quantite - arrivee.quantite
    else:
        #règle 2 : arrivée vide
        score+=1000
    
    return score

def recherche_mouvement(mouvement,numero_voulu):
    #fonction récursive cherchant un mouvement non essayé pour un niveau de test donné.
    if mouvement.numero_du_coup < numero_voulu:
        for mouve in mouvement.enfants:
            retour=recherche_mouvement(mouve,numero_voulu)
            if type(retour) is Mouvement:
                return retour
    if mouvement.tried==False:# and mouvement.numero_du_coup==numero_voulu
        return mouvement
    return None

def solveur(plateau):
    victoire=False
    defaite=False
    numero_coup=0
    mouvements_possibles=Mouvement(None,0,None,None,None,None,None)
    mouvements_possibles.tried=True
    mouvement_actuel=mouvements_possibles
    #le niveau des coups que l'on essaie : d'abord tous les premiers coups possibles, puis les 2è etc
    numero_test_actuel=1
    while not victoire:
        numero_coup+=1
        plateau.affichage()
        #mouvements possibles
        mouvements=[]
        for i in range(plateau.nb_fioles-1):
            for j in range(i+1,plateau.nb_fioles):
                #vers la droite : si fiole de départ non vide et si même couleur et si nombre de balles pas plus grand que la capacité de la fiole d'arrivée et si (départ a plus d'une seule couleur ou l'arrivée n'est pas vide)
                for sens in range(2):
                    if sens==0:
                        a,b=i,j
                    else:
                        a,b=j,i
                    if plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite > 0:
                        if plateau.fioles[a].balles[-1].couleur == plateau.fioles[b].balles[-1].couleur and plateau.fioles[a].balles[-1].nombre + plateau.fioles[b].quantite <= plateau.fioles[b].taille:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
                    elif plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite == 0:
                        if plateau.fioles[a].nb_couleurs>1:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
        if mouvements==[]:
            for fiole in plateau.fioles:
                if fiole.nb_couleurs>1 or (fiole.nb_couleurs==1 and fiole.quantite<fiole.taille):
                    defaite=True
                    break
            if not defaite:
                victoire=True
        else:
            mouvements.sort(key=priorite_mouvements)
            #retirer les mouvements identiques
            copie=mouvements[:]
            #mouvements=[]
            decalage=0
            for i in range(len(copie)-1):
                if copie[i][0].numero==copie[i+1][0].numero and [(balle.couleur,balle.nombre) for balle in copie[i][1].balles] == [(balle.couleur,balle.nombre) for balle in copie[i+1][1].balles]:
                    mouvements.remove(mouvements[i+1-decalage])
                    decalage+=1
            #ajouter les mouvements possibles en enfan au mouvement actuel
            for mouve in mouvements:
                if mouve[1].quantite>0:
                    mouvement_actuel.enfants.append(Mouvement(mouvement_actuel,numero_coup,mouve[0],mouve[1],mouve[0].balles[-1].couleur,mouve[0].balles[-1].nombre,mouve[1].balles[-1].nombre))
                else:
                    mouvement_actuel.enfants.append(Mouvement(mouvement_actuel,numero_coup,mouve[0],mouve[1],mouve[0].balles[-1].couleur,mouve[0].balles[-1].nombre,0))
            #action
            mouvement_actuel=mouvement_actuel.enfants[0]
            print("choix : ",mouvement_actuel.fiole_depart.affichage(),mouvement_actuel.fiole_arrivee.affichage(),"\n")
            mouvement_actuel.jouer()
            
        if defaite:
            print("PERDU",numero_test_actuel)
            defaite=False
            #1) annuler tous les coups pour revenir à la situation initiale et marquer le parent de cette série de coups du niveau actuel comme "tried"
            #mouvement_actuel.affichage()
            while mouvement_actuel.numero_du_coup>0:
                if mouvement_actuel.numero_du_coup==numero_test_actuel:
                    mouvement_actuel.tried=True
                mouvement_actuel.inverser()
                mouvement_actuel=mouvement_actuel.parent
            #plateau.affichage()
            #2) chercher un autre mouvement du même niveau non tried
            nouveau_mouvement=recherche_mouvement(mouvements_possibles,numero_test_actuel)
            #2.5) s'il n'y en a pas le niveau augmente de 1 et chercher un mouvement du nouveau niveau 
            if type(nouveau_mouvement) is not Mouvement:
                numero_test_actuel+=1
                nouveau_mouvement=recherche_mouvement(mouvements_possibles,numero_test_actuel)
            #3) reprendre à partir de là,
            #ce qui veut dire refaire les coups qui ont mené à ce nouveau mouvement depuis le début, puis jouer le mouvement
            rejouer=[nouveau_mouvement]

            mouvement_actuel=nouveau_mouvement
            while mouvement_actuel.numero_du_coup>1:
                mouvement_actuel=mouvement_actuel.parent
                rejouer.append(mouvement_actuel)
            rejouer.reverse()
            for mouve in rejouer:
                mouve.jouer()
            mouvement_actuel=rejouer[-1]
            numero_coup=numero_test_actuel
    
    return mouvement_actuel

def solveur_hidden(plateau):
    victoire=False
    defaite=False
    numero_coup=0
    mouvements_possibles=Mouvement(None,0,None,None,None,None,None)
    mouvements_possibles.tried=True
    mouvement_actuel=mouvements_possibles
    #le niveau des coups que l'on essaie : d'abord tous les premiers coups possibles, puis les 2è etc
    numero_test_actuel=1
    while not victoire:
        numero_coup+=1
        sleep(0.9)
        plateau=modif_plateau_hidden(plateau)
        plateau.affichage()
        #mouvements possibles
        mouvements=[]
        for i in range(plateau.nb_fioles-1):
            for j in range(i+1,plateau.nb_fioles):
                #vers la droite : si fiole de départ non vide et si même couleur et si nombre de balles pas plus grand que la capacité de la fiole d'arrivée et si (départ a plus d'une seule couleur ou l'arrivée n'est pas vide)
                for sens in range(2):
                    if sens==0:
                        a,b=i,j
                    else:
                        a,b=j,i
                    if plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite > 0:
                        if plateau.fioles[a].balles[-1].couleur == plateau.fioles[b].balles[-1].couleur and plateau.fioles[a].balles[-1].nombre + plateau.fioles[b].quantite <= plateau.fioles[b].taille:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
                    elif plateau.fioles[a].quantite > 0 and plateau.fioles[b].quantite == 0:
                        if plateau.fioles[a].nb_couleurs>1:
                            mouvements.append((plateau.fioles[a],plateau.fioles[b]))
                            print("{} --> {}".format(a,b))
        if mouvements==[]:
            for fiole in plateau.fioles:
                if fiole.nb_couleurs>1 or (fiole.nb_couleurs==1 and fiole.quantite<fiole.taille):
                    defaite=True
                    break
            if not defaite:
                victoire=True
        else:
            mouvements.sort(key=priorite_mouvements)
            #retirer les mouvements identiques
            copie=mouvements[:]
            #mouvements=[]
            decalage=0
            for i in range(len(copie)-1):
                if copie[i][0].numero==copie[i+1][0].numero and [(balle.couleur,balle.nombre) for balle in copie[i][1].balles] == [(balle.couleur,balle.nombre) for balle in copie[i+1][1].balles]:
                    mouvements.remove(mouvements[i+1-decalage])
                    decalage+=1
            #ajouter les mouvements possibles en enfan au mouvement actuel
            for mouve in mouvements:
                if mouve[1].quantite>0:
                    mouvement_actuel.enfants.append(Mouvement(mouvement_actuel,numero_coup,mouve[0],mouve[1],mouve[0].balles[-1].couleur,mouve[0].balles[-1].nombre,mouve[1].balles[-1].nombre))
                else:
                    mouvement_actuel.enfants.append(Mouvement(mouvement_actuel,numero_coup,mouve[0],mouve[1],mouve[0].balles[-1].couleur,mouve[0].balles[-1].nombre,0))
            #action
            mouvement_actuel=mouvement_actuel.enfants[0]
            print("choix : ",mouvement_actuel.fiole_depart.affichage(),mouvement_actuel.fiole_arrivee.affichage(),"\n")
            mouvement_actuel.jouer()
            mouvement_actuel.fiole_depart.clique()
            sleep(0.3)
            mouvement_actuel.fiole_arrivee.clique()
            sleep(0.3)
                        
        if defaite:
            print("PERDU",numero_test_actuel)
            defaite=False
            #1) annuler tous les coups pour revenir à la situation initiale et marquer le parent de cette série de coups du niveau actuel comme "tried"
            #mouvement_actuel.affichage()
            while mouvement_actuel.numero_du_coup>0:
                if mouvement_actuel.numero_du_coup==numero_test_actuel:
                    mouvement_actuel.tried=True
                mouvement_actuel.inverser()
                mouvement_actuel=mouvement_actuel.parent
            sleep(0.2)
            mouse.position = (1165,217)
            sleep(0.2)
            mouse.click(Button.left)
            #plateau.affichage()
            #2) chercher un autre mouvement du même niveau non tried
            nouveau_mouvement=recherche_mouvement(mouvements_possibles,numero_test_actuel)
            #2.5) s'il n'y en a pas le niveau augmente de 1 et chercher un mouvement du nouveau niveau 
            if type(nouveau_mouvement) is not Mouvement:
                numero_test_actuel+=1
                nouveau_mouvement=recherche_mouvement(mouvements_possibles,numero_test_actuel)
            #3) reprendre à partir de là,
            #ce qui veut dire refaire les coups qui ont mené à ce nouveau mouvement depuis le début, puis jouer le mouvement
            rejouer=[nouveau_mouvement]

            mouvement_actuel=nouveau_mouvement
            while mouvement_actuel.numero_du_coup>1:
                mouvement_actuel=mouvement_actuel.parent
                rejouer.append(mouvement_actuel)
            rejouer.reverse()
            for mouve in rejouer:
                mouve.jouer()
                mouve.fiole_depart.clique()
                sleep(0.5)
                mouve.fiole_arrivee.clique()
                sleep(0.5)

            mouvement_actuel=rejouer[-1]
            numero_coup=numero_test_actuel
    
    return mouvement_actuel  

def modif_plateau_hidden(plateau):
    dico_couleurs={"orange":(215, 111, 0),"cyan":(7, 162, 124),"magenta":(131, 3, 156),"jaune":(208, 187, 0),"rouge":(174, 0, 0),"bleu":(1, 90, 174),"gris":(139, 139, 139),"violet":(90, 12, 164),"vert":(3, 142, 0),"caché":(126, 126, 126)}
    im = ImageGrab.grab(bbox =(968,441,1768,1464))
    #im.show()
    px=im.load()
    decalage_y=89
    #haut
    if plateau.n_fioles_haut==6:
        x0,y0=69,130
        decalage_x=130
    elif plateau.n_fioles_haut==5:
        x0,y0=91,130
        decalage_x=151.75
    for x in range(plateau.n_fioles_haut):
        plateau.fioles[x].reset()
        fini=False
        for y in range(4):
            if y==3:
                fini=True
            couleur=px[x0+x*decalage_x,y0+y*decalage_y]
            #print(couleur)
            if bonne_couleur(couleur,dico_couleurs["gris"],0.1) or bonne_couleur(couleur,dico_couleurs["caché"],0.1):
                #test au cas par cas, caché est plus sombre que le gris normal
                if abs(mean(couleur)-mean(dico_couleurs["gris"])) > abs(mean(couleur)-mean(dico_couleurs["caché"])):
                    plateau.fioles[x].initialiser(Balles("caché",1),fini)
                else:
                    plateau.fioles[x].initialiser(Balles("gris",1),fini)
                continue
            for color in dico_couleurs.keys():
                if bonne_couleur(couleur,dico_couleurs[color],0.1):
                    plateau.fioles[x].initialiser(Balles(color,1),fini)
    #bas
    if plateau.n_fioles_bas==5:
        x0,y0=96,648
        decalage_x=151.75
    elif plateau.n_fioles_bas==4:
        x0,y0=126,648
        decalage_x=182
    for x in range(plateau.n_fioles_bas):
        plateau.fioles[plateau.n_fioles_haut+x].reset()
        fini=False
        for y in range(4):
            if y==3:
                fini=True
            couleur=px[x0+x*decalage_x,y0+y*decalage_y]
            #print(couleur)
            if bonne_couleur(couleur,dico_couleurs["gris"],0.1) or bonne_couleur(couleur,dico_couleurs["caché"],0.1):
                #test au cas par cas, caché est plus sombre que le gris normal
                if abs(mean(couleur)-mean(dico_couleurs["gris"])) > abs(mean(couleur)-mean(dico_couleurs["caché"])):
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles("caché",1),fini)
                else:
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles("gris",1),fini)
                continue
            for color in dico_couleurs.keys():
                if bonne_couleur(couleur,dico_couleurs[color],0.1):
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles(color,1),fini)
    return plateau

def initialisation_plateau(plateau,hidden):
    dico_couleurs={"orange":(215, 111, 0),"cyan":(7, 162, 124),"magenta":(131, 3, 156),"jaune":(208, 187, 0),"rouge":(174, 0, 0),"bleu":(1, 90, 174),"gris":(139, 139, 139),"violet":(90, 12, 164),"vert":(3, 142, 0),"caché":(126, 126, 126)}
    sleep(2)
    im = ImageGrab.grab(bbox =(968,441,1768,1464))
    #im.show()
    px=im.load()
    decalage_y=89
    #haut
    if plateau.n_fioles_haut==6:
        x0,y0=69,130
        decalage_x=130
    elif plateau.n_fioles_haut==5:
        x0,y0=91,130
        decalage_x=151.75
    for x in range(plateau.n_fioles_haut):
        plateau.ajouter_fiole(Fiole((968+x0+x*decalage_x,441+y0),4,x))
        fini=False
        for y in range(4):
            if y==3:
                fini=True
            couleur=px[x0+x*decalage_x,y0+y*decalage_y]
            #print(couleur)
            if bonne_couleur(couleur,dico_couleurs["gris"],0.1) or bonne_couleur(couleur,dico_couleurs["caché"],0.1):
                #test au cas par cas, caché est plus sombre que le gris normal
                if abs(mean(couleur)-mean(dico_couleurs["gris"])) > abs(mean(couleur)-mean(dico_couleurs["caché"])):
                    plateau.fioles[x].initialiser(Balles("caché",1),fini)
                else:
                    plateau.fioles[x].initialiser(Balles("gris",1),fini)
                continue
            for color in dico_couleurs.keys():
                if bonne_couleur(couleur,dico_couleurs[color],0.1):
                    plateau.fioles[x].initialiser(Balles(color,1),fini)
    #bas
    if plateau.n_fioles_bas==5:
        x0,y0=96,648
        decalage_x=151.75
    elif plateau.n_fioles_bas==4:
        x0,y0=126,648
        decalage_x=182
    for x in range(plateau.n_fioles_bas):
        plateau.ajouter_fiole(Fiole((968+x0+x*decalage_x,441+y0),4,plateau.n_fioles_haut+x))
        fini=False
        for y in range(4):
            if y==3:
                fini=True
            couleur=px[x0+x*decalage_x,y0+y*decalage_y]
            #print(couleur)
            if bonne_couleur(couleur,dico_couleurs["gris"],0.1) or bonne_couleur(couleur,dico_couleurs["caché"],0.1):
                #test au cas par cas, caché est plus sombre que le gris normal
                if abs(mean(couleur)-mean(dico_couleurs["gris"])) > abs(mean(couleur)-mean(dico_couleurs["caché"])):
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles("caché",1),fini)
                else:
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles("gris",1),fini)
                continue
            for color in dico_couleurs.keys():
                if bonne_couleur(couleur,dico_couleurs[color],0.1):
                    plateau.fioles[plateau.n_fioles_haut+x].initialiser(Balles(color,1),fini)
    return plateau
    


#main
mode=1
for i in range(6):
    mode+=1
    if mode>3:
        mode=1
    if mode<3:
        hidden=False
    else:
        hidden=True
    if mode==1:
        plateau=Plateau(5,4)
    else:
        plateau=Plateau(6,5)
    plateau=initialisation_plateau(plateau,hidden)
    plateau.affichage()
    if hidden:
        mouvements_solution=solveur_hidden(plateau)
    else:
        mouvements_solution=solveur(plateau)

    print("victoire")
    if not hidden:
        #exécution des coups
        ordre=[]
        while mouvements_solution.numero_du_coup>0:
            ordre.append(mouvements_solution)
            mouvements_solution=mouvements_solution.parent
        ordre.reverse()
        for mouvement in ordre:
            mouvement.fiole_depart.clique()
            sleep(0.6)
            mouvement.fiole_arrivee.clique()
            sleep(0.6)

    sleep(1)
    mouse.position = (1355,1388)
    sleep(0.2)
    mouse.click(Button.left)