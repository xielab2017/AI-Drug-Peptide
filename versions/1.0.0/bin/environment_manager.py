#!/usr/bin/env python3
"""
Peptide AI Environment Manager
Complementary Python module for managing the peptide development environment

This module provides Python-based functionality that complements the shell script
for environment setup, validation, and management.
"""

import os
import sys
import json
import subprocess
import platform
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

class PeptideEnvironmentManager:
    """Main class for managing the peptide development environment"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.peptide_env'
        self.models_dir = Path.home() / 'peptide_models'
        self.config_file = self.config_dir / 'config.json'
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'python_executable': sys.executable,
        }
        
        # Add conda info if available
        try:
            conda_info = subprocess.run(['conda', 'info', '--json'], 
                                       capture_output=True, text=True)
            if conda_info.returncode == 0:
                info['conda'] = json.loads(conda_info.stdout)
        except FileNotFoundError:
            info['conda'] = None
            
        return info
        
    def check_conda_environment(self, env_name: str = 'peptide_dev') -> bool:
        """Check if conda environment exists and is properly configured"""
        try:
            result = subprocess.run(['conda', 'env', 'list'], 
                                  capture_output=True, text=True, check=True)
            
            environments = result.stdout
            return env_name in environments
            
        except subprocess.CalledProcessError:
            self.logger.error("Conda not found or not available")
            return False
            
    def verify_package_installation(self, package_name: str) -> Tuple[bool, str]:
        """Verify if a Python package is installed and get version info"""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Unknown')
            return True, version
        except ImportError:
            return False, "Not installed"
            
    def verify_command_line_tool(self, command: str) -> Tuple[bool, str]:
        """Verify if a command line tool is available"""
        try:
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "Not available"
            
    def create_comprehensive_report(self) -> str:
        """Generate comprehensive environment validation report"""
        
        # System info
        system_info = self.get_system_info()
        
        # Check conda environment
        conda_env_ok = self.check_conda_environment()
        
        # Define tools and packages to check
        command_line_tools = {
            'git': 'Git',
            'conda': 'Conda/Anaconda',
            'docker': 'Docker',
        }
        
        python_packages = {
            'Bio': 'Biopython',
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'sklearn': 'Scikit-learn',
            'matplotlib': 'Matplotlib',
            'seaborn': 'Seaborn',
            'streamlit': 'Streamlit',
            'transformers': 'Transformers',
            'torch': 'PyTorch',
            'reportlab': 'ReportLab',
            'py2neo': 'Py2Neo',
            'sqlalchemy': 'SQLAlchemy',
            'psycopg2': 'Psycopg2',
        }
        
        # Generate report
        report_lines = [
            "="*80,
            "PEPTIDE AI DEVELOPMENT ENVIRONMENT - COMPREHENSIVE REPORT",
            f"Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}",
            "="*80,
            "",
            "SYSTEM INFORMATION:",
            "-"*40,
            f"Platform: {system_info['platform']}",
            f"System: {system_info['system']} {system_info['release']}",
            f"Architecture: {system_info['machine']} ({system_info['architecture'][0]})",
            f"Python: {system_info['python_version']}",
            f"Python Executable: {system_info['python_executable']}",
            "",
        ]
        
        # Conda environment status
        report_lines.extend([
            "CONDA ENVIRONMENT STATUS:",
            "-"*40,
            f"Environment 'peptide_dev': {'✓ EXISTS' if conda_env_ok else '✗ NOT FOUND'}",
            "",
        ])
        
        # Command line tools status
        report_lines.extend([
            "COMMAND LINE TOOLS STATUS:",
            "-"*40,
        ])
        
        for cmd, name in command_line_tools.items():
            available, version = self.verify_command_line_tool(cmd)
            status = "✓ AVAILABLE" if available else "✗ NOT FOUND"
            report_lines.append(f"{name:20} | {status}")
            if available and version:
                report_lines.append(f"{' '*20}  Version: {version}")
        
        report_lines.append("")
        
        # Python packages status
        report_lines.extend([
            "PYTHON PACKAGES STATUS:",
            "-"*40,
        ])
        
        for package, name in python_packages.items():
            installed, version = self.verify_package_installation(package)
            status = "✓ INSTALLED" if installed else "✗ NOT INSTALLED"
            report_lines.append(f"{name:20} | {status}")
            if installed and version:
                report_lines.append(f"{' '*20}  Version: {version}")
        
        report_lines.extend([
            "",
            "SPECIAL REQUIREMENTS:",
            "-"*40,
            f"SignalP 6.0: Manual download required from DTU",
            f"ProGen2 Weights: Check /data/models/ directory",
            f"Database Setup: Run configuration scripts in ~/.peptide_env/",
            "",
            "DIRECTORIES:",
            "-"*40,
            f"Config Directory: {self.config_dir} {'✓ EXISTS' if self.config_dir.exists() else '✗ NOT FOUND'}",
            f"Models Directory: {self.models_dir} {'✓ EXISTS' if self.models_dir.exists() else '✗ NOT FOUND'}",
            "",
            "NEXT STEPS:",
            "-"*40,
            "1. Activate environment: conda activate peptide_dev",
            "2. Verify all installations above",
            "3. Set up databases if needed",
            "4. Download SignalP 6.0 manually",
            "5. Run ProGen2 weight download when ready",
            "",
            "="*80,
        ])
        
        return "\n".join(report_lines)
        
    def save_configuration(self, config: Dict) -> None:
        """Save environment configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.logger.info(f"Configuration saved to {self.config_file}")
        
    def load_configuration(self) -> Dict:
        """Load environment configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def test_database_connections(self) -> Dict:
        """Test database connections"""
        results = {}
        
        # Test PostgreSQL connection
        try:
            import psycopg2
            # This would require actual credentials
            results['postgresql'] = {'status': 'Package available', 'connected': False}
        except ImportError:
            results['postgresql'] = {'status': 'Package not installed', 'connected': False}
            
        # Test Neo4j connection
        try:
            from py2neo import Graph
            # This would require actual connection URI
            results['neo4j'] = {'status': 'Package available', 'connected': False}
        except ImportError:
            results['neo4j'] = {'status': 'Package not installed', 'connected': False}
            
        return results
        
    def create_sample_analysis_script(self) -> None:
        """Create a sample peptide analysis script to test the environment"""
        
        script_content = '''#!/usr/bin/env python3
"""
Sample Peptide Analysis Script
Demonstrates basic functionality of the peptide development environment
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_protein
import streamlit as st

