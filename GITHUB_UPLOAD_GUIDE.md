# 📤 Guia de Upload para GitHub - Robot Sim 4

**Data:** 11/12/2025  
**Versão:** 2.0.0 (Pós-Padronização)

---

## ✅ Preparação Completa

Seu projeto está **pronto para upload** no GitHub! Aqui está o guia completo:

---

## 🧹 Limpeza Recomendada (OPCIONAL)

### Opção 1: Manter os Backups Localmente (Recomendado)

Os arquivos `.backup` já estão no `.gitignore`, então **não serão enviados** para o GitHub automaticamente.

```bash
# Não precisa fazer nada! Os backups ficarão apenas no seu computador
```

### Opção 2: Remover os Backups

Se você já testou e está tudo funcionando, pode remover os backups:

```bash
# ⚠️ CUIDADO: Isso remove os backups permanentemente!
cd /home/lhmt-jhoni/Gazebo/robotSim4
rm *.backup
```

---

## 📋 Checklist Pré-Upload

Antes de fazer upload, verifique:

- [x] `.gitignore` atualizado (já feito!)
- [ ] Código testado e funcionando
- [ ] README.md atualizado com novos nomes
- [ ] Documentação completa
- [ ] Sem arquivos sensíveis (senhas, tokens, etc.)

---

## 🚀 Opções de Upload

### **Opção A: Repositório Já Existe no GitHub**

Se você já tem um repositório no GitHub:

```bash
cd /home/lhmt-jhoni/Gazebo/robotSim4

# 1. Verificar status
git status

# 2. Adicionar todos os arquivos modificados
git add .

# 3. Fazer commit
git commit -m "feat: Padronização de nomenclatura v2.0.0

- Implementada nomenclatura híbrida padronizada
- Renomeados 5 links principais (link1→link_base, etc.)
- Renomeadas 5 joints (joint1→joint_azimuth, etc.)
- Renomeados 6 sensores
- Atualizados 4 scripts Python
- Criada documentação completa

BREAKING CHANGE: Tópicos de controle renomeados
- joint1 → joint_azimuth
- joint2 → joint_elevation

Documentação:
- NOMENCLATURA_SUGERIDA.md
- TABELA_NOMENCLATURA.md
- HIERARQUIA_ROBO.md
- CHANGELOG_NOMENCLATURA.md
- IMPLEMENTACAO_COMPLETA.md"

# 4. Enviar para o GitHub
git push origin main
# ou
git push origin master
```

---

### **Opção B: Criar Novo Repositório no GitHub**

Se ainda não tem repositório:

#### **Passo 1: Criar Repositório no GitHub**

1. Acesse: https://github.com/new
2. Nome do repositório: `robotSim4` (ou outro nome)
3. Descrição: "Sistema de rastreamento solar com Gazebo - Placa rastreadora e prato parabólico"
4. Visibilidade: **Público** ou **Privado** (sua escolha)
5. **NÃO** marque "Add a README file" (já temos um)
6. **NÃO** marque "Add .gitignore" (já temos um)
7. Clique em **"Create repository"**

#### **Passo 2: Conectar e Enviar**

```bash
cd /home/lhmt-jhoni/Gazebo/robotSim4

# 1. Inicializar git (se ainda não foi feito)
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Fazer primeiro commit
git commit -m "feat: Versão 2.0.0 com nomenclatura padronizada

Sistema de rastreamento solar com Gazebo incluindo:
- Modelo SDF com 5 links e 5 joints
- 6 sensores de luz (4 quadrantes + tubo solar + foco)
- Prato parabólico refletor
- 5 GUIs de controle e monitoramento
- Documentação completa

Nomenclatura padronizada (v2.0.0):
- Links: link_base, link_tower, link_arm, link_tracker_plate, link_dish
- Joints: joint_azimuth, joint_elevation
- Sensores: sensor_quadrant_1-4, sensor_sun_tube, sensor_focus_camera"

# 4. Adicionar repositório remoto
# Substitua SEU_USUARIO pelo seu nome de usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/robotSim4.git

# 5. Renomear branch para main (se necessário)
git branch -M main

# 6. Enviar para o GitHub
git push -u origin main
```

---

## 📝 Atualizar README.md (Recomendado)

Antes de fazer upload, atualize o README.md com os novos nomes:

```bash
# Editar README.md para refletir novos nomes
nano README.md
# ou
code README.md
```

**Mudanças sugeridas no README.md:**
- Atualizar referências de `joint1` → `joint_azimuth`
- Atualizar referências de `joint2` → `joint_elevation`
- Adicionar seção sobre a padronização v2.0.0
- Mencionar a documentação nova

---

## 🔍 Verificar Antes de Enviar

```bash
# Ver quais arquivos serão enviados
git status

# Ver diferenças
git diff

# Ver arquivos ignorados (não serão enviados)
git status --ignored
```

**Arquivos que NÃO serão enviados (no .gitignore):**
- ✅ `*.backup` (13 arquivos)
- ✅ `__pycache__/`
- ✅ `*.pyc`
- ✅ `.vscode/`
- ✅ `*.log`

---

## 📊 Tamanho do Repositório

```bash
# Ver tamanho total (sem backups)
du -sh --exclude="*.backup" .
```

**Estimativa:** ~10-15 MB (sem os backups)

---

## 🏷️ Criar Tag de Versão (Opcional)

Para marcar esta versão importante:

