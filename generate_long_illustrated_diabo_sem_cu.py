import os
import sys
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


LONG_ILLUSTRATED_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas brenhas profundas do Rio Uaupés, no Alto Rio Negro, a mitologia dos povos indígenas Desana e Tuyuka guarda um dos contos cosmogônicos mais fascinantes da Amazônia.",
        "duration": 9.0,
        "motion": "zoom_in",
        "prompt": "Indigenous Amazonian mythology painting, Rio Uaupes river at twilight, misty ancient rainforest, Desana and Tuyuka tribe territory, artistic painting style, 9:16 vertical, 8k"
    },
    {
        "scene_id": 2,
        "narration": "Esta narrativa foi preservada pela tradição oral dos pajés e imortalizada nas pinturas vibrantes do mestre artista indígena Feliciano Lana, hoje em acervo no Museu da Amazônia.",
        "duration": 10.0,
        "motion": "pan_left",
        "prompt": "Master indigenous artist Feliciano Lana painting mythic Amazonian legend on canvas, vivid colors, Desana indigenous mythology, 9:16 vertical, 8k"
    },
    {
        "scene_id": 3,
        "narration": "Segundo o mito ancestral, nos tempos primordiais, a entidade conhecida como Diabo Sem Cú habitava as densas florestas tropicais, vagando isolada entre as grandes árvores.",
        "duration": 9.5,
        "motion": "zoom_out",
        "prompt": "Mythological entity Meno Diabo Sem Cu roaming deep dark Amazon rainforest at night, spirit of the woods, indigenous folklore illustration, 9:16 vertical, 8k"
    },
    {
        "scene_id": 4,
        "narration": "A criatura possuía uma anatomia única e misteriosa: não tinha orifício de saída em seu corpo, o que fazia acumular uma força interna descomunal e uma fúria incansável.",
        "duration": 9.8,
        "motion": "pan_right",
        "prompt": "Ancient indigenous warrior exploring dark Amazon jungle with torch, shadowy mythical creature in background, tribal story illustration, 9:16 vertical, 8k"
    },
    {
        "scene_id": 5,
        "narration": "Em uma noite de grande travessia, guerreiros e sabedores indígenas encontraram a criatura nas margens de uma igarapé sagrada, travando um confronto de espíritos e magia ancestral.",
        "duration": 10.2,
        "motion": "zoom_in",
        "prompt": "Mythic confrontation at the edge of Amazon river, indigenous shaman in ritual headdress facing giant mystical spirit, glowing water, 9:16 vertical, 8k"
    },
    {
        "scene_id": 6,
        "narration": "Pressionada pelo poder das rezas dos pajés, a entidade caiu nas águas correntes do rio. Em um estalo mágico, sua energia acumulada se transformou e se dissipou na água.",
        "duration": 9.5,
        "motion": "pan_left",
        "prompt": "Mystical transformation scene, glowing magical energy bursting into river water, indigenous myth artwork, vibrant colors, 9:16 vertical, 8k"
    },
    {
        "scene_id": 7,
        "narration": "Foi nesse momento exato que nasceram os sarapós, os famosos peixes elétricos de corpo alongado que habitam o leito dos rios amazônicos, conhecidos por emitirem impulsos de energia.",
        "duration": 10.0,
        "motion": "zoom_out",
        "prompt": "Group of electric knife fish Sarapos glowing underwater in clear Amazon river, bioluminescent water, indigenous myth illustration, 9:16 vertical, 8k"
    },
    {
        "scene_id": 8,
        "narration": "Para os povos Desana e Tuyuka, a forma fina e ondulante dos peixes sarapós e sua descarga de energia são a lembrança viva da força represada da criatura mitológica.",
        "duration": 9.2,
        "motion": "pan_right",
        "prompt": "Indigenous fishermen in canoe watching glowing electric Sarapo fish swimming in crystal clear river at dawn, mythic painting, 9:16 vertical, 8k"
    },
    {
        "scene_id": 9,
        "narration": "Esta riqueza de simbolismos demonstra como a cosmologia indígena explica a origem da biodiversidade e dos animais através de ensinamentos morais e espirituais.",
        "duration": 9.0,
        "motion": "zoom_in",
        "prompt": "Art gallery exhibit in Museu da Amazonia MUSA displaying indigenous Desana paintings, warm wooden architecture in rainforest, 9:16 vertical, 8k"
    },
    {
        "scene_id": 10,
        "narration": "Gostou de conhecer a história ilustrada da origem dos sarapós no acervo do MUSA? Compartilhe este vídeo e siga o canal para mais mitos da cultura brasileira!",
        "duration": 9.5,
        "motion": "zoom_out",
        "prompt": "Majestic Amazonian river sunset with indigenous canoe silhouette, glowing stars overhead, mythic storybook ending, 9:16 vertical, 8k"
    }
]


