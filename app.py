import streamlit as st
import numpy as np
from midiutil import MIDIFile
import io

st.title("🧬 BioMusic")
st.write("DNA & 蛋白质序列转音乐（音乐化版）")

# ========== 五声音阶音池（C大调，不会难听） ==========
PENTATONIC_LOW = [48, 50, 52, 55, 57]      # 低音区 C3-D3-E3-G3-A3
PENTATONIC_MID = [60, 62, 64, 67, 69]      # 中音区 C4-D4-E4-G4-A4
PENTATONIC_HIGH = [72, 74, 76, 79, 81]     # 高音区 C5-D5-E5-G5-A5

# ========== 氨基酸映射：性质 → 音区 + 时值 + 音色 ==========
AA_MUSIC_MAP = {
    # 疏水：低音 + 长音（沉稳）
    'A': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'V': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'I': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'L': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'M': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'F': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    'W': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80, 'track': 0},
    
    # 亲水：中音 + 中音（流动）
    'S': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    'T': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    'C': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    'Y': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    'N': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    'Q': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90, 'track': 0},
    
    # 酸性：高音 + 短音（尖锐跳跃）
    'D': {'pool': PENTATONIC_HIGH, 'duration': 0.25, 'vol': 100, 'track': 0},
    'E': {'pool': PENTATONIC_HIGH, 'duration': 0.25, 'vol': 100, 'track': 0},
    
    # 碱性：中高音 + 跳跃节奏
    'K': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95, 'track': 0},
    'R': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95, 'track': 0},
    'H': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95, 'track': 0},
    
    # 特殊：装饰音
    'G': {'pool': PENTATONIC_MID, 'duration': 0.25, 'vol': 70, 'track': 0},
    'P': {'pool': PENTATONIC_MID, 'duration': 0.25, 'vol': 70, 'track': 0},
}

DNA_MAP = {
    'A': {'note': 60, 'freq': 261.63, 'dur': 0.5},
    'T': {'note': 62, 'freq': 293.66, 'dur': 