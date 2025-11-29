# Home Assistant Integration Setup Guide

Complete guide to installing the IndexTTS custom component in Home Assistant.

## Prerequisites

- Home Assistant running on 192.168.4.49
- SSH access to HA (already configured with SSH keys)
- IndexTTS API running on 192.168.4.192:5150
- HA version 2024.1.0 or later

## Installation Steps

### Option 1: Git Clone (Recommended)

SSH into Home Assistant and clone directly:

```bash
ssh root@192.168.4.49

# Navigate to custom_components
cd /root/.homeassistant/custom_components

# Clone the repo
git clone https://github.com/vhillaire/index-tts.git
cd index-tts

# Copy just the HA component
cp -r indextts_ha /root/.homeassistant/custom_components/indextts

# Verify structure
ls -la /root/.homeassistant/custom_components/indextts/
# Should show:
# - __init__.py
# - manifest.json
# - tts.py
# - config_flow.py
# - services.yaml
# - README.md
```

### Option 2: Manual File Copy

If git is not available:

1. **Create directory structure:**
```bash
ssh root@192.168.4.49
mkdir -p /root/.homeassistant/custom_components/indextts
```

2. **Copy these files from your dev machine:**
   - `indextts_ha/__init__.py`
   - `indextts_ha/manifest.json`
   - `indextts_ha/tts.py`
   - `indextts_ha/config_flow.py`
   - `indextts_ha/services.yaml`
   - `indextts_ha/README.md`

```bash
# From your dev machine
scp -r indextts_ha/* root@192.168.4.49:/root/.homeassistant/custom_components/indextts/
```

### Step 2: Fix Permissions

```bash
ssh root@192.168.4.49

# Make files readable by HA
chmod -R 755 /root/.homeassistant/custom_components/indextts/
chmod 644 /root/.homeassistant/custom_components/indextts/*.py
chmod 644 /root/.homeassistant/custom_components/indextts/manifest.json
```

### Step 3: Restart Home Assistant

**Option A: Via UI**
- Settings → System → Restart

**Option B: Via Command**
```bash
ssh root@192.168.4.49
docker restart homeassistant  # or: systemctl restart homeassistant
```

Wait 1-2 minutes for HA to fully start.

### Step 4: Verify Integration Loaded

Check HA logs:
```bash
ssh root@192.168.4.49

# Check logs for IndexTTS
docker logs homeassistant | grep -i indextts

# Or navigate in UI: Settings → System → Logs (search "indextts")
```

Expected output:
```
2025-11-29 12:00:00 DEBUG (MainThread) [custom_components.indextts] IndexTTS integration loading
```

### Step 5: Configure Integration

**Via UI (Recommended):**
1. Go to Settings → Devices & Services
2. Click "Create Integration" (bottom right)
3. Search for "IndexTTS"
4. Click it
5. Enter configuration:
   - **API URL**: `http://192.168.4.192:5150`
   - **Default Voice**: `default` (or your voice ID)
6. Click "Create"

**Via YAML (Advanced):**
If UI config doesn't work, edit `/root/.homeassistant/configuration.yaml`:

```yaml
indextts:
  api_url: http://192.168.4.192:5150
  default_voice: default

tts:
  - platform: indextts
```

Then restart HA.

### Step 6: Test the Integration

**Test 1: Check service is available**

In HA Developer Tools → Services, search for `tts.indextts_speak`:

```yaml
service: tts.indextts_speak
data:
  message: "Hello from IndexTTS!"
  entity_id: media_player.living_room_speaker
```

**Test 2: Test with emotion**

```yaml
service: tts.indextts_speak
data:
  message: "[Happy:80]Welcome to IndexTTS!"
  entity_id: media_player.living_room_speaker
```

**Test 3: Check logs for errors**

```bash
ssh root@192.168.4.49
docker logs homeassistant | grep -A5 "indextts"
```

## Configuration

### Minimal Configuration

```yaml
# configuration.yaml
indextts:
  api_url: http://192.168.4.192:5150
```

### Full Configuration

```yaml
indextts:
  api_url: http://192.168.4.192:5150
  default_voice: my_voice
  cache_dir: tts_cache
```

**Parameters:**
- `api_url`: IndexTTS API endpoint (required)
- `default_voice`: Default voice ID to use (optional, default: "default")
- `cache_dir`: Directory to cache generated audio (optional)

## First Run

### 1. Extract a Voice

First, you need at least one voice in the library. Extract from media:

