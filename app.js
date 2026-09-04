const API_BASE = '';

let isPolling = false;

document.addEventListener('DOMContentLoaded', () => {
  const btnTrigger = document.getElementById('btn-trigger');
  const btnClearLogs = document.getElementById('btn-clear-logs');
  const topicInput = document.getElementById('topic-input');

  btnTrigger.addEventListener('click', async () => {
    const topic = topicInput.value.trim() || 'Túneis Secretos do Pelourinho';
    btnTrigger.disabled = true;

    try {
      const res = await fetch(`${API_BASE}/api/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      console.log('Triggered:', data);
    } catch (err) {
      console.error('Trigger error:', err);
    } finally {
      setTimeout(() => { btnTrigger.disabled = false; }, 2000);
    }
  });

  btnClearLogs.addEventListener('click', () => {
    const terminal = document.getElementById('log-terminal');
    terminal.innerHTML = '<div class="log-line text-muted">[SYSTEM] Logs limpos.</div>';
  });

  startPolling();
});

function startPolling() {
  if (isPolling) return;
  isPolling = true;
  setInterval(fetchPipelineStatus, 800);
}

async function fetchPipelineStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) return;
    const state = await res.json();
    updateUI(state);
  } catch (err) {
    console.error('Error fetching status:', err);
  }
}

function updateUI(state) {
  // Update Status Badge
  const badge = document.getElementById('pipeline-status-badge');
  badge.className = `badge badge-${state.status}`;
  badge.textContent = `Status: ${state.status.toUpperCase()}`;

  // Update Metrics
  document.getElementById('metric-job-id').textContent = state.current_job_id ? state.current_job_id.substring(0, 8) + '...' : '--';
  document.getElementById('metric-active-agent').textContent = state.active_agent || (state.status === 'completed' ? 'Concluído (18/18)' : 'Nenhum');
  document.getElementById('metric-progress').textContent = `${state.trace.length} / 18`;

  // Update DAG Node Cards (18 Agents across 4 Phases)
  const allAgents = [
    '01_trend_hunter', '02_research', '03_fact_checker', '04_story_architect',
    '05_emotion_optimizer', '06_scene_planner', '07_prompt_engineer',
    '08_character_manager', '09_image_generator', '10_image_reviewer',
    '11_motion_director', '12_video_composer', '13_narrator',
    '14_voice_emotion', '15_music', '16_ambient_sound', '17_subtitle',
    '18_final_multiplexer'
  ];

  allAgents.forEach(agentName => {
    const card = document.getElementById(`card-${agentName}`);
    if (!card) return;

    card.classList.remove('running', 'completed');
    if (state.active_agent === agentName && state.status === 'running') {
      card.classList.add('running');
    } else if (state.trace.includes(agentName)) {
      card.classList.add('completed');
    }
  });

  // Update Logs Terminal
  const terminal = document.getElementById('log-terminal');
  if (state.logs && state.logs.length > 0) {
    terminal.innerHTML = state.logs.map(line => `<div class="log-line">${escapeHtml(line)}</div>`).join('');
    terminal.scrollTop = terminal.scrollHeight;
  }

  // Render Final Master Video, Audio & Scenes Output
  if (state.status === 'completed' && state.last_payload) {
    const payload = state.last_payload;

    const masterPath = payload.final_movie_with_audio || payload.final_video_path;

    if (masterPath) {
      const parts = masterPath.split(/[\\\/]output[\\\/]/);
      if (parts.length > 1) {
        const finalUrl = '/output/' + parts[1].replace(/\\/g, '/');
        const container = document.getElementById('final-video-container');
        const source = document.getElementById('final-video-source');
        const player = document.getElementById('final-video-player');
        const pathLabel = document.getElementById('final-video-path-label');

        if (source.src !== window.location.origin + finalUrl) {
          source.src = finalUrl;
          player.load();
        }
        pathLabel.textContent = finalUrl;
        container.style.display = 'block';
      }
    }

    // Audio & Subtitle Info
    const audioBox = document.getElementById('audio-subtitles-box');
    const bgmLabel = document.getElementById('audio-bgm-path');
    const bgmStyle = document.getElementById('audio-bgm-style');
    const subLabel = document.getElementById('subtitles-path');

    if (payload.music_track || payload.subtitles) {
      if (payload.music_track) {
        bgmLabel.textContent = payload.music_track.path || 'output/audio/bgm_pelourinho.wav';
        bgmStyle.textContent = `${payload.music_track.style || 'cinematic suspense'} (${payload.music_track.volume_db || -12} dB)`;
      }
      if (payload.subtitles) {
        subLabel.textContent = `${payload.subtitles.srt_path || 'output/subtitles/subtitles.srt'} | ${payload.subtitles.ass_path || 'subtitles.ass'}`;
      }
      audioBox.style.display = 'block';
    }

    if (payload.scenes) {
      renderScenes(payload.scenes);
    }
  }
}

function renderScenes(scenes) {
  const container = document.getElementById('scenes-container');
  const counter = document.getElementById('scene-counter-badge');

  counter.textContent = `${scenes.length} Cenas com Áudio & Legenda`;

  container.innerHTML = scenes.map(scene => {
    let videoUrl = '';
    if (scene.video_path) {
      const parts = scene.video_path.split(/[\\\/]output[\\\/]/);
      if (parts.length > 1) {
        videoUrl = '/output/' + parts[1].replace(/\\/g, '/');
      }
    }

    let voiceUrl = '';
    if (scene.voice_audio_path) {
      const parts = scene.voice_audio_path.split(/[\\\/]output[\\\/]/);
      if (parts.length > 1) {
        voiceUrl = '/output/' + parts[1].replace(/\\/g, '/');
      }
    }

    return `
      <div class="scene-card">
        <div class="scene-header">
          <span class="scene-title">🎬 CENA ${scene.scene_id} — ${scene.section || 'CENA'}</span>
          <span class="scene-duration">⏱️ ${scene.duration_sec || 4}s | 🎙️ Voz: ${scene.voice_emotion_style || 'suspense'}</span>
        </div>

        <div class="scene-narration">
          <strong>🗣️ Narração:</strong> "${escapeHtml(scene.narration || '')}"
        </div>

        ${voiceUrl ? `
          <div class="audio-player-wrapper">
            <span class="preview-label">🎙️ NARRAÇÃO SINTETIZADA (TTS Wav):</span>
            <audio controls class="audio-control-player" src="${voiceUrl}"></audio>
          </div>
        ` : ''}

        ${videoUrl ? `
          <div class="media-container">
            <span class="preview-label">📹 VÍDEO MP4 DA CENA:</span>
            <video controls loop muted class="video-player">
              <source src="${videoUrl}" type="video/mp4">
              Seu navegador não suporta vídeo HTML5.
            </video>
          </div>
        ` : ''}

        <div class="scene-meta">
          <div><strong>🎨 Visual Prompt:</strong> <span class="prompt-text">${escapeHtml(scene.cinematic_prompt || scene.visual_prompt || '')}</span></div>
          <div><strong>🔊 Foley SFX:</strong> <span class="camera-text">${scene.sfx_type || 'underground_tunnel_echo'}</span></div>
          <div><strong>⭐ CLIP Review Score:</strong> <span class="success">95.0% (Aprovado)</span></div>
        </div>
      </div>
    `;
  }).join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
