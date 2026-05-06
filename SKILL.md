---
name: hidream-model-gen
description: Generate images and videos using Vivago AI / HiDream. Use for text-to-image, image-to-image, text-to-video, image-to-video, keyframe-to-video, and template video generation. Includes browser login, token refresh, and agent-friendly CLI scripts with JSON outputs.
dependencies:
  - requests
  - pillow
---

# HiDream / Vivago Generation Skill

Agent-ready integration with Vivago AI / HiDream generation APIs.

## Agent Quick Start

1. Start with the health check:

```bash
python3 scripts/healthcheck.py --json
```

2. If auth is missing, run browser login once:

```bash
python3 scripts/vivago_login.py --env overseas-prod login
```

3. Use the CLI matching the request:

```bash
# Text to image
python3 scripts/txt2img.py --prompt "a clean product photo of a ceramic mug" --wh-ratio 1:1

# Image to image
python3 scripts/img2img.py --prompt "make this a polished 3D app icon" --image ./assets/source.png --wh-ratio 1:1

# Text to video
python3 scripts/txt2vid.py --prompt "a ceramic mug gently rotating on a clean desk" --duration 5 --wh-ratio 1:1

# Image to video
python3 scripts/img2video.py --prompt "gentle camera push in" --image ./assets/source.png --duration 5 --wh-ratio 1:1
```

Default outputs are written under `assets/`:

- `assets/txt2img_results.json`
- `assets/img2img_results.json`
- `assets/txt2vid_results.json`
- `assets/img2video_results.json`

Each result JSON includes:

- `results`: raw API task results
- `asset_urls`: ready-to-use image/video URLs

For videos, return or send the URL in `asset_urls`; do not upload the video file unless explicitly requested.

## Supported Features

### Image Generation
- **Text to Image** (`txt2img`): Generate images from text descriptions
- **Image to Image** (`img2img`): Transform existing images based on prompts, including style transfer, image editing, and multi-image fusion

### Video Generation
- **Text to Video** (`txt2vid`): Generate videos from text descriptions
- **Image to Video** (`img2vid`): Generate videos from static images
- **Keyframe to Video** (`keyframe_to_video`): Generate transition videos from start and end keyframes
- **Video Templates** (`template_to_video`): 181 pre-defined video effects
- Supports multiple model versions (v3Pro, v3L, kling-video-o1)

### Additional Features
- Image upload to Vivago storage
- Batch generation (up to 4 images)
- Multiple aspect ratios (1:1, 4:3, 3:4, 16:9, 9:16)
- Automatic retry with polling

## Architecture

### Core Modules

```
scripts/
├── vivago_client.py       # Main API client
├── vivago_login.py        # Browser login, ticket refresh, local auth cache
├── healthcheck.py         # Fast auth/config readiness check
├── cli_utils.py           # Shared CLI output and URL helpers
├── txt2img.py             # Text-to-image CLI
├── img2img.py             # Image-to-image CLI
├── txt2vid.py             # Text-to-video CLI
├── img2video.py           # Image-to-video CLI
├── template_manager.py    # Template management
├── config_loader.py       # Configuration loading
├── enums.py              # Type enums (TaskStatus, AspectRatio, etc.)
├── exceptions.py         # Structured exceptions
└── config/               # Modular configuration files
```

### Code Quality

- **Type Safety**: Complete type annotations and enums
- **Exception Handling**: Structured exception hierarchy
- **CI/CD**: GitHub Actions for automated testing
- **Modular Config**: Split configuration files for maintainability

## Setup

### Authentication

This skill can authenticate in either of two ways:

1. Use an existing `HIDREAM_AUTHORIZATION` or `HIDREAM_TOKEN`.
2. Use the bundled Vivago browser login helper. When no token env var is set, `create_client()` automatically reads the local Vivago auth cache, refreshes an expired ticket when possible, or opens the browser login flow when needed.

#### Bundled Login

Authentication data is stored under `~/.config/vivago-auth/` (or `$XDG_CONFIG_HOME/vivago-auth/`) and is managed by `scripts/vivago_login.py`.

```bash
# Login once and save the local auth cache
python scripts/vivago_login.py --env overseas-prod login

# Print a valid ticket, refreshing it if needed
python scripts/vivago_login.py --env overseas-prod token

# Check auth status without printing secrets
python scripts/vivago_login.py --env overseas-prod status

# Remove cached auth
python scripts/vivago_login.py --env overseas-prod logout
```

Supported auth environments:

- `overseas-dev`
- `overseas-prod` (default for Vivago API generation)
- `domestic-dev`
- `domestic-prod`

Environment controls:

```bash
export VIVAGO_AUTH_ENV="overseas-prod"
export VIVAGO_AUTH_AUTO_LOGIN=1
```

Set `VIVAGO_AUTH_AUTO_LOGIN=0` to restore the older behavior where a missing token fails immediately.

