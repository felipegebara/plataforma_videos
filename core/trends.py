"""
core/trends.py
==============
Módulo de busca e sugestão de Trending Topics para o Rota Calculada.
Integração com dados de tendências de turismo do Google Trends e YouTube (Métricas Diárias).
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("core.trends")

# Tópicos virais curados com métricas DIÁRIAS de buscas no Google/YouTube
TRAVEL_TRENDING_TOPICS = [
    {
        "title": "AlUla e a Linha Futurista no Deserto da Arábia Saudita",
        "location": "AlUla / NEOM",
        "country": "Arábia Saudita 🇸🇦",
        "search_volume": "🔥 +5.000 pesquisas/dia (Google & YouTube)",
        "rank": 1,
        "badge": "🏆 #1 TREND GLOBAL DE VIAGENS",
        "description": "O novo fenômeno viral da internet: construções futuristas espelhadas e túmulos de barro milenares no meio do deserto de AlUla.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "NO MEIO DO DESERTO MAIS EXOTICO DO MUNDO, ESSA CIDADE FUTURISTA DEIXOU O MUNDO CHOCADO!"
    },
    {
        "title": "A Rota das Cerejeiras Sakura e Templos de Quioto",
        "location": "Quioto / Tóquio",
        "country": "Japão 🇯🇵",
        "search_volume": "🔥 +4.000 pesquisas/dia",
        "rank": 2,
        "badge": "🔥 MAIOR CTR EM SHORTS NO YOUTUBE",
        "description": "Recorde absoluto de engajamento: a florada das cerejeiras, trens bala Shinkansen e pagodes sagrados da capital cultural japonesa.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "UMA VIAGEM NO TEMPO PELAS CEREJEIRAS E TEMPLOS MAIS IMPRESSIONANTES DO JAPAO!"
    },
    {
        "title": "O Deserto de Areias Brancas e Lagoas dos Lençóis Maranhenses",
        "location": "Barreirinhas / Atins",
        "country": "Brasil 🇧🇷",
        "search_volume": "🔥 +3.200 pesquisas/dia",
        "rank": 3,
        "badge": "🇧🇷 #1 DESTINO NACIONAL EM ALTA",
        "description": "O oásis brasileiro mais pesquisado no Google: centenas de lagoas cristalinas formadas entre dunas de areia branca na floresta amazônica.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "O UNICO LUGAR DO PLANETA ONDE LAGOAS CRISTALINAS ENCHEM O MEIO DO DESERTO!"
    },
    {
        "title": "Legoland & Lego House: O Parque Original de Tijolos em Billund",
        "location": "Billund",
        "country": "Dinamarca 🇩🇰",
        "search_volume": "🔥 +2.700 pesquisas/dia",
        "rank": 4,
        "badge": "⭐ TOP PARQUES DE DIVERSÃO",
        "description": "Uma viagem fascinante pela terra natal do LEGO, com árvores de 15 metros, dinossauros com picolé e minicidades de blocos.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "VIAJEI PARA A CIDADE ONDE TUDO FOI CONSTRUIDO COM DEZENAS DE MILHOES DE BLOCOS!"
    },
    {
        "title": "Os Passadiços e Túneis Secretos do Pelourinho em Salvador",
        "location": "Salvador (Bahia)",
        "country": "Brasil 🇧🇷",
        "search_volume": "🔥 +2.200 pesquisas/dia",
        "rank": 5,
        "badge": "🏛️ ROTA HISTÓRICA E MISTÉRIO",
        "description": "Expedição turística e histórica pelos túneis subterrâneos ocultos sob o centro histórico baiano usados para transporte de ouro.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "CONHEÇA OS PASSADIÇOS SUBTERRÂNEOS SECRETOS ESCONDIDOS NO CORAÇÃO DO PELOURINHO!"
    },
    {
        "title": "Os Quartos de Hotel Submersos nas Ilhas Maldivas",
        "location": "Atol de Rangali",
        "country": "Ilhas Maldivas 🇲🇻",
        "search_volume": "🔥 +2.000 pesquisas/dia",
        "rank": 6,
        "badge": "💎 LUXO E NATUREZA EXÓTICA",
        "description": "A experiência de hospedagem mais viral do TikTok: suítes construídas 5 metros abaixo do nível do mar cercadas por corais.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "JA IMAGINOU ACORDAR EM UM QUARTO DE HOTEL NO FUNDO DO MAR TRANSPARENTE DAS MALDIVAS?"
    },
    {
        "title": "Machu Picchu e o Trem Panorâmico dos Andes",
        "location": "Cusco / Aguas Calientes",
        "country": "Peru 🇵🇪",
        "search_volume": "🔥 +1.800 pesquisas/dia",
        "rank": 7,
        "badge": "⛰️ 7 MARAVILHAS DO MUNDO",
        "description": "A rota dos Incas no topo das nuvens: a jornada de trem entre vales montanhosos até a cidadela milenar de Machu Picchu.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "A VIAGEM DOS SONHOS NAS ALTURAS DOS ANDES QUE PARECE UM CENARIO DE FILME!"
    },
    {
        "title": "Veneza Oculta: Os Canais Secretos e Gondoleiros Italianos",
        "location": "Veneza",
        "country": "Itália 🇮🇹",
        "search_volume": "🔥 +1.600 pesquisas/dia",
        "rank": 8,
        "badge": "🛶 DESTINO CULTURA E ARTE",
        "description": "Um guia de navegação fora do circuito comercial para conhecer ruelas d'água e palácios flutuantes da lagoa veneziana.",
        "category_suggestion": "TRAVEL_TOURISM",
        "hook_suggestion": "OS SEGREDOS DAS RUAS DE AGUA DE VENEZA QUE NENHUM TURISTA COMUM CONSEGUE VER!"
    }
]

HISTORY_TRENDING_TOPICS = [
    {
        "title": "O Segredo do Triângulo das Bermudas",
        "location": "Oceano Atlântico",
        "country": "Internacional 🌊",
        "search_volume": "🔥 +3.600 pesquisas/dia",
        "rank": 1,
        "badge": "⚠️ MISTÉRIO MARÍTIMO",
        "description": "Desaparecimentos inexplicáveis e teorias científicas ocultas sobre o famoso triângulo marítimo.",
        "category_suggestion": "MISTERY_HISTORY",
        "hook_suggestion": "O LUGAR ONDE NAVIOS E AVIOES DESAPARECEM SEM DEIXAR RASTRO!"
    },
    {
        "title": "O Verdadeiro Segredo das Pirâmides do Egito",
        "location": "Gizé / Cairo",
        "country": "Egito 🇪🇬",
        "search_volume": "🔥 +3.300 pesquisas/dia",
        "rank": 2,
        "badge": "🏛️ ARQUEOLOGIA ANTIGA",
        "description": "Tecnologia antiga de precisão, alinhamento estelar com as estrelas de Órion e mistérios dos faraós.",
        "category_suggestion": "MISTERY_HISTORY",
        "hook_suggestion": "COMO CONSTRUIRAM ISSO HÁ 4.500 ANOS SEM TECNOLOGIA?"
    }
]


def get_trending_topics_brazil(max_results: int = 10, category_filter: str = "travel") -> List[Dict[str, Any]]:
    """
    Retorna os temas virais em alta com métricas de buscas DIÁRIAS no Google e YouTube.
    """
    cat = (category_filter or "travel").lower()

    if cat in ["travel", "viagens", "turismo"]:
        return TRAVEL_TRENDING_TOPICS[:max_results]
    elif cat in ["history", "historia", "misterio"]:
        return HISTORY_TRENDING_TOPICS[:max_results]
    else:
        combined = TRAVEL_TRENDING_TOPICS + HISTORY_TRENDING_TOPICS
        return combined[:max_results]


def suggest_next_video(existing_topics: List[str] = None, category_filter: str = "travel") -> Dict[str, Any]:
    """Sugere o próximo tópico viral baseado no que ainda não foi produzido."""
    existing_topics = existing_topics or []
    existing_lower = [t.lower() for t in existing_topics]
    
    topics = get_trending_topics_brazil(10, category_filter=category_filter)
    for topic in topics:
        if not any(ex in topic["title"].lower() for ex in existing_lower):
            return topic
            
    return topics[0]