async def generate_voice(text: str, out_path: str):
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural")
            await communicate.save(out_path)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 100:
                return
        except Exception:
            await asyncio.sleep(1.0)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        with open(out_path, "wb") as f:
            f.write(b"MOCK")


def produce_long_illustrated_video():
    topic_id = "diabo_sem_cu_longo_ilustrado"
    print(f"\n==========================================")
    print(f"[VÍDEO LONGO ILUSTRADO - MUSA] Gerando Vídeo Completo (10 Cenas Ilustradas)")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in LONG_ILLUSTRATED_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        prompt_txt = sc["prompt"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Geração da Ilustração Artística HD 9:16 via Pollinations AI
        enc_p = urllib.parse.quote(prompt_txt)
        ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={1200 + scene_id}"
        
        try:
            req = urllib.request.Request(ai_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=18) as resp:
                with open(img_path, "wb") as f:
                    f.write(resp.read())
            print(f"  ✓ Cena {scene_id}: Ilustração Artística 9:16 gerada com sucesso")
        except Exception as e:
            print(f"  ⚠️ Erro ao gerar ilustração da cena {scene_id} ({e}), usando canvas art...")
            img = Image.new("RGB", (1080, 1920), (25, 45, 30))
            img.save(img_path)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 40)
            except Exception:
                font = ImageFont.load_default()

            line1 = "DIABO SEM CÚ"
            line2 = "A ORIGEM DOS SARAPÓS (MUSA)"

            draw.text((540, 290), line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            img.convert("RGB").save(img_path)

        # Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # Renderizar Vídeo MP4 com Movimento OpenCV
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        img_cv = cv2.imread(str(img_path))
        h_cv, w_cv, _ = img_cv.shape
        fps = 24
        total_f = int(dur * fps)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_v = cv2.VideoWriter(str(scene_mp4), fourcc, fps, (w_cv, h_cv))

        for f_idx in range(total_f):
            prog = f_idx / float(total_f)
            if motion == "zoom_in":
                scale = 1.0 + (0.08 * prog)
            elif motion == "zoom_out":
                scale = 1.08 - (0.08 * prog)
            else:
                scale = 1.04

            nw, nh = int(w_cv * scale), int(h_cv * scale)
            resized = cv2.resize(img_cv, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

            if motion == "pan_left":
                sx = int((nw - w_cv) * (1.0 - prog))
            elif motion == "pan_right":
                sx = int((nw - w_cv) * prog)
            else:
                sx = (nw - w_cv) // 2

            sy = (nh - h_cv) // 2
            out_v.write(resized[sy : sy + h_cv, sx : sx + w_cv])

        out_v.release()

        # Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.5))

        current_time += voice_dur
        print(f"  [SCENE] Cena {scene_id} renderizada com ilustração artística ({voice_dur:.2f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Longo com Áudio
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None
    )

    print(f"[OK] VÍDEO LONGO ILUSTRADO DO MUSA CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_long_illustrated_video()


if __name__ == "__main__":
    main()
