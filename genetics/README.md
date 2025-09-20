# 🧬 Genetics Framework - DNA-to-Therapeutics Optimization

## Complete 5-Layer Genetics Ontology for Therapeutic Discovery

This module extends the Field of Truth (FoT) protein discovery system into a comprehensive **DNA-to-therapeutics optimization platform**.

---

## 🚀 **Quick Start**

### Launch the Genetics Streamlit App
```bash
# From the main FoTProtein directory
streamlit run genetics_streamlit_app.py --server.port 8513
```

### Use the Genetics Modules
```python
from genetics.genetics_ontology import GeneticsOntology, VirtueType
from genetics.genetics_optimization import GeneticsOptimizer  
from genetics.genetics_simulation import GeneticsSimulator

# Create genetics ontology
ontology = GeneticsOntology()

# Set up multi-objective optimizer
optimizer = GeneticsOptimizer(population_size=100, generations=50)

# Run genetics simulation
simulator = GeneticsSimulator()
virtue_scores = simulator.calculate_virtue_scores()
```

---

## 🏗️ **5-Layer Architecture**

### **Layer 1: Genomic Foundation**
- **Entities:** Chromosomes, Genes, Exons, Introns, SNPs, Promoters, Enhancers
- **Focus:** Static blueprint and sequence-level constraints

### **Layer 2: Epigenomic Control**  
- **Entities:** DNA Methylation, Histone Marks, Chromatin Loops, TADs
- **Focus:** Context-specific gene accessibility and regulation

### **Layer 3: Regulatory Networks**
- **Entities:** Transcription Factors, miRNAs, lncRNAs, Regulatory Circuits
- **Focus:** Dynamic control over transcription and translation

### **Layer 4: Proteostasis Networks**
- **Entities:** Transcripts, Ribosomes, Chaperones, Proteasome, Quality Control
- **Focus:** Protein synthesis, folding, and degradation capacity

### **Layer 5: Phenotypic/Therapeutic**
- **Entities:** Therapies, Metabolic Pathways, Cellular Phenotypes
- **Focus:** High-level therapeutic objectives and interventions

---

## ⚖️ **Enhanced Virtue Framework**

### **Fidelity (Enhanced Justice)**
```
Fidelity = P(correct_isoform) × P(proper_timing) × (1 - genetic_variant_impact)
```

### **Robustness (Enhanced Temperance)**
```
Robustness = (1 - stress_susceptibility) × variant_tolerance × network_stability
```

### **Efficiency (Enhanced Prudence)**
```
Efficiency = output_benefit / (ATP_cost + ribosome_usage + chaperone_cost)
```

### **Resilience (Enhanced Recovery)**
```
Resilience = recovery_rate × adaptive_capacity × repair_efficiency
```

### **Parsimony (Enhanced Simplicity)**
```
Parsimony = 1 / (1 + regulatory_complexity + pathway_redundancy)
```

---

## 🎯 **Multi-Objective Optimization**

### **NSGA-II Implementation**
```python
from genetics.genetics_optimization import GeneticsOptimizer, OptimizationVariable

# Set up optimization variables
variables = [
    OptimizationVariable('tf_p53_activity', 0.5, 0.0, 2.0, 'continuous'),
    OptimizationVariable('hsp70_inducer_dose', 0.0, 0.0, 2.0, 'continuous'),
    OptimizationVariable('choline_dose', 0.0, 0.0, 1000.0, 'continuous')
]

# Run optimization
optimizer = GeneticsOptimizer(population_size=100, generations=50)
for var in variables:
    optimizer.add_variable(var)
    
pareto_solutions = optimizer.run_optimization()
```

### **Pareto-Optimal Policy Generation**
Each optimization generates therapeutic policies optimizing multiple competing objectives:
- Minimize folding error
- Minimize energy cost  
- Minimize stress damage
- Minimize therapy cost
- Minimize regulatory complexity

---

## 🔬 **Simulation Capabilities**

