#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Modal Analítica Completa: Robô Rastreador Solar
Contexto: Dissertação de Mestrado
Autor: [Seu Nome/Joint System]

Objetivo:
    Calcular frequências naturais dos principais componentes e do sistema global,
    considerando materiais distintos para cada subsistema:
    1. Estrutura do Robô (Torre/Braços): Aço Estrutural ASTM A36
    2. Refletor Parabólico: Compósito de Fibra de Vidro
    3. Reforço do Refletor: Costelas de Alumínio 6061-T6

Metodologia:
    - Método da Energia de Rayleigh (Sistemas Contínuos Simplificados)
    - Modelo de Vigas de Euler-Bernoulli com Massa Concentrada na Ponta
"""

import numpy as np
import math

# ==============================================================================
# CLASSE DE MATERIAIS
# ==============================================================================
class Material:
    def __init__(self, name, E, rho, nu):
        self.name = name
        self.E = E          # Young's Modulus (Pa)
        self.rho = rho      # Density (kg/m3)
        self.nu = nu        # Poisson's Ratio

# Definição dos Materiais do Projeto
STEEL_A36 = Material("Aço ASTM A36", 200e9, 7850, 0.26)
ALUMINUM_6061 = Material("Alumínio 6061-T6", 68.9e9, 2700, 0.33)
FIBERGLASS = Material("Fibra de Vidro/Epóxi", 30e9, 1900, 0.28)

# ==============================================================================
# ANALISADOR DO PRATO (FIBRA + COSTELAS ALUMÍNIO)
# ==============================================================================
class DishAnalyzer:
    def __init__(self, n_ribs=6):
        self.R = 1.5              # Raio 1.5m (Diam 3m)
        self.h_skin = 0.01        # 10mm espessura
        self.n_ribs = n_ribs      # 6 costelas
        
        # Dimensões da Costela (Alumínio)
        self.b_rib = 0.05         # 5cm largura
        self.h_rib = 0.10         # 10cm altura
        self.L_rib = 1.5          # Igual ao raio
        
    def analyze(self):
        """Retorna massa total e frequência natural do prato"""
        # 1. Massa da Pele (Fibra)
        # Área superficial aprox de paraboloide raso ~ 1.05 * pi * R^2
        area_skin = 1.05 * np.pi * self.R**2
        mass_skin = area_skin * self.h_skin * FIBERGLASS.rho
        
        # 2. Massa das Costelas (Alumínio)
        # ATUALIZADO: Massa real medida do arquivo CAD (costelas.stl)
        mass_ribs = 28.16  # kg (Volume 0.010431 m3 * 2700 kg/m3)
        
        total_mass = mass_skin + mass_ribs
        
        # 3. Rigidez e Frequência Fundamental (Método Rayleigh - Modo Guarda-Chuva)
        # Rigidez Placa
        D_plate = (FIBERGLASS.E * self.h_skin**3) / (12 * (1 - FIBERGLASS.nu**2))
        K_plate_eq = 16 * np.pi * D_plate / (self.R**2)
        
        # Rigidez Costelas
        # Inércia equivalente retrocalculada baseada na massa realista
        # Se 6 costelas pesam 28kg, cada uma pesa ~4.7kg.
        # Assumindo perfil tubular ou T otimizado.
        # Vamos manter uma inércia de área razoável para um perfil de 10cm de altura
        # I_rib estimado para um perfil T ou I leve de 100mm altura
        # I ~ 80 cm^4 = 80e-8 m^4 (Estimativa conservadora para perfil leve)
        I_rib = 80e-8 
        
        K_rib_eq = (4 * ALUMINUM_6061.E * I_rib) / (self.L_rib**3)
        
        K_total = K_plate_eq + (self.n_ribs * K_rib_eq)
        
        # Massa Efetiva (1/3 placa + 1/5 costelas para modo quártico)
        M_eq = (mass_skin / 3.0) + (mass_ribs / 5.0)
        
        omega = math.sqrt(K_total / M_eq)
        freq = omega / (2 * math.pi)
        
        return {
            "mass": total_mass,
            "freq": freq,
            "I_rib": I_rib,
            "mass_skin": mass_skin,
            "mass_ribs": mass_ribs
        }

# ==============================================================================
# ANALISADOR DO BRAÇO (AÇO - VIGA TUBO RETANGULAR)
# ==============================================================================
class ArmAnalyzer:
    def __init__(self, tip_mass):
        self.L = 2.0                # Comprimento 2m
        self.tip_mass = tip_mass    # Massa do prato na ponta
        
        # Perfil Tubo Retangular Aço
        self.b = 0.15   # 150mm largura
        self.h = 0.20   # 200mm altura
        self.t = 0.006  # 6mm parede
        
    def analyze(self):
        # Propriedades da Seção
        area_outer = self.b * self.h
        area_inner = (self.b - 2*self.t) * (self.h - 2*self.t)
        area = area_outer - area_inner
        
        I_y = (self.b * self.h**3 - (self.b - 2*self.t)*(self.h - 2*self.t)**3) / 12
        I_x = (self.h * self.b**3 - (self.h - 2*self.t)*(self.b - 2*self.t)**3) / 12
        
        # Usando I_y (menor inércia se for de pé? assumindo flexão vertical)
        # Vamos usar a inércia que resiste à gravidade (Eixo X da seção, flexão em torno de Y global)
        I_flex = I_y 
        
        beam_mass = area * self.L * STEEL_A36.rho
        
        # Frequência Beam Cantilever com Tip Mass
        # Método aproximação de Dunkerley ou Rayleigh
        # f = 1 / (2pi) * sqrt( 3EI / (L^3 * (M_tip + 0.24*M_beam)) )
        
        k_beam = (3 * STEEL_A36.E * I_flex) / (self.L**3)
        m_eff = self.tip_mass + (0.24 * beam_mass)
        
        omega = math.sqrt(k_beam / m_eff)
        freq = omega / (2 * math.pi)
        
        return {
            "freq": freq,
            "beam_mass": beam_mass,
            "stiffness_k": k_beam,
            "I_flex": I_flex
        }

# ==============================================================================
# ANALISADOR DA TORRE (AÇO - VIGA TUBO QUADRADO ROBUSTO)
# ==============================================================================
class TowerAnalyzer:
    def __init__(self, top_mass):
        self.H = 1.3                # Altura até a junta do braço
        self.top_mass = top_mass    # Massa do Braço + Prato
        
        # Perfil Torre (Mais larga para aguentar torção)
        self.side = 0.30  # 300mm
        self.t = 0.008    # 8mm parede
        
    def analyze(self):
        area = self.side**2 - (self.side - 2*self.t)**2
        I = (self.side**4 - (self.side - 2*self.t)**4) / 12
        
        tower_mass = area * self.H * STEEL_A36.rho
        
        # Modelo Cantilever com Massa no Topo (Pêndulo Invertido Elástico)
        k_tower = (3 * STEEL_A36.E * I) / (self.H**3)
        m_eff = self.top_mass + (0.24 * tower_mass)
        
        omega = math.sqrt(k_tower / m_eff)
        freq = omega / (2 * math.pi)
        
        return {
            "freq": freq,
            "tower_mass": tower_mass,
            "stiffness_k": k_tower
        }

# ==============================================================================
# EXECUÇÃO E RELATÓRIO
# ==============================================================================
if __name__ == "__main__":
    print("="*80)
    print("ANÁLISE MODAL COMPLETA - DISSERTAÇÃO ROBÔ SOLAR")
    print("="*80)
    
    # 1. PRATO
    dish = DishAnalyzer(n_ribs=6)
    res_dish = dish.analyze()
    print(f"\n[1] CONJUNTO DO REFLETOR (FIBRA + 6x ALUMÍNIO)")
    print(f"    - Massa Pele (Fibra):   {res_dish['mass_skin']:.2f} kg")
    print(f"    - Massa Ribs (Al):      {res_dish['mass_ribs']:.2f} kg")
    print(f"    - Massa Total Prato:    {res_dish['mass']:.2f} kg")
    print(f"    - Freq. Natural (Local):{res_dish['freq']:.2f} Hz  <-- Vibração 'de pele'")

    # 2. BRAÇO
    # O braço carrega o prato + tracker (estimado 5kg)
    load_on_arm = res_dish['mass'] + 5.0 
    arm = ArmAnalyzer(tip_mass=load_on_arm)
    res_arm = arm.analyze()
    print(f"\n[2] BRAÇO DE ELEVAÇÃO (AÇO)")
    print(f"    - Carga na Ponta:       {load_on_arm:.2f} kg")
    print(f"    - Massa do Braço:       {res_arm['beam_mass']:.2f} kg")
    print(f"    - Rigidez Flexural (K): {res_arm['stiffness_k']/1e3:.1f} kN/m")
    print(f"    - Freq. Natural (Braço):{res_arm['freq']:.2f} Hz   <-- Modo de 'Balanço vertical'")

    # 3. TORRE
    # A torre carrega Braço + Prato + Mecanismos (estimado 20kg juntas)
    load_on_tower = res_arm['beam_mass'] + load_on_arm + 20.0
    tower = TowerAnalyzer(top_mass=load_on_tower)
    res_tower = tower.analyze()
    print(f"\n[3] TORRE DA BASE (AÇO)")
    print(f"    - Carga no Topo:        {load_on_tower:.2f} kg")
    print(f"    - Massa da Torre:       {res_tower['tower_mass']:.2f} kg")
    print(f"    - Freq. Natural (Torre):{res_tower['freq']:.2f} Hz   <-- Modo de 'Pêndulo'")

    print("\n" + "="*80)
    print("CONCLUSÃO GERAL DOS MODOS")
    print(f"Modo 1 (Dominante - Torre oscilando): {res_tower['freq']:.2f} Hz")
    print(f"Modo 2 (Sub-dominante - Braço fletindo): {res_arm['freq']:.2f} Hz")
    print(f"Modo 3 (Local - Prato vibrando):      {res_dish['freq']:.2f} Hz")
    print("="*80)
