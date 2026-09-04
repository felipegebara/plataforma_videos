# Rota Calculada — AI Video Studio PRO 🌟🎬

**Plataforma Autônoma de Produção e Distribuição de Vídeos Virais para YouTube, Shorts e TikTok.**
Equipada com **Legendas Dinâmicas (Whisper CapCut-style)**, **Roteiros Inteligentes (Gemini / OpenAI LLM)**, **Vozes Neurais e MiniMax AI Ultra-Realista**, **Fallback de Stock HD (Pexels/Pixabay)**, **Criador de Séries** e **Upload Automático para o YouTube**.

---

## 🚀 Visão Geral e Novas Funcionalidades

O **Rota Calculada AI Video Studio PRO** é um ecossistema completo para canais de história, lendas, turismo e mistérios. Ele converte ideias ou pastas de vídeos brutos em conteúdos prontos para publicação em segundos.

### ✨ Recursos Principais
- 💬 **Interface Web Conversacional (Multi-Aba)**:
  - **Aba Chat IA**: Criação de vídeos por comandos de voz/texto com seletor de vozes neurais e barra de progresso em tempo real.
  - **Aba Biblioteca**: Visualizador de todos os vídeos produzidos, download rápido de MP4 e envio direto para o YouTube.
  - **Aba Séries**: Geração automática de até 20 Shorts em lote a partir de uma pasta de clipes brutos.
  - **Aba Trends**: Sugestões de tendências com rankings, países e volume diário de buscas no Google & YouTube (`+5.000 buscas/dia`).
- 📝 **Legendas Dinâmicas Palavra por Palavra (`core/subtitles.py`)**:
  - Transcrição via **OpenAI Whisper** com estilo animado amarelo/branco e contorno preto (estilo CapCut/TikTok) para máxima retenção.
- 🤖 **Roteiros Únicos via Gemini & OpenAI (`core/llm.py`)**:
  - Geração de narrações virais personalizadas em português brasileiro via **Google Gemini 1.5-Flash** ou **OpenAI GPT-4o-mini**.
- 🎙️ **Vozes Neurais & MiniMax AI (`core/voice_profiles.py` & `core/minimax_client.py`)**:
  - Alternância entre voz clássica (`Antônio`), lendas (`Francisca`), jovem/viral (`Leila`), ação (`Júlio`) e **MiniMax AI Speech-01 Ultra-Realista**.
- 🎬 **Fallback de Stock Video HD (`core/pexels_provider.py`)**:
  - Quando não houver arquivos de vídeo gravados locais, o motor busca e baixa automaticamente b-rolls cinematográficos do **Pexels** e **Pixabay**.
- 📤 **Publicação Direta no YouTube (`core/youtube_uploader.py`)**:
  - Botão de 1 clique para postar o Short direto no seu canal com título otimizado, descrição e hashtags (`#Shorts #RotaCalculada`).

---

## 🏗️ Arquitetura do Sistema

```
                         Interface do Usuário (ui/index.html)
                                    │
                                    ▼
                    FastAPI Application Server (api/server.py)
                    ├── Persistência SQLite (core/db.py)
                    ├── Gerenciador .env (core/config.py)
                    └── Message Broker (core/broker.py)
                                    │
                                    ▼
                  Motor Unificado de Produção (core/engine.py)
                    ├── Roteirização via Gemini / OpenAI (core/llm.py)
                    ├── Voz Neural & MiniMax TTS (core/resilience.py)
                    ├── Legendas Dinâmicas Whisper (core/subtitles.py)
                    ├── Stock Video HD (core/pexels_provider.py)
                    ├── BGM Temática (core/bgm_manager.py)
                    ├── Agente 19: Viral Packaging & Thumbnails
                    └── YouTube Auto-Upload (core/youtube_uploader.py)
```

---

## 🔑 Configuração de Variavéis de Ambiente (`.env`)

Copie o arquivo `.env.example` para `.env` na raiz do projeto e preencha suas chaves:

```env
# === Rota Calculada AI Studio — Configurações de API ===

# Google Gemini (Gratuito em gemini.google.com/app)
GEMINI_API_KEY=sua_chave_aqui

# OpenAI (Alternativa para Roteiros)
OPENAI_API_KEY=sua_chave_aqui

# Pexels (Gratuito em pexels.com/api)
PEXELS_API_KEY=sua_chave_aqui

# Pixabay (Gratuito em pixabay.com/api/docs/)
PIXABAY_API_KEY=sua_chave_aqui

# MiniMax (platform.minimaxi.com)
MINIMAX_API_KEY=sua_chave_aqui
MINIMAX_GROUP_ID=seu_group_id_aqui

# YouTube Data API (Console Google Cloud)
YOUTUBE_CLIENT_SECRET_PATH=client_secret.json
```

---

## 🛠️ Instalação e Execução

### 1. Clonar o Repositório
```bash
git clone https://github.com/felipegebara/plataforma_videos.git
cd "lendas e historia"
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o Studio

#### 🖱️ No Windows (1 Clique)
Execute dando 2 cliques em:
```bash
iniciar_studio.bat
```

#### 💻 Pelo Terminal
```bash
python desktop_launcher.py
```

Acesse o estúdio no navegador em: 👉 **`http://127.0.0.1:8000`**

---

## 🛡️ Git e Segurança

O projeto já está pré-configurado com um `.gitignore` rigoroso para proteger suas credenciais e não subir arquivos pesados no Git:
- **Protegidos pelo `.gitignore`**: Arquivos `.env`, chaves `.key`, vídeos renderizados (`output/videos/`), áudios temporários (`output/audio/`), gravações brutas e banco de dados SQLite (`*.sqlite3`).
- **Commits limpos**: Apenas código fonte, configurações base e arquivos necessários para execução são mantidos no versionamento.

---

## 📄 Licença
Propriedade do Canal **Rota Calculada**. Todos os direitos reservados.
