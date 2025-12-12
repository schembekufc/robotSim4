# 🚀 Guia GitHub CLI - Upload Automático

**Opção 1 - Segura e Automática**

---

## 📋 Passo a Passo

### **1. Instalar GitHub CLI** ⏳ EM ANDAMENTO

```bash
sudo apt install gh -y
```

Digite sua senha quando solicitado.

---

### **2. Fazer Login no GitHub** 👤 VOCÊ FAZ

Depois da instalação, execute:

```bash
gh auth login
```

**Escolha as opções:**

1. **What account do you want to log into?**
   - Escolha: `GitHub.com`

2. **What is your preferred protocol for Git operations?**
   - Escolha: `HTTPS`

3. **Authenticate Git with your GitHub credentials?**
   - Escolha: `Yes`

4. **How would you like to authenticate GitHub CLI?**
   - Escolha: `Login with a web browser` ⭐ (MAIS FÁCIL)

5. **Vai mostrar um código (ex: ABCD-1234)**
   - Copie o código
   - Pressione Enter
   - Navegador vai abrir
   - Cole o código
   - Autorize o GitHub CLI

**Pronto!** Você está autenticado de forma segura! ✅

---

### **3. Criar Repositório e Fazer Push** 🤖 EU FAÇO

Depois que você fizer login, **ME AVISE** e eu executo:

```bash
gh repo create robotSim4 \
  --public \
  --description "Sistema de rastreamento solar com Gazebo - Placa rastreadora e prato parabólico" \
  --source=. \
  --remote=origin \
  --push
```

Isso vai:
- ✅ Criar repositório `robotSim4` no GitHub
- ✅ Configurar como público
- ✅ Adicionar descrição
- ✅ Conectar ao repositório local
- ✅ Fazer push automaticamente (com Git LFS!)

**Tempo:** ~5-7 minutos para upload

---

## 🔐 Por Que É Seguro?

- ✅ Você faz login no **SEU navegador**
- ✅ GitHub CLI usa **OAuth** (não senha)
- ✅ Você autoriza **apenas** o que o CLI pode fazer
- ✅ Você pode revogar acesso a qualquer momento
- ✅ Eu **NÃO** tenho acesso à sua senha

---

## 📊 O Que Vai Acontecer

1. **GitHub CLI instalado** ⏳
2. **Você faz login** (navegador) 👤
3. **Eu crio repositório** 🤖
4. **Upload automático** 🚀
5. **Pronto!** ✅

---

## 🆘 Se Der Erro

### **Erro: "gh: command not found"**
```bash
# Aguarde a instalação terminar
# Depois tente novamente
```

### **Erro: "failed to authenticate"**
```bash
# Faça login novamente
gh auth login
```

### **Erro: "repository already exists"**
```bash
# O repositório já foi criado
# Apenas faça push:
git push -u origin main
```

---

## ✅ Checklist

- [ ] Instalar GitHub CLI (`sudo apt install gh`)
- [ ] Fazer login (`gh auth login`)
- [ ] **ME AVISAR** que fez login
- [ ] Eu crio repositório e faço push
- [ ] Verificar no GitHub

---

## 📝 Comandos Resumidos

```bash
# 1. Instalar (em andamento)
sudo apt install gh -y

# 2. Login (VOCÊ FAZ)
gh auth login
# Escolha: GitHub.com → HTTPS → Yes → Web browser

# 3. Criar e fazer push (EU FAÇO depois que você fizer login)
gh repo create robotSim4 --public --source=. --remote=origin --push
```

---

**Status Atual:** ⏳ Aguardando instalação do GitHub CLI...

**Próximo passo:** Você faz login com `gh auth login`

**Depois:** Me avise e eu faço o resto! 🚀
