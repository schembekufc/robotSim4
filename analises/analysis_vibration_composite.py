#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Análise Modal Analítica: Refletor Híbrido (Compósito + Alumínio)
Autor: [Seu Nome/Joint System]
Contexto: Dissertação de Mestrado - Simulação Robótica
Método: Quociente de Rayleigh (Energético)

Descrição:
    Este script calcula a frequência natural fundamental de vibração de um refletor
    parabólico composto por uma pele de fibra de vidro reforçada por uma estrutura
    traseira de varetas de alumínio.
    Assume-se o modo de vibração 'Guarda-chuva' (Umbrella Mode) como o fundamental
    para estruturas apoiadas centralmente.
"""

import numpy as np
import math

class StructuralAnalysis:
    def __init__(self):
        # 1. DEFINIÇÃO DE MATERIAIS
        # -------------------------
        # Fibra de Vidro (Pele do Prato)
        self.E_glass = 30e9       # Pa (30 GPa)
        self.rho_glass = 1900     # kg/m^3
        self.nu_glass = 0.28      # Coeficiente de Poisson
        
        # Alumínio 6061-T6 (Estrutura de Reforço)
        self.E_al = 68.9e9        # Pa (68.9 GPa)
        self.rho_al = 2700        # kg/m^3
        
        # 2. DEFINIÇÃO GEOMÉTRICA
        # -----------------------
        self.R = 1.5              # Raio externo (m) -> Diâmetro 3.0m
        self.h_skin = 0.01        # Espessura da pele de fibra (10 mm)
        
        # Estrutura de Reforço (Costelas Radiais)
        self.num_ribs = 8         # Quantidade de varetas
        self.rib_width = 0.05     # Largura da vareta (5 cm)
        self.rib_height = 0.10    # Altura da vareta (10 cm) - Perfil "em pé" para rigidez
        self.L_rib = self.R       # Comprimento da vareta (do centro à borda)

    def calculate_properties(self):
        """Calcula propriedades derivadas (Áreas, Inércias, Massas)"""
        
        # --- Componente 1: Pele (Prato) ---
        # Massa aproximada (considerando curvatura rasa, Area ~ pi*R^2)
        # Sendo conservador com a curvatura: Area_sup = pi*R^2 * Fator
        fator_curvatura_area = 1.05 
        self.area_skin = np.pi * self.R**2 * fator_curvatura_area
        self.vol_skin = self.area_skin * self.h_skin
        self.mass_skin = self.vol_skin * self.rho_glass
        
        # Rigidez à flexão da placa (D)
        self.D_plate = (self.E_glass * self.h_skin**3) / (12 * (1 - self.nu_glass**2))

        # --- Componente 2: Reforços (Ribs) ---
        self.area_section_rib = self.rib_width * self.rib_height
        self.vol_one_rib = self.area_section_rib * self.L_rib
        self.mass_one_rib = self.vol_one_rib * self.rho_al
        self.mass_ribs_total = self.mass_one_rib * self.num_ribs
        
        # Momento de Inércia de Área da vareta (bh^3 / 12)
        self.I_rib = (self.rib_width * self.rib_height**3) / 12

        self.mass_total = self.mass_skin + self.mass_ribs_total
        
        return {
            "Massa Pele": self.mass_skin,
            "Massa Reforços": self.mass_ribs_total,
            "Massa Total": self.mass_total,
            "Inercia Vareta": self.I_rib,
            "Rigidez Placa D": self.D_plate
        }

    def run_rayleigh_analysis(self):
        """
        Aplica o Método de Rayleigh: omega^2 = U_max / T*_max
        Assumindo função de forma w(r) = (r/R)^2 (Deflexão parabólica radial)
        """
        print("Executando Método de Rayleigh...")
        
        # 1. Energia Potencial Elástica (Strain Energy) - U
        # U = U_plate + U_ribs
        
        # Para placa circular deformando w = c * r^2:
        # Curvatura k = d2w/dr2 = 2c.
        # Simplificação de Energia de Placa com deformação simétrica:
        # U_plate proportional to D * Integral((laplacian w)^2) dA
        # Laplacian(c*r^2) em coordenadas polares = 4c
        # U_plate = (1/2) * D * Integral((4c)^2) * 2*pi*r dr  [de 0 a R]
        # Integral(r dr) de 0 a R = R^2 / 2
        # U_plate = (1/2) * D * 16c^2 * 2*pi * (R^2/2) = 8 * pi * D * R^2 * c^2
        # Fator de rigidez equivalente K_plate tal que U = 1/2 * K_plate * w_tip^2
        # w_tip = c * R^2  => c = w_tip / R^2
        # U_plate = 8 * pi * D * R^2 * (w_tip^2 / R^4) = (8 * pi * D / R^2) * w_tip^2
        # Logo: 1/2 * K_plate = 8 * pi * D / R^2
        self.K_plate_eq = 16 * np.pi * self.D_plate / (self.R**2)
        
        # Para as Varetas (Beams):
        # U_beam = (1/2) * EI * Integral((d2w/dr2)^2) dr
        # w'' = 2c. (w''^2) = 4c^2
        # Integral de 0 a L de 4c^2 dr = 4c^2 * L
        # U_beam = 0.5 * EI * 4c^2 * L = 2 * EI * L * c^2
        # Substituindo c = w_tip / L^2 (sendo L=R): 
        # U_beam = 2 * EI * L * (w_tip^2 / L^4) = (2 * EI / L^3) * w_tip^2
        self.K_rib_eq = (4 * self.E_al * self.I_rib) / (self.L_rib**3) # Stiffness per rib
        
        self.K_total = self.K_plate_eq + (self.num_ribs * self.K_rib_eq)
        
        # 2. Energia Cinética Equivalente (Kinetic Energy) - T
        # T = 1/2 * omega^2 * Integral(rho * w^2) dV
        # w = w_tip * (r/R)^2
        
        # Massa Equivalente da Pele (Plate):
        # Integral (rho * h * (w_tip * r^2/R^2)^2 ) * 2*pi*r dr
        # = rho * h * w_tip^2 / R^4 * 2*pi * Integral(r^5) dr
        # Integral(r^5) = R^6 / 6
        # M_eq_plate = rho * h * 2*pi * (R^6/6) / R^4 = rho * h * pi * R^2 / 3
        # Ou seja, M_eq_plate = Mass_plate / 3
        self.M_eq_plate = self.mass_skin / 3.0
        
        # Massa Equivalente das Varetas:
        # Integral (rho_al * A_rib * (w_tip * r^2/L^2)^2) dr
        # = rho * A * w_tip^2 / L^4 * Integral(r^4) dr
        # Integral(r^4) = L^5 / 5
        # M_eq_rib = rho * A * L^5/5 / L^4 = (rho * A * L) / 5
        # M_eq_rib = Mass_rib / 5
        self.M_eq_ribs = (self.mass_one_rib * self.num_ribs) / 5.0
        
        self.M_total_eq = self.M_eq_plate + self.M_eq_ribs
        
        # 3. Frequência Natural
        # omega_n = sqrt(K_total / M_total_eq)
        self.omega_n = math.sqrt(self.K_total / self.M_total_eq)
        self.freq_hz = self.omega_n / (2 * math.pi)
        
        return self.freq_hz

if __name__ == "__main__":
    sim = StructuralAnalysis()
    props = sim.calculate_properties()
    freq = sim.run_rayleigh_analysis()
    
    # Gerando Relatório Formatado
    print("-" * 60)
    print("RELATÓRIO DE CÁLCULO DE VIBRAÇÃO")
    print("-" * 60)
    print(f"Raio do Refletor: {sim.R} m")
    print(f"Material Pele: Fibra de Vidro (h={sim.h_skin*1000} mm)")
    print(f"Material Reforço: {sim.num_ribs}x Varetas Alumínio ({sim.rib_width*100}x{sim.rib_height*100} cm)")
    print("-" * 60)
    print(f"Massa Pele: {props['Massa Pele']:.2f} kg")
    print(f"Massa Reforços: {props['Massa Reforços']:.2f} kg")
    print(f"Massa Total: {props['Massa Total']:.2f} kg")
    print("-" * 60)
    print(f"Rigidez Eq. Pele (K_plate): {sim.K_plate_eq:.2f} N/m")
    print(f"Rigidez Eq. Reforços (K_ribs_tot): {sim.num_ribs * sim.K_rib_eq:.2f} N/m")
    print(f"Rigidez Total (K_eq): {sim.K_total:.2f} N/m")
    print("-" * 60)
    print(f"Massa Eq. Dinâmica (M_eq): {sim.M_total_eq:.2f} kg")
    print("-" * 60)
    print(f"RESULTADO FINAL:")
    print(f"Frequência Natural Fundamental: {freq:.4f} Hz")
    print("-" * 60)
