# Streamlit Cloud Deployment Guide
## FoT Protein Discovery Dashboard

This guide covers deploying the optimized protein discovery dashboard to Streamlit Cloud for free hosting.

## 📁 File Structure

```
streamlit_dashboard/
├── data/                                    # Exported data files
│   ├── protein_discovery_data.json.gz      # Complete dataset (17.5 MB)
│   ├── proteins.csv                         # Full CSV export (65.2 MB)
│   ├── top_proteins.csv                     # Top 1000 proteins (0.3 MB)
│   ├── high_priority_proteins.csv           # High priority only (43.0 MB)
│   ├── druggable_proteins.csv               # All druggable (65.2 MB)
│   └── summary.json                         # Quick stats (< 1 MB)
├── streamlit_cloud_optimized.py             # Main dashboard app
├── export_optimized.py                      # Data export script
└── requirements.txt                         # Dependencies
```

## 🚀 Deployment Steps

### Step 1: Prepare Repository

1. **Create GitHub Repository**
   ```bash
   # Navigate to streamlit_dashboard folder
   cd streamlit_dashboard
   
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit: FoT Protein Discovery Dashboard"
   
   # Push to GitHub
   git remote add origin https://github.com/yourusername/fot-protein-dashboard.git
   git push -u origin main
   ```

2. **Handle Large Files with Git LFS**
   ```bash
   # Install Git LFS
   brew install git-lfs  # macOS
   git lfs install
   
   # Track large files
   git lfs track "data/*.csv"
   git lfs track "data/*.json.gz"
   
   # Commit LFS configuration
   git add .gitattributes
   git commit -m "Add Git LFS tracking for large data files"
   git push
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub account

2. **Create New App**
   - Click "New app"
   - Select your GitHub repository
   - Choose main branch
   - Set main file path: `streamlit_cloud_optimized.py`
   - Click "Deploy"

3. **Configure Settings** (Optional)
   - App name: `fot-protein-discovery`
   - URL: `https://fot-protein-discovery.streamlit.app`

## 📊 Data Loading Strategy

The dashboard uses a hierarchical loading approach:

### Primary: Compressed JSON (Best)
- **File:** `data/protein_discovery_data.json.gz` (17.5 MB)
- **Pros:** Complete dataset, fast loading, small size
- **Contains:** All proteins + metadata + quantum data

### Fallback: CSV Files
- **File:** `data/proteins.csv` (65.2 MB)
- **Pros:** Standard format, universally supported
- **Limitation:** May be too large for free Streamlit Cloud

### Emergency: Summary Only
- **File:** `data/summary.json` (< 1 MB)
- **Pros:** Always loads, provides basic stats
- **Limitation:** Only 10 sample proteins for demo

## 🔧 Optimization Features

### Memory Efficiency
```python
@st.cache_data
def load_optimized_data():
    """Cached data loading with fallbacks"""
    # Tries compressed JSON first
    # Falls back to CSV if needed
    # Uses summary as last resort
```

### Performance Optimizations
- **Batched processing** during export
- **Compressed storage** (gzip JSON)
- **Intelligent sampling** for large visualizations
- **Hierarchical loading** with fallbacks

### File Size Management
| File Type | Size | Use Case |
|-----------|------|----------|
| `summary.json` | < 1 MB | Basic stats, always loads |
| `top_proteins.csv` | 0.3 MB | Top 1000 performers |
| `protein_discovery_data.json.gz` | 17.5 MB | Complete dataset |
| `high_priority_proteins.csv` | 43.0 MB | High priority subset |
| `proteins.csv` | 65.2 MB | Full dataset |

## 🎯 Free Tier Considerations

### Streamlit Cloud Limits
- **Memory:** ~1 GB RAM
- **Storage:** Repository size limits
- **Bandwidth:** Reasonable for dashboards
- **Compute:** Sufficient for data analysis

### Optimization Strategies
1. **Use compressed files** (`*.gz`)
2. **Sample large datasets** for visualization
3. **Cache data loading** with `@st.cache_data`
4. **Progressive loading** (summary → full data)

## 🔍 Monitoring & Performance

### Load Time Optimization
```python
# Sample large datasets for performance
if len(df) > 10000:
    df_sample = df.sample(n=10000, random_state=42)
```

### Error Handling
```python
try:
    # Load primary data source
    with gzip.open(json_path, 'rt') as f:
        data = json.load(f)
except Exception:
    # Fallback to CSV
    proteins_df = pd.read_csv(csv_path)
```

## 📱 Features Included

### Dashboard Capabilities
- **Real-time analytics** from static data
- **Interactive visualizations** with Plotly
- **Protein detail views** with full sequences
- **Export functionality** for filtered datasets
- **Responsive design** for mobile/desktop

### Data Export Options
- High priority proteins (CSV)
- Druggable candidates (CSV)  
- Summary statistics (JSON)
- Custom filtered datasets

## 🚨 Troubleshooting

### Common Issues

1. **File Too Large Error**
   ```bash
   # Use Git LFS for files > 100MB
   git lfs track "data/large_file.csv"
   ```

2. **Memory Issues on Streamlit Cloud**
   ```python
   # Reduce sample size in visualizations
   df_sample = df.sample(n=5000)
   ```

3. **Loading Timeout**
   ```python
   # Use progressive loading
   with st.spinner("Loading data..."):
       data = load_cached_data()
   ```

### Performance Tips
- Keep individual files under 100MB
- Use `@st.cache_data` for expensive operations
- Sample large datasets for visualizations
- Implement graceful fallbacks

## 🔄 Data Updates

### Refreshing Dashboard Data
1. Run export script: `python3 export_optimized.py`
2. Commit new data files
3. Push to GitHub
4. Streamlit Cloud auto-redeploys

### Automated Updates (Future)
```bash
# Cron job to refresh data daily
0 2 * * * cd /path/to/project && python3 export_optimized.py && git add . && git commit -m "Daily data update" && git push
```

## 🎉 Success Metrics

### Performance Targets
- **Load time:** < 10 seconds
- **Memory usage:** < 800MB
- **Responsiveness:** Smooth interactions
- **Data completeness:** 251,941 proteins

### Expected Results
- ✅ **251,941 total proteins** loaded
- ✅ **Multiple visualization types** working
- ✅ **Export functionality** operational
- ✅ **Mobile responsive** design
- ✅ **Free hosting** on Streamlit Cloud

## 📞 Support

For deployment issues:
1. Check Streamlit Cloud logs
2. Verify data file sizes
3. Test locally first: `streamlit run streamlit_cloud_optimized.py`
4. Monitor memory usage in dashboard

---
**Ready for production deployment! 🚀**
