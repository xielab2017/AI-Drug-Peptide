#!/usr/bin/env python3
"""
物种ID映射表
提供常用物种的名称到NCBI物种ID的映射
"""

SPECIES_MAPPING = {
    # 常用模式生物
    "Human": {"ncbi_id": 9606, "scientific_name": "Homo sapiens", "common_name": "Human"},
    "Mouse": {"ncbi_id": 10090, "scientific_name": "Mus musculus", "common_name": "Mouse"},
    "Rat": {"ncbi_id": 10116, "scientific_name": "Rattus norvegicus", "common_name": "Rat"},
    "Cow": {"ncbi_id": 9913, "scientific_name": "Bos taurus", "common_name": "Cow"},
    "Pig": {"ncbi_id": 9823, "scientific_name": "Sus scrofa", "common_name": "Pig"},
    "Chicken": {"ncbi_id": 9031, "scientific_name": "Gallus gallus", "common_name": "Chicken"},
    "Zebrafish": {"ncbi_id": 7955, "scientific_name": "Danio rerio", "common_name": "Zebrafish"},
    "Fruitfly": {"ncbi_id": 7227, "scientific_name": "Drosophila melanogaster", "common_name": "Fruit fly"},
    "Worm": {"ncbi_id": 6239, "scientific_name": "Caenorhabditis elegans", "common_name": "Nematode"},
    "Yeast": {"ncbi_id": 559292, "scientific_name": "Saccharomyces cerevisiae", "common_name": "Baker's yeast"},
    
    # 灵长类动物
    "Chimpanzee": {"ncbi_id": 9598, "scientific_name": "Pan troglodytes", "common_name": "Chimpanzee"},
    "Macaque": {"ncbi_id": 9544, "scientific_name": "Macaca mulatta", "common_name": "Rhesus macaque"},
    "Marmoset": {"ncbi_id": 9483, "scientific_name": "Callithrix jacchus", "common_name": "Common marmoset"},
    
    # 其他哺乳动物
    "Dog": {"ncbi_id": 9615, "scientific_name": "Canis lupus familiaris", "common_name": "Dog"},
    "Cat": {"ncbi_id": 9685, "scientific_name": "Felis catus", "common_name": "Cat"},
    "Horse": {"ncbi_id": 9796, "scientific_name": "Equus caballus", "common_name": "Horse"},
    "Sheep": {"ncbi_id": 9940, "scientific_name": "Ovis aries", "common_name": "Sheep"},
    "Goat": {"ncbi_id": 9925, "scientific_name": "Capra hircus", "common_name": "Goat"},
    
    # 鸟类
    "Duck": {"ncbi_id": 8839, "scientific_name": "Anas platyrhynchos", "common_name": "Mallard duck"},
    "Turkey": {"ncbi_id": 9103, "scientific_name": "Meleagris gallopavo", "common_name": "Turkey"},
    
    # 鱼类
    "Medaka": {"ncbi_id": 8090, "scientific_name": "Oryzias latipes", "common_name": "Japanese medaka"},
    "Fugu": {"ncbi_id": 31033, "scientific_name": "Takifugu rubripes", "common_name": "Japanese pufferfish"},
    "Tilapia": {"ncbi_id": 8128, "scientific_name": "Oreochromis niloticus", "common_name": "Nile tilapia"},
    
    # 两栖动物
    "Frog": {"ncbi_id": 8364, "scientific_name": "Xenopus tropicalis", "common_name": "Western clawed frog"},
    "Axolotl": {"ncbi_id": 8296, "scientific_name": "Ambystoma mexicanum", "common_name": "Axolotl"},
    
    # 爬行动物
    "Lizard": {"ncbi_id": 8504, "scientific_name": "Anolis carolinensis", "common_name": "Green anole"},
    "Snake": {"ncbi_id": 8570, "scientific_name": "Python bivittatus", "common_name": "Burmese python"},
    
    # 无脊椎动物
    "Mosquito": {"ncbi_id": 7159, "scientific_name": "Aedes aegypti", "common_name": "Yellow fever mosquito"},
    "Honeybee": {"ncbi_id": 7460, "scientific_name": "Apis mellifera", "common_name": "Western honey bee"},
    "Silkworm": {"ncbi_id": 7091, "scientific_name": "Bombyx mori", "common_name": "Silkworm"},
    
    # 植物
    "Arabidopsis": {"ncbi_id": 3702, "scientific_name": "Arabidopsis thaliana", "common_name": "Thale cress"},
    "Rice": {"ncbi_id": 4530, "scientific_name": "Oryza sativa", "common_name": "Rice"},
    "Maize": {"ncbi_id": 4577, "scientific_name": "Zea mays", "common_name": "Maize"},
    "Tomato": {"ncbi_id": 4081, "scientific_name": "Solanum lycopersicum", "common_name": "Tomato"},
    
    # 细菌
    "Ecoli": {"ncbi_id": 562, "scientific_name": "Escherichia coli", "common_name": "E. coli"},
    "Bacillus": {"ncbi_id": 1423, "scientific_name": "Bacillus subtilis", "common_name": "B. subtilis"},
    "Pseudomonas": {"ncbi_id": 287, "scientific_name": "Pseudomonas aeruginosa", "common_name": "P. aeruginosa"},
}

def get_species_info(species_name: str) -> dict:
    """
    获取物种信息
    
    Args:
        species_name: 物种名称（支持多种格式）
    
    Returns:
        包含ncbi_id, scientific_name, common_name的字典
    """
    # 尝试直接匹配
    if species_name in SPECIES_MAPPING:
        return SPECIES_MAPPING[species_name]
    
    # 尝试不区分大小写匹配
    for key, value in SPECIES_MAPPING.items():
        if key.lower() == species_name.lower():
            return value
    
    # 尝试匹配科学名称
    for key, value in SPECIES_MAPPING.items():
        if value["scientific_name"].lower() == species_name.lower():
            return value
    
    # 尝试匹配通用名称
    for key, value in SPECIES_MAPPING.items():
        if value["common_name"].lower() == species_name.lower():
            return value
    
    # 如果都没找到，返回None
    return None

def get_species_list() -> list:
    """获取所有支持的物种列表"""
    return list(SPECIES_MAPPING.keys())

def validate_species_list(species_list: list) -> tuple:
    """
    验证物种列表
    
    Args:
        species_list: 物种名称列表
    
    Returns:
        (valid_species, invalid_species): 有效和无效的物种列表
    """
    valid_species = []
    invalid_species = []
    
    for species in species_list:
        species_info = get_species_info(species)
        if species_info:
            valid_species.append(species)
        else:
            invalid_species.append(species)
    
    return valid_species, invalid_species

def main():
    """测试函数"""
    print("支持的物种列表:")
    for species in get_species_list():
        info = get_species_info(species)
        print(f"  {species}: {info['scientific_name']} (NCBI ID: {info['ncbi_id']})")
    
    print("\n测试物种验证:")
    test_species = ["Human", "Mouse", "InvalidSpecies", "Rat"]
    valid, invalid = validate_species_list(test_species)
    print(f"有效物种: {valid}")
    print(f"无效物种: {invalid}")

if __name__ == "__main__":
    main()
