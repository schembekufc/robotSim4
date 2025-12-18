# Solução para Erros ODE: Trimesh-trimesh contact hash table bucket overflow

## 🔴 Problema
```
ODE Message 2: Trimesh-trimesh contact hash table bucket overflow - 
close contacts might not be culled in AddContactToNode() [collision_trimesh_trimesh.cpp:224]
```

Este erro ocorre quando **malhas triangulares (trimeshes) complexas** geram mais pontos de contato do que o ODE consegue processar eficientemente.

## 📍 Origem no Arquivo SDF

### 1. **Prato Parabólico (`link_dish`)**
- **Arquivo:** `formas/parabolic_dish.stl`
- **Linha:** 251-260 (collision)
- **Problema:** Mesh STL complexa usada para colisão

### 2. **Costelas (`link_ribs`)**
- **Arquivo:** `formas/costelas2.stl`
- **Linha:** 931-938 (collision)
- **Problema:** Mesh STL com muitos triângulos

## ✅ Soluções Possíveis

### **Opção 1: Simplificar Geometria de Colisão (RECOMENDADO)**

Substitua as meshes complexas por **primitivas geométricas** para colisão, mantendo as meshes apenas para visual:

#### Para o Prato Parabólico:
```xml
<!-- Visual mantém a mesh detalhada -->
<visual name="visual_dish_reflector">
  <geometry>
    <mesh>
      <uri>file://formas/parabolic_dish.stl</uri>
    </mesh>
  </geometry>
</visual>

<!-- Colisão usa cilindro simples -->
<collision name="collision_dish">
  <geometry>
    <cylinder>
      <radius>1.5</radius>     <!-- Raio do prato -->
      <length>0.5</length>      <!-- Profundidade aproximada -->
    </cylinder>
  </geometry>
</collision>
```

#### Para as Costelas:
```xml
<!-- Visual mantém a mesh detalhada -->
<visual name="visual_ribs">
  <geometry>
    <mesh>
      <uri>file://formas/costelas2.stl</uri>
    </mesh>
  </geometry>
</visual>

<!-- REMOVER a colisão se não for necessária -->
<!-- OU usar geometria simplificada -->
<collision name="collision_ribs">
  <geometry>
    <box>
      <size>3.0 0.1 0.3</size>  <!-- Aproximação de uma costela -->
    </box>
  </geometry>
</collision>
```

---

### **Opção 2: Desabilitar Colisão (se não for crítica)**

Se a colisão entre prato e costelas **não for necessária** para a simulação:

```xml
<link name="link_dish">
  <!-- Remover completamente o bloco <collision> -->
</link>

<link name="link_ribs">
  <!-- Remover completamente o bloco <collision> -->
</link>
```

---

### **Opção 3: Mudar Motor de Física para Bullet**

**Você já está usando Bullet!** (Linha 28 do SDF)

```xml
<physics name="physics_engine" type="bullet">
```

✅ **Bullet lida melhor com trimeshes** que o ODE. O erro pode estar vindo de algum componente interno ainda usando ODE.

Verifique se o Gazebo está realmente usando Bullet:
```bash
gz sim 01_three_link_with_tracker_plate.sdf --verbose
```

---

### **Opção 4: Ajustar Parâmetros de Contato ODE**

Se precisar manter as meshes, aumente os limites da tabela hash:

```xml
<physics name="physics_engine" type="bullet">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  
  <!-- Adicionar configurações de contato -->
  <ode>
    <collision detector="bullet">
      <max_contacts>20</max_contacts>  <!-- Padrão: 10 -->
    </collision>
  </ode>
</physics>
```

---

### **Opção 5: Simplificar Meshes no Blender/MeshLab**

Se precisar manter colisão com mesh, reduza o número de triângulos:

**No Blender:**
1. Abrir `parabolic_dish.stl` e `costelas2.stl`
2. Selecionar mesh → Modifier Properties
3. Adicionar **Decimate Modifier**
4. Ajustar **Ratio** para 0.3 (70% de redução)
5. Exportar como novo STL

**No MeshLab:**
```bash
meshlabserver -i parabolic_dish.stl -o parabolic_dish_simplified.stl -s simplify.mlx
```

---

## 🚀 Implementação Rápida (Recomendada)

### **1. Desabilitar colisão das costelas:**
```xml
<link name="link_ribs">
  <!-- Remover o bloco <collision> completamente -->
</link>
```

### **2. Simplificar colisão do prato:**
```xml
<link name="link_dish">
  <collision name="collision_dish">
    <geometry>
      <cylinder>
        <radius>1.5</radius>
        <length>0.5</length>
      </cylinder>
    </geometry>
  </collision>
</link>
```

---

## 🧪 Teste

Após implementar, execute:
```bash
gz sim 01_three_link_with_tracker_plate.sdf
```

Se os erros persistirem, verifique se há outras meshes complexas no modelo.

---

## 📌 Resumo

| Solução | Dificuldade | Eficácia |
|---------|------------|----------|
| Simplificar geometria de colisão | ⭐⭐ Fácil | ⭐⭐⭐⭐⭐ Alta |
| Desabilitar colisão | ⭐ Muito Fácil | ⭐⭐⭐⭐ Alta |
| Ajustar parâmetros ODE | ⭐⭐ Fácil | ⭐⭐ Baixa |
| Simplificar mesh | ⭐⭐⭐ Média | ⭐⭐⭐⭐ Alta |

**Recomendação:** Comece pela **Opção 1** (simplificar geometria de colisão).