```bash
# From your dev machine with IndexTTS running
curl -F "file=@my_recording.mp4" \
  -F "voice_name=my_voice" \
  http://192.168.4.192:5150/api/extract
```

Response:
```json
{
  "voice_id": "voice_abc123",
  "name": "my_voice",
  "duration": 45.2,
  "created_at": "2025-11-29T12:00:00",
  "message": "Voice extracted successfully"
}
```

### 2. List Available Voices

```bash
curl http://192.168.4.192:5150/api/voices
```

### 3. Use in HA

In HA Developer Tools → Services:

```yaml
service: tts.indextts_speak
data:
  message: "Hello from my voice!"
  entity_id: media_player.living_room_speaker
  voice: my_voice
```

## Troubleshooting

### Integration Not Showing in Services

**Check 1: Files are in correct location**
```bash
ssh root@192.168.4.49
ls -la /root/.homeassistant/custom_components/indextts/
```

Should show at least: `__init__.py`, `manifest.json`, `tts.py`

**Check 2: manifest.json is valid JSON**
```bash
ssh root@192.168.4.49
python3 -m json.tool /root/.homeassistant/custom_components/indextts/manifest.json
```

**Check 3: Restart HA and check logs**
```bash
ssh root@192.168.4.49
docker restart homeassistant
sleep 30
docker logs homeassistant | grep -i indextts
```

### API Connection Error

**Check 1: API is running**
```bash
curl http://192.168.4.192:5150/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "IndexTTS API",
  "version": "0.2.0",
  "port": 5150
}
```

**Check 2: Network connectivity from HA to API**
```bash
ssh root@192.168.4.49
# From HA machine, try to reach API
curl http://192.168.4.192:5150/health

# If that fails, check firewall:
# - Is IndexTTS listening on 0.0.0.0:5150?
# - Is HA network allowed to connect?
```

**Check 3: HA logs for connection errors**
```bash
ssh root@192.168.4.49
docker logs homeassistant | grep -i "indextts\|connection\|timeout"
```

### Service Call Fails

**Check 1: Media player exists and is available**

In HA Developer Tools → States, look for your media player entity (e.g., `media_player.living_room_speaker`).

**Check 2: Voice exists**

```bash
curl http://192.168.4.192:5150/api/voices
```

Verify the voice_id exists in the response.

**Check 3: Check HA logs**

```bash
ssh root@192.168.4.49
docker logs homeassistant | tail -50
```

Look for error messages from indextts.

### Emotion Tags Not Working

**Check 1: Emotion tag syntax is correct**

Valid: `[Happy:80]text`  
Invalid: `[happy:80]text` (lowercase doesn't work in some cases)

Valid emotions:
- Happy, Angry, Sad, Afraid, Disgusted, Melancholic, Surprised, Calm

**Check 2: Intensity is 0-100**

Valid: `[Happy:80]`  
Invalid: `[Happy:200]` (exceeds 100)

## Monitoring

### Check Integration Status

**Via Developer Tools:**
1. Tools → States
2. Search for `indextts` entities

**Via Command Line:**
```bash
ssh root@192.168.4.49

# Check if custom component is loaded
docker exec homeassistant python3 -c "
import json
with open('/root/.homeassistant/custom_components/indextts/manifest.json') as f:
    print(json.dumps(json.load(f), indent=2))
"
```

### Monitor API Calls

**From HA machine:**
```bash
# Watch API responses
ssh root@192.168.4.49
watch "curl -s http://192.168.4.192:5150/health | python3 -m json.tool"
```

**From dev machine:**
```bash
# Monitor API logs while making calls
docker logs indextts-api -f  # if running in Docker
# or
tail -f /var/log/indextts_api.log  # if running as service
```

## Updates

To update to a newer version:

```bash
ssh root@192.168.4.49
cd /root/.homeassistant/custom_components/indextts

# Pull latest
git pull

# Restart HA
docker restart homeassistant
```

## Uninstallation

To remove the integration:

```bash
ssh root@192.168.4.49

# Remove component
rm -rf /root/.homeassistant/custom_components/indextts

# Remove config from configuration.yaml if added manually

# Restart HA
docker restart homeassistant
```

## Next Steps

1. **Extract your voices** - Use media files to create voice profiles
2. **Create automations** - Use IndexTTS in HA automations with emotions
3. **Set up media players** - Ensure HA has media players configured
4. **Test scenarios** - Try security alerts, greetings, reminders

See [README.md](README.md) for usage examples and [AUTOMATIONS.yaml](AUTOMATIONS.yaml) for automation templates.

---

**Support**: Check GitHub issues or see main [README.md](../README.md)
