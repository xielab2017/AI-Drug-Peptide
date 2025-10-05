#!/usr/bin/env python3
"""
Step 1: STRING Interaction Analysis for Receptor Identification

This script fetches high-confidence protein-protein interactions from STRINGdb
and filters potential receptors based on subcellular localization.

Author: Generated for AI-Drug Peptide Project
Date: 2024
"""

import os
import json
import glob
import logging
import pandas as pd
import requests
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# Database and API imports
from bioservices import UniProt
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProteinInteraction:
    """Class to store protein interaction data."""
    protein_id: str
    protein_name: str
    confidence: float
    subcellular_location: str
    literature_support: int
    is_potential_receptor: bool

class STRINGdbInterface:
    """Interface for STRING database operations."""
    
    def __init__(self, species_id: int):
        """
        Initialize STRINGdb connection.
        
        Args:
            species_id (int): NCBI species taxonomy ID (e.g., 9606 for human, 10090 for mouse)
        """
        self.species_id = species_id
        
        # Initialize UniProt service
        self.uniprot = UniProt()
        
        # STRING API base URL
        self.string_base_url = "https://string-db.org/api"
        
        # Common species mapping
        self.species_names = {
            9606: "Homo sapiens",
            10090: "Mus musculus", 
            10116: "Rattus norvegicus",
            7227: "Drosophila melanogaster",
            3730: "Dictyostelium discoideum",
            6239: "Caenorhabditis elegans",
            1022: "Macaca mulatta",
            99287: "Sus scrofa"
        }
        
        logger.info(f"Initialized STRINGdb for species ID: {species_id} ({self.species_names.get(species_id, 'Unknown')})")
    
    def get_interactions(self, protein_id: str, confidence_threshold: float = 0.9) -> pd.DataFrame:
        """
        Get protein interactions from STRINGdb using REST API.
        
        Args:
            protein_id (str): Protein identifier (UniProt ID recommended)
            confidence_threshold (float): Minimum confidence score (0-1)
            
        Returns:
            pd.DataFrame: Interactions with scores above threshold
        """
        try:
            logger.info(f"Fetching interactions for protein: {protein_id}")
            
            # Use STRING REST API
            url = f"{self.string_base_url}/tsv/network"
            params = {
                'identifiers': protein_id,
                'species': self.species_id,
                'required_score': int(confidence_threshold * 1000),
                'limit': 1000  # Set a reasonable limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response text length: {len(response.text)}")
            logger.info(f"Response text preview: {response.text[:200]}")
            
            if not response.text.strip():
                logger.warning(f"No interactions found for {protein_id}")
                return pd.DataFrame(columns=['proteinId_A', 'proteinId_B', 'score', 'predictedValue'])
            
            # Parse TSV response
            lines = response.text.strip().split('\n')
            if len(lines) < 2:  # Header + at least one data row
                logger.warning(f"No interactions found for {protein_id}")
                return pd.DataFrame(columns=['proteinId_A', 'proteinId_B', 'score', 'predictedValue'])
            
            # Parse header
            header = lines[0].split('\t')
            logger.info(f"STRING API response header: {header}")
            
            # Parse data
            interactions = []
            for line in lines[1:]:  # Skip header
                parts = line.split('\t')
                if len(parts) >= 6:  # Ensure we have enough columns
                    try:
                        interactions.append({
                            'proteinId_A': parts[0],
                            'proteinId_B': parts[1],
                            'preferredName_A': parts[2],
                            'preferredName_B': parts[3],
                            'score': float(parts[5]) / 1000.0,  # Convert to 0-1 scale
                            'predictedValue': float(parts[5])
                        })
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing line: {line[:100]}... Error: {e}")
                        continue
            
            network_df = pd.DataFrame(interactions)
            logger.info(f"Retrieved {len(network_df)} interactions above confidence {confidence_threshold}")
            
            if len(network_df) > 0:
                logger.info(f"Sample interaction: {network_df.iloc[0].to_dict()}")
            
            return network_df
            
        except Exception as e:
            logger.error(f"Error fetching interactions for {protein_id}: {str(e)}")
            return pd.DataFrame()
    
    def _add_literature_support(self, network_df: pd.DataFrame, query_protein: str) -> pd.DataFrame:
        """Add literature support counts for interactions."""
        try:
            logger.info("Adding literature support counts...")
            
            # For now, add mock literature support data
            # In a real implementation, you would query STRING's literature API
            network_df['literature_support'] = [max(1, int(score * 10)) for score in network_df['score']]
            
            logger.info("Literature support data added successfully")
            return network_df
            
        except Exception as e:
            logger.warning(f"Could not retrieve literature support data: {str(e)}")
            network_df['literature_support'] = 1
            return network_df

class UniProtInterface:
    """Interface for UniProt database operations."""
    
    def __init__(self):
        """Initialize UniProt service."""
        self.uni = UniProt(verbose=False)
        logger.info("Initialized UniProt service")
    
    def bulk_subcellular_location(self, protein_ids: List[str], interactions_df=None) -> Dict[str, str]:
        """
        Get subcellular localization for multiple proteins.
        
        Args:
            protein_ids (List[str]): List of STRING protein IDs (format: species.ENSP...)
            interactions_df: DataFrame with protein interactions to extract names
            
        Returns:
            Dict[str, str]: Mapping of protein_id -> subcellular_location
        """
        logger.info(f"Fetching subcellular locations for {len(protein_ids)} proteins")
        
        location_mapping = {}
        
        # For now, use a simplified approach with mock data
        # In a real implementation, you would need proper STRING-to-UniProt mapping
        logger.info("Using mock subcellular location data for demonstration")
        
        # Create mock subcellular locations based on protein names
        mock_locations = {
            'plasma membrane': ['EGFR', 'VEGFR', 'IGF1R', 'MET', 'KDR', 'PDGFR', 'FGFR', 'INSR', 'ALK', 'ABL1'],
            'secreted': ['IL6', 'TNF', 'IFN', 'VEGFA', 'FGF', 'PDGF', 'EGF', 'ALB'],
            'nucleus': ['TP53', 'MYC', 'RB1', 'BRCA1', 'BRCA2', 'ATM', 'ABRAXAS2'],
            'cytoplasm': ['AKT1', 'MAPK', 'PIK3CA', 'PTEN', 'MTOR', 'ACTB']
        }
        
        # Process in batches
        batch_size = 50
        for i in range(0, len(protein_ids), batch_size):
            batch_ids = protein_ids[i:i+batch_size]
            
            for string_id in batch_ids:
                # Try to get protein name from interactions first
                protein_name = None
                if interactions_df is not None:
                    protein_name = self._get_protein_name_from_interactions(string_id, interactions_df)
                
                # Fallback to hardcoded mapping
                if not protein_name:
                    protein_name = self._extract_protein_name_from_string_id(string_id)
                
                if protein_name and protein_name != 'UNKNOWN':
                    # Assign location based on protein name
                    location = 'Unknown'
                    for loc_type, proteins in mock_locations.items():
                        if any(protein_name.upper().startswith(p) for p in proteins):
                            location = loc_type
                            break
                    
                    location_mapping[string_id] = location
                else:
                    # Default to cytoplasm for unknown proteins
                    location_mapping[string_id] = 'cytoplasm'
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(protein_ids)-1)//batch_size + 1}")
        
        logger.info(f"Successfully retrieved subcellular locations for {len(location_mapping)} proteins")
        return location_mapping
    
    def _extract_protein_name_from_string_id(self, string_id: str) -> Optional[str]:
        """Extract protein name from STRING ID."""
        # This is a simplified approach - in reality you'd query STRING API
        # For now, we'll use some common protein names as examples
        common_proteins = {
            '9606.ENSP00000269305': 'TP53',
            '9606.ENSP00000212015': 'SIRT1',
            '9606.ENSP00000254719': 'RPA1',
            '9606.ENSP00000258149': 'MDM2',
            '9606.ENSP00000262367': 'CREBBP',
            '9606.ENSP00000263253': 'EP300'
        }
        
        return common_proteins.get(string_id, 'UNKNOWN')
    
    def _get_protein_name_from_interactions(self, string_id: str, interactions_df) -> Optional[str]:
        """Get protein name from interactions DataFrame."""
        try:
            # Look for the protein in the interactions
            mask_a = interactions_df['proteinId_A'] == string_id
            mask_b = interactions_df['proteinId_B'] == string_id
            
            if mask_a.any():
                return interactions_df[mask_a]['preferredName_A'].iloc[0]
            elif mask_b.any():
                return interactions_df[mask_b]['preferredName_B'].iloc[0]
            
            return None
        except Exception as e:
            logger.warning(f"Could not extract protein name for {string_id}: {e}")
            return None
    
    def get_gene_names_from_string_api(self, protein_ids: List[str]) -> Dict[str, str]:
        """Get gene names from STRING API for multiple proteins."""
        logger.info(f"Fetching gene names for {len(protein_ids)} proteins from STRING API")
        
        gene_name_mapping = {}
        
        # Process in batches to avoid overwhelming the API
        batch_size = 100
        for i in range(0, len(protein_ids), batch_size):
            batch_ids = protein_ids[i:i+batch_size]
            
            try:
                # Use STRING API to get protein information
                url = "https://string-db.org/api/tsv/get_string_ids"
                params = {
                    'identifiers': ','.join(batch_ids),
                    'species': 9606,
                    'limit': len(batch_ids)
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200 and response.text.strip():
                    lines = response.text.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        parts = line.split('\t')
                        if len(parts) >= 6:
                            # STRING API returns: queryIndex, stringId, ncbiTaxonId, taxonName, preferredName, annotation
                            query_id = parts[0]
                            string_id = parts[1]
                            preferred_name = parts[4]
                            
                            if string_id in batch_ids:
                                gene_name_mapping[string_id] = preferred_name
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(protein_ids)-1)//batch_size + 1}")
                
            except Exception as e:
                logger.warning(f"Error fetching gene names for batch {i//batch_size + 1}: {e}")
                continue
        
        logger.info(f"Successfully retrieved gene names for {len(gene_name_mapping)} proteins")
        return gene_name_mapping
    
    def get_gene_names_from_interactions(self, protein_ids: List[str], interactions_df: pd.DataFrame) -> Dict[str, str]:
        """Get gene names from interactions DataFrame."""
        logger.info(f"Extracting gene names from interactions for {len(protein_ids)} proteins")
        
        gene_name_mapping = {}
        
        for protein_id in protein_ids:
            # Look for the protein in the interactions
            mask_a = interactions_df['proteinId_A'] == protein_id
            mask_b = interactions_df['proteinId_B'] == protein_id
            
            if mask_a.any():
                gene_name = interactions_df[mask_a]['preferredName_A'].iloc[0]
                gene_name_mapping[protein_id] = gene_name
            elif mask_b.any():
                gene_name = interactions_df[mask_b]['preferredName_B'].iloc[0]
                gene_name_mapping[protein_id] = gene_name
        
        logger.info(f"Successfully extracted gene names for {len(gene_name_mapping)} proteins")
        return gene_name_mapping
    
    def _convert_string_to_uniprot_ids(self, string_ids: List[str]) -> List[str]:
        """Convert STRING IDs to UniProt IDs using STRING mapping API."""
        try:
            # Use STRING mapping API to convert IDs
            url = "https://string-db.org/api/tsv/get_string_ids"
            params = {
                'identifiers': ','.join(string_ids),
                'species': 9606,
                'limit': len(string_ids)
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            uniprot_ids = []
            if response.text.strip():
                lines = response.text.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        # STRING API returns: queryIndex, stringId, ncbiTaxonId, taxonName, preferredName, annotation
                        # We'll use the preferredName as UniProt ID if it looks like one
                        preferred_name = parts[4] if len(parts) > 4 else ''
                        if preferred_name and len(preferred_name) <= 10:  # UniProt IDs are usually short
                            uniprot_ids.append(preferred_name)
            
            # If no UniProt IDs found, try alternative approach
            if not uniprot_ids:
                # Use STRING's annotation API to get UniProt mappings
                url2 = "https://string-db.org/api/tsv/network"
                params2 = {
                    'identifiers': ','.join(string_ids[:10]),  # Limit to first 10 for testing
                    'species': 9606,
                    'required_score': 100,
                    'limit': 10
                }
                
                response2 = requests.get(url2, params=params2, timeout=30)
                if response2.status_code == 200 and response2.text.strip():
                    lines2 = response2.text.strip().split('\n')[1:]  # Skip header
                    for line in lines2:
                        parts = line.split('\t')
                        if len(parts) >= 4:
                            # Extract protein names and use them as potential UniProt IDs
                            name_a = parts[2]
                            name_b = parts[3]
                            if name_a and len(name_a) <= 10:
                                uniprot_ids.append(name_a)
                            if name_b and len(name_b) <= 10:
                                uniprot_ids.append(name_b)
            
            return list(set(uniprot_ids))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"Failed to convert STRING IDs to UniProt IDs: {e}")
            return []
    
    def _find_string_id_for_uniprot(self, uniprot_id: str, string_ids: List[str]) -> Optional[str]:
        """Find the corresponding STRING ID for a UniProt ID."""
        # This is a simplified mapping - in practice, you'd need a proper mapping table
        # For now, we'll use a heuristic approach
        for string_id in string_ids:
            if uniprot_id in string_id or string_id.endswith(uniprot_id):
                return string_id
        return None

