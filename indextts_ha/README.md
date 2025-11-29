# IndexTTS Home Assistant Integration

Complete guide to installing and using IndexTTS as a TTS service in Home Assistant.

## Overview

This integration allows Home Assistant to use IndexTTS for text-to-speech synthesis with:
- **Your own cloned voices** - Use voices extracted from personal media
- **Emotion control** - Add emotional context to announcements
- **Remote API** - Connects to IndexTTS running on a separate machine (e.g., 192.168.4.192:5150)
- **Caching** - Generated audio is cached for faster playback
- **Security-appropriate emotions** - Alerts sound urgent, greetings sound friendly

## Architecture

```
Home Assistant (192.168.4.49)
    ↓ HTTP requests
IndexTTS API (192.168.4.192:5150)
    ↓ GPU synthesis
Audio output → media_player
```

## Installation

### Step 1: Download the Integration

Copy the `indextts_ha/` directory to your Home Assistant `custom_components/`:

```bash
# SSH into Home Assistant
ssh root@192.168.4.49

# Navigate to custom_components
cd /root/.homeassistant/custom_components

# Copy from your dev machine (or git clone)
# If using git:
git clone https://github.com/vhillaire/index-tts.git
cp -r index-tts/indextts_ha ./
```

Or manually:
```bash
# Create directory structure
mkdir -p /root/.homeassistant/custom_components/indextts

# Copy files (indextts_ha/*)
# - __init__.py
# - manifest.json
# - tts.py
# - config_flow.py
```

### Step 2: Restart Home Assistant

Go to Settings → System → Restart Home Assistant (or restart the container)

### Step 3: Configure IndexTTS Integration

**Via UI (Recommended)**:
1. Settings → Devices & Services
2. Click "Create Integration"
3. Search for "IndexTTS"
4. Enter:
   - **API URL**: `http://192.168.4.192:5150`
   - **Default Voice**: `default` (or your voice ID)
5. Save

