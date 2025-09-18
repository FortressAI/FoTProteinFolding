# 🧬 FoT Protein Discovery Dashboard

## 🚀 Quick Start

### Local Testing
```bash
# Install dependencies
python3 -m pip install streamlit plotly pandas numpy

# Run dashboard
streamlit run streamlit_protein_dashboard.py
```

### Free Deployment to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add streamlit_protein_dashboard.py requirements.txt .streamlit/
   git commit -m "🧬 Add Streamlit protein dashboard"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file: `streamlit_protein_dashboard.py`
   - Deploy automatically!

## 📊 Dashboard Features

- **🔍 Interactive Analytics**: Real-time protein discovery analysis
- **🧬 Protein Browser**: Searchable database with advanced filtering
- **📈 Visualizations**: Plotly-based charts and graphs
- **📥 Data Export**: CSV/JSON download capabilities
- **⚛️ Quantum Metrics**: vQbit coherence and validation scores
- **🎯 Druggability Assessment**: Comprehensive molecular property analysis

## 🎛️ Dashboard Sections

### 📊 Analytics Tab
- Druglikeness score distribution
- Priority level pie charts
- Molecular weight vs druglikeness scatter plots
- Therapeutic class breakdown
- Discovery timeline analysis

### 🔬 Protein Browser Tab  
- Advanced filtering (druglikeness, priority, class, molecular weight)
- Text search across sequences and metadata
- Expandable protein detail cards
- Real-time filtering with instant results

### 📥 Export Tab
- Download filtered data as CSV or JSON
- Timestamped file naming
- Full dataset or filtered subset export

## 🔧 Configuration

### Demo Mode (Default)
- Uses realistic mock data
- No external dependencies
- Perfect for portfolio/demo

### Production Mode
- File: `streamlit_protein_dashboard_neo4j.py`
- Connects to real Neo4j database
- Requires database credentials

## 🌐 Live Demo

After deployment, your dashboard will be available at:
`https://[username]-[repo-name]-streamlit-protein-dashboard-[hash].streamlit.app`

## 📋 Files

- `streamlit_protein_dashboard.py` - Main dashboard (demo mode)
- `streamlit_protein_dashboard_neo4j.py` - Production version
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `STREAMLIT_DEPLOYMENT_GUIDE.md` - Detailed deployment guide

## 🎯 Key Benefits

✅ **Free Hosting** - Deploy on Streamlit Cloud at no cost  
✅ **Professional Interface** - Publication-ready visualizations  
✅ **Real-time Analysis** - Interactive protein exploration  
✅ **Data Export** - Easy CSV/JSON downloads  
✅ **Mobile Responsive** - Works on all devices  
✅ **Auto-Updates** - Syncs with GitHub pushes  

## 🔒 Security

- Demo version uses mock data only
- Production version supports environment variables for credentials
- No sensitive data exposed in demo mode

## 📈 Scaling

- **Free Tier**: 1GB RAM, community support
- **Upgrade Options**: Teams plan for private deployments
- **Self-hosting**: Docker deployment available

---

**🎉 Result**: Professional web dashboard showcasing your 251,941+ protein discoveries!
