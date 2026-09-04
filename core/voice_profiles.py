"""
core/voice_profiles.py
=====================
Perfis de voz neurais em português brasileiro para narração no Rota Calculada AI Video Studio.
"""
from typing import Dict, Any, List, Optional

VOICE_PROFILES: Dict[str, Dict[str, Any]] = {
    "antonio": {
        "id": "antonio",
        "name": "Antônio (Narrador Clássico)",
        "description": "Voz masculina encorpada, ideal para mistérios, história e fatos.",
        "edge_tts_voice": "pt-BR-AntonioNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "category_match": ["MISTERY_HISTORY", "TRAVEL_TOURISM", "DEFAULT"]
    },
    "francisca": {
        "id": "francisca",
        "name": "Francisca (Narradora Expressiva)",
        "description": "Voz feminina clara, perfeita para lendas, folclore e contos.",
        "edge_tts_voice": "pt-BR-FranciscaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "category_match": ["LEGENDS_FOLKLORE", "CREATIVE_ART"]
    },
    "leila": {
        "id": "leila",
        "name": "Leila (Jovem & Dinâmica)",
        "description": "Voz feminina jovem e rápida para curiosidades e Shorts virais.",
        "edge_tts_voice": "pt-BR-LeilaNeural",
        "rate": "+5%",
        "pitch": "+0Hz",
        "category_match": ["VIRAL_CURIOSITY", "FUN_FACTS"]
    },
    "julio": {
        "id": "julio",
        "name": "Júlio (Impactante & Moderno)",
        "description": "Voz masculina jovem e enérgica para ação e tecnologia.",
        "edge_tts_voice": "pt-BR-JulioNeural",
        "rate": "+5%",
        "pitch": "+0Hz",
        "category_match": ["ACTION_DRAMA", "TECH_INNOVATION"]
    },
    "drama_m": {
        "id": "drama_m",
        "name": "Antônio (Dramático & Grave)",
        "description": "Tom mais lento e grave para mitos obscuros e conspirações.",
        "edge_tts_voice": "pt-BR-AntonioNeural",
        "rate": "-10%",
        "pitch": "-5Hz",
        "category_match": ["DARK_MYSTERY", "HORROR"]
    },
    "drama_f": {
        "id": "drama_f",
        "name": "Francisca (Dramática)",
        "description": "Tom calmo e tenso para relatos históricos dramáticos.",
        "edge_tts_voice": "pt-BR-FranciscaNeural",
        "rate": "-10%",
        "pitch": "-2Hz",
        "category_match": ["HISTORICAL_DRAMA"]
    },
    "minimax_m": {
        "id": "minimax_m",
        "name": "MiniMax AI (Masculino Ultra-Realista)",
        "description": "Voz sintética hiper-realista alimentada pelo modelo MiniMax Speech-01.",
        "edge_tts_voice": "minimax-male-qn-qingse",
        "rate": "+0%",
        "pitch": "+0Hz",
        "category_match": ["MINIMAX"]
    },
    "minimax_f": {
        "id": "minimax_f",
        "name": "MiniMax AI (Feminino Ultra-Realista)",
        "description": "Voz feminina jovem hiper-realista alimentada pelo modelo MiniMax Speech-01.",
        "edge_tts_voice": "minimax-female-shaonv",
        "rate": "+0%",
        "pitch": "+0Hz",
        "category_match": ["MINIMAX"]
    }
}


def get_voice_for_category(category: str) -> Dict[str, Any]:
    """Retorna o perfil de voz mais adequado para uma determinada categoria."""
    for voice_id, profile in VOICE_PROFILES.items():
        if category in profile.get("category_match", []):
            return profile
    return VOICE_PROFILES["antonio"]


def get_voice_profile(voice_id_or_name: Optional[str]) -> Dict[str, Any]:
    """Busca um perfil por ID ou nome da voz do edge_tts."""
    if not voice_id_or_name:
        return VOICE_PROFILES["antonio"]
    
    # Busca por ID exato
    if voice_id_or_name in VOICE_PROFILES:
        return VOICE_PROFILES[voice_id_or_name]
    
    # Busca por nome do edge_tts
    for profile in VOICE_PROFILES.values():
        if profile["edge_tts_voice"] == voice_id_or_name:
            return profile
            
    # Retorna padrão
    return VOICE_PROFILES["antonio"]


def list_voices() -> List[Dict[str, Any]]:
    """Retorna a lista de todas as vozes para a interface UI."""
    return list(VOICE_PROFILES.values())
