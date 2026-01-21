# 🛠️ SOLUÇÃO MANUAL - Otimizar 2_Torre.dae no Blender

## ⚠️ A otimização automática encontrou problemas

Vou te orientar a fazer manualmente no Blender (é rápido e fácil!):

---

## 📋 Passo a Passo (5 minutos)

### **1. Abrir Blender**
```bash
blender
```

### **2. Importar o Arquivo**
- File → Import → Collada (.dae)
- Navegar até: `2_Torre_original.dae`
- Clicar em "Import /home/lhmt-jhoni/Gazebo/robotSim4/models/catia/COLLADA"
- **Aguardar** (pode demorar 30-60 segundos)

### **3. Selecionar o Objeto**
- Clicar no objeto 3D na viewport (deve ficar laranja)
- Ou pressionar `A` para selecionar tudo

### **4. Adicionar Modificador Decimate**
- No painel direito, clicar na aba "Modifiers" (ícone de chave inglesa 🔧)
- Clicar em "Add Modifier" → "Decimate"
- Em "Ratio", digitar: **0.12** (12% dos polígonos)
- Aguardar o Blender processar

### **5. Aplicar o Modificador**
- Clicar na setinha para baixo ao lado de "Decimate"
- Selecionar "Apply"

### **6. Exportar**
- File → Export → Collada (.dae)
- Navegar até: `/home/lhmt-jhoni/Gazebo/robotSim4/models/catia/`
- Nome do arquivo: `2_Torre.dae`
- Marcar opção "Triangulate" (se disponível)
- Clicar em "Export COLLADA"

### **7. Fechar Blender**
- File → Quit
- Não precisa salvar o projeto

---

## ✅ Resultado Esperado

- **Arquivo original:** `2_Torre_original.dae` = 123 MB
- **Arquivo otimizado:** `2_Torre.dae` = ~10-15 MB
- **Redução:** ~88%

---

## 🎯 Alternativa Mais Rápida

Se preferir, posso te ajudar com uma solução alternativa:

### **Opção A: Usar arquivo de menor resolução**
Se você tem `2_Torre2.dae` (86 MB), podemos usar ele:
```bash
cp /home/lhmt-jhoni/testes/formas/catia/2_Torre2.dae models/catia/2_Torre.dae
```

### **Opção B: Usar Git LFS**
Configurar Git LFS para aceitar arquivos grandes:
```bash
sudo apt install git-lfs
git lfs install
git lfs track "*.dae"
git add .gitattributes
```

### **Opção C: Simplificar mais drasticamente**
Usar ratio 0.05 (5% dos polígonos) = arquivo ainda menor

---

## 🆘 Se Tiver Dúvidas

Me avise qual opção você prefere:
1. **Manual no Blender** (recomendado - 5 minutos)
2. **Usar 2_Torre2.dae** (mais rápido mas ainda grande)
3. **Git LFS** (aceita arquivos grandes)
4. **Tentar outro método automático**

---

**Qual você prefere?** 🤔
