"""
Database Wrappers - 蛋白/肽相关数据库API封装
"""

import requests
import json
from typing import List, Dict, Optional


class UniProtClient:
    """UniProt 数据库客户端"""
    
    BASE_URL = "https://rest.uniprot.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
    
    def search(
        self, 
        query: str, 
        size: int = 10,
        fields: List[str] = None
    ) -> List[Dict]:
        """
        搜索 UniProt
        
        Args:
            query: 搜索查询
            size: 返回数量
            fields: 返回字段
            
        Returns:
            蛋白列表
        """
        url = f"{self.BASE_URL}/search"
        
        params = {
            "query": query,
            "size": size
        }
        
        if fields:
            params["fields"] = ",".join(fields)
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        for hit in data.get("results", []):
            results.append({
                "accession": hit.get("primaryAccession"),
                "id": hit.get("uniProtkbId"),
                "protein_name": hit.get("proteinName", {}).get("fullName", {}).get("value", ""),
                "organism": hit.get("organism", {}).get("scientificName", ""),
                "sequence": hit.get("sequence", {}).get("value", ""),
                "length": hit.get("sequence", {}).get("length", 0)
            })
        
        return results
    
    def get_protein(self, accession: str) -> Dict:
        """
        获取蛋白详细信息
        
        Args:
            accession: UniProt accession
            
        Returns:
            蛋白信息
        """
        url = f"{self.BASE_URL}/uniprotkb/{accession}"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "accession": data.get("primaryAccession"),
            "id": data.get("uniProtkbId"),
            "protein_name": data.get("proteinName", {}).get("fullName", {}).get("value", ""),
            "organism": data.get("organism", {}).get("scientificName", ""),
            "sequence": data.get("sequence", {}).get("value", ""),
            "length": data.get("sequence", {}).get("length", 0),
            "function": data.get("function", [{}])[0].get("value", ""),
            "keywords": [kw.get("text") for kw in data.get("keywords", [])]
        }
    
    def download_fasta(self, accession: str) -> str:
        """
        下载 FASTA 格式
        
        Args:
            accession: UniProt accession
            
        Returns:
            FASTA 序列
        """
        url = f"{self.BASE_URL}/uniprotkb/{accession}.fasta"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.text


class PDBClient:
    """PDB 数据库客户端"""
    
    BASE_URL = "https://data.rcsb.org/rest/v1"
    
    def __init__(self):
        pass
    
    def get_entry(self, pdb_id: str) -> Dict:
        """
        获取 PDB 条目
        
        Args:
            pdb_id: PDB ID (如 1ABC)
            
        Returns:
            PDB 条目信息
        """
        url = f"{self.BASE_URL}/core/entry/{pdb_id.upper()}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def search(
        self, 
        query: str, 
        size: int = 10
    ) -> List[Dict]:
        """
        搜索 PDB
        
        Args:
            query: 搜索查询
            size: 返回数量
            
        Returns:
            PDB 条目列表
        """
        url = f"{self.BASE_URL}/core/entry"
        
        params = {
            "query": query,
            "page_size": size
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        return [
            {
                "pdb_id": h.get("rcsb_entry_container_identifiers", {}).get("pdb_id", ""),
                "title": h.get("struct", {}).get("title", ""),
                "resolution": h.get("rcsb_entry_info", {}).get("resolution_combined", [None])[0],
                "method": h.get("exptl", [{}])[0].get("method", "")
            }
            for h in data.get("result_set", [{}]).get("hits", [])
        ]
    
    def get_sequence(self, pdb_id: str) -> str:
        """
        获取 PDB 序列
        
        Args:
            pdb_id: PDB ID
            
        Returns:
            蛋白序列
        """
        entry = self.get_entry(pdb_id)
        
        # 提取多肽链序列
        sequences = []
        for poly in entry.get("polymer_entities", []):
            seq = poly.get("entity_poly", {}).get("pdbx_seq_one_letter_code", "")
            if seq:
                sequences.append(seq)
        
        return "\n".join(sequences)


class AlphaFoldDBClient:
    """AlphaFold 数据库客户端"""
    
    BASE_URL = "https://alphafold.ebi.ac.uk/api"
    
    def __init__(self):
        pass
    
    def get_prediction(self, uniprot_id: str) -> Dict:
        """
        获取 AlphaFold 预测
        
        Args:
            uniprot_id: UniProt ID
            
        Returns:
            预测信息
        """
        url = f"{self.BASE_URL}/prediction/{uniprot_id}"
        
        response = requests.get(url)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            entry = data[0]
            return {
                "uniprot_id": entry.get("uniProtId"),
                "pdb_url": entry.get("pdbUrl"),
                "predicted_aligned_error_url": entry.get("predictedAlignedErrorUrl"),
                "pae_plot_url": entry.get("paePlotUrl"),
                "model_confidence": entry.get("modelConfidence"),
                "qm8_mean_predicted_aligned_error": entry.get("qm8MeanPredictedAlignedError")
            }
        
        return None


# CLI 测试
if __name__ == "__main__":
    # 测试 UniProt
    print("=== UniProt 测试 ===")
    uniprot = UniProtClient()
    results = uniprot.search("kinase human", size=3)
    for r in results:
        print(f"- {r['accession']}: {r['protein_name'][:40]}")
    
    # 测试 PDB
    print("\n=== PDB 测试 ===")
    pdb = PDBClient()
    results = pdb.search("hemoglobin", size=3)
    for r in results:
        print(f"- {r['pdb_id']}: {r['title'][:40]}")
    
    # 测试 AlphaFold
    print("\n=== AlphaFold 测试 ===")
    af = AlphaFoldDBClient()
    result = af.get_prediction("P53_HUMAN")
    if result:
        print(f"Found: {result['uniprot_id']}")
        print(f"Confidence: {result['model_confidence']}")
