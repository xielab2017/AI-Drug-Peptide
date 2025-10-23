#!/usr/bin/env python3
"""
AI-Drug Peptide - 核心分析脚本包
包含所有核心分析功能的Python脚本
"""

__version__ = "1.0.0"
__description__ = "Core analysis scripts for AI-Drug Peptide platform"

# 导入所有核心脚本
from .workflow import *
from .step1_string_interaction import *
from .step2_docking_prediction import *
from .step3_conservation_check import *
from .step4_merge_results import *
from .input_init import *
from .secretion_analysis import *
from .peptide_optim import *
from .report_generator import *
from .visual_dashboard import *

__all__ = [
    'workflow',
    'step1_string_interaction',
    'step2_docking_prediction', 
    'step3_conservation_check',
    'step4_merge_results',
    'input_init',
    'secretion_analysis',
    'peptide_optim',
    'report_generator',
    'visual_dashboard'
]
