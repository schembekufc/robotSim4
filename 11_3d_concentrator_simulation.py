import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # Import necessário para projeção 3D

# ==========================================
# PARTE 1: SIMULAÇÃO E TABELA DE EFICIÊNCIA
# ==========================================
def simulacao_com_borda(
    diametro_prato=3.0,
    distancia_focal=1.8,
    raio_receptor=0.02,      # Raio 2cm (Diâmetro 4cm)
    diametro_spot_alvo=0.02, # Spot 2cm (Menor que receptor = 100% Eficiência inicial)
    erro_rastreamento_graus=0.0,
    num_raios=50000
):
    # Cálculo da divergência para o tamanho do spot
    theta_max = np.arctan((diametro_spot_alvo / 2) / distancia_focal)
    
    # Geração de raios
    r = (diametro_prato / 2) * np.sqrt(np.random.rand(num_raios))
    phi = 2 * np.pi * np.random.rand(num_raios)
    x_inc = r * np.cos(phi)
    y_inc = r * np.sin(phi)
    
    # Vetor Solar com Erro
    erro_rad = np.radians(erro_rastreamento_graus)
    vec_base = np.array([np.sin(erro_rad), 0, -np.cos(erro_rad)])
    
    theta_div = theta_max * np.sqrt(np.random.rand(num_raios))
    phi_div = 2 * np.pi * np.random.rand(num_raios)
    du = theta_div * np.cos(phi_div)
    dv = theta_div * np.sin(phi_div)
    
    raios = np.zeros((num_raios, 3))
    raios[:, 0] = vec_base[0] + du
    raios[:, 1] = vec_base[1] + dv
    raios[:, 2] = vec_base[2]
    raios = raios / np.linalg.norm(raios, axis=1)[:, np.newaxis]
    
    # Reflexão
    z_surf = (x_inc**2 + y_inc**2) / (4 * distancia_focal)
    nx = -x_inc / (2 * distancia_focal)
    ny = -y_inc / (2 * distancia_focal)
    nz = np.ones(num_raios)
    normais = np.vstack((nx, ny, nz)).T
    normais = normais / np.linalg.norm(normais, axis=1)[:, np.newaxis]
    
    dot = np.sum(raios * normais, axis=1)
    raios_ref = raios - 2 * dot[:, np.newaxis] * normais
    
    # Interseção
    t = (distancia_focal - z_surf) / raios_ref[:, 2]
    x_foco = x_inc + t * raios_ref[:, 0]
    y_foco = y_inc + t * raios_ref[:, 1]
    
    # Contagem
    dist = np.sqrt(x_foco**2 + y_foco**2)
    acertos = np.sum(dist <= raio_receptor)
    return (acertos / num_raios) * 100

# Gerar e Imprimir Tabela
print("Calculando eficiência...")
erros_tabela = np.linspace(0, 1.0, 11)
dados = []
for e in erros_tabela:
    eff = simulacao_com_borda(erro_rastreamento_graus=e)
    dados.append([e, eff])

print("\n--- Tabela de Resultados ---")
print(f"{'Erro (Graus)':<15} {'Eficiência (%)':<15}")
for row in dados:
    print(f"{row[0]:<15.2f} {row[1]:<15.2f}")
print("-" * 30)


# ==========================================
# PARTE 2: VISUALIZAÇÃO 3D DO PRATO
# ==========================================
def plot_concentrator_3d_grid(
    diametro_prato=3.0,
    distancia_focal=1.8,
    raio_receptor=0.02,
    diametro_spot_alvo=0.02,
    erros_para_plotar=[0.0, 0.4, 1.0], 
    num_raios_visuais=100
):
    print(f"\nGerando gráficos 3D para erros: {erros_para_plotar}...")
    fig = plt.figure(figsize=(18, 6))
    theta_max = np.arctan((diametro_spot_alvo / 2) / distancia_focal)

    for i, erro_graus in enumerate(erros_para_plotar):
        ax = fig.add_subplot(1, 3, i+1, projection='3d')

        # 1. Desenhar Superfície do Prato
        r_grid = np.linspace(0, diametro_prato/2, 30)
        phi_grid = np.linspace(0, 2*np.pi, 50)
        R, PHI = np.meshgrid(r_grid, phi_grid)
        X = R * np.cos(PHI)
        Y = R * np.sin(PHI)
        Z = (X**2 + Y**2) / (4 * distancia_focal)
        ax.plot_surface(X, Y, Z, alpha=0.2, color='cyan')

        # 2. Desenhar Receptor (Alvo)
        phi_rec = np.linspace(0, 2*np.pi, 30)
        x_rec = raio_receptor * np.cos(phi_rec)
        y_rec = raio_receptor * np.sin(phi_rec)
        z_rec = np.ones_like(x_rec) * distancia_focal
        ax.plot(x_rec, y_rec, z_rec, color='red', linewidth=3, label='Receptor')

        # 3. Traçar Raios (Ray Tracing Visual)
        for _ in range(num_raios_visuais):
            r = (diametro_prato / 2) * np.sqrt(np.random.rand())
            phi = 2 * np.pi * np.random.rand()
            x_i = r * np.cos(phi)
            y_i = r * np.sin(phi)
            z_i = (x_i**2 + y_i**2) / (4 * distancia_focal)

            # Vetor Solar
            erro_rad = np.radians(erro_graus)
            vec_sol = np.array([np.sin(erro_rad), 0, -np.cos(erro_rad)])
            
            # Divergência Visual
            th_div = theta_max * np.sqrt(np.random.rand())
            ph_div = 2 * np.pi * np.random.rand()
            vec_sol[0] += th_div * np.cos(ph_div)
            vec_sol[1] += th_div * np.sin(ph_div)
            vec_sol = vec_sol / np.linalg.norm(vec_sol)

            # Reflexão
            norm = np.array([-x_i/(2*distancia_focal), -y_i/(2*distancia_focal), 1])
            norm = norm / np.linalg.norm(norm)
            vec_ref = vec_sol - 2 * np.dot(vec_sol, norm) * norm
            
            # Interseção
            t = (distancia_focal - z_i) / vec_ref[2]
            x_f = x_i + t * vec_ref[0]
            y_f = y_i + t * vec_ref[1]
            
            # Checar se acertou (Cor verde) ou errou (Cor cinza)
            dist = np.sqrt(x_f**2 + y_f**2)
            cor = 'green' if dist <= raio_receptor else 'gray' 

            # Plotar linha do raio refletido
            ax.plot([x_i, x_f], [y_i, y_f], [z_i, distancia_focal], color=cor, alpha=0.5, linewidth=0.8)

        ax.set_title(f'Erro: {erro_graus}°')
        ax.set_xlabel('X')
        ax.set_zlim(0, distancia_focal+0.2)
        ax.view_init(elev=10, azim=45) # Ângulo de visão

    plt.tight_layout()
    plt.subplots_adjust(top=0.9) # Adiciona margem superior para não cortar títulos
    plt.show()

# Chamada da função para gerar o gráfico
plot_concentrator_3d_grid()