def analyze_peptide_sequence(sequence: str) -> dict:
    """Basic peptide sequence analysis"""
    
    peptide = Seq(sequence, generic_protein)
    
    analysis = {
        'sequence': str(peptide),
        'length': len(peptide),
        'molecular_weight': calculate_molecular_weight(peptide),
        'amino_acid_composition': dict(peptide.count()),
        'hydrophobicity': calculate_hydrophobicity(peptide),
    }
    
    return analysis

def calculate_molecular_weight(peptide):
    """Calculate approximate molecular weight"""
    # Amino acid weights in Daltons
    weights = {
        'A': 89.09, 'R': 174.20, 'N': 132.12, 'D': 133.10, 'C': 121.16,
        'Q': 146.15, 'E': 147.13, 'G': 75.07, 'H': 155.16, 'I': 131.17,
        'L': 131.17, 'K': 146.19, 'M': 149.21, 'F': 165.19, 'P': 115.13,
        'S': 105.09, 'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
    }
    
    # Subtract water (18.015) for each peptide bond
    total_weight = sum(weights.get(aa, 0) for aa in peptide)
    return total_weight - (len(peptide) - 1) * 18.015

def calculate_hydrophobicity(peptide):
    """Calculate hydrophobicity using Kyte-Doolittle scale"""
    
    hydropathy_scale = {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
    }
    
    return sum(hydropathy_scale.get(aa, 0) for aa in peptide) / len(peptide)

def create_streamlit_app():
    """Create a simple Streamlit app for peptide analysis"""
    
    st.title("Peptide Analysis Dashboard")
    st.write("Enter a peptide sequence to analyze:")
    
    sequence = st.text_input("Peptide Sequence:", "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG")
    
    if sequence and sequence.strip():
        try:
            analysis = analyze_peptide_sequence(sequence.strip())
            
            st.subheader("Analysis Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Length", analysis['length'])
                st.metric("Molecular Weight", f"{analysis['molecular_weight']:.2f} Da")
                st.metric("Hydrophobicity", f"{analysis['hydrophobicity']:.3f}")
            
            with col2:
                st.subheader("Amino Acid Composition")
                composition_df = pd.DataFrame(
                    list(analysis['amino_acid_composition'].items()),
                    columns=['Amino Acid', 'Count']
                )
                st.dataframe(composition_df, use_container_width=True)
                
            # Visualization
            fig, ax = plt.subplots()
            ax.bar(composition_df['Amino Acid'], composition_df['Count'])
            ax.set_xlabel('Amino Acid')
            ax.set_ylabel('Count')
            ax.set_title('Amino Acid Composition')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error analyzing sequence: {e}")

if __name__ == "__main__":
    # Run Streamlit app
    import subprocess
    import sys
    
    print("Starting Streamlit app...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
'''
        
        script_path = self.config_dir / 'sample_analysis.py'
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        # Make it executable
        os.chmod(script_path, 0o755)
        
        self.logger.info(f"Sample analysis script created at {script_path}")
        
    def run_environment_test(self) -> bool:
        """Run comprehensive environment test"""
        self.logger.info("Running environment test...")
        
        # Test basic imports
        test_imports = [
            'numpy', 'pandas', 'Bio', 'sklearn', 
            'matplotlib', 'seaborn', 'streamlit'
        ]
        
        failed_imports = []
        for module in test_imports:
            try:
                importlib.import_module(module)
                self.logger.info(f"✓ {module} import successful")
            except ImportError as e:
                self.logger.error(f"✗ {module} import failed: {e}")
                failed_imports.append(module)
                
        # Test file operations
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"✓ Models directory accessible: {self.models_dir}")
        except PermissionError:
            self.logger.error(f"✗ Permission denied for models directory: {self.models_dir}")
            failed_imports.append("models_directory")
            
        # Return test result
        success = len(failed_imports) == 0
        if success:
            self.logger.info("✓ Environment test passed!")
        else:
            self.logger.error(f"✗ Environment test failed. Issues: {failed_imports}")
            
        return success


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Peptide Environment Manager")
    parser.add_argument('--report', action='store_true', 
                       help='Generate comprehensive environment report')
    parser.add_argument('--test', action='store_true',
                       help='Run environment test')
    parser.add_argument('--sample-script', action='store_true',
                       help='Create sample analysis script')
    
    args = parser.parse_args()
    
    manager = PeptideEnvironmentManager()
    
    if args.report:
        report = manager.create_comprehensive_report()
        print(report)
        
        # Save report to file
        report_path = manager.config_dir / 'environment_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")
        
    if args.test:
        success = manager.run_environment_test()
        sys.exit(0 if success else 1)
        
    if args.sample_script:
        manager.create_sample_analysis_script()
        
    if not any([args.report, args.test, args.sample_script]):
        parser.print_help()


if __name__ == "__main__":
    main()
