# 📘 Guia de Configuração do GitHub

## ✅ Status Atual

- ✅ Repositório Git local inicializado
- ✅ Primeiro commit realizado (19 arquivos)
- ✅ Identidade Git configurada (Nome: Jhoni)

## 🚀 Próximos Passos para Conectar ao GitHub

### 1. Criar uma Conta no GitHub (se ainda não tiver)

Acesse: https://github.com/signup

### 2. Criar um Novo Repositório no GitHub

1. Faça login no GitHub
2. Clique no botão **"+"** no canto superior direito → **"New repository"**
3. Preencha:
   - **Repository name**: `robotSim4` (ou outro nome de sua preferência)
   - **Description**: "Gazebo solar tracker simulation with GUI interfaces"
   - **Visibilidade**: 
     - ✅ **Public** (qualquer um pode ver) - Recomendado para portfólio
     - 🔒 **Private** (só você vê) - Use se quiser manter privado
   - ⚠️ **NÃO marque** "Initialize with README" (já temos um)
4. Clique em **"Create repository"**

### 3. Conectar seu Repositório Local ao GitHub

Após criar o repositório, o GitHub mostrará instruções. Use estes comandos:

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu nome de usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/robotSim4.git

# Enviar seu código para o GitHub
git push -u origin main
```

**Nota**: Você precisará autenticar. O GitHub recomenda usar um **Personal Access Token** em vez de senha.

### 4. Criar um Personal Access Token (PAT)

1. No GitHub, vá em: **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome (ex: "robotSim4-laptop")
4. Marque o escopo: **repo** (acesso completo a repositórios)
5. Clique em **"Generate token"**
6. ⚠️ **COPIE O TOKEN** (você não verá novamente!)
7. Use o token como senha quando o Git pedir

### 5. Alternativa: Usar SSH (Mais Seguro)

Se preferir não usar tokens toda vez:

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu_email@example.com"

# Copiar a chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar no GitHub: Settings → SSH and GPG keys → New SSH key
# Cole a chave e salve

# Mudar a URL do repositório para SSH
git remote set-url origin git@github.com:SEU_USUARIO/robotSim4.git

# Agora pode fazer push sem senha
git push -u origin main
```

## 📝 Comandos Git Básicos para o Dia a Dia

### Fazer Mudanças e Salvar

```bash
# Ver o status (arquivos modificados)
git status

# Adicionar arquivos modificados
git add .                    # Adiciona todos
git add arquivo.py           # Adiciona um arquivo específico

# Fazer commit (salvar mudanças)
git commit -m "Descrição clara do que você mudou"

# Enviar para o GitHub
git push
```

### Ver Histórico

```bash
# Ver histórico de commits
git log

# Ver histórico resumido
git log --oneline

# Ver mudanças em um arquivo
git log -p arquivo.py
```

### Desfazer Mudanças

```bash
# Desfazer mudanças não salvas em um arquivo
git checkout -- arquivo.py

# Voltar para um commit anterior (cuidado!)
git reset --hard COMMIT_ID
```

### Trabalhar com Branches (Ramificações)

```bash
# Criar uma nova branch para testar algo
git checkout -b nova-funcionalidade

# Voltar para a branch principal
git checkout main

# Mesclar mudanças de outra branch
git merge nova-funcionalidade
```

## 🎯 Boas Práticas

1. **Commits frequentes**: Faça commits pequenos e frequentes
2. **Mensagens claras**: Descreva o que mudou (ex: "Add camera calibration feature")
3. **Não commite arquivos grandes**: Use `.gitignore` para excluir logs, cache, etc.
4. **Use branches**: Teste novas funcionalidades em branches separadas
5. **Pull antes de Push**: Se trabalhar em múltiplos computadores, sempre faça `git pull` antes de `git push`

## 🆘 Problemas Comuns

### "Permission denied" ao fazer push
→ Verifique seu token/SSH key

### "Conflict" ao fazer pull
→ Você tem mudanças locais conflitantes. Use `git stash` para guardar temporariamente

### Esqueci de adicionar arquivo no último commit
```bash
git add arquivo_esquecido.py
git commit --amend --no-edit
```

## 📚 Recursos para Aprender Mais

- [GitHub Docs (Português)](https://docs.github.com/pt)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Visualizador Git Interativo](https://git-school.github.io/visualizing-git/)

---

**Dúvidas?** Pergunte! Estou aqui para ajudar. 😊