**Via YAML** (if UI doesn't work):
```yaml
# configuration.yaml
indextts:
  api_url: http://192.168.4.192:5150
  default_voice: default

tts:
  - platform: indextts
```

## Usage

### Basic Announcement

```yaml
service: tts.indextts_speak
data:
  message: "Hello world"
  entity_id: media_player.living_room_speaker
```

### With Emotion

```yaml
service: tts.indextts_speak
data:
  message: "[Happy:80]Welcome home!"
  entity_id: media_player.living_room_speaker
```

### Emotion Syntax

Use emotion tags in brackets: `[Emotion:Intensity]text`

**Supported emotions:**
- `[Happy:0-100]` - Upbeat, welcoming
- `[Calm:0-100]` - Soothing, relaxed
- `[Angry:0-100]` - Urgent, alert
- `[Sad:0-100]` - Concerned, gentle
- `[Afraid:0-100]` - Worried, cautious
- `[Surprised:0-100]` - Astonished, sharp
- `[Disgusted:0-100]` - Disapproving, critical
- `[Melancholic:0-100]` - Wistful, reflective

**Examples:**
```yaml
# High intensity greeting
"[Happy:90]Great to see you!"

# Calm reminder
"[Calm:70]Don't forget your keys"

# Security alert
"[Angry:85]Front door opened at midnight!"

# Mixed emotions
"[Excited:80]You won the lottery![Calm:60] Let me explain the details."
```

### Automation Example

```yaml
automation:
  - id: "morning_greeting"
    alias: "Morning Greeting"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: tts.indextts_speak
      data:
        message: "[Happy:80]Good morning! Time to wake up!"
        entity_id: media_player.bedroom_speaker
        cache: true

  - id: "security_alert"
    alias: "Security Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.motion_detected
      to: "on"
    condition:
      condition: time
      after: "22:00:00"
      before: "06:00:00"
    action:
      service: tts.indeftts_speak
      data:
        message: "[Angry:90]Alert! Motion detected at night!"
        entity_id: media_player.hallway_speaker
        cache: false
```

See `AUTOMATIONS.yaml` for more examples.

## Service Options

### tts.indextts_speak

**Data Parameters:**

- `message` (required): Text to speak
  - Supports emotion tags: `[Emotion:Intensity]text`
  
- `entity_id` (required): Media player to play audio
  - e.g., `media_player.living_room_speaker`
  
- `voice` (optional): Voice ID to use
  - Default: configured default voice
  - Available voices from `/api/voices`
  
- `emotion` (optional): Emotion to apply
  - Format: `emotion_name:intensity`
  - e.g., `happy:80`
  - Alternative to inline tags in message
  
- `cache` (optional): Cache generated audio
  - `true`: Reuse if same message + voice + emotion (default)
  - `false`: Always generate new audio
  
- `speed` (optional): Speech speed multiplier
  - Default: 1.0
  - Range: 0.5-2.0

**Examples:**

```yaml
# Minimal
service: tts.indextts_speak
data:
  message: "Hello"
  entity_id: media_player.speaker

# With emotion in message
service: tts.indextts_speak
data:
  message: "[Happy:80]Welcome home!"
  entity_id: media_player.speaker

# With emotion option
service: tts.indextts_speak
data:
  message: "Good morning"
  entity_id: media_player.speaker
  voice: "bedroom_voice"
  emotion: "calm:70"
  cache: true

# No caching (security alert)
service: tts.indeftts_speak
data:
  message: "[Angry:90]Intruder alert!"
  entity_id: media_player.speaker
  cache: false
```

## Voice Management

### Extract Voice from Media (via API)

```bash
# From HA machine, call the extraction API
curl -F "file=@video.mp4" \
  -F "voice_name=my_voice" \
  http://192.168.4.192:5150/api/extract
```

### List Available Voices

```bash
curl http://192.168.4.192:5150/api/voices
```

Response:
```json
{
  "voices": [
    {
      "voice_id": "voice_abc123",
      "name": "My Voice",
      "description": "Extracted from personal recording",
      "gender": "male",
      "created_at": "2025-11-29T10:30:00"
    }
  ],
  "count": 1
}
```

## Common Use Cases

### 1. Welcoming Guests

```yaml
- alias: "Guest Arrival"
  trigger:
    platform: state
    entity_id: sensor.front_door
    to: "opened"
  action:
    service: tts.indextts_speak
    data:
      message: "[Happy:85]Welcome! Come on in!"
      entity_id: media_player.living_room_speaker
```

### 2. Security Alerts

```yaml
- alias: "Intruder Alert"
  trigger:
    platform: state
    entity_id: binary_sensor.motion_hallway
    to: "on"
  condition:
    condition: time
    after: "22:00:00"
    before: "06:00:00"
  action:
    service: tts.indeftts_speak
    data:
      message: "[Angry:90]ALERT! Motion detected in hallway!"
      entity_id: media_player.hallway_speaker
      cache: false
```

### 3. Gentle Reminders

```yaml
- alias: "Medication Reminder"
  trigger:
    platform: time
    at: "08:00:00"
  action:
    service: tts.indextts_speak
    data:
      message: "[Calm:75]Time for your morning medication."
      entity_id: media_player.bedroom_speaker
```

### 4. Information Updates

```yaml
- alias: "Weather Report"
  trigger:
    platform: time
    at: "07:00:00"
  action:
    service: tts.indeftts_speak
    data:
      message: |
        [Happy:60]Good morning!
        [Calm:70]It's {{ state_attr('weather.home', 'temperature') }} degrees
        and {{ states('weather.home') }}.
      entity_id: media_player.bedroom_speaker
```

## Troubleshooting

### Integration Won't Load

**Check:**
1. Restart Home Assistant after installing
2. Verify file permissions: `chmod 755 /root/.homeassistant/custom_components/indextts/`
3. Check HA logs: Settings → System → Logs
4. Verify manifest.json syntax (valid JSON)

**Error: "ImportError: No module named 'homeassistant'"**
- Normal during development
- HA provides these modules at runtime

### Can't Connect to API

**Check:**
1. API is running: `curl http://192.168.4.192:5150/health`
2. Firewall allows 192.168.4.49 → 192.168.4.192:5150
3. API URL in config is correct (no typos)
4. Check HA logs for connection errors

**Test connection from HA:**
```bash
ssh root@192.168.4.49
curl http://192.168.4.192:5150/health
```

### Audio Won't Play

**Check:**
1. Media player is available: `states('media_player.living_room_speaker')`
2. Media player is not in "muted" state
3. Volume is not 0
4. Audio file was generated: check HA logs
5. Player supports WAV format

### Synthesis Timeout

**Check:**
1. API is running and responsive
2. Model is loaded (first request takes longer)
3. Reduce message length
4. Check GPU is available: `nvidia-smi` on API machine
5. Increase timeout in config if needed

## Performance Tips

- **Cache enabled** (default): Identical messages reuse generated audio
- **Disable cache** for security alerts: Always generate fresh audio
- **Batch messages**: Synthesis runs in background; send multiple requests
- **Off-peak scheduling**: Run voice extraction during off-peak hours
- **Local speaker**: Use local media_player for faster playback

## API Reference

For detailed API documentation, see [API_SERVER.md](../API_SERVER.md) in the main project.

**Key Endpoints:**
- `GET /health` - Service health
- `GET /api/voices` - List voices
- `POST /api/extract` - Clone voice from media
- `POST /api/synthesize` - Generate speech

## Security Notes

- API runs on local network (192.168.x.x)
- No authentication by default (configure if exposed to internet)
- Audio files cached locally in HA
- Consider firewall rules for API machine
- Emotion tags are processed on API machine

## Limitations

- **Network-dependent**: Synthesis requires active connection to API machine
- **Latency**: First synthesis request takes ~30-60 seconds (model load)
- **Languages**: Currently supports English
- **Voices**: Limited to extracted voices (one per speaker/character)

## Future Enhancements

- [ ] Real-time emotion adjustment
- [ ] Multiple language support
- [ ] Voice priority queue
- [ ] Authentication/authorization
- [ ] Audio analysis (emotion detection)
- [ ] Integration with HA voice assistant

## Support

- **Documentation**: See [API_SERVER.md](../API_SERVER.md)
- **Examples**: See [AUTOMATIONS.yaml](AUTOMATIONS.yaml)
- **Issues**: Report on GitHub: vhillaire/index-tts

---

**Status**: Ready for testing (Phase 3 complete - dormant until models download)
