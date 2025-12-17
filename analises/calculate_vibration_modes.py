#!/usr/bin/env python3
"""
Cálculo Estimado dos Modos de Vibração do Prato Parabólico
Modelo Simplificado: Placa Circular
"""

import numpy as np

# ==========================================
# PROPRIEDADES DO MATERIAL (Fibra de Vidro)
# ==========================================
E = 30e9       # Módulo de Young (Pa) - Aprox 30 GPa para Fibra/Resina
rho = 1900     # Densidade (kg/m^3)
nu = 0.3       # Coeficiente de Poisson

# ==========================================
# GEOMETRIA
# ==========================================
R = 1.5        # Raio (m) - Diâmetro de 3m
h = 0.01       # Espessura (m) - 1cm

print(f"=== Análise de Vibração (Modelo Placa Circular) ===")
print(f"Material: Fibra de Vidro")
print(f"Módulo de Young (E): {E/1e9:.1f} GPa")
print(f"Densidade: {rho} kg/m³")
print(f"Raio (R): {R} m")
print(f"Espessura (h): {h*100} cm")

# ==========================================
# CÁLCULO
# ==========================================
# Rigidez à flexão da placa (D)
# D = (E * h^3) / (12 * (1 - nu^2))
D = (E * h**3) / (12 * (1 - nu**2))

print(f"\nRigidez à flexão (D): {D:.2f} N.m")

# Frequência Natural (f_ij)
# f = (lambda_ij^2 / (2 * pi * R^2)) * sqrt(D / (rho * h))
# Onde lambda_ij são constantes adimensionais que dependem das condições de contorno.

# CASO 1: CENTRO ENGASTADO (Fixado no braço), BORDA LIVRE
# Modos de vibração (n=diâmetros nodais, s=círculos nodais)
# Valores lambda² aproximados para placa engastada no centro:
modes_clamped = {
    "Modo 1 (Guarda-chuva/Simbólico)": 3.75, 
    "Modo 2 (1 Diâmetro nodal)": 20.91,
    "Modo 3 (2 Diâmetros nodais)": 59.8,
}

print(f"\n--- Frequências Naturais Estimadas (Centro Engastado) ---")
term = np.sqrt(D / (rho * h)) / (2 * np.pi * R**2)

for mode_name, lambda_sq in modes_clamped.items():
    freq = lambda_sq * term
    print(f"{mode_name}: {freq:.2f} Hz")

print(f"\nNOTA: Estes valores são para uma placa plana.")
print(f"Como sua geometria é parabólica (concha), a curvatura AUMENTA a rigidez.")
print(f"Portanto, as frequências reais serão MAIORES que estas.")

# Fator de correção grosseiro para conchas rasas (apenas estimativa)
curvature_factor = 1.5 # Chute conservador para concha rasa
print(f"\n--- Estimativa com Correção de Curvatura (Fator ~{curvature_factor}x) ---")
print(f"Modo Fundamental Estimado: {3.75 * term * curvature_factor:.2f} Hz")
