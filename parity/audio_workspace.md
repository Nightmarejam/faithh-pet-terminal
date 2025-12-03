# AUDIO WORKSPACE PARITY FILE
**Version**: 1.0  
**Last Updated**: 2025-11-19  
**Owner**: Jonathan  
**Auto-Update**: Via FAITHH session summaries

---

## 🎯 Core Principle
**One VoiceMeeter config for ALL workflows** - no disabling/enabling needed

---

## 🔌 Hardware Inventory

### Audio Interfaces
```yaml
UAD_Volt_1:
  location: "Windows Desktop"
  type: "USB Audio Interface"
  inputs: "1x XLR/TRS Combo"
  outputs: "Line out + Headphone out"
  use: "Mastering monitoring, DAW output"
  
PreSonus_Studio_1824c:
  location: "Travel rig"
  type: "USB Audio Interface"  
  inputs: "6x preamps (expandable)"
  outputs: "Multiple outs"
  use: "Mobile recording, multi-track"
```

### Microphones
```yaml
Blue_Yeti:
  location: "Windows Desktop"
  connection: "USB Direct"
  use: "Streaming commentary, Discord"
  
Blue_Yeti_Classic:
  location: "Monitor speakers"
  type: "Passive speakers"
  connection: "Via Sonarworks → VoiceMeeter A1 output"
  use: "Corrected monitoring"
```

### Video
```yaml
Elgato_4K_X:
  type: "Capture Card"
  connection: "PCIe"
  use: "Game capture (1080 Ti output), includes audio"
  
Razer_Kiyo_Pro:
  type: "Webcam"
  connection: "USB"
  use: "Face cam for streaming"
```

---

## 🎛️ VoiceMeeter Configuration (Universal)

### Hardware Inputs

```yaml
Stereo_Input_1:
  device: "Blue Yeti (USB)"
  type: "Microphone"
  routing:
    A1: true   # Always hear yourself
    B1: varies # Streaming: ON, Mastering: OFF
    B2: varies # Remote collab: ON, else: OFF
  use: "Commentary, voice, remote collab mic"

Stereo_Input_2:
  device: "DISABLED"
  reason: "Elgato audio handled by OBS directly"

Stereo_Input_3:
  device: "UAD Volt 1"
  type: "Stereo Line Input"
  routing:
    A1: true   # Always monitor DAW output
    B1: false  # Never to stream
    B2: false  # Never to Sonobus
  use: "WaveLab/Luna playback monitoring ONLY"
```

### Virtual Inputs

```yaml
VAIO_VoiceMeeter_Input:
  windows_name: "VoiceMeeter Input"
  routing:
    A1: true   # Hear it
    B1: false  # DON'T stream private comms
    B2: varies # Sonobus: return audio from collaborator
  hard_wired_apps:
    - Discord (comms device)
    - Sonobus (return audio)
  use: "Private communications"

VAIO3_VoiceMeeter_Input:
  windows_name: "VoiceMeeter Input (VAIO3)"
  routing:
    A1: true   # Always hear
    B1: true   # Games/desktop TO stream
    B2: false  # Not to Sonobus
  default_apps:
    - All games
    - System sounds
    - Browser
    - Music players
    - Everything not hard-wired
  use: "Desktop audio catch-all FOR STREAMING"
```

### Outputs

```yaml
A1_Hardware_Out:
  device: "Speakers (Yeti Classic)"
  processing: "Sonarworks Reference 4"
  use: "Personal monitoring (corrected)"
  always_enabled: true
  
B1_Virtual_Out:
  device: "VoiceMeeter Output"
  processing: "None (flat)"
  use: "OBS stream mix"
  toggle: "Enable for streaming, disable for mastering"
  
B2_Virtual_Out:
  device: "VoiceMeeter Aux"
  processing: "None (flat)"
  use: "Sonobus send"
  toggle: "Enable for remote collab only"
  
B3_Virtual_Out:
  device: "VoiceMeeter VAIO3 Out"
  processing: "None"
  use: "Future - DAW recording bus"
  status: "Not implemented yet"
```

