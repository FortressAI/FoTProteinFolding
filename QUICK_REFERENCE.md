# 🧬 FoT Protein Dashboard - Quick Reference Card

## 🚀 Getting Started (30 seconds)
1. **Access:** Open dashboard URL or run `python3 -m streamlit run streamlit_app.py --server.port 8512`
2. **Wait:** See "Loading CHUNKED dataset: 251,941 proteins" in sidebar
3. **Explore:** Start with 🏠 Dashboard Overview

## 📊 Key Numbers to Know
- **Total Proteins:** 251,941 discoveries
- **🌟 Excellent:** 99,493 proteins (≥0.9 validation)
- **⭐ Very Good:** 81,053 proteins (0.8-0.9 validation)  
- **✅ Good:** 71,395 proteins (0.7-0.8 validation)

## 🎯 What Each Score Means
| Metric | Range | Good Value | Meaning |
|--------|-------|------------|---------|
| **Druglikeness** | 0-1 | ≥0.7 | Drug development potential |
| **Validation** | 0-1 | ≥0.9 | Discovery confidence |
| **Energy** | negative | Lower = better | Protein stability |
| **Quantum Coherence** | 0-1 | Higher = more quantum | Quantum properties |

## 🔍 How to Find What You Want

### **Find the Best Proteins:**
1. Go to 🔍 **Protein Explorer**
2. Set **Quality Filter** → "Excellent Only"
3. Set **Priority Filter** → "HIGH"
4. Browse results

### **Search for Specific Sequences:**
1. Go to 🔍 **Protein Explorer**  
2. Enter amino acids in **Search Box** (e.g., "MKLLISVI")
3. Results show matching proteins

### **Get 2D/3D Visualizations:**
1. Expand any protein card
2. Find **"🔬 Advanced 2D/3D Analytics & Visualizations"**
3. Check the box to load full analysis
4. Wait 5-10 seconds for charts/3D models

## 🏠 Dashboard Sections Quick Guide

| Section | Use When You Want To... |
|---------|------------------------|
| 🏠 **Dashboard Overview** | See summary stats and recent discoveries |
| 🔍 **Protein Explorer** | Search, filter, and browse all proteins |
| 📊 **Analytics Deep Dive** | View statistical charts and correlations |
| 📥 **Data Export** | Download filtered protein datasets |

## ⚡ Quick Actions

### **Find Drug Candidates:**
```
Filter: Druglikeness ≥ 0.7 + Priority = HIGH + Quality = Excellent
```

### **Find Stable Proteins:**
```
Sort by: Energy (lowest first) + Validation ≥ 0.8
```

### **Find Novel Discoveries:**
```
Filter: Priority = HIGH + recent timestamps
```

## 🚨 Troubleshooting (Quick Fixes)

| Problem | Quick Fix |
|---------|-----------|
| No proteins showing | Clear all filters, set to "All" |
| Dashboard slow | Use smaller page sizes (10 instead of 50) |
| Analytics won't load | Wait 15 seconds, refresh if needed |
| Data not loading | Check sidebar for loading progress |

## 🎯 Pro Tips
- **Best proteins:** Start with Excellent + HIGH priority
- **Performance:** Don't load multiple 3D analytics at once
- **Search:** Use partial sequences (3-6 amino acids work well)
- **Export:** Apply filters before exporting for manageable files

## 📱 Mobile/Small Screen Tips
- Use sidebar navigation for section switching
- Expand one protein at a time for readability
- Use search instead of browsing on mobile
- Stick to 2D visualizations on smaller screens

---
**🧬 Need more help? See the full User Guide: `STREAMLIT_USER_GUIDE.md` ✨**
