#!/usr/bin/env python3

import sys
import random
from collections import Counter
import itertools
import numpy as np

entrada = [1, 1, 1, 1]


BarajaMus = [1,1,1,1,1,1,1,1,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,10,10,10,10,11,11,11,11,12,12,12,12,12,12,12,12]

def valor_carta(carta):
    if carta < 10:
        return carta
    else:
        return 10

def barajar(Baraja):
    return random.shuffle(Baraja)


def mano(Baraja):
    barajar(Baraja)
    mano = [Baraja[0],Baraja[1],Baraja[2],Baraja[3]]
    return mano

manos_posibles = list(itertools.combinations(BarajaMus,4))

def manos_distintas_mus(Baraja):
    manos_distintas_segun_mus = []
    for mano in manos_posibles:
        mano = sorted(mano)
        if mano not in manos_distintas_segun_mus:
            manos_distintas_segun_mus.append(mano)
    return manos_distintas_segun_mus
        

def baraja_sin_mano(Baraja, mano):
    nueva_baraja = Baraja.copy()
    for x in mano:
        nueva_baraja.remove(x)
    return nueva_baraja
        
def manos_posibles_restantes(Baraja, mano):
    return list(itertools.combinations(baraja_sin_mano(Baraja, mano),4))

def num_manos_posibles_restantes(Baraja, mano):
    return len(manos_posibles_restantes(Baraja, mano))




def ganar_grande(mano1, mano2):
    gana_grande = 0
    mano1 = sorted(mano1, reverse=True)
    mano2 = sorted(mano2, reverse=True)
    if mano1 == mano2:
        gana_grande += 1
    else:
        for j in [0,1,2,3]:
            if mano1[j] > mano2[j]:
                gana_grande += 1
                return gana_grande
            elif mano1[j] < mano2[j]:
                break
        return gana_grande
    return gana_grande

def ganar_chica(mano1, mano2):
    gana_chica = 0
    mano1 = sorted(mano1)
    mano2 = sorted(mano2)
    
    if mano1 == mano2:
        gana_chica += 1
    else:
        for j in [0,1,2,3]:
            if valor_carta(mano1[j]) < valor_carta(mano2[j]):
                gana_chica += 1
                return gana_chica
            elif valor_carta(mano1[j]) > valor_carta(mano2[j]):
                return gana_chica
    return gana_chica

def clasificar_par(mano):
    conteo = Counter(mano)
    repetidos = {num: veces for num, veces in conteo.items() if veces > 1}
    frecuencias = list(repetidos.values())
    codigo = 0
    output = []
    if 4 in frecuencias:
        codigo = 3
    elif len(frecuencias) == 2:
        codigo = 3 
    elif 3 in frecuencias:
        codigo = 2
    elif 2 in frecuencias:
        codigo = 1
    else:
        codigo = 0
    return [codigo, sorted(repetidos.keys(), reverse=True)]

def tener_par(Baraja, mano):
    num_manos_con_par = 0
    manos_con_par = []
    for m in manos_posibles_restantes(Baraja, mano):
        if clasificar_par(m)[0] != 0:
            num_manos_con_par += 1
            manos_con_par.append(m)
    return [num_manos_con_par, manos_con_par]


def ganar_pares(mano1, mano2):
    gana_pares = 0
    mano1 = sorted(mano1, reverse=True)
    mano2 = sorted(mano2, reverse=True)
    if clasificar_par(mano1)[0] > clasificar_par(mano2)[0]:
        gana_pares += 1
        return gana_pares
    elif clasificar_par(mano1)[0] < clasificar_par(mano2)[0]:
        return gana_pares
    elif clasificar_par(mano1)[0] == clasificar_par(mano2)[0] and clasificar_par(mano1)[0] != 0:
        if len(clasificar_par(mano1)[1]) == 2 and len(clasificar_par(mano2)[1]) == 2:
            duples1 = sorted(clasificar_par(mano1)[1], reverse=True)
            duples2 = sorted(clasificar_par(mano2)[1], reverse=True)
            if duples1[0] > duples2[0]:
                gana_pares += 1
                return gana_pares
            elif duples1[0] < duples2[0]:
                return gana_pares
            elif duples1[0] == duples2[0]:
                if duples1[1] >= duples2[1]:
                    gana_pares += 1
                    return gana_pares
                elif duples1[1] < duples2[1]:
                    return gana_pares
        
        if clasificar_par(mano1)[1][0] > clasificar_par(mano2)[1][0]:
            if len(clasificar_par(mano1)[1]) > len(clasificar_par(mano2)[1]):
                return gana_pares
            if len(clasificar_par(mano1)[1]) < len(clasificar_par(mano2)[1]):
                gana_pares += 1
                return gana_pares
            else:
                gana_pares += 1
                return gana_pares
        elif clasificar_par(mano1)[1][0] < clasificar_par(mano1)[1][0]:
            return gana_pares
        elif clasificar_par(mano1)[1][0] == clasificar_par(mano2)[1][0]:
            gana_pares += 1
            return gana_pares
        return gana_pares
    