---

## 🎬 Workflow Scenarios

### Workflow 1: Streaming Games

```yaml
name: "Game Streaming"
purpose: "Stream to Twitch/YouTube"
duration: "2-6 hours"

voicemeeter_config:
  inputs:
    blue_yeti:
      enabled: true
      routing: [A1, B1]  # Your voice on stream
    vaio3_desktop:
      enabled: true
      routing: [A1, B1]  # Game audio on stream
    vaio_discord:
      enabled: true
      routing: [A1]      # Friends private
    volt_1:
      enabled: false     # Not needed for streaming
  
  outputs:
    A1: true   # Your monitoring
    B1: true   # To OBS
    B2: false  # Not needed

obs_config:
  audio_sources:
    - "VoiceMeeter Output (B1)" → Your voice + game audio
    - "Elgato 4K X" → Game capture includes audio automatically
  video_sources:
    - Game Capture (1080 Ti DirectX)
    - Video Capture (Elgato 4K X passthrough)
    - Video Capture (Razer Kiyo Pro face cam)

discord_config:
  input: "Blue Yeti"
  output: "VoiceMeeter Aux Input (VAIO)"
  result: "Friends in your ears, not on stream"

windows_audio:
  default_playback: "VoiceMeeter Input (VAIO3)"
  default_comms: "VoiceMeeter Aux Input (VAIO)"
```

---

### Workflow 2: Audio Mastering

```yaml
name: "Mastering Session"
purpose: "WaveLab mastering work"
duration: "1-4 hours"
key_requirement: "NO game/stream audio interference"

voicemeeter_config:
  inputs:
    blue_yeti:
      enabled: false     # Muted during critical listening
    vaio3_desktop:
      enabled: false     # NO desktop audio during mastering
    vaio_discord:
      enabled: false     # No distractions
    volt_1:
      enabled: true
      routing: [A1]      # ONLY monitor WaveLab output
  
  outputs:
    A1: true   # Corrected monitoring
    B1: false  # No streaming
    B2: false  # No collaboration

wavelab_config:
  output_device: "UAD Volt 1 (Direct)"
  monitoring: "Through VoiceMeeter Input 3"
  flow: |
    WaveLab → Volt 1 Line Out → VoiceMeeter Input 3 → A1 → Sonarworks → Yeti Classic Speakers

alternative_direct_monitoring:
  wavelab_output: "Speakers (Yeti Classic)" via Sonarworks
  voicemeeter: "Not in signal path"
  note: "Simpler, bypasses VoiceMeeter entirely"
  trade_off: "Can't record session or route elsewhere"

recommended_approach: "Direct monitoring (WaveLab → Sonarworks → Speakers)"
reason: "Cleanest signal path, lowest latency, no accidental desktop audio"
```

---

### Workflow 3: Remote Recording (Sonobus)

```yaml
name: "Remote Collaboration"
purpose: "Record with partner on M2 Mac Mini (Luna DAW)"
duration: "2-4 hours"
network: "Sonobus over internet"

voicemeeter_config:
  inputs:
    blue_yeti:
      enabled: true
      routing: [A1, B2]  # Your mic → to partner
    vaio3_desktop:
      enabled: false     # No desktop audio
    vaio_discord:
      enabled: false     # Use Sonobus comms instead
    volt_1:
      enabled: true
      routing: [A1]      # Monitor Luna/DAW output
  
  outputs:
    A1: true   # Your monitoring
    B1: false  # No streaming
    B2: true   # To Sonobus

sonobus_config:
  input_device: "VoiceMeeter Aux (B2)"
  output_device: "VoiceMeeter Aux Input (VAIO)"
  connection: "Partner's M2 Mac Mini"
  quality: "High quality, low latency"
  
  flow: |
    Your Mic → VoiceMeeter Input 1 → B2 → Sonobus → Partner
    Partner → Sonobus → VAIO → VoiceMeeter A1 → Your ears

luna_daw_on_mac_mini:
  operator: "Business partner"
  monitoring: "Through partner's setup"
  recording: "Both your mics tracked separately"
  
windows_during_session:
  default_playback: "VoiceMeeter Aux Input (VAIO)" 
  reason: "Sonobus return audio goes here"
```

