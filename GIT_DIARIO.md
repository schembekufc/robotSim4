# 🔄 Guia de Atualização do GitHub

Como o Git não salva automaticamente na nuvem, você precisa seguir estes 3 passos sempre que fizer alterações importantes.

---

## ⚡ Fluxo de Trabalho (Cheat Sheet)

Sempre que você editar arquivos e quiser salvar no GitHub:

### **1. Adicionar as mudanças**
Prepara os arquivos para serem salvos.

```bash
git add .
```
*(O ponto `.` significa "todos os arquivos modificados")*

---

### **2. Criar um "Commit" (Ponto de Salvamento)**
Salva uma "foto" do projeto com uma mensagem explicando o que mudou.

```bash
git commit -m "Descreva aqui o que você fez"
```

**Exemplos de mensagens:**
- `"fix: corrigi erro na velocidade da joint1"`
- `"feat: adicionei nova GUI de controle"`
- `"docs: atualizei o README"`

---

### **3. Enviar para o GitHub (Push)**
Envia seus commits locais para a nuvem.

```bash
git push
```
*(Não precisa mais digitar `origin main`, só `git push` já funciona)*

---

## 💡 Resumo Visual

```mermaid
graph LR
    A[Seu Computador] -- 1. git add --> B(Staging Area)
    B -- 2. git commit --> C(Repositório Local)
    C -- 3. git push --> D[GitHub (Nuvem)]
```

---

## 🔍 Comandos Úteis

### **Ver o que mudou**
Antes de commitar, veja quais arquivos foram alterados:
```bash
git status
```

### **Baixar atualizações (Pull)**
Se você (ou outra pessoa) mudou algo direto no site do GitHub, baixe para seu PC:
```bash
git pull
```

### **Ver histórico**
Veja o que foi feito recentemente:
```bash
git log --oneline
```

---

## ⚠️ Cuidado com Arquivos Grandes

Se você adicionar **novos** arquivos 3D grandes (> 50 MB), lembre-se de rastreá-los com LFS **antes** de commitar:

```bash
git lfs track "*.dae"
git add .gitattributes
```

(Mas para os arquivos atuais, já está tudo configurado!)
