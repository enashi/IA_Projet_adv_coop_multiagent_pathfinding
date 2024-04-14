#===============================================================================================#
#                                   Import des bibliothèques                                    #
#===============================================================================================#
from __future__ import absolute_import, print_function, unicode_literals

import time
import random
import numpy as np
import sys
from itertools import chain

import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

#------------------------------------------------------------#
# Stratégie une : Greedy best-first + gestion des collisions #
#------------------------------------------------------------#
def greedy_best_first(p):
    game = p.game
    players = p.players
    initStates = p.initStates
    goalStates = p.goal
    wallStates = p.wall
    nbCols = p.colonnes
    nbLignes = p.lignes
    nbPlayers = len(players)
    score = [0]*nbPlayers
    iterations = 100
    
        #-----------------------------------#
        #   Attribution des fioles          #
        #-----------------------------------#

    objectifs = goalStates
    
    random.shuffle(objectifs)
    
    # attribution des fioles à l'opposée
    """
    tmp = []
    for i in range(nbPlayers):
        tmp.append(objectifs[i])
    for i in range(nbPlayers):
        objectifs[i] = tmp[5-i]
    """

    print("Objectif joueur 0", objectifs[0])
    print("Objectif joueur 1", objectifs[1])
    print("Objectif joueur 2", objectifs[2])
    print("Objectif joueur 3", objectifs[3])
    print("Objectif joueur 4", objectifs[4])
    print("Objectif joueur 5", objectifs[5])

    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True
    for w in wallStates:            # putting False for walls
        g[w]=False

        #-----------------------------------#
        # Boucle principale de déplacements #
        #-----------------------------------#


    posPlayers = initStates
    eq1 = 0     # points de l'équipe 1
    eq2 = 0     # points de l'équipe 2
    index = [0]*nbPlayers   # indice dans le path (remis à zéro lors de recalcul)
    draw = [0]*2    # somme des cases parcourues par chaque équipe


    pb = [0] * nbPlayers
    path = [0] * nbPlayers
    for i in range(nbPlayers):
        pb[i] = ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan')
        path[i] = probleme.greedy(pb[i])

    startTime = time.time()
    for i in range(iterations):
        # liste des cases occupées à l'itération i
        occupied = [0]*nbPlayers
        # récupération des cases occupées
        for j in range(nbPlayers):
            row, col = posPlayers[j]
            # on suppose qu'un agent peut traverser un agent ayant atteint son objectif
            if score[j] == 0:
                occupied[j] = (row, col)

        for j in range(nbPlayers):
            # en cas de blocage
            if len(path[j]) == index[j]+1:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                path[j] = probleme.greedy(pb[j], occupied)
                index[j] = 0
                continue
            # on récupère la prochaine case
            row, col = path[j][index[j]+1].etat
            # si elle est occupée, on recalcule le chemin
            if (row, col) in occupied:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                path[j] = probleme.greedy(pb[j], occupied)
                index[j] = 0
                if len(path[j]) <= index[j]+1:
                    continue
                row, col = path[j][index[j]+1].etat
            # on met à jour la position de l'agent
            posPlayers[j]=(row,col)
            players[j].set_rowcol(row,col)
            occupied[j] = (row, col)
            index[j] += 1
            if j in range(3):
                draw[0] += 1
            else:
                draw[1] += 1
            if (row,col) == objectifs[j]:
                occupied[j] = 0
                score[j] += 1
                if j in range(3):
                    eq1 += 1
                else:
                    eq2 += 1
                print("le joueur " + str(j) + " a atteint son but!")

        
        if eq1 == eq2:
            if eq1 == 3:
                if draw[0] < draw[1]:
                    print("Equipe 1 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break 
                elif draw[1] < draw[0]:
                    print("Equipe 2 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
                else:
                    print("Egalité")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
        else:
            if eq1 == 3:
                print("Equipe 1 gagne !")
                break 
            if eq2 == 3:
                print("Equipe 2 gagne !")
                break

        
        # on passe a l'iteration suivante du jeu
        game.mainiteration()

    # ================ FIN DE PROGRAMME =====================
    """
    Commune à toutes les stratégies.
    """
        
    print("temps total:", time.time() - startTime)
    print ("scores:", score)
    pygame.quit()


#-------------------------------------------#
# Stratégie deux : Path-slicing basé sur A* #
#-------------------------------------------#
def path_slicing(p):
    game = p.game
    players = p.players
    initStates = p.initStates
    goalStates = p.goal
    wallStates = p.wall
    nbCols = p.colonnes
    nbLignes = p.lignes
    nbPlayers = len(players)
    score = [0]*nbPlayers
    iterations = 100
    
        #-----------------------------------#
        #   Attribution des fioles          #
        #-----------------------------------#
    
    objectifs = goalStates
    
    random.shuffle(objectifs)
    
    # attribution des fioles à l'opposée
    """
    tmp = []
    for i in range(nbPlayers):
        tmp.append(objectifs[i])
    for i in range(nbPlayers):
        objectifs[i] = tmp[5-i]
    """

    print("Objectif joueur 0", objectifs[0])
    print("Objectif joueur 1", objectifs[1])
    print("Objectif joueur 2", objectifs[2])
    print("Objectif joueur 3", objectifs[3])
    print("Objectif joueur 4", objectifs[4])
    print("Objectif joueur 5", objectifs[5])

    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True
    for w in wallStates:            # putting False for walls
        g[w]=False

        #-----------------------------------#
        # Boucle principale de déplacements #
        #-----------------------------------#


    posPlayers = initStates
    eq1 = 0     # points de l'équipe 1
    eq2 = 0     # points de l'équipe 2
    index = [0]*nbPlayers   # indice dans le path (remis à zéro lors de recalcul)
    draw = [0]*2    # somme des cases parcourues par chaque équipe

    pb = [0] * nbPlayers
    path = [0] * nbPlayers
    pathslicing = [0]*nbPlayers
    for i in range(nbPlayers):
        pb[i] = ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan')
        if i in range(nbPlayers):
            path[i] = probleme.astar(pb[i])

    startTime = time.time()
    for i in range(iterations):
        # liste des cases occupées à l'itération i
        occupied = [0]*nbPlayers
        # récupération des cases occupées
        for j in range(nbPlayers):
            row, col = posPlayers[j]
            # on suppose qu'un agent peut traverser un agent ayant atteint son objectif
            if score[j] == 0:
                occupied[j] = (row, col)

        for j in range(nbPlayers):
            if len(path[j]) == index[j]+1:
                continue
            # on récupère la prochaine case
            row, col = path[j][index[j]+1].etat
            # si elle est occupée, on recalcule le chemin
            if (row, col) in occupied:
                pb[j] = ProblemeGrid2D(posPlayers[j], (row,col), g, 'manhattan')
                pathslicing[j] = probleme.astar_col(pb[j], occupied)
                path[j] = path[j][0:index[j]+1] + pathslicing[j] + path[j][index[j]+2:]
                row, col = path[j][index[j]+1].etat
            posPlayers[j]=(row,col)
            players[j].set_rowcol(row,col)
            occupied[j] = (row, col)
            index[j] += 1
            if j in range(3):
                draw[0] += 1
            else:
                draw[1] += 1
            if (row,col) == objectifs[j]:
                occupied[j] = 0
                score[j] += 1
                if j in range(3):
                    eq1 += 1
                else:
                    eq2 += 1
                print("le joueur " + str(j) + " a atteint son but!")

        
        if eq1 == eq2:
            if eq1 == 3:
                if draw[0] < draw[1]:
                    print("Equipe 1 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break 
                elif draw[1] < draw[0]:
                    print("Equipe 2 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
                else:
                    print("Egalité")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
        else:
            if eq1 == 3:
                print("Equipe 1 gagne !")
                break 
            if eq2 == 3:
                print("Equipe 2 gagne !")
                break

        
        # on passe a l'iteration suivante du jeu
        game.mainiteration()

    # ================ FIN DE PROGRAMME =====================
    """
    Commune à toutes les stratégies.
    """
        
    print("temps total:", time.time() - startTime)
    print ("scores:", score)
    pygame.quit()

#--------------------------------------------------------#
# Stratégie trois : A* indépendants au sein d'une équipe #
#--------------------------------------------------------#
def astar_col(p):
    game = p.game
    players = p.players
    initStates = p.initStates
    goalStates = p.goal
    wallStates = p.wall
    nbCols = p.colonnes
    nbLignes = p.lignes
    nbPlayers = len(players)
    score = [0]*nbPlayers
    iterations = 100
    
        #-----------------------------------#
        #   Attribution des fioles          #
        #-----------------------------------#
    
    objectifs = goalStates
    
    random.shuffle(objectifs)
    
    # attribution des fioles à l'opposée
    """
    tmp = []
    for i in range(nbPlayers):
        tmp.append(objectifs[i])
    for i in range(nbPlayers):
        objectifs[i] = tmp[5-i]
    """
    
    print("Objectif joueur 0", objectifs[0])
    print("Objectif joueur 1", objectifs[1])
    print("Objectif joueur 2", objectifs[2])
    print("Objectif joueur 3", objectifs[3])
    print("Objectif joueur 4", objectifs[4])
    print("Objectif joueur 5", objectifs[5])

    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True
    for w in wallStates:            # putting False for walls
        g[w]=False

        #-----------------------------------#
        # Boucle principale de déplacements #
        #-----------------------------------#


    posPlayers = initStates
    eq1 = 0     # points de l'équipe 1
    eq2 = 0     # points de l'équipe 2
    index = [0]*nbPlayers   # indice dans le path (remis à zéro lors de recalcul)
    draw = [0]*2    # somme des cases parcourues par chaque équipe

    pb = [0] * nbPlayers
    path = [0] * nbPlayers
    for i in range(nbPlayers):
        pb[i] = ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan')
        path[i] = probleme.astar(pb[i])

    startTime = time.time()
    for i in range(iterations):
        # liste des cases occupées à l'itération i
        occupied = [0]*nbPlayers
        # récupération des cases occupées
        for j in range(nbPlayers):
            row, col = posPlayers[j]
            # on suppose qu'un agent peut traverser un agent ayant atteint son objectif
            if score[j] == 0:
                occupied[j] = (row, col)

        for j in range(nbPlayers):
            # en cas de blocage
            if len(path[j]) == index[j]+1:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                path[j] = probleme.astar_col(pb[j], occupied)
                index[j] = 0
                continue
            # on récupère la prochaine case
            row, col = path[j][index[j]+1].etat
            # si elle est occupée, on recalcule le chemin
            if (row, col) in occupied:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                path[j] = probleme.astar_col(pb[j], occupied)
                index[j] = 0
                if len(path[j]) <= index[j]+1:
                    continue
                row, col = path[j][index[j]+1].etat
            # on met à jour la position de l'agent
            posPlayers[j]=(row,col)
            players[j].set_rowcol(row,col)
            occupied[j] = (row, col)
            index[j] += 1
            if j in range(3):
                draw[0] += 1
            else:
                draw[1] += 1
            if (row,col) == objectifs[j]:
                occupied[j] = 0
                score[j] += 1
                if j in range(3):
                    eq1 += 1
                else:
                    eq2 += 1
                print("le joueur " + str(j) + " a atteint son but!")

        
        if eq1 == eq2:
            if eq1 == 3:
                if draw[0] < draw[1]:
                    print("Equipe 1 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break 
                elif draw[1] < draw[0]:
                    print("Equipe 2 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
                else:
                    print("Egalité")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
        else:
            if eq1 == 3:
                print("Equipe 1 gagne !")
                break 
            if eq2 == 3:
                print("Equipe 2 gagne !")
                break

        
        # on passe a l'iteration suivante du jeu
        game.mainiteration()

    # ================ FIN DE PROGRAMME =====================
    """
    Commune à toutes les stratégies.
    """
        
    print("temps total:", time.time() - startTime)
    print ("scores:", score)
    pygame.quit()

#-----------------------------------#
# Stratégie quatre : Coopérative A* #
#-----------------------------------#
def coopA(p):
    game = p.game
    players = p.players
    initStates = p.initStates
    goalStates = p.goal
    wallStates = p.wall
    nbCols = p.colonnes
    nbLignes = p.lignes
    nbPlayers = len(players)
    score = [0]*nbPlayers
    iterations = 100
    
        #-----------------------------------#
        #   Attribution des fioles          #
        #-----------------------------------#
    
    objectifs = goalStates
    
    random.shuffle(objectifs)
    
    # attribution des fioles à l'opposée
    """
    tmp = []
    for i in range(nbPlayers):
        tmp.append(objectifs[i])
    for i in range(nbPlayers):
        objectifs[i] = tmp[5-i]
    """
    
    print("Objectif joueur 0", objectifs[0])
    print("Objectif joueur 1", objectifs[1])
    print("Objectif joueur 2", objectifs[2])
    print("Objectif joueur 3", objectifs[3])
    print("Objectif joueur 4", objectifs[4])
    print("Objectif joueur 5", objectifs[5])

    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True
    for w in wallStates:            # putting False for walls
        g[w]=False

        #-----------------------------------#
        # Boucle principale de déplacements #
        #-----------------------------------#

    posPlayers = initStates
    eq1 = 0     # points de l'équipe 1
    eq2 = 0     # points de l'équipe 2
    index = [0]*nbPlayers   # indice dans le path (remis à zéro lors de recalcul)
    draw = [0]*2    # somme des cases parcourues par chaque équipe

    pb = [0] * nbPlayers
    path = [0] * nbPlayers
    for i in range(nbPlayers):
        pb[i] = ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan')
        if i in range(nbPlayers):
            path[i] = probleme.astar(pb[i])
    
    startTime = time.time()
    for i in range(iterations):
        # liste des cases occupées à l'itération i
        occupied = [0]*nbPlayers
        # récupération des cases occupées
        for j in range(nbPlayers):
            row, col = posPlayers[j]
            # on suppose qu'un agent peut traverser un agent ayant atteint son objectif
            if score[j] == 0:
                occupied[j] = (row, col)

        # calcul des chemins en prenant en compte les chemins pris par les alliés
        if i == 0:
            path[1] = probleme.coopAstar(pb[1], i, [path[0]], [objectifs[0]], occupied)
            path[2] = probleme.coopAstar(pb[2], i, [path[0], path[1]], [objectifs[0], objectifs[1]], occupied)
            path[4] = probleme.coopAstar(pb[4], i, [path[3]], [objectifs[3]], occupied)
            path[5] = probleme.coopAstar(pb[5], i, [path[3], path[4]], [objectifs[3], objectifs[4]], occupied)  


        for j in range(nbPlayers):
            # en cas de blocage
            if len(path[j]) <= index[j]+1:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                if j == 0:
                    path[j] = probleme.coopAstar(pb[j], i, [path[1], path[2]], [objectifs[1], objectifs[2]], occupied)
                if j == 1:
                    path[j] = probleme.coopAstar(pb[j], i, [path[0], path[2]], [objectifs[0], objectifs[2]], occupied)
                if j == 2:
                    path[j] = probleme.coopAstar(pb[j], i, [path[0], path[1]], [objectifs[0], objectifs[1]], occupied)
                if j == 3:
                    path[j] = probleme.coopAstar(pb[j], i, [path[4], path[5]], [objectifs[4], objectifs[5]], occupied)
                if j == 4:
                    path[j] = probleme.coopAstar(pb[j], i, [path[3], path[5]], [objectifs[3], objectifs[5]], occupied)
                if j == 5:
                    path[j] = probleme.coopAstar(pb[j], i, [path[3], path[4]], [objectifs[3], objectifs[4]], occupied)
                index[j] = 0
                continue
            # on récupère la prochaine case
            (row, col) = path[j][index[j]+1].etat
            # si elle est occupée, on recalcule un chemin
            if (row, col) in occupied:
                pb[j] = ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan')
                if j == 0:
                    path[j] = probleme.coopAstar(pb[j], i, [path[1], path[2]], [objectifs[1], objectifs[2]], occupied)
                if j == 1:
                    path[j] = probleme.coopAstar(pb[j], i, [path[0], path[2]], [objectifs[0], objectifs[2]], occupied)
                if j == 2:
                    path[j] = probleme.coopAstar(pb[j], i, [path[0], path[1]], [objectifs[0], objectifs[1]], occupied)
                if j == 3:
                    path[j] = probleme.coopAstar(pb[j], i, [path[4], path[5]], [objectifs[4], objectifs[5]], occupied)
                if j == 4:
                    path[j] = probleme.coopAstar(pb[j], i, [path[3], path[5]], [objectifs[3], objectifs[5]], occupied)
                if j == 5:
                    path[j] = probleme.coopAstar(pb[j], i, [path[3], path[4]], [objectifs[3], objectifs[4]], occupied)
                index[j] = 0
                if len(path[j]) <= index[j]+1:
                    continue
                row, col = path[j][index[j]+1].etat       
            # on met à jour la position de l'agent
            posPlayers[j]=(row,col)
            players[j].set_rowcol(row,col)
            occupied[j] = (row, col)
            index[j] += 1
            if j in range(3):
                draw[0] += 1
            else:
                draw[1] += 1
            if (row,col) == objectifs[j]:
                occupied[j] = 0
                score[j] += 1
                if j in range(3):
                    eq1 += 1
                else:
                    eq2 += 1
                print("le joueur " + str(j) + " a atteint son but!")

        
        if eq1 == eq2:
            if eq1 == 3:
                if draw[0] < draw[1]:
                    print("Equipe 1 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break 
                elif draw[1] < draw[0]:
                    print("Equipe 2 gagne ! (plus court)")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
                else:
                    print("Egalité")
                    print("Equipe 1 : ", draw[0])
                    print("Equipe 2 : ", draw[1])
                    break
        else:
            if eq1 == 3:
                print("Equipe 1 gagne !")
                break 
            if eq2 == 3:
                print("Equipe 2 gagne !")
                break

        
        # on passe a l'iteration suivante du jeu
        game.mainiteration()

    # ================ FIN DE PROGRAMME =====================
    """
    Commune à toutes les stratégies.
    """
    
    print("temps total:", time.time() - startTime)
    print ("scores:", score)
    pygame.quit()
