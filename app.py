import streamlit as st
import numpy as np
from midiutil import MIDIFile
import io

st.title("🧬 BioMusic")
st.write("DNA & 蛋白质序列转音乐（音乐化版）")

PENTATONIC_LOW = [48, 50, 52, 55, 57]
PENTATONIC_MID = [60, 62, 64, 67, 69]
PENTATONIC_HIGH = [72, 74, 76, 79, 81]

AA_MUSIC_MAP = {
    'A': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'V': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'I': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'L': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'M': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'F': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'W': {'pool': PENTATONIC_LOW, 'duration': 1.0, 'vol': 80},
    'S': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'T': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'C': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'Y': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'N': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'Q': {'pool': PENTATONIC_MID, 'duration': 0.5, 'vol': 90},
    'D': {'pool': PENTATONIC_HIGH, 'duration': 0.25, 'vol': 100},
    'E': {'pool': PENTATONIC_HIGH, 'duration': 0.25, 'vol': 100},
    'K': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95},
    'R': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95},
    'H': {'pool': PENTATONIC_HIGH, 'duration': 0.5, 'vol': 95},
    'G': {'pool': PENTATONIC_MID, 'duration': 0.25, 'vol': 70},
    'P': {'pool': PENTATONIC_MID, 'duration': 0.25, 'vol': 70},
}

DNA_MAP = {
    'A': {'note': 60, 'freq': 261.63, 'dur': 0.5},
    'T': {'note': 62, 'freq': 293.66, 'dur': 0.5},
    'C': {'note': 64, 'freq': 329.63, 'dur': 0.5},
    'G': {'note': 67, 'freq': 392.00, 'dur': 0.5},
}

CHORD_PROGRESSION = [
    [48, 52, 55],
    [45, 48, 52],
    [41, 45, 48],
    [43, 47, 50],
]

def parse_fasta(content):
    lines = content.strip().split('\n')
    seq = ''
    for line in lines:
        if not line.startswith('>'):
            seq += line.strip()
    return seq

def generate_musical_midi(sequence, mapping_type="protein"):
    midi = MIDIFile(3)
    for track in range(3):
        midi.addTempo(track, 0, 100)
    
    current_time = 0.0
    
    if mapping_type == "dna":
        for i, base in enumerate(sequence.upper()):
            if base in DNA_MAP:
                midi.addNote(0, 0, DNA_MAP[base]['note'], current_time, DNA_MAP[base]['dur'], 100)
                chord_idx = (i // 4) % 4
                for note in CHORD_PROGRESSION[chord_idx]:
                    midi.addNote(1, 0, note, current_time, 2.0, 60)
                midi.addNote(2, 0, CHORD_PROGRESSION[chord_idx][0] - 12, current_time, 2.0, 70)
                current_time += DNA_MAP[base]['dur']
    else:
        for i, aa in enumerate(sequence.upper()):
            if aa not in AA_MUSIC_MAP:
                continue
            info = AA_MUSIC_MAP[aa]
            note = info['pool'][i % len(info['pool'])]
            midi.addNote(0, 0, note, current_time, info['duration'], info['vol'])
            
            if i % 8 == 0:
                chord_idx = (i // 8) % 4
                for chord_note in CHORD_PROGRESSION[chord_idx]:
                    midi.addNote(1, 0, chord_note, current_time, 4.0, 50)
                midi.addNote(2, 0, CHORD_PROGRESSION[chord_idx][0] - 12, current_time, 4.0, 60)
            
            current_time += info['duration']
    
    buffer = io.BytesIO()
    midi.writeFile(buffer)
    return buffer.getvalue()

def generate_wav_simple(sequence, mapping_type="protein"):
    audio = []
    sample_rate = 44100
    
    if mapping_type == "dna":
        for base in sequence.upper():
            if base in DNA_MAP:
                freq = DNA_MAP[base]['freq']
                t = np.linspace(0, 0.5, int(sample_rate * 0.5), False)
                wave = np.sin(2 * np.pi * freq * t) * 0.3
                audio.extend(wave)
    else:
        for i, aa in enumerate(sequence.upper()):
            if aa not in AA_MUSIC_MAP:
                continue
            info = AA_MUSIC_MAP[aa]
            freq = info['pool'][i % len(info['pool'])]
            freq_hz = 440 * (2 ** ((freq - 69) / 12))
            t = np.linspace(0, info['duration'], int(sample_rate * info['duration']), False)
            wave = (np.sin(2 * np.pi * freq_hz * t) * 0.6 + np.sin(2 * np.pi * freq_hz * 2 * t) * 0.3) * 0.3
            audio.extend(wave)
    
    return np.array(audio, dtype=np.float32)

mode = st.selectbox("选择模式", ["DNA模式", "蛋白质模式（音乐化）"])

if mode == "DNA模式":
    valid_chars = set('ATCG')
    example = "ATGCGATCGATCGATCGATCG"
    input_label = "输入DNA序列（ATCG）"
else:
    valid_chars = set('AVILMFWGPSTCYNDEQKRH')
    example = "MKTAYIAKQR"
    input_label = "输入蛋白质序列（20种氨基酸）"

input_method = st.radio("输入方式", ["手动输入", "上传FASTA文件"])

if input_method == "手动输入":
    seq = st.text_area(input_label, example, height=150)
else:
    uploaded = st.file_uploader("上传FASTA文件", type=['fasta', 'txt'])
    if uploaded:
        content = uploaded.read().decode('utf-8')
        seq = parse_fasta(content)
        st.text_area("解析的序列", seq[:500] + ("..." if len(seq) > 500 else ""), height=100)
    else:
        seq = ""

if st.button("🎵 生成音乐"):
    clean_seq = seq.upper().replace(' ', '')
    if not clean_seq or not all(c in valid_chars for c in clean_seq):
        st.error("序列包含无效字符")
    else:
        if len(clean_seq) > 1000:
            clean_seq = clean_seq[:1000]
            st.warning("序列超过1000，已截断")
        
        map_type = "dna" if mode == "DNA模式" else "protein"
        
        audio = generate_wav_simple(clean_seq, map_type)
        st.audio(audio, sample_rate=44100)
        
        midi_data = generate_musical_midi(clean_seq, map_type)
        st.download_button(
            label="⬇️ 下载 MIDI（含和弦伴奏）",
            data=midi_data,
            file_name="biomusic_chord.mid",
            mime="audio/midi"
        )
        
        st.success(f"生成完成！{len(clean_seq)} 个残基，{'带和弦伴奏' if map_type == 'protein' else '简单模式'}")

st.divider()
st.write("**改进说明：** 蛋白质模式使用五声音阶 + 性质分组节奏 + 和弦伴奏（C-Am-F-G）")