#### Manual Token

If you prefer to provide a Vivago.ai API Token manually:

#### Step 1: Login to Vivago.ai
1. Visit [https://vivago.ai/](https://vivago.ai/) and log in to your account
2. Check your remaining credits and consider subscribing to a suitable plan if needed

#### Step 2: Obtain Your Token
1. After logging in, visit [https://vivago.ai/prod-api/user/token](https://vivago.ai/prod-api/user/token)
2. The page will return your API Token (in JWT format)
3. Copy this Token for configuration

> **Security Note**: The Token is your credential for accessing the API. Please keep it secure and do not share it with others.

### Environment Variables

Export it securely in your current session:

```bash
export HIDREAM_AUTHORIZATION="your_vivago_api_token"
```

> **Note:** `STORAGE_AK` and `STORAGE_SK` are deprecated and removed. The image upload uses secure pre-signed URLs provided by the Vivago API.

### File Output Configuration

**Important:** By default, all generated resources (JSON results, downloaded images, and videos) will be output to the `assets/` directory within the current working folder. Ensure this directory exists or the system has permission to create it.


### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from scripts import create_client, VivagoClient
from scripts.enums import AspectRatio, PortName, TaskStatus
from scripts.exceptions import TaskFailedError, TaskTimeoutError

# Create client
client = create_client()

# Text to image
results = client.text_to_image(
    prompt="a beautiful sunset over mountains",
    port=PortName.KLING_IMAGE,  # or PortName.NANO_BANANA
    wh_ratio=AspectRatio.RATIO_16_9,
    batch_size=2
)

# Image to video (using local image)
results = client.image_to_video(
    prompt="camera slowly zooming out",
    image_uuid=client.upload_image("/path/to/image.jpg"),
    port=PortName.V3PRO,
    wh_ratio=AspectRatio.RATIO_16_9,
    duration=5
)

# Keyframe to video (using start and end images)
results = client.keyframe_to_video(
    prompt="smooth transition from start to end",
    start_image_uuid=client.upload_image("/path/to/start.jpg"),
    end_image_uuid=client.upload_image("/path/to/end.jpg"),
    port=PortName.V3PRO,
    wh_ratio=AspectRatio.RATIO_16_9,
    duration=5
)

# Video Templates - use pre-defined effects
results = client.template_to_video(
    image_uuid=client.upload_image("/path/to/image.jpg"),
    template="ghibli",  # See available templates below
    wh_ratio=AspectRatio.RATIO_9_16
)
```

### Error Handling

```python
from scripts.exceptions import (
    TaskFailedError,
    TaskRejectedError,
    TaskTimeoutError,
    InvalidPortError
)

try:
    results = client.image_to_video(...)
except TaskFailedError as e:
    print(f"Task failed: {e.task_id}")
except TaskRejectedError as e:
    print(f"Content rejected: {e.reason}")
except TaskTimeoutError as e:
    print(f"Timeout after {e.timeout_seconds}s")
except InvalidPortError as e:
    print(f"Invalid port: {e.port}, available: {e.available}")
```

### Command Line (Best for AI Agents)

**For AI Agents:** The easiest way to use this skill is through the provided CLI scripts. They automatically handle API communication, polling, and result parsing. By default, they use **HiDream's native models**.

**Health Check:**
```bash
python3 scripts/healthcheck.py --json
```

**Text to Image:**
```bash
python3 scripts/txt2img.py \
  --prompt "a futuristic city" \
  --wh-ratio 16:9 \
  --batch-size 2
```
Output: `assets/txt2img_results.json`. Defaults to the `hidream-txt2img` model.

**Text to Video:**
```bash
python3 scripts/txt2vid.py \
  --prompt "a cybernetic dragon flying over a futuristic city" \
  --wh-ratio 16:9 \
  --duration 5
```
Output: `assets/txt2vid_results.json`. Defaults to the `v3Pro` model.

**Image to Video:**
```bash
python3 scripts/img2video.py \
  --prompt "slow motion falling leaves" \
  --image ./assets/source_image.jpg \
  --duration 5
```
Output: `assets/img2video_results.json`.

**Image to Image:**
```bash
python3 scripts/img2img.py \
  --prompt "turn this portrait into a cinematic editorial photo" \
  --image ./assets/source_image.jpg \
  --wh-ratio 16:9
```
Output: `assets/img2img_results.json`.

## API Reference

### Enums

```python
from scripts.enums import (
    TaskStatus,      # PENDING, COMPLETED, PROCESSING, FAILED, REJECTED
    AspectRatio,     # RATIO_1_1, RATIO_4_3, RATIO_16_9, etc.
    PortCategory,    # TEXT_TO_IMAGE, IMAGE_TO_VIDEO, etc.
    PortName         # KLING_IMAGE, V3PRO, NANO_BANANA, etc.
)
```

### Models

| Feature | Available Versions | Default |
|---------|-------------------|---------|
| Text to Image | v3L (HiDream), kling-image-o1 | **v3L** (via port `hidream-txt2img`) |
| Image to Image | kling-image-o1, nano-banana-2 | **Kling O1** (via port `kling-image`) |
| Image to Video | v3Pro, v3L, kling-video-o1 | **v3Pro** |
| Keyframe to Video | v3Pro, v3L | **v3Pro** |

> **Note for AI Agents:** By default, all CLI tools (`txt2img.py`, `txt2vid.py`) are pre-configured to use HiDream's native models (`hidream-txt2img` for images, `v3Pro` for videos). You don't need to specify the model unless explicitly requested by the user.

### Aspect Ratios

- `1:1` - Square
- `4:3` - Standard
- `3:4` - Portrait
- `16:9` - Widescreen
- `9:16` - Mobile/Vertical

### Task Status Codes

```python
from scripts.enums import TaskStatus

TaskStatus.PENDING     # 0 - Pending
TaskStatus.COMPLETED   # 1 - Completed
TaskStatus.PROCESSING  # 2 - Processing
TaskStatus.FAILED      # 3 - Failed
TaskStatus.REJECTED    # 4 - Rejected (content review)
```

## File Structure

```
vivago-ai-skill/
├── scripts/
│   ├── __init__.py         # Package exports
│   ├── vivago_client.py    # Core API client
│   ├── vivago_login.py     # Browser login and token refresh
│   ├── txt2img.py          # Text-to-image CLI
│   ├── img2img.py          # Image-to-image CLI
│   ├── txt2vid.py          # Text-to-video CLI
│   ├── img2video.py        # Image-to-video CLI
│   ├── template_manager.py # Template management
│   ├── config_loader.py    # Configuration loader
│   ├── enums.py            # Type enums
│   ├── exceptions.py       # Exception classes
│   ├── logging_config.py   # Logging configuration
│   └── config/             # Modular config files
│       ├── base.json
│       ├── text_to_image.json
│       ├── text_to_video.json
│       ├── image_to_image.json
│       ├── image_to_video.json
│       ├── keyframe_to_video.json
│       └── template_to_video.json
├── requirements.txt
└── SKILL.md               # This file
```

## Important Notes

### Feishu Channel Messaging Guidelines

When sending generated content through Feishu (飞书) channel:

| Content Type | Send Method | Example |
|-------------|-------------|---------|
| **Images** | ✅ Direct file upload | Attach image file directly |
| **Videos** | ❌ **Must send as link** | `https://media.vivago.ai/{video_uuid}` |

**⚠️ Critical**: Videos **CANNOT** be sent as file attachments in Feishu. Always construct and send the direct media URL:

```
https://media.vivago.ai/b1268f08-ac32-4b83-863f-a419797d768e.mp4
```

**Why**: Feishu does not support playable video attachments. Sending video files directly will result in delivery failure or unplayable content.

### Image Download

Images can be downloaded using the correct URL format:

```
https://storage.vivago.ai/image/{image_name}.jpg
```

**Example:**
```python
from scripts import create_client
import requests

client = create_client()

# Generate image
results = client.text_to_image(prompt="a cute cat")
image_name = results[0].get('image', '')

# Download image
image_url = f"https://storage.vivago.ai/image/{image_name}.jpg"
response = requests.get(image_url)
with open("output.jpg", "wb") as f:
    f.write(response.content)
```

**Sending via Feishu:**
```python
# Download and send through Feishu
image_data = requests.get(image_url).content
# Then send image_data as file attachment via Feishu API
```

### Asynchronous Processing
- API calls are asynchronous with automatic polling
- Images are automatically resized to max 1024px on longest side before upload
- Video generation supports 5 or 10 second durations
- Batch size for images: 1-4, for videos: 1
- All API calls include automatic retry logic

## Error Handling

The client handles common errors:
- Network timeouts (with retry)
- Rate limiting (with exponential backoff)
- Invalid parameters (validation before API call)
- Task failures (structured exceptions)

### Exception Hierarchy

```
VivagoError (base)
├── VivagoAPIError
├── MissingCredentialError
├── InvalidPortError
├── ImageUploadError
├── TemplateNotFoundError
└── TaskError
    ├── TaskFailedError
    ├── TaskRejectedError
    └── TaskTimeoutError
```

## Video Templates Reference

The following **181 video templates** are available via `template_to_video()`:

### Quick Categories

| Category | Count | Example Templates |
|----------|-------|-------------------|
| **Style Transfer** | 20+ | ghibli, 1930s-2000s vintage styles |
| **Harry Potter** | 4 | magic_reveal_ravenclaw, gryffindor, hufflepuff, slytherin |
| **Wings/Fantasy** | 10+ | angel_wings, phoenix_wings, crystal_wings, fire_wings |
| **Superheroes** | 5+ | iron_man, cat_woman, ghost_rider |
| **Dance** | 10+ | apt, dadada, dance, limbo_dance |
| **Effects** | 15+ | ash_out, metallic_liquid, flash_flood |
| **Thanksgiving** | 10+ | turkey_chasing, autumn_feast, gratitude_photo |
| **Comics/Cartoon** | 8+ | gta_star, anime_figure, bring_comics_to_life |
| **Products** | 8+ | glasses_display, music_box, food_product_display |
| **Scenes** | 20+ | romantic_kiss, graduation, starship_chef |

### Popular Templates

| Template ID | Description |
|-------------|-------------|
| `ghibli` / `ghibli2` | Studio Ghibli animation style |
| `magic_reveal_ravenclaw` | Harry Potter Ravenclaw transformation |
| `magic_reveal_gryffindor` | Harry Potter Gryffindor transformation |
| `magic_reveal_hufflepuff` | Harry Potter Hufflepuff transformation |
| `magic_reveal_slytherin` | Harry Potter Slytherin transformation |
| `iron_man` | Iron Man armor assembly |
| `angel_wings` / `phoenix_wings` / `crystal_wings` / `fire_wings` | Wing transformations |
| `cat_woman` | Cat Woman style |
| `ghost_rider` | Ghost Rider flaming skull |
| `joker` | Joker villain style |
| `mermaid` | Mermaid underwater scene |
| `snow_white` | Snow White princess |
| `barbie` | Barbie princess transformation |
| `me_in_hand` | Miniature figure in hand |
| `music_box` | Rotating figure on music box |
| `anime_figure` | Transform into anime figure |
| `gta_star` | GTA game style transformation |
| `apt` / `dadada` / `dance` | Dance templates |
| `ash_out` | Disintegrate into ashes |
| `eye_of_the_storm` | Thunder god awakening |
| `metallic_liquid` | Metal mask transformation |
| `flash_flood` | Water/flood effect |
| `turkey_chasing` / `turkey_away` / `turkey_giant` | Thanksgiving turkey scenes |
| `autumn_feast` / `autumn_stroll` | Autumn scenes |
| `renovation_of_old_photos` | Colorize B&W photos |
| `graduation` | Graduation ceremony |
| `glasses` / `glasses_display` | Glasses/eyewear showcase |
| `bikini` / `sexy_man` / `sexy_pants` | Fashion/beach |
| `romantic_kiss` / `boyfriends_rose` / `girlfriends_rose` | Romantic scenes |
| `ai_archaeologist` / `starship_chef` / `cyber_cooker` | Sci-fi characters |
| `jungle_reign` / `panther_queen` / `roar_of_the_dustlands` / `tiger_snuggle` | Animal companions |
| `instant_sadness` / `headphone_vibe` / `relax` | Emotion/reaction |
| `frost_alert` | Cold/freeze effect |
| `bald_me` | Bald transformation |
| `boom_hair` / `curl_pop` / `long_hair` | Hair transformations |
| `muscles` | Muscle transformation |
| `face_punch` / `gun_point` | Action effects |
| `static_shot` / `tracking_shot` / `orbit_shot` / `push_in` / `zoom_out` / `handheld_shot` | Camera movements |
| `earth_zoom_in` / `earth_zoom_out` | Earth zoom effects |

### View All Templates

```python
from scripts.template_manager import get_template_manager

manager = get_template_manager()
templates = manager.list_templates()

print(f"Total templates: {len(templates)}")
for tid, name in sorted(templates.items()):
    print(f"  {tid}: {name}")
```

### Usage Example

```python
from scripts import create_client

client = create_client()

# Upload image
image_uuid = client.upload_image("/path/to/photo.jpg")

# Apply Ghibli style template
results = client.template_to_video(
    image_uuid=image_uuid,
    template="ghibli",
    wh_ratio="9:16"
)

# Harry Potter transformation
results = client.template_to_video(
    image_uuid=image_uuid,
    template="magic_reveal_ravenclaw",
    wh_ratio="9:16"
)
```

## Changelog

### v0.9.0 (2026-03-09)
- ✅ Code review complete (P0-P3)
- ✅ Added GitHub Actions CI
- ✅ Added type safety module (enums.py)
- ✅ Added structured exceptions (exceptions.py)
- ✅ Split configuration into modular files
- ✅ Archived redundant code and tests
- ✅ Pinned dependency versions

### v0.8.2 (2026-03-08)
- ✅ Template testing: 44 templates, 40 passed (90.9%)
- ✅ Fixed metallic_liquid naming issue
- ✅ Marked long_hair as deprecated

### v0.8.0 (2026-03-07)
- ✅ Completed Tier 1-4 testing
- ✅ Established smart test optimization system