```bash
# Criar tag
git tag -a v2.0.0 -m "Versão 2.0.0 - Nomenclatura Padronizada

- Implementada nomenclatura híbrida
- Breaking changes nos nomes de links e joints
- Documentação completa adicionada"

# Enviar tag para o GitHub
git push origin v2.0.0
```

---

## 📄 Estrutura que Será Enviada

```
robotSim4/
├── 📄 01_three_link_with_tracker_plate.sdf  # Modelo principal (ATUALIZADO)
├── 🐍 02_unified_control_gui.py             # GUI unificada (ATUALIZADO)
├── 🐍 03_light_sensor_gui.py                # GUI sensores (ATUALIZADO)
├── 🐍 04_sun_control_gui.py                 # GUI sol
├── 🐍 05_balls_control_gui.py               # GUI esferas
├── 🐍 tracker_auto_control_gui.py           # Controle auto (ATUALIZADO)
├── 🐍 tracker_auto_control.py               # Controle auto CLI (ATUALIZADO)
├── 🐍 plate_light_gui_images.py             # GUI imagens
├── 📁 formas/                               # Malhas 3D
│   ├── Espelho.dae
│   └── parabolic_dish.stl
├── 📄 lens_mask.obj                         # Máscara lente
├── 🐍 generate_parabolic_dish.py            # Utilitário
├── 🐍 calculate_dish_inertia.py             # Utilitário
├── 🐍 generate_lens_mask.py                 # Utilitário
├── 🐍 fix_mesh.py                           # Utilitário
├── 🐍 fix_mesh_trimesh.py                   # Utilitário
├── 📖 README.md                             # Documentação principal
├── 📖 NOMENCLATURA_SUGERIDA.md              # Análise nomenclatura (NOVO)
├── 📖 TABELA_NOMENCLATURA.md                # Tabelas comparativas (NOVO)
├── 📖 HIERARQUIA_ROBO.md                    # Diagrama estrutural (NOVO)
├── 📖 RESUMO_EXECUTIVO.md                   # Plano implementação (NOVO)
├── 📖 CHANGELOG_NOMENCLATURA.md             # Registro mudanças (NOVO)
├── 📖 IMPLEMENTACAO_COMPLETA.md             # Guia testes (NOVO)
├── 📖 GITHUB_UPLOAD_GUIDE.md                # Este arquivo (NOVO)
├── 📖 CHANGELOG_SPHERES.md                  # Changelog esferas
├── 📖 FIXES_SPHERES.md                      # Fixes esferas
├── 📖 GITHUB_SETUP.md                       # Setup GitHub
├── 📖 GIT_CHEATSHEET.md                     # Git cheatsheet
├── 📖 GIT_LOCAL_GUIDE.md                    # Git local
├── 📖 OSCILLATORY_CONTROL_GUIDE.md          # Guia controle
├── 📖 PRATO_PARABOLICO_GUIA.md              # Guia prato
└── 📄 .gitignore                            # Arquivos ignorados (ATUALIZADO)
```

**Arquivos NÃO enviados (ignorados):**
- ❌ `*.backup` (13 arquivos)
- ❌ `__pycache__/`
- ❌ `*.pyc`
- ❌ `.vscode/`

---

## ⚠️ Avisos Importantes

### 1. **Breaking Changes**

Esta versão contém mudanças incompatíveis! Se alguém clonar o repositório:
- ✅ Funcionará perfeitamente (tudo atualizado junto)
- ⚠️ Não será compatível com versões antigas

### 2. **Documentação**

Considere adicionar no README.md:
```markdown
## ⚠️ Versão 2.0.0 - Breaking Changes

Esta versão implementa nomenclatura padronizada. 
Veja `CHANGELOG_NOMENCLATURA.md` para detalhes.

**Principais mudanças:**
- `joint1` → `joint_azimuth`
- `joint2` → `joint_elevation`
- Links renomeados para nomes descritivos
```

### 3. **Licença**

Considere adicionar um arquivo `LICENSE`:
```bash
# Exemplo: MIT License
touch LICENSE
```

---

## 🎯 Comando Rápido (Tudo de Uma Vez)

Se você já tem repositório configurado:

```bash
cd /home/lhmt-jhoni/Gazebo/robotSim4
git add .
git commit -m "feat: Padronização de nomenclatura v2.0.0"
git push origin main
```

---

## 🆘 Problemas Comuns

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/robotSim4.git
```

### Erro: "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

### Erro: "Permission denied (publickey)"
```bash
# Use HTTPS em vez de SSH
git remote set-url origin https://github.com/SEU_USUARIO/robotSim4.git
```

---

## ✅ Checklist Final

Antes de fazer upload:

- [ ] Código testado e funcionando
- [ ] `.gitignore` atualizado (já feito! ✅)
- [ ] README.md atualizado com novos nomes
- [ ] Sem arquivos sensíveis (senhas, tokens)
- [ ] Documentação completa (já feito! ✅)
- [ ] Commit message descritivo
- [ ] Tag de versão criada (opcional)

---

## 🎊 Pronto para Upload!

Seu projeto está **100% pronto** para ser enviado ao GitHub!

**Recomendação:**
1. ✅ Teste a simulação uma última vez
2. ✅ Atualize o README.md (opcional)
3. ✅ Faça o commit e push
4. ✅ Compartilhe o link! 🚀

---

**Boa sorte com o upload!** 🎉

Se tiver dúvidas, consulte:
- `GITHUB_SETUP.md` - Configuração do GitHub
- `GIT_CHEATSHEET.md` - Comandos Git úteis
- `GIT_LOCAL_GUIDE.md` - Guia Git local
