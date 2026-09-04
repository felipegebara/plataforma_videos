import asyncio
import edge_tts

async def main():
    text = "Sob o solo colonial do Pelourinho, existe uma Salvador que a história oficial tentou ocultar."
    voice = "pt-BR-AntonioNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("test_edge_voice.mp3")
    print("Voz Neural Humana gerada com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())