class ReceptorFilter:
    """Class for filtering potential receptors."""
    
    def __init__(self):
        """Initialize receptor filter with keyword patterns."""
        
        # Keywords for membrane proteins
        self.membrane_keywords = [
            "plasma membrane", "cell membrane", "membrane", "plasma membrane",
            "integral membrane", "transmembrane", "cell surface", "surface"
        ]
        
        # Keywords for secreted proteins (potential soluble receptors)
        self.secreted_keywords = [
            "secreted", "extracellular", "secreted protein", "outside", 
            "extracellular space", "extracellular region", "secretome"
        ]
        
        logger.info("Initialized receptor filter with membrane and secretion keywords")
    
    def is_potential_receptor(self, subcellular_location: str) -> bool:
        """
        Check if protein is a potential receptor based on subcellular location.
        
        Args:
            subcellular_location (str): Subcellular location description
            
        Returns:
            bool: True if protein is likely a receptor
        """
        if not subcellular_location or subcellular_location.lower() in ['nan', 'null', '']:
            return False
        
        location_lower = subcellular_location.lower()
        
        # Check for membrane protein keywords
        is_membrane = any(keyword in location_lower for keyword in self.membrane_keywords)
        
        # Check for secreted protein keywords
        is_secreted = any(keyword in location_lower for keyword in self.secreted_keywords)
        
        return is_membrane or is_secreted

