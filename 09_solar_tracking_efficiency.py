import numpy as np
import matplotlib.pyplot as plt

def simulacao_concentrador_dissertacao(
    diametro_prato=3.0,      # Diâmetro do espelho (m)
    distancia_focal=1.8,     # Distância focal (m)
    raio_receptor=0.02,      # 2 cm (Diâmetro 4cm)
    diametro_spot_alvo=0.02, # 2 cm (Spot menor -> Margem de segurança)
    erro_rastreamento_graus=0.0,
    num_raios=50000
):
    """
    Simula o concentrador com os parâmetros exatos da dissertação.
    Spot de 2cm dentro de um Receptor de 4cm (Margem de segurança).
    """
    # 1. Ângulo de divergência para Spot de 2cm
    # Isso simula o tamanho físico do sol + erros do espelho focando em 2cm
    theta_max = np.arctan((diametro_spot_alvo / 2) / distancia_focal)
    
    # 2. Geração de raios no prato
    r = (diametro_prato / 2) * np.sqrt(np.random.rand(num_raios))
    theta = 2 * np.pi * np.random.rand(num_raios)
    x_inc = r * np.cos(theta)
    y_inc = r * np.sin(theta)
    
    # 3. Vetor Solar com Erro
    erro_rad = np.radians(erro_rastreamento_graus)
    vec_base = np.array([np.sin(erro_rad), 0, -np.cos(erro_rad)])
    
    # Adicionando divergência (spot size) ao redor do vetor base
    theta_div = theta_max * np.sqrt(np.random.rand(num_raios))
    phi_div = 2 * np.pi * np.random.rand(num_raios)
    du = theta_div * np.cos(phi_div)
    dv = theta_div * np.sin(phi_div)
    
    raios = np.zeros((num_raios, 3))
    raios[:, 0] = vec_base[0] + du
    raios[:, 1] = vec_base[1] + dv
    raios[:, 2] = vec_base[2]
    raios = raios / np.linalg.norm(raios, axis=1)[:, np.newaxis]
    
    # 4. Reflexão
    z_surf = (x_inc**2 + y_inc**2) / (4 * distancia_focal)
    nx = -x_inc / (2 * distancia_focal)
    ny = -y_inc / (2 * distancia_focal)
    nz = np.ones(num_raios)
    normais = np.vstack((nx, ny, nz)).T
    normais = normais / np.linalg.norm(normais, axis=1)[:, np.newaxis]
    
    dot = np.sum(raios * normais, axis=1)
    raios_ref = raios - 2 * dot[:, np.newaxis] * normais
    
    # 5. Interseção com plano focal
    t = (distancia_focal - z_surf) / raios_ref[:, 2]
    x_foco = x_inc + t * raios_ref[:, 0]
    y_foco = y_inc + t * raios_ref[:, 1]
    
    # 6. Eficiência
    dist = np.sqrt(x_foco**2 + y_foco**2)
    acertos = np.sum(dist <= raio_receptor)
    return (acertos / num_raios) * 100

# --- EXECUTANDO A SIMULAÇÃO ---
# Intervalo de 0 a 2 graus com passo de 0.05
erros = np.arange(0, 2.05, 0.05)
eficiencias = []

print("Simulando curva da dissertação (0 a 2°)...")
for e in erros:
    eff = simulacao_concentrador_dissertacao(erro_rastreamento_graus=e)
    eficiencias.append(eff)

# --- PLOTAGEM DO GRÁFICO ---
plt.figure(figsize=(10, 6))

# Plot principal
plt.plot(erros, eficiencias, 'o-', color='darkred', linewidth=2, label='Eficiência Simulada')

# Linhas de Referência (Eficiência = 100% - Perda)
# Perda 5% -> Efic 95%
plt.axhline(95, color='green', linestyle='--', alpha=0.8, label='Perda 5% (Efic. 95%)')
# Perda 10% -> Efic 90%
plt.axhline(90, color='orange', linestyle='--', alpha=0.8, label='Perda 10% (Efic. 90%)')
# Perda 50% -> Efic 50%
plt.axhline(50, color='blue', linestyle='--', alpha=0.8, label='Perda 50% (Efic. 50%)')
# Perda 70% -> Efic 30%
plt.axhline(30, color='purple', linestyle='--', alpha=0.8, label='Perda 70% (Efic. 30%)')

plt.title('Queda de Eficiência por Erro de Rastreamento')
plt.xlabel('Erro de Rastreamento (Graus)')
plt.ylabel('Eficiência (%)')
plt.ylim(-2, 105) # Ajuste para mostrar o zero claramente
plt.xlim(0, 1.2)
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()
