# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import functools
import time



def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 



    
###############################################################################

class Probleme(object):
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,heuristique):
        self.init=init
        self.but=but
        self.heuristique=heuristique
        
    @abstractmethod
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        pass
        
    @abstractmethod    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        pass
        
    @abstractmethod
    def successeurs(self,etat):
        """ retourne une liste avec les successeurs possibles
            """
        pass
        
    @abstractmethod
    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        pass
    
    



###############################################################################

@functools.total_ordering # to provide comparison of nodes
class Noeud:
    def __init__(self, etat, time, g, pere=None):
        self.etat = etat
        self.time = time
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.etat) + " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(s,self.time+1,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            print (n)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return            
        
        
###############################################################################
# A*
###############################################################################

def astar(p,verbose=False,stepwise=False):
    """
    application de l'algorithme a-star
    sur un probleme donné
        """
        
    startTime = time.time()

    nodeInit = Noeud(p.init,0,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

    reserve = {}        
    bestNoeud = nodeInit
    
    while frontiere != [] and not p.estBut(bestNoeud.etat):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
        stop_stepwise=""
        if stepwise==True:
            stop_stepwise = input("Press Enter to continue (s to stop)...")
            print ("best", min_f, "\n", bestNoeud)
            print ("Frontière: \n", frontiere)
            print ("Réserve:", reserve)
            if stop_stepwise=="s":
                stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
    if verbose:
        bestNoeud.trace(p)          
        print ("=------------------------------=")
        print ("Nombre de noeuds explorés", len(reserve))
        c=0
        for (f,n) in frontiere:
            if p.immatriculation(n.etat) not in reserve:
                c+=1
        print ("Nombre de noeuds de la frontière", c)
        print ("Nombre de noeuds en mémoire:", c + len(reserve))
        print ("temps de calcul:", time.time() - startTime)
        print ("=------------------------------=")
     
    n=bestNoeud
    path = []
    while n!=None :
        path.append(n)
        n = n.pere
    return path[::-1] # extended slice notation to reverse list


###############################################################################
# AUTRES ALGOS DE RESOLUTIONS...
###############################################################################

def greedy(p, occupied=[], verbose=False,stepwise=False):
	"""
	application de l'algorithme greedy best-first sur un probleme donné, en prenant en compte
	les cases occupées par les agents à un instant donné
	"""
        
	startTime = time.time()

	nodeInit = Noeud(p.init,0,0,None)
	frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

	reserve = {}        
	bestNoeud = nodeInit
    
	while frontiere != [] and not p.estBut(bestNoeud.etat):              
		(min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
		if p.immatriculation(bestNoeud.etat) not in reserve:            
			reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
			nouveauxNoeuds = bestNoeud.expand(p)
			for n in nouveauxNoeuds:
				if n.etat not in occupied:
                    f = p.h_value(n.etat,p.but) #distManhattan
                    heapq.heappush(frontiere, (f,n)) #Ajoute le noeud au sommet de la frontiere
				else:
                    occupied[occupied.index(n.etat)] = 0 #Rend la case qui etait occupée non occupée

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
		stop_stepwise=""
		if stepwise==True:
			stop_stepwise = input("Press Enter to continue (s to stop)...")
			print ("best", min_f, "\n", bestNoeud)
			print ("Frontière: \n", frontiere)
			print ("Réserve:", reserve)
			if stop_stepwise=="s":
				stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
	if verbose:
		bestNoeud.trace(p)          
		print ("=------------------------------=")
		print ("Nombre de noeuds explorés", len(reserve))
		c=0
		for (f,n) in frontiere:
			if p.immatriculation(n.etat) not in reserve:
				c+=1
		print ("Nombre de noeuds de la frontière", c)
		print ("Nombre de noeuds en mémoire:", c + len(reserve))
		print ("temps de calcul:", time.time() - startTime)
		print ("=------------------------------=")
     
	n=bestNoeud
	path = []
	while n!=None :
		path.append(n)
		n = n.pere
	return path[::-1] # extended slice notation to reverse list


def astar_col(p, occupied=[], verbose=False,stepwise=False):
	"""
	application de l'algorithme a-star sur un probleme donné, en prenant en compte
	les cases occupées par les agents à un instant donné
	"""
        
	startTime = time.time()

	nodeInit = Noeud(p.init,0,0,None)
	frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

	reserve = {}        
	bestNoeud = nodeInit
    
	while frontiere != [] and not p.estBut(bestNoeud.etat):              
		(min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
		if p.immatriculation(bestNoeud.etat) not in reserve:            
			reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
			nouveauxNoeuds = bestNoeud.expand(p)
			for n in nouveauxNoeuds:
				if n.etat not in occupied:
                    f = n.g+p.h_value(n.etat,p.but) #Cout du noeud + distManhattan
					heapq.heappush(frontiere, (f,n))
				else:
					occupied[occupied.index(n.etat)] = 0

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
		stop_stepwise=""
		if stepwise==True:
			stop_stepwise = input("Press Enter to continue (s to stop)...")
			print ("best", min_f, "\n", bestNoeud)
			print ("Frontière: \n", frontiere)
			print ("Réserve:", reserve)
			if stop_stepwise=="s":
				stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
	if verbose:
		bestNoeud.trace(p)          
		print ("=------------------------------=")
		print ("Nombre de noeuds explorés", len(reserve))
		c=0
		for (f,n) in frontiere:
			if p.immatriculation(n.etat) not in reserve:
				c+=1
		print ("Nombre de noeuds de la frontière", c)
		print ("Nombre de noeuds en mémoire:", c + len(reserve))
		print ("temps de calcul:", time.time() - startTime)
		print ("=------------------------------=")
     
	n=bestNoeud
	path = []
	while n!=None :
		path.append(n)
		n = n.pere
	return path[::-1] # extended slice notation to reverse list


def coopAstar(p, t, allies=[], objectifs=[], occupied=[], verbose=False,stepwise=False):
	"""
	application de l'algorithme a-star sur un probleme donné, en prenant en compte
	les cases occupées par les agents de l'autre équipe à un instant donné ainsi que
	les chemins empruntés par les alliés.
	"""
        
	startTime = time.time()

	nodeInit = Noeud(p.init,t,0,None)
	frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

	reserve = {}        
	bestNoeud = nodeInit

	while frontiere != [] and not p.estBut(bestNoeud.etat):              
		(min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
		if p.immatriculation(bestNoeud.etat) not in reserve:            
			reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
			nouveauxNoeuds = bestNoeud.expand(p)
			for n in nouveauxNoeuds:
            	# vaut True si le nouveau noeud n'est dans aucun des chemins pris
            	# par les alliés
				free = True
				for i in range(len(allies)):
					if n.time >= len(allies[i]):
						continue
					for j in range(len(allies[i])):
						# si la case est occupée par un alliée au même moment, on ne 
 						# la considère pas
						if n.etat == allies[i][j].etat and n.time == allies[i][j].time and n.etat != objectifs[i]:
							free = False
							break
						# on ne considère pas non plus un échange de cases
						if allies[i][bestNoeud.time].etat == n.etat and allies[i][n.time].etat == bestNoeud.etat:
							free = False
							break  
					if not free:
						break
				if n.etat not in occupied and free:
					f = n.g+p.h_value(n.etat,p.but)
					heapq.heappush(frontiere, (f,n))
				# si on passe sur une case occupée, elle ne le sera normalement plus
				# à l'itération suivante
				elif n.etat in occupied:
					occupied[occupied.index(n.etat)] = 0

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
		stop_stepwise=""
		if stepwise==True:
			stop_stepwise = input("Press Enter to continue (s to stop)...")
			print ("best", min_f, "\n", bestNoeud)
			print ("Frontière: \n", frontiere)
			print ("Réserve:", reserve)
			if stop_stepwise=="s":
				stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
	if verbose:
		bestNoeud.trace(p)          
		print ("=------------------------------=")
		print ("Nombre de noeuds explorés", len(reserve))
		c=0
		for (f,n) in frontiere:
			if p.immatriculation(n.etat) not in reserve:
				c+=1
		print ("Nombre de noeuds de la frontière", c)
		print ("Nombre de noeuds en mémoire:", c + len(reserve))
		print ("temps de calcul:", time.time() - startTime)
		print ("=------------------------------=")
     
	n=bestNoeud
	path = []
	while n!=None :
		path.append(n)
		n = n.pere
	return path[::-1] # extended slice notation to reverse list


