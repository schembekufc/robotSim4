import numpy as np
import matplotlib.pyplot as plt

def simulacao_spot_data(
    diametro_prato=3.0,
    distancia_focal=1.8,
    raio_receptor=0.02,      # 2 cm (Diâmetro 4cm)
    diametro_spot_alvo=0.02, # 2 cm (Spot menor -> Margem de segurança)
    erro_rastreamento_graus=0.0,
    num_raios=10000          # Quantidade de raios para a simulação
):
    """
    Simula o traçado de raios (Ray Tracing) para um concentrador parabólico,
    retornando as coordenadas x, y onde cada raio atinge o plano focal.
    """
    # 1. Ângulo de divergência (Tamanho do Spot Solar)
    theta_max = np.arctan((diametro_spot_alvo / 2) / distancia_focal)

    # 2. Geração de pontos aleatórios na superfície do prato
    r = (diametro_prato / 2) * np.sqrt(np.random.rand(num_raios))
    phi = 2 * np.pi * np.random.rand(num_raios)
    x_inc = r * np.cos(phi)
    y_inc = r * np.sin(phi)

    # 3. Vetor Solar (Direção Base + Divergência)
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
    # Normalização
    raios = raios / np.linalg.norm(raios, axis=1)[:, np.newaxis]

    # 4. Reflexão na Superfície Parabólica
    z_surf = (x_inc**2 + y_inc**2) / (4 * distancia_focal)
    nx = -x_inc / (2 * distancia_focal)
    ny = -y_inc / (2 * distancia_focal)
    nz = np.ones(num_raios)
    normais = np.vstack((nx, ny, nz)).T
    normais = normais / np.linalg.norm(normais, axis=1)[:, np.newaxis]

    # Lei da Reflexão Vetorial: R = I - 2(N.I)N
    dot = np.sum(raios * normais, axis=1)
    raios_ref = raios - 2 * dot[:, np.newaxis] * normais

    # 5. Interseção com o Plano Focal
    t = (distancia_focal - z_surf) / raios_ref[:, 2]
    x_foco = x_inc + t * raios_ref[:, 0]
    y_foco = y_inc + t * raios_ref[:, 1]

    return x_foco, y_foco, raio_receptor

def plot_grade_6_situacoes():
    """
    Gera uma grade de 6 gráficos (Spot Diagrams) mostrando a evolução da perda
    de eficiência com o aumento do erro de rastreamento.
    """
    # Cenários representativos de erro (em graus)
    erros = [0.0, 0.1, 0.2, 0.5, 0.8, 1.0]

    # Aumentar o tamanho da fonte padrão para todos os elementos do plot
    plt.rcParams.update({'font.size': 12})

    # Configuração da figura (2 linhas x 3 colunas)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12)) # Aumentei o figsize para acomodar fontes maiores
    axes_flat = axes.flatten()

    print("Gerando grade de simulações...")

    for i, ax in enumerate(axes_flat):
        erro = erros[i]

        # Executa a simulação para este erro
        x, y, r_rec = simulacao_spot_data(erro_rastreamento_graus=erro)

        # Calcula Eficiência (Quem entrou vs Quem saiu)
        dist = np.sqrt(x**2 + y**2)
        mask_dentro = dist <= r_rec
        eficiencia = (np.sum(mask_dentro) / len(x)) * 100

        # --- DESENHO DO GRÁFICO ---

        # 1. Borda do Receptor (Círculo Tracejado)
        circulo = plt.Circle((0, 0), r_rec, color='black', fill=False,
                             linewidth=2, linestyle='--', label='Receptor')
        ax.add_artist(circulo)

        # 2. Raios Perdidos (Vermelho) - Plotados primeiro para ficarem no fundo
        ax.scatter(x[~mask_dentro], y[~mask_dentro], s=2, c='red', alpha=0.4, label='Perda')

        # 3. Raios Capturados (Dourado)
        ax.scatter(x[mask_dentro], y[mask_dentro], s=2, c='gold', alpha=0.4, label='Capturado')

        # Configurações de Eixos e Zoom
        ax.set_aspect('equal')
        limite_zoom = 0.05 # 5cm de raio de visão
        ax.set_xlim(-limite_zoom, limite_zoom)
        ax.set_ylim(-limite_zoom, limite_zoom)

        # Título Informativo
        ax.set_title(f"Erro: {erro:.1f}° | Efic.: {eficiencia:.1f}%", fontsize=16, fontweight='bold') # Aumentei a fonte do título

        # Remove números dos eixos para limpar o visual
        ax.set_xticks([])
        ax.set_yticks([])

        # --- LEGENDA OTIMIZADA ---
        # Adiciona legenda apenas no primeiro gráfico (índice 0)
        if i == 0:
            # markerscale=6 aumenta as bolinhas na legenda para ficarem bem visíveis
            ax.legend(loc='upper left', markerscale=6, fontsize=15, framealpha=0.9, edgecolor='gray') # Aumentei a fonte da legenda

    plt.suptitle("Impacto do Erro de Rastreamento no Foco Solar (Spot Diagram)", fontsize=20, y=0.95) # Ajustei a posição
    plt.tight_layout()
    plt.subplots_adjust(top=0.88) # Adiciona margem superior para o suptitle não ser cortado
    plt.show()
    print("Gráfico gerado com sucesso.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    plot_grade_6_situacoes()
