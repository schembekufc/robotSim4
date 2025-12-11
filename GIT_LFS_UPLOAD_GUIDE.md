# 🚀 GUIA FINAL - Upload com Git LFS

**Data:** 11/12/2025 - 17:33  
**Arquivo:** 2_Torre.dae completo (123 MB) ✅

---

## ✅ Situação Atual

**Arquivo restaurado:**
- ✅ `models/catia/2_Torre.dae` = **123 MB** (arquivo completo)
- ✅ SDF já configurado para usar este arquivo
- ✅ Todos os caminhos relativos

**Problema:**
- ❌ 123 MB excede limite do GitHub (100 MB)

**Solução:**
- ✅ Usar **Git LFS** (Large File Storage)

---

## 📋 Passo a Passo - Git LFS

### **1. Instalar Git LFS**

```bash
sudo apt install git-lfs
```

Digite sua senha quando solicitado.

---

### **2. Inicializar Git LFS**

```bash
cd /home/lhmt-jhoni/Gazebo/robotSim4
git lfs install
```

Deve mostrar: `Git LFS initialized.`

---

### **3. Rastrear Arquivos Grandes**

```bash
# Rastrear o arquivo da torre (123 MB)
git lfs track "models/catia/2_Torre.dae"

# Rastrear o prato parabólico (18 MB)
git lfs track "formas/parabolic_dish.stl"
```

Isso cria um arquivo `.gitattributes`

---

### **4. Adicionar .gitattributes ao Git**

```bash
git add .gitattributes
```

---

### **5. Adicionar Todos os Arquivos**

```bash
git add .
```

---

### **6. Verificar o Que Será Enviado**

```bash
# Ver arquivos LFS
git lfs ls-files

# Ver status
git status
```

Deve mostrar `2_Torre.dae` e `parabolic_dish.stl` como arquivos LFS.

---

### **7. Fazer Commit**

```bash
git commit -m "feat: Projeto completo v2.0.0 com Git LFS

- Nomenclatura padronizada (Opção 3 - Híbrida)
- Arquivos 3D organizados em models/catia/
- Caminhos relativos no SDF
- Git LFS para arquivos grandes (2_Torre.dae 123 MB)
- Documentação completa

Componentes:
- 5 links renomeados (link_base, link_tower, link_arm, etc.)
- 5 joints renomeadas (joint_azimuth, joint_elevation, etc.)
- 6 sensores padronizados
- 4 scripts Python atualizados
- 11 documentos criados

BREAKING CHANGE: Tópicos de controle renomeados
- joint1 → joint_azimuth
- joint2 → joint_elevation"
```

---

### **8. Fazer Push para o GitHub**

```bash
git push origin main
```

**Observação:** O upload pode demorar alguns minutos devido ao tamanho dos arquivos.

---

## 📊 O Que o Git LFS Faz

**Arquivos Normais (< 50 MB):**
- Enviados diretamente para o repositório Git

**Arquivos LFS (> 50 MB):**
- `2_Torre.dae` (123 MB) → Armazenado no LFS
- `parabolic_dish.stl` (18 MB) → Armazenado no LFS
- Git guarda apenas um **ponteiro** pequeno
- Arquivos reais ficam no servidor LFS do GitHub

**Vantagem:**
- ✅ Repositório Git fica leve
- ✅ Clone rápido
- ✅ Arquivos grandes baixados sob demanda

---

## 💰 Limites do Git LFS (Gratuito)

| Item | Limite Gratuito |
|------|-----------------|
| **Armazenamento** | 1 GB |
| **Bandwidth/mês** | 1 GB |

**Seu caso:**
- `2_Torre.dae` = 123 MB
- `parabolic_dish.stl` = 18 MB
- **Total LFS** = ~141 MB ✅ (dentro do limite!)

---

## 🆘 Se Não Quiser Usar Git LFS

### **Alternativa: GitHub Releases**

1. Fazer upload do código sem `2_Torre.dae`
2. Criar um Release no GitHub
3. Anexar `2_Torre.dae` no Release (até 2 GB)
4. Usuários baixam separadamente

**Desvantagem:** Não funciona "out of the box"

---

## ✅ Checklist Final

Execute os comandos na ordem:

```bash
# 1. Instalar Git LFS
sudo apt install git-lfs

# 2. Inicializar
git lfs install

# 3. Rastrear arquivos grandes
git lfs track "models/catia/2_Torre.dae"
git lfs track "formas/parabolic_dish.stl"

# 4. Adicionar .gitattributes
git add .gitattributes

# 5. Adicionar tudo
git add .

# 6. Verificar
git lfs ls-files
git status

# 7. Commit
git commit -m "feat: Projeto completo v2.0.0 com Git LFS"

# 8. Push
git push origin main
```

---

## 📝 Arquivos que Serão Enviados

**Via Git Normal:**
- ✅ Código Python (~200 KB)
- ✅ Documentação (~500 KB)
- ✅ SDF (~30 KB)
- ✅ Modelos pequenos (~4 MB)

**Via Git LFS:**
- 🔵 `models/catia/2_Torre.dae` (123 MB)
- 🔵 `formas/parabolic_dish.stl` (18 MB)

**Ignorados (não enviados):**
- ❌ `2_Torre_original.dae` (123 MB - duplicado)
- ❌ `*.backup` (arquivos de backup)

---

## 🎯 Está Tudo Pronto!

**Próxima ação:** Execute os comandos acima! 🚀

**Tempo estimado:** 5-10 minutos (incluindo upload)

---

**Boa sorte com o upload!** 🎉