def tener_juego(Baraja, mano):
    num_manos_con_juego = 0
    manos_con_juego = []
    for m in manos_posibles_restantes(Baraja, mano):
        suma = sum(valor_carta(carta) for carta in m)
        if suma > 30:
            num_manos_con_juego += 1
            manos_con_juego.append(m)
    return [num_manos_con_juego, manos_con_juego]
        
        
def ganar_juego(mano1, mano2):
    gana_juego = 0
    suma1 = sum(valor_carta(carta) for carta in mano1)
    suma2 = sum(valor_carta(carta) for carta in mano2)
    if suma1 > 30 and suma2 > 30:
        if suma1 > 32 and suma2 > 32:
            if suma1 >= suma2:
                gana_juego += 1
                return gana_juego
            else:
                return gana_juego
            return gana_juego
        elif suma1 < 33 and suma2 > 32:
            gana_juego += 1
            return gana_juego
        elif suma1 < 33 and suma2 < 33:
            if suma1 <= suma2:
                gana_juego += 1
                return gana_juego
            else:
                return gana_juego
        return gana_juego
    
def tener_punto(Baraja, mano):
    num_manos_con_punto = 0
    manos_con_punto = []
    for m in manos_posibles_restantes(Baraja, mano):
        suma = sum(valor_carta(carta) for carta in m)
        if suma < 31:
            num_manos_con_punto += 1
            manos_con_punto.append(m)
    return [num_manos_con_punto, manos_con_punto]

    
def ganar_punto(mano1, mano2):
    gana_punto = 0
    suma1 = sum(valor_carta(carta) for carta in mano1)
    suma2 = sum(valor_carta(carta) for carta in mano2)
    if suma1 < 31 and suma2 < 31:
        if suma1 >= suma2:
            gana_punto += 1
            return gana_punto
        else:
            return gana_punto
    return gana_punto



def probabilidades_mus(Baraja, mano):
    prob_ganar_grande = 0
    prob_ganar_chica = 0
    prob_ganar_pares = 0
    prob_ganar_juego = 0
    prob_ganar_punto = 0
    manos_posibles = manos_posibles_restantes(Baraja,mano)
    for mano_oponente in manos_posibles:
        if ganar_grande(mano, mano_oponente) == 1:
            prob_ganar_grande += 1
        if ganar_chica(mano, mano_oponente) == 1:
            prob_ganar_chica += 1
    for mano_oponente in tener_par(Baraja, mano)[1]:
        if ganar_pares(mano, mano_oponente) == 1:
            prob_ganar_pares += 1
    for mano_oponente in tener_juego(Baraja, mano)[1]:
        if ganar_juego(mano, mano_oponente) == 1:
            prob_ganar_juego += 1
    for mano_oponente in tener_punto(Baraja, mano)[1]:
        if ganar_punto(mano, mano_oponente) == 1:
            prob_ganar_punto += 1
    
    return [float(prob_ganar_grande/num_manos_posibles_restantes(Baraja, mano))*100,
            float(prob_ganar_chica/num_manos_posibles_restantes(Baraja, mano))*100,
            float(prob_ganar_pares/tener_par(Baraja, mano)[0])*100,
            float(prob_ganar_juego/tener_juego(Baraja, mano)[0])*100,
            float(prob_ganar_punto/tener_punto(Baraja, mano)[0])*100]
    
conteo = Counter(entrada)
repetidos = {num: veces for num, veces in conteo.items() if veces > 1}
frecuencias = list(repetidos.values())

probabilidades_mus(BarajaMus, entrada)


distribucion_grande = []
distribucion_chica = []
distribucion_pares = []
distribucion_juego = []
distribucion_punto = []


manos = manos_distintas_mus(BarajaMus)
for mano in manos:
    probabilidades = probabilidades_mus(BarajaMus, mano)
    distribucion_grande.append(probabilidades[0])
    distribucion_chica.append(probabilidades[1])
    distribucion_pares.append(probabilidades[2])
    distribucion_juego.append(probabilidades[3])
    distribucion_punto.append(probabilidades[4])
percentiles_grande = np.percentile(distribucion_grande, np.arange(0, 100, 0.1))
percentiles_chica = np.percentile(distribucion_chica, np.arange(0, 100, 0.1))
percentiles_pares = np.percentile(distribucion_pares, np.arange(0, 100, 0.1))
percentiles_juego = np.percentile(distribucion_juego, np.arange(0, 100, 0.1))
percentiles_punto = np.percentile(distribucion_punto, np.arange(0, 100, 0.1))
for p, val in zip(np.arange(0, 100.1, 0.1), percentiles_grande):
    print(val)
for p, val in zip(np.arange(0, 100.1, 0.1), percentiles_chica):
    print(val)
for p, val in zip(np.arange(0, 100.1, 0.1), percentiles_pares):
    print(val)
for p, val in zip(np.arange(0, 100.1, 0.1), percentiles_juego):
    print(val)
for p, val in zip(np.arange(0, 100.1, 0.1), percentiles_punto):
    print(val)