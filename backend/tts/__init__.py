import os
import json
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

from tts import commons, utils
from tts.data_utils import TextAudioLoader, TextAudioCollate, TextAudioSpeakerLoader, TextAudioSpeakerCollate
from tts.models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence
import soundfile as sf


from scipy.io.wavfile import write


def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm


def infer(script: str, hps, net_g):
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    output_path = os.path.join(current_dir, "output_audio.wav")
    stn_tst = get_text(script, hps)
    with torch.no_grad():
        x_tst = stn_tst.cpu().unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cpu()
        sid = torch.LongTensor([25]).cpu()
        audio = net_g.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8, length_scale=1.0)[0][
            0, 0].data.cpu().float().numpy()
    # `audio`는 NumPy 배열 형태의 음성 데이터이고, `hps.data.sampling_rate`는 해당 데이터의 샘플링 레이트입니다.
    sf.write(output_path, audio, hps.data.sampling_rate)
    return output_path
