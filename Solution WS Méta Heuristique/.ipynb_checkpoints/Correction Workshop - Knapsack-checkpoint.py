"""
Created on Tue May  7 11:41:59 2019

@author: bcohen
"""

import random
import numpy as np

# nombre d'objets disponibles pour le sac
global nb_objets

# dictionnaires associant un numero d'objet a sa taille et sa valeur
global taille_objets
global valeur_objets

# capacite du sac en taille totale
global capacite

# nombre d'objets disponibles pour le sac (pour ne pas avoir a recalculer la
# taille des dictionnaires)
global nb_objets


def taille_contenu(sac):
    """
    Cette fonction renvoie la somme des tailles des objets dans le sac
    """
    # recherche des objets presents dans le sac
    objets = [i for i, val in enumerate(sac) if val]
    
    # somme de la valeurs des objets presents
    return sum(taille_objets[o] for o in objets)

def nb_objets_contenu(sac):
    """
    Cette fonction renvoie le nombre d'objets dans le sac
    """
    return sum(sac) # SOLUTION

def valeur_contenu(sac):
    """
    Cette fonction renvoie la somme des valeurs des objets dans le sac
    """
    # recherche des objets presents dans le sac
    objets = [i for i, val in enumerate(sac) if val]
    
    # somme de la valeurs des objets presents
    return sum(valeur_objets[o] for o in objets)

def random_solution():
    """
    Cette fonction genere une solution aleatoire valide, i.e. un sac dont le
	contenu n'excede pas sa capacite
    """
    sac=list(np.random.choice(a=[False, True], size=nb_objets))

    while (taille_contenu(sac)>capacite):
        objets = [i for i, val in enumerate(sac) if val]
        objet_supprime=random.choice(objets)
        sac[objet_supprime]=False 

    return sac


def voisinage(sac):
    """
    Cette fonction est un generateur de tous les voisins valides d'une solution
    """
    for i in range(len(sac)):
        # cas du retrait d'un objet deja present dans le sac
        if (sac[i]):
            if nb_objets_contenu(sac)>0:
                sac_voisin=list(sac)
                sac_voisin[i]=False
                yield(sac_voisin)
        # cas de l'ajout d'un objet dans le sac
        else:
            taille=taille_contenu(sac)
            if (taille+taille_objets[i]<=capacite):
                sac_voisin=list(sac)
                sac_voisin[i]=True
                yield(sac_voisin)


def hill_climbing(element_initial):
    """
    1. On part d'un element de notre ensemble de recherche qu'on declare
	   element courant
    2. On considere le voisinage de l'element courant et on choisit le meilleur
	   d'entre eux comme nouvel element courant
    3. On boucle jusqu'a convergence
    """

    element_courant = element_initial
    nouveau=True
    nb_iter=0 # uniquement utilise pour l'affichage
    
    while (nouveau):
        nb_iter+=1
        
        # On parcours tous les voisins de la solution courante pour garder
		# la meilleure
        meilleur=element_courant
        valeur_meilleur=valeur_contenu(meilleur)

        for voisin in voisinage(element_courant):
            valeur_voisin=valeur_contenu(voisin)
            if valeur_voisin>valeur_meilleur:
                valeur_meilleur=valeur_voisin
                meilleur=voisin

        nouveau=(meilleur!=element_courant)
        element_courant=meilleur

    return element_courant

def recherche_tabou(element_initial, taille_tabou, iter_max):
    """
    1. On part d'un element de notre ensemble de recherche qu'on declare
	   element courant
    2. On considere le voisinage de l'element courant et on choisit le meilleur
	   d'entre eux comme nouvel element courant, parmi ceux absents de la liste
	   tabou, et on l'ajoute a la liste tabou
    3. On boucle jusqu'a condition de sortie.
    """
    nb_iter = 0
    
    liste_tabou = list()

    # variables solutions pour la recherche du voisin optimal non tabou
    element_courant = element_initial
    meilleur=element_courant
    meilleur_global=element_courant

    # variables valeurs pour la recherche du voisin optimal non tabou
    valeur_meilleur=0
    valeur_meilleur_global=0
    
    while (nb_iter<iter_max):
        nb_iter += 1
        
        valeur_meilleur=0
        
        # on parcours tous les voisins de la solution courante
        for voisin in voisinage(element_courant):
            valeur_voisin=valeur_contenu(voisin)
                     
            if (valeur_voisin>valeur_meilleur and
			    all(voisin != tabou for tabou in liste_tabou)):
                    # meilleure solution non taboue trouvee
                    valeur_meilleur=valeur_voisin
                    meilleur=voisin
        
        # on met a jour la meilleure solution rencontree depuis le debut
        if valeur_meilleur>valeur_meilleur_global:
            meilleur_global=meilleur
            valeur_meilleur_global=valeur_meilleur

        # on passe au meilleur voisin non tabou trouve
        element_courant=meilleur
        
        # on met a jour la liste tabou
        liste_tabou.append(element_courant)
        if len(liste_tabou)>=taille_tabou:
            liste_tabou.pop(0)
	
    return hill_climbing(meilleur_global)

def random_objets(taille_max, val_max):
    """
    Cette fonction genere des objets de taille et de valeur aleatoire
    renvoie un tuple de 2 listes : taille et valeur
    """
    taille_objets={k: random.randint(1,taille_max) for k in range(nb_objets)}
    valeur_objets={k: random.randint(1,val_max) for k in range(nb_objets)}

    return taille_objets,valeur_objets

nb_objets=100
capacite=20

random.seed(a=3)
taille_objets, valeur_objets=random_objets(10, 10)

valeur_max=0
for _ in range (200):
    sac=random_solution()
    sol_courante=recherche_tabou(sac, taille_tabou=5, iter_max=30)
    val=valeur_contenu(sol_courante)
    if (val>valeur_max):
        valeur_max=val
        sol=sol_courante

print("valeur finale = "+str(valeur_contenu(sol)))
print ("objets selectionnes :")
print([i for i, x in enumerate(sol) if x])