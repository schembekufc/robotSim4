# 🎓 Guia Prático: Git Local para Iniciantes

## 📍 Você está aqui

✅ Repositório Git inicializado  
✅ Primeiro commit feito (19 arquivos)  
🎯 **Agora**: Aprender a usar Git localmente antes de conectar ao GitHub

---

## 🔍 Comandos Essenciais para Explorar

### 1. Ver o Status do Repositório

```bash
git status
```

**O que mostra:**
- Arquivos modificados (em vermelho)
- Arquivos prontos para commit (em verde)
- Branch atual

**Quando usar:** Sempre que quiser saber o que mudou

---

### 2. Ver o Histórico de Commits

```bash
# Histórico completo
git log

# Histórico resumido (uma linha por commit)
git log --oneline

# Histórico com gráfico de branches
git log --oneline --graph --all

# Ver últimos 5 commits
git log --oneline -5
```

**O que mostra:**
- Hash do commit (código único)
- Autor e data
- Mensagem do commit

---

### 3. Ver Diferenças (O que mudou)

```bash
# Ver mudanças não salvas
git diff

# Ver mudanças em um arquivo específico
git diff plate_light_gui_images.py

# Ver mudanças entre commits
git diff 2ade870 HEAD
```

**O que mostra:**
- Linhas adicionadas (em verde, com +)
- Linhas removidas (em vermelho, com -)

---

## 🛠️ Fluxo de Trabalho Básico

### Cenário: Você vai modificar um arquivo

```bash
# 1. Ver status antes de começar
git status

# 2. Fazer suas modificações no código
# (edite os arquivos normalmente)

# 3. Ver o que mudou
git diff

# 4. Adicionar arquivos modificados
git add plate_light_gui_images.py    # Arquivo específico
# OU
git add .                             # Todos os arquivos

# 5. Ver status novamente (arquivos em verde = prontos)
git status

# 6. Fazer commit (salvar mudanças)
git commit -m "Add feature X to plate light GUI"

# 7. Ver histórico atualizado
git log --oneline
```

---

## 🌿 Trabalhando com Branches (Ramificações)

Branches permitem testar coisas sem afetar o código principal.

### Criar e Usar uma Branch

```bash
# Ver branches existentes
git branch

# Criar nova branch
git branch experimento

# Mudar para a nova branch
git checkout experimento
# OU (criar e mudar ao mesmo tempo)
git checkout -b experimento

# Fazer mudanças e commits normalmente
# ... edite arquivos ...
git add .
git commit -m "Testing new feature"

# Voltar para a branch principal
git checkout main

# Ver diferenças entre branches
git diff main experimento

# Mesclar mudanças da branch experimento para main
git checkout main
git merge experimento

# Deletar branch após mesclar
git branch -d experimento
```

---

## ⏪ Desfazendo Coisas

### Desfazer Mudanças Não Salvas

```bash
# Desfazer mudanças em um arquivo (antes de git add)
git checkout -- plate_light_gui_images.py

# Desfazer todas as mudanças não salvas
git checkout -- .
```

### Remover Arquivo do Staging (depois de git add)

```bash
# Tirar arquivo do "pronto para commit"
git reset plate_light_gui_images.py

# Tirar todos os arquivos
git reset
```

### Desfazer Último Commit (mantendo mudanças)

```bash
# Desfaz commit mas mantém as mudanças
git reset --soft HEAD~1

# Desfaz commit e tira do staging
git reset HEAD~1

# ⚠️ CUIDADO: Desfaz commit e APAGA mudanças
git reset --hard HEAD~1
```

### Adicionar Arquivo Esquecido no Último Commit

```bash
git add arquivo_esquecido.py
git commit --amend --no-edit
```

---

## 📊 Visualizando o Histórico

### Ver Mudanças em um Commit Específico

```bash
# Ver detalhes de um commit
git show 2ade870

# Ver apenas arquivos modificados
git show --name-only 2ade870

# Ver estatísticas
git show --stat 2ade870
```

### Ver Histórico de um Arquivo

```bash
# Ver todos os commits que modificaram o arquivo
git log plate_light_gui_images.py

# Ver mudanças linha por linha
git log -p plate_light_gui_images.py

# Ver quem modificou cada linha (blame)
git blame plate_light_gui_images.py
```

---

## 🎯 Exercícios Práticos

### Exercício 1: Fazer uma Pequena Mudança

1. Abra o arquivo `README.md`
2. Adicione seu nome na seção "Autor"
3. Salve o arquivo
4. Execute:
   ```bash
   git status
   git diff README.md
   git add README.md
   git commit -m "Update author name in README"
   git log --oneline
   ```

### Exercício 2: Criar uma Branch de Teste

1. Crie uma branch chamada `teste`:
   ```bash
   git checkout -b teste
   ```
2. Modifique qualquer arquivo
3. Faça um commit
4. Volte para `main`:
   ```bash
   git checkout main
   ```
5. Veja que suas mudanças não estão lá!
6. Mescle as mudanças:
   ```bash
   git merge teste
   ```

### Exercício 3: Explorar o Histórico

```bash
# Ver todos os commits
git log --oneline

# Ver mudanças do primeiro commit
git show 2ade870

# Ver arquivos no primeiro commit
git show --name-only 2ade870
```

---

## 🔍 Comandos de Inspeção Úteis

```bash
# Ver configuração do Git
git config --list

# Ver repositórios remotos (vazio por enquanto)
git remote -v

# Ver tamanho do repositório
du -sh .git

# Ver todos os arquivos rastreados
git ls-files

# Buscar no histórico de commits
git log --grep="GUI"

# Ver commits por autor
git log --author="Jhoni"
```

---

## 💡 Dicas Importantes

1. **Commits pequenos e frequentes** são melhores que commits gigantes
2. **Mensagens claras** ajudam você a entender o que fez depois
3. **Use branches** para experimentar sem medo
4. **`git status`** é seu melhor amigo - use sempre que estiver perdido
5. **Não tenha medo de errar** - quase tudo pode ser desfeito no Git

---

## 🆘 Se Algo Der Errado

```bash
# Ver o que aconteceu recentemente
git reflog

# Voltar para um estado anterior (último recurso)
git reflog  # encontre o hash do estado bom
git reset --hard HASH_DO_ESTADO_BOM
```

---

## 📚 Próximos Passos

Quando se sentir confortável com Git local:
1. ✅ Leia o arquivo `GITHUB_SETUP.md`
2. ✅ Crie uma conta no GitHub
3. ✅ Conecte seu repositório local ao GitHub
4. ✅ Faça seu primeiro `git push`

---

**Dúvidas?** Experimente os comandos e pergunte! 😊
