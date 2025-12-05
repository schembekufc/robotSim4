# 📊 Cheat Sheet: Comandos Git Mais Usados

## 🎯 Comandos do Dia a Dia

### Ver Status
```bash
git status              # Ver o que mudou
git diff                # Ver diferenças detalhadas
git log --oneline       # Ver histórico resumido
```

### Salvar Mudanças
```bash
git add .                           # Adicionar todos os arquivos
git add arquivo.py                  # Adicionar arquivo específico
git commit -m "Mensagem clara"      # Fazer commit
```

### Branches
```bash
git branch                  # Listar branches
git branch nome             # Criar branch
git checkout nome           # Mudar para branch
git checkout -b nome        # Criar e mudar
git merge nome              # Mesclar branch
git branch -d nome          # Deletar branch
```

### Desfazer
```bash
git checkout -- arquivo.py      # Desfazer mudanças não salvas
git reset                       # Tirar do staging
git reset --soft HEAD~1         # Desfazer último commit (mantém mudanças)
```

---

## 🔍 Comandos de Inspeção

```bash
git log --oneline --graph --all     # Histórico visual
git show HASH                       # Ver commit específico
git show --stat HASH                # Estatísticas do commit
git blame arquivo.py                # Ver quem modificou cada linha
git ls-files                        # Listar arquivos rastreados
```

---

## 📈 Fluxo de Trabalho Visual

```
┌─────────────────────────────────────────────────────────┐
│  Arquivos Modificados (Working Directory)              │
│  ↓ git add                                              │
│  Staging Area (Prontos para Commit)                    │
│  ↓ git commit                                           │
│  Repositório Local (Histórico de Commits)              │
│  ↓ git push (quando conectar ao GitHub)                │
│  Repositório Remoto (GitHub)                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Estados dos Arquivos

```
Untracked (não rastreado)
    ↓ git add
Staged (pronto para commit)
    ↓ git commit
Committed (salvo no histórico)
    ↓ modificar arquivo
Modified (modificado)
    ↓ git add
Staged (pronto para commit)
    ...
```

---

## 💡 Dicas Rápidas

✅ **Sempre use `git status`** quando estiver perdido  
✅ **Commits pequenos** são melhores que grandes  
✅ **Mensagens claras** ajudam você depois  
✅ **Use branches** para experimentar  
✅ **`git log --oneline`** para ver o histórico  

---

## 🆘 Socorro Rápido

| Problema | Solução |
|----------|---------|
| Fiz mudanças erradas | `git checkout -- .` |
| Adicionei arquivo errado | `git reset arquivo.py` |
| Commit com mensagem errada | `git commit --amend` |
| Quero voltar atrás | `git reset --soft HEAD~1` |
| Estou completamente perdido | `git status` e respire fundo 😊 |

---

## 📚 Arquivos de Ajuda

1. **GIT_LOCAL_GUIDE.md** - Guia completo para iniciantes
2. **GITHUB_SETUP.md** - Como conectar ao GitHub
3. **README.md** - Documentação do projeto
4. **Este arquivo** - Referência rápida

---

**Imprima mentalmente:** `git status` é seu melhor amigo! 🚀
