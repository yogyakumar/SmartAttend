from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import librosa
import soundfile as sf
import subprocess
import wave
import streamlit as st
import imageio_ffmpeg


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def _pcm_wav_to_array(audio_bytes):
    with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        raw = wav_file.readframes(frame_count)

    if frame_count <= 0:
        raise ValueError("Recorded audio is empty.")

    if sample_width == 1:
        audio = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        audio = (audio - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {sample_width} bytes")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    return np.asarray(audio, dtype=np.float32), int(sample_rate)


def _ffmpeg_decode(audio_bytes):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    result = subprocess.run(
        [
            ffmpeg_exe,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            "pipe:0",
            "-f",
            "wav",
            "-ac",
            "1",
            "-ar",
            "16000",
            "pipe:1",
        ],
        input=audio_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0 or not result.stdout:
        error = result.stderr.decode("utf-8", errors="ignore").strip()
        raise ValueError(error or "The recorded audio format could not be decoded.")

    return _pcm_wav_to_array(result.stdout)


def _decode_audio(audio_bytes):
    if not audio_bytes:
        raise ValueError("No audio data was received.")

    try:
        audio, sample_rate = _pcm_wav_to_array(audio_bytes)
    except Exception:
        audio, sample_rate = _ffmpeg_decode(audio_bytes)

    if sample_rate != 16000:
        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=16000,
        )
        sample_rate = 16000

    audio = np.asarray(audio, dtype=np.float32)

    if audio.size == 0:
        raise ValueError("Recorded audio is empty.")

    return audio, sample_rate


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()
        audio, sample_rate = _decode_audio(audio_bytes)

        duration = len(audio) / sample_rate
        if duration < 0.5:
            raise ValueError("Recording is too short. Please record for at least 1 second.")

        wav = preprocess_wav(audio, source_sr=sample_rate)
        if wav is None or len(wav) == 0:
            raise ValueError("Voice preprocessing returned empty audio.")

        embedding = encoder.embed_utterance(wav)
        if embedding is None:
            raise ValueError("Resemblyzer returned no embedding.")

        return np.asarray(embedding, dtype=np.float32).tolist()

    except Exception as e:
        st.error(f"Voice recognition failed: {e}")
        return None


def verify_voice_embedding(new_embedding, stored_embeddings, threshold=0.65):
    if new_embedding is None or not stored_embeddings:
        return False, 0.0

    new_embedding = np.asarray(new_embedding, dtype=np.float32)
    best_score = -1.0

    for stored in stored_embeddings:
        if stored is None:
            continue
        stored = np.asarray(stored, dtype=np.float32)
        if new_embedding.shape != stored.shape:
            continue
        similarity = float(np.dot(new_embedding, stored))
        best_score = max(best_score, similarity)

    return best_score >= threshold, best_score


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_embedding = np.asarray(new_embedding, dtype=np.float32)
    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding is None:
            continue
        stored_embedding = np.asarray(stored_embedding, dtype=np.float32)
        if new_embedding.shape != stored_embedding.shape:
            continue
        similarity = float(np.dot(new_embedding, stored_embedding))
        if similarity > best_score:
            best_score = similarity
            best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()
        audio, sample_rate = _decode_audio(audio_bytes)

        segments = librosa.effects.split(audio, top_db=30)
        identified_results = {}

        for start, end in segments:
            if (end - start) < sample_rate * 0.5:
                continue

            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio, source_sr=sample_rate)
            if wav is None or len(wav) == 0:
                continue

            embedding = encoder.embed_utterance(wav)
            sid, score = identify_speaker(embedding, candidates_dict, threshold)

            if sid is not None:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results

    except Exception as e:
        st.error(f"Bulk voice processing failed: {e}")
        return {}