---

## 📊 Quick Reference Matrix

| Scenario | Blue Yeti→ | VAIO3→ | Volt 1→ | A1 | B1 | B2 | Key App |
|----------|-----------|---------|---------|----|----|----|---------| 
| Streaming | A1+B1 | A1+B1 | OFF | ON | ON | OFF | OBS |
| Mastering | OFF | OFF | A1 | ON | OFF | OFF | WaveLab |
| Remote Collab | A1+B2 | OFF | A1 | ON | OFF | ON | Sonobus |
| Idle/Desktop | A1 | A1 | OFF | ON | OFF | OFF | - |

---

## 🔧 Application-Specific Settings

### OBS Studio
```yaml
audio_settings:
  desktop_audio: "DISABLED"
  mic_auxiliary: "VoiceMeeter Output"
  
advanced_audio:
  voicemeeter_output:
    monitor: "Monitor and Output"
    tracks: [1]
  elgato_4k_x:
    monitor: "Monitor and Output"  
    tracks: [1]
    note: "Audio comes with video capture automatically"

encoding:
  gpu: "NVIDIA NVENC (1080 Ti)"
  bitrate: "6000-9000 kbps"
```

### WaveLab 11.2
```yaml
preferred_config:
  audio_device: "Speakers (Yeti Classic)"
  routing: "Direct through Sonarworks"
  voicemeeter: "Bypassed for cleanest path"
  
alternative_config:
  audio_device: "UAD Volt 1"
  monitoring: "Via VoiceMeeter Input 3 → A1"
  use_when: "Need to record session or route elsewhere"
```

### Discord
```yaml
voice_settings:
  input_device: "Blue Yeti"
  output_device: "VoiceMeeter Aux Input (VAIO)"
  noise_suppression: "Enabled (Krisp)"
  echo_cancellation: "Enabled"
  
result: "You hear friends, stream doesn't"
```

### Sonobus
```yaml
audio_settings:
  input: "VoiceMeeter Aux (B2)"
  output: "VoiceMeeter Aux Input (VAIO)"
  sample_rate: "48000 Hz"
  buffer_size: "Auto (or 128 samples)"
  quality: "High"
  
connection_settings:
  public_server: true
  group_name: "[your_private_group]"
  password: "[set_password]"
```

---

## 🚦 Startup Procedures

### Pre-Streaming Checklist
```
1. [ ] Launch VoiceMeeter Potato
2. [ ] Verify A1 = Speakers (Yeti Classic)
3. [ ] Enable B1 (OBS output)
4. [ ] Disable B2 (Sonobus)
5. [ ] Blue Yeti → A1 + B1
6. [ ] VAIO3 → A1 + B1
7. [ ] Launch OBS
8. [ ] Verify "VoiceMeeter Output" in OBS audio
9. [ ] Launch Discord
10. [ ] Test levels (speak, play game audio)
11. [ ] Start streaming
```

### Pre-Mastering Checklist
```
1. [ ] Launch VoiceMeeter Potato
2. [ ] MUTE all inputs except Volt 1
3. [ ] Volt 1 → A1 ONLY
4. [ ] Disable B1, B2 (no outputs needed)
5. [ ] Launch WaveLab
6. [ ] Output: UAD Volt 1 OR Speakers (Yeti Classic) direct
7. [ ] Close Discord, browsers, games
8. [ ] Test playback
9. [ ] Verify Sonarworks correction active
```

