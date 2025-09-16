// FoT Protein Discovery Database Schema
// Exported: 2025-09-16T09:44:05.541364
// For Prior Art Project

// Create node constraints
CREATE CONSTRAINT discovery_id IF NOT EXISTS FOR (d:Discovery) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT vqbit_id IF NOT EXISTS FOR (v:VQbit) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT quantum_state_id IF NOT EXISTS FOR (q:QuantumState) REQUIRE q.id IS UNIQUE;
CREATE CONSTRAINT protein_family_name IF NOT EXISTS FOR (p:ProteinFamily) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT therapeutic_target_name IF NOT EXISTS FOR (t:TherapeuticTarget) REQUIRE t.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX discovery_validation_score IF NOT EXISTS FOR (d:Discovery) ON (d.validation_score);
CREATE INDEX discovery_timestamp IF NOT EXISTS FOR (d:Discovery) ON (d.timestamp);
CREATE INDEX vqbit_residue IF NOT EXISTS FOR (v:VQbit) ON (v.residue_index);
CREATE INDEX vqbit_amino_acid IF NOT EXISTS FOR (v:VQbit) ON (v.amino_acid);
CREATE INDEX vqbit_entanglement IF NOT EXISTS FOR (v:VQbit) ON (v.entanglement_degree);
CREATE INDEX quantum_entanglement_strength IF NOT EXISTS FOR ()-[r:QUANTUM_ENTANGLED]-() ON (r.entanglement_strength);

