#!/usr/bin/env python3
"""
Cálculo dos Modos de Vibração do Robô (Sistema Multicorpos)
Baseado na rigidez dos controladores de junta e inércia dos componentes.
"""

import numpy as np

print("=== Análise Modal do Robô Completo ===")
print("Considerando rigidez definida pelos ganhos P dos controladores.\n")

# ==========================================
# 1. PARÂMETROS DO SISTEMA (Do SDF)
# ==========================================

# --- Ganhos Proporcionais (Rigidez K) ---
# Estes atuam como "molas" torcionais nas juntas
# Unidade: N.m/rad (SDF usa gains adimensionais ou N.m/rad dependendo do plugin,
# mas assumindo coerência física padrão do Gazebo para JointPositionController)
K_azimuth = 1000.0  
K_elevation = 4000.0

# --- Massas e Inércias (Simplificadas) ---
# Link Tower
m_tower = 20.0
# Izz da torre (rotação azimuth)
J_tower_z = 2.0 

# Link Arm + Dish + Cilindros (Conjunto móvel na elevação)
# Arm
m_arm = 25.0
# Dish (Prato)
m_dish = 145.5
# Tracker
m_tracker = 0.5
# Cilindros
m_cyl = 2.5 + 2.0 + 1.0 # (cylinder + cylinder_green + orange) = 5.5

m_total_elevation = m_arm + m_dish + m_tracker + m_cyl

# Estimativa de Inércia combinada para Elevação (Eixo Y local)
# Precisamos transportar as inércias para o eixo da junta (Teorema dos eixos paralelos J = Icm + md^2)

# Distância aproximada dos CMs ao eixo de rotação (Elevation Joint)
d_arm = 1.0      # Chute: braço de 2m, CM no meio
d_dish = 0.5     # Prato está "atrás" ou "em cima" da junta
d_tracker = 2.5  # Tracker está longe (na ponta)

# J_elevation_total (Estimativa grosseira mas útil)
# J = J_arm + (m_arm * d_arm^2) + J_dish + (m_dish * d_dish^2) ...
J_arm_y = 8.0 + (m_arm * 1.0**2) 
J_dish_y = 83.0 + (m_dish * 0.1**2) # Prato tem inércia própria grande + massa * distancia pequena
J_tracker_y = (m_tracker * 2.5**2)

J_elevation_total = J_arm_y + J_dish_y + J_tracker_y

# Para Azimuth, a inércia é tudo isso girando em torno do eixo Z vertical
# Se o braço estiver esticado, a inércia é máxima.
d_elevation_cm_to_azimuth_axis = 0.5 # Distância horizontal média
J_azimuth_total = J_tower_z + J_elevation_total # Simplificação: Izz total

print(f"--- Parâmetros Estimados ---")
print(f"Massa Móvel (Elevação): {m_total_elevation:.2f} kg")
print(f"Inércia Total Estimada (Azimuth): {J_azimuth_total:.2f} kg.m²")
print(f"Inércia Total Estimada (Elevação): {J_elevation_total:.2f} kg.m²")
print(f"Rigidez Azimuth (Kp): {K_azimuth}")
print(f"Rigidez Elevation (Kp): {K_elevation}")

# ==========================================
# 2. CÁLCULO DAS FREQUÊNCIAS NATURAIS
# ==========================================
# Sistema desacoplado (simplificação): wn = sqrt(K / J)
# f = wn / (2*pi)

# AZIMUTH
wn_az = np.sqrt(K_azimuth / J_azimuth_total)
f_az = wn_az / (2 * np.pi)

# ELEVATION
wn_el = np.sqrt(K_elevation / J_elevation_total)
f_el = wn_el / (2 * np.pi)

print(f"\n--- Resultados Preliminares (Modos de Junta) ---")
print(f"1. Modo Azimuth (Giro da Base):")
print(f"   Frequência Natural: {f_az:.4f} Hz")
print(f"   Período: {1.0/f_az:.4f} s")

print(f"\n2. Modo Elevation (Balanço do Braço):")
print(f"   Frequência Natural: {f_el:.4f} Hz")
print(f"   Período: {1.0/f_el:.4f} s")

print(f"\n--- Análise ---")
if f_el < 1.0:
    print("ALERTA CRÍTICO: Frequência de elevação muito baixa (< 1Hz).")
    print("O robô vai se comportar de forma lenta e oscilatória.")
    print("Sugestão: Aumentar Kp da junta de elevação drasticamente.")
    required_kp = J_elevation_total * (2 * np.pi * 2.0)**2 # Para ter 2Hz
    print(f"Para ter pelo menos 2Hz na elevação, Kp deveria ser aprox: {required_kp:.0f}")

elif f_el < 5.0:
    print("Atenção: Frequência baixa. O controle pode parecer 'mole'.")
else:
    print("Rigidez parece adequada para movimentos normais.")