### Pre-Remote Recording Checklist
```
1. [ ] Launch VoiceMeeter Potato
2. [ ] Blue Yeti → A1 + B2
3. [ ] Volt 1 → A1
4. [ ] Enable B2 (Sonobus output)
5. [ ] Disable B1 (no streaming)
6. [ ] Launch Sonobus
7. [ ] Input: VoiceMeeter Aux (B2)
8. [ ] Output: VoiceMeeter Aux Input (VAIO)
9. [ ] Connect to partner
10. [ ] Test bidirectional audio
11. [ ] Partner launches Luna on Mac Mini
```

---

## 🔄 Auto-Update Instructions

### How This File Updates
```yaml
trigger: "After any audio workflow session"
method: "FAITHH session summary → extract audio notes → update this file"

update_sources:
  - FAITHH conversation analysis
  - Manual notes in session summaries
  - Changes to VoiceMeeter config
  - New hardware additions
  - Workflow refinements

version_control:
  location: "~/ai-stack/parity/audio_workspace.md"
  git_tracked: true
  backup: "Automatic via git commits"
```

### Manual Update Triggers
```
Update this file when:
- [ ] Hardware changes (new interface, mic, etc)
- [ ] Software updates break routing
- [ ] Discover better routing method
- [ ] Add new workflow
- [ ] Change app configurations
```

### FAITHH Integration
```python
# Auto-update via FAITHH memory suggestions
def update_audio_parity(session_summary):
    """
    Detects audio-related discussions and updates parity file
    """
    audio_keywords = ['voicemeeter', 'wavelab', 'obs', 'sonobus', 
                      'routing', 'volt', 'yeti', 'elgato']
    
    if any(kw in session_summary.lower() for kw in audio_keywords):
        # Extract audio configuration changes
        # Update this parity file
        # Commit to git
        pass
```

---

## 🐛 Troubleshooting

### No Audio in OBS
```
Check:
1. VoiceMeeter B1 enabled?
2. OBS Mic/Aux = "VoiceMeeter Output"?
3. Blue Yeti → B1 routing active?
4. VAIO3 → B1 routing active?
5. OBS audio not muted in mixer?
```

### Discord Friends Can't Hear You
```
Check:
1. Discord input = Blue Yeti?
2. Blue Yeti physically connected?
3. Windows privacy settings allow mic?
4. Discord input sensitivity correct?
```

### Can't Hear Discord Friends
```
Check:
1. Discord output = VoiceMeeter Aux Input (VAIO)?
2. VAIO → A1 routing enabled in VoiceMeeter?
3. A1 output not muted?
4. Discord output volume up?
```

### No Sound During Mastering
```
Check:
1. WaveLab output device correct?
2. If using Volt 1: Input 3 → A1 enabled?
3. If direct: Sonarworks active?
4. A1 hardware output selected?
5. Master fader not at -∞?
```

### Sonobus Not Connecting
```
Check:
1. Internet connection stable?
2. Firewall allowing Sonobus?
3. Correct group name/password?
4. Partner connected to same group?
5. Audio devices selected correctly?
```

---

## 📈 Future Enhancements

### Planned Additions
```
- [ ] Automate workflow switching (bash scripts)
- [ ] Save VoiceMeeter presets (XML configs)
- [ ] OBS scene collection per workflow
- [ ] Automated gain staging script
- [ ] Session logger (track hours per workflow)
```

### Hardware Wishlist
```
- [ ] Stream Deck (workflow quick-switching)
- [ ] Secondary monitor (OBS/VoiceMeeter always visible)
- [ ] Presonus FaderPort (tactile DAW control)
```

---

## 📝 Session Log Template

```markdown
### [DATE] - [WORKFLOW NAME]
**Duration**: X hours
**Purpose**: Brief description

Changes Made:
- 

Issues Encountered:
- 

Solutions Applied:
- 

Notes for Next Time:
- 

Updated Parity File: [Y/N]
```

---

**Last Manual Update**: 2025-11-19  
**Next Review**: After first mastering session  
**Maintained By**: Jonathan + FAITHH auto-updates