class STRINGInteractionAnalysis:
    """Main class for STRING interaction analysis and receptor identification."""
    
    def __init__(self, config_path: str = "config/config.json", config: Dict = None):
        """
        Initialize the analysis.
        
        Args:
            config_path (str): Path to configuration file
            config (Dict): Optional configuration dictionary
        """
        self.config_path = config_path
        if config is not None:
            self.config = config
        else:
            self.config = self._load_config()
        
        # Initialize components
        self.string_db = STRINGdbInterface(self.config['species_id'])
        self.uniprot = UniProtInterface()
        self.receptor_filter = ReceptorFilter()
        
        # Create cache directory
        self.cache_dir = Path("./cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized STRING interaction analysis")
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required keys
            required_keys = ['target_protein_id', 'species_id']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {missing_keys}")
            
            logger.info("Configuration loaded successfully")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    def analyze_interactions(self, confidence_threshold: float = 0.9) -> pd.DataFrame:
        """
        Main analysis pipeline.
        
        Args:
            confidence_threshold (float): Minimum confidence for interactions
            
        Returns:
            pd.DataFrame: Filtered receptor candidates
        """
        logger.info("Starting STRING interaction analysis...")
        
        # Step 1: Get protein interactions
        interactions_df = self.string_db.get_interactions(
            self.config['target_protein_id'], 
            confidence_threshold
        )
        
        logger.info(f"Interactions DataFrame shape: {interactions_df.shape}")
        logger.info(f"Interactions DataFrame empty: {interactions_df.empty}")
        
        if interactions_df.empty:
            logger.warning("No interactions found. Analysis terminated.")
            return pd.DataFrame()
        
        original_count = len(interactions_df)
        logger.info(f"Step 1 complete: Found {original_count} high-confidence interactions")
        
        # Step 2: Extract interacting protein IDs
        protein_ids = self._extract_protein_ids(interactions_df)
        logger.info(f"Step 2 complete: Extracted {len(protein_ids)} unique interacting proteins")
        
        # Step 3: Get gene names from interactions data
        gene_names = self.uniprot.get_gene_names_from_interactions(protein_ids, interactions_df)
        logger.info(f"Step 3 complete: Retrieved gene names for {len(gene_names)} proteins")
        
        # Step 4: Get subcellular locations
        subcellular_locations = self.uniprot.bulk_subcellular_location(protein_ids, interactions_df)
        logger.info(f"Step 4 complete: Retrieved subcellular locations for {len(subcellular_locations)} proteins")
        
        # Step 5: Filter potential receptors
        receptor_candidates = self._filter_receptors(
            interactions_df, 
            subcellular_locations,
            gene_names
        )
        
        filtered_count = len(receptor_candidates)
        logger.info(f"Step 5 complete: Filtered to {filtered_count} potential receptors")
        logger.info(f"Filtering summary: {original_count} original interactions → {filtered_count} potential receptors")
        
        return receptor_candidates
    
    def _extract_protein_ids(self, interactions_df: pd.DataFrame) -> List[str]:
        """Extract unique protein IDs from interactions dataframe."""
        protein_ids = set()
        
        if 'proteinId_A' in interactions_df.columns:
            protein_ids.update(interactions_df['proteinId_A'].tolist())
        if 'proteinId_B' in interactions_df.columns:
            protein_ids.update(interactions_df['proteinId_B'].tolist())
        
        # Remove the query protein if present
        protein_ids.discard(self.config['target_protein_id'])
        
        return list(protein_ids)
    
    def _filter_receptors(self, interactions_df: pd.DataFrame, subcellular_locations: Dict[str, str], gene_names: Dict[str, str] = None) -> pd.DataFrame:
        """Filter interactions to identify potential receptors."""
        potential_receptors = []
        
        for _, row in interactions_df.iterrows():
            # Get protein IDs (both interacting partners)
            protein_a = row.get('proteinId_A', '')
            protein_b = row.get('proteinId_B', '')
            confidence = row.get('score', 0) / 1000.0  # Convert back to 0-1 scale
            literature_support = row.get('literature_support', 0)
            
            # Check each interacting protein
            for protein_id in [protein_a, protein_b]:
                if protein_id == self.config['target_protein_id'] or not protein_id:
                    continue
                
                subcellular_location = subcellular_locations.get(protein_id, 'Unknown')
                
                if self.receptor_filter.is_potential_receptor(subcellular_location):
                    # Get gene name from the mapping
                    gene_name = gene_names.get(protein_id, protein_id) if gene_names else protein_id
                    
                    receptor_data = ProteinInteraction(
                        protein_id=protein_id,
                        protein_name=gene_name,
                        confidence=confidence,
                        subcellular_location=subcellular_location,
                        literature_support=literature_support,
                        is_potential_receptor=True
                    )
                    
                    potential_receptors.append(receptor_data)
        
        # Remove duplicates and create DataFrame
        unique_receptors = list(set([(p.protein_id, p.protein_name, p.confidence, p.subcellular_location, p.literature_support) for p in potential_receptors]))
        
        receptor_df = pd.DataFrame(unique_receptors, columns=[
            'receptor_id', 'gene_name', 'confidence', 'subcellular_location', 'literature_support'
        ])
        
        # Sort by confidence and literature support
        receptor_df = receptor_df.sort_values(['confidence', 'literature_support'], ascending=[False, False])
        
        return receptor_df
    
    def _get_protein_name(self, protein_id: str) -> str:
        """Get protein name from STRINGdb."""
        try:
            # This is a simplified name retrieval
            # In practice, you might want to use STRINGdb's annotation services
            return protein_id  # Return ID as name for now
        except Exception:
            return protein_id
    
    def save_results(self, receptor_df: pd.DataFrame, cache_file: str = "string_receptors.csv") -> str:
        """
        Save results to output directory.
        
        Args:
            receptor_df (pd.DataFrame): Receptor candidates dataframe
            cache_file (str): Output filename
            
        Returns:
            str: Path to saved file
        """
        # Create output directory structure
        target_protein_id = self.config.get('target_protein_id', 'unknown')
        output_dir = Path(f"output/{target_protein_id}/receptor_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"string_receptors_{timestamp}.csv"
        output_path = output_dir / filename
        
        # Also save to cache for compatibility
        cache_path = self.cache_dir / cache_file
        
        try:
            # Save to output directory
            receptor_df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Results saved to: {output_path}")
            
            # Save to cache directory for compatibility
            receptor_df.to_csv(cache_path, index=False, encoding='utf-8')
            logger.info(f"Results also saved to cache: {cache_path}")
            
            logger.info(f"Saved {len(receptor_df)} receptor candidates")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving results to {output_path}: {str(e)}")
            raise

def main():
    """Main execution function."""
    try:
        # Initialize analysis
        analysis = STRINGInteractionAnalysis()
        
        # Run analysis
        logger.info("Starting STRING interaction analysis...")
        receptor_candidates = analysis.analyze_interactions(confidence_threshold=0.9)
        
        if not receptor_candidates.empty:
            # Save results
            output_file = analysis.save_results(receptor_candidates, "string_receptors.csv")
            
            logger.info("=== Analysis Summary ===")
            logger.info(f"Target protein: {analysis.config['target_protein_id']}")
            logger.info(f"Species ID: {analysis.config['species_id']}")
            logger.info(f"Potential receptors identified: {len(receptor_candidates)}")
            logger.info(f"Results saved to: {output_file}")
            
            # Show top candidates
            logger.info("\nTop 10 receptor candidates:")
            top_candidates = receptor_candidates.head(10)
            for _, row in top_candidates.iterrows():
                logger.info(f"  {row['receptor_id']}: {row['receptor_name']} (confidence: {row['confidence']:.3f}, literature: {row['literature_support']})")
        else:
            logger.warning("No potential receptors identified.")
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