### **Complete Systems Modeling**
```python
from genetics.genetics_simulation import GeneticsSimulator

simulator = GeneticsSimulator()

# Load genetic context
simulator.load_genetic_context("PATIENT_001", ["rs1042522", "rs17878362"])

# Simulate regulatory networks
tf_levels = {"TP53": 1.2, "MYC": 0.8}
mirna_levels = {"miR-21": 1.5, "miR-34a": 0.6}
simulator.simulate_regulatory_network(tf_levels, mirna_levels)

# Simulate proteostasis
chaperone_levels = {"HSP70": 1.3, "HSP90": 0.9}
simulator.simulate_proteostasis(chaperone_levels)

# Apply therapeutic interventions
therapies = {"hsp70_inducer": 0.8, "choline": 750, "antioxidant": 1.0}
simulator.simulate_therapy_effects(therapies)

# Get final virtue scores
virtue_scores = simulator.calculate_virtue_scores()
```

---

## 📊 **Streamlit App Features**

### **Platform Overview**
- 5-layer architecture visualization
- Enhanced virtue score dashboard
- Real-time genetics metrics

### **Genetic Variants Analysis**
- SNP impact assessment
- Variant distribution analysis
- High-impact variant identification

### **Regulatory Network Simulation**
- TF/miRNA network modeling
- Interactive network visualization
- Regulation strength analysis

### **Proteostasis Modeling**
- Protein folding capacity analysis
- Chaperone assistance simulation
- Stress level assessment

### **Therapy Optimization**
- Personalized intervention recommendations
- Therapy combination optimization
- Efficacy prediction

### **Multi-Objective Optimization**
- NSGA-II optimization interface
- Pareto front visualization
- Policy generation

---

## 🔗 **Integration with FoT System**

### **Data Compatibility**
- Uses same chunked JSON.gz data from 262,792 protein discoveries
- Extends existing proteins with genetics context
- Preserves all original protein analysis capabilities

### **vQbit Integration**
```python
# Proteostasis simulation integrates with vQbit engine
def simulate_protein_folding(self, protein_sequence: str, 
                           chaperone_assistance: Dict[str, float]) -> float:
    # Get base folding probability from vQbit analysis
    vqbit_analysis = self.vqbit_engine.analyze_protein_sequence(protein_sequence)
    base_folding_success = vqbit_analysis.get('folding_probability', 0.5)
    
    # Apply chaperone assistance
    chaperone_boost = sum(assistance * efficacy for assistance, efficacy in chaperone_assistance.items())
    
    # Return enhanced folding success rate
    return min(1.0, base_folding_success * (1 + chaperone_boost))
```

### **Non-Breaking Design**
- Original protein app continues on port 8512
- Genetics app runs independently on port 8513  
- Shared data infrastructure
- Compatible Neo4j schema extensions

---

## 🧪 **Testing**

### **Run Component Tests**
```bash
python3 -c "
from genetics.genetics_ontology import GeneticsOntology
from genetics.genetics_optimization import GeneticsOptimizer
from genetics.genetics_simulation import GeneticsSimulator

ontology = GeneticsOntology()
optimizer = GeneticsOptimizer()
simulator = GeneticsSimulator()
print('✅ All genetics components working')
"
```

### **Test Streamlit App**
```bash
# Check dependencies
python3 -c "import streamlit, plotly, networkx; print('✅ Dependencies OK')"

# Run app
streamlit run genetics_streamlit_app.py --server.port 8513
```

---

## 🔮 **Future Enhancements**

### **Planned Extensions**
- Single-cell integration for cell-type specific networks
- Temporal dynamics modeling
- Population genetics with linkage disequilibrium
- Pharmacogenomics and drug metabolism prediction
- Multi-omics integration (proteomics, metabolomics, microbiome)

### **Advanced Features**
- Hierarchical multi-scale optimization
- Bayesian uncertainty quantification  
- Robust optimization under genetic variation
- Real-time policy adaptation

---

## 📚 **Documentation**

For complete documentation, visit: [Genetics Framework Wiki](https://github.com/FortressAI/FoTProteinFolding/wiki/Genetics-Framework)

**The Genetics Framework transforms FoT from protein discovery into a complete precision medicine platform, enabling personalized therapeutic optimization through virtue-guided multi-objective optimization across the full DNA-to-therapy pipeline.**
