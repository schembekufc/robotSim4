#!/usr/bin/env python3
"""
Cálculo Modos de Vibração Estrutural - Material: AÇO
Modelo Simplificado: Vigas em Balanço (Cantilever Beam) para os Links
"""

import numpy as np

# ==========================================
# PROPRIEDADES DO AÇO (Estrutural ASTM A36)
# ==========================================
E_steel = 200e9   # Módulo de Young (200 GPa)
rho_steel = 7850  # Densidade (kg/m^3) - Bem mais pesado que fibra!

print(f"=== Análise de Vibração ESTRUTURAL (Material: AÇO) ===")
print(f"Módulo de Young (E): {E_steel/1e9} GPa")
print(f"Densidade: {rho_steel} kg/m³")

# ==========================================
# 1. ANÁLISE DO BRAÇO (Viga Tubo Quadrado/Redondo)
# ==========================================
# Vamos assumir que o braço ("link_arm" ou a torre) seja um tubo de aço.
# Dimensões hipotéticas para uma estrutura desse porte (Baseadas no visual)
L_arm = 2.0       # Comprimento (m)
# Tubo quadrado 100x100mm com parede 5mm
b = 0.1          
h = 0.1
t = 0.005

# Área da seção transversal
Area_section = (b*h) - ((b-2*t)*(h-2*t))
# Momento de Inércia de Área (I_area) para tubo quadrado: (bh^3 - b'h'^3)/12
I_area = ( (b*h**3) - ((b-2*t)*(h-2*t)**3) ) / 12

mass_per_length = Area_section * rho_steel
total_mass_beam = mass_per_length * L_arm

print(f"\n--- Componente: Braço Principal (Tubo Aço 100x100x5mm) ---")
print(f"Comprimento: {L_arm} m")
print(f"Massa estimada da viga: {total_mass_beam:.2f} kg")
print(f"Momento de Inércia de Área (I): {I_area:.2e} m^4")

# MODO 1: Viga em Balanço (Engastada-Livre)
# wn = (beta^2) * sqrt(EI / (rho * A * L^4))
# Para o 1º modo, beta^2 = 3.516
beta_sq = 3.516
wn_beam = beta_sq * np.sqrt( (E_steel * I_area) / (mass_per_length * L_arm**4) )
f_beam = wn_beam / (2 * np.pi)

print(f"-> Frequência Natural (Viga sozinha): {f_beam:.2f} Hz")

# Mas espere! O braço segura o PRATO na ponta (Massa Concentrada).
# Isso reduz MUITO a frequência.
# Modelo: Viga sem massa com massa na ponta (Mola k = 3EI/L^3) + Massa M
M_tip = 150.0 # Prato + Tracker + Suportes
k_eq = (3 * E_steel * I_area) / (L_arm**3) # Rigidez equivalente da viga na ponta
wn_loaded = np.sqrt(k_eq / M_tip)
f_loaded = wn_loaded / (2 * np.pi)

print(f"-> Rigidez Flexural Eq. na ponta: {k_eq/1000:.1f} kN/m")
print(f"-> Frequência Natural (COM Prato de {M_tip}kg na ponta): {f_loaded:.2f} Hz")


# ==========================================
# 2. ANÁLISE DO PRATO PARABÓLICO (Se fosse de Aço)
# ==========================================
# Se o prato fosse feito de chapa de aço fina (ex: 2mm) em vez de fibra(10mm).
h_dish_steel = 0.002 # 2mm espessura
R_dish = 1.5
nu_steel = 0.3

# Rigidez à flexão da placa (D)
D_steel = (E_steel * h_dish_steel**3) / (12 * (1 - nu_steel**2))

# Frequência (Placa engastada centro)
# Modo 1 (Guarda-chuva): lambda^2 = 3.75 (aprox)
# f = (lambda^2 / 2pi*R^2) * sqrt(D/rho*h)
term_steel = np.sqrt(D_steel / (rho_steel * h_dish_steel)) / (2 * np.pi * R_dish**2)
f_dish_steel = 3.75 * term_steel * 1.5 # Fator curvatura

print(f"\n--- Componente: Prato Parabólico (Chapa Aço 2mm) ---")
print(f"-> Frequência Natural Estimada: {f_dish_steel:.2f} Hz")
