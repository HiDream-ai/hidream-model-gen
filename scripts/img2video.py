#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image to Video Generator
Generate videos from images using Vivago AI.
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vivago_client import create_client
from scripts.exceptions import MissingCredentialError
from scripts.cli_utils import collect_asset_urls, default_output, save_json, video_url

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate videos from images using Vivago AI'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='Text description of video motion'
    )
    
    parser.add_argument(
        '--image', '-i',
        required=True,
        help='Path to source image or image_uuid'
    )
    
    parser.add_argument(
        '--wh-ratio', '-r',
        default='16:9',
        choices=['1:1', '4:3', '3:4', '16:9', '9:16'],
        help='Aspect ratio (default: 16:9)'
    )
    
    parser.add_argument(
        '--port',
        '--version',
        '-v',
        dest='port',
        default='v3Pro',
        choices=['v3Pro', 'v3L', 'kling-video'],
        help='Model port (default: v3Pro)'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=5,
        choices=[5, 10],
        help='Video duration in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--mode', '-m',
        default='Slow',
        choices=['Slow', 'Fast'],
        help='Generation mode (default: Slow)'
    )
    
    parser.add_argument(
        '--fast-mode',
        action='store_true',
        help='Enable fast mode'
    )
    
    parser.add_argument(
        '--motion-strength',
        type=int,
        default=9,
        help='Motion strength (default: 9)'
    )
    
    parser.add_argument(
        '--negative-prompt', '-np',
        default='',
        help='What to avoid in generation'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=default_output('img2video_results.json'),
        help='Output JSON file (default: assets/img2video_results.json)'
    )
    
    parser.add_argument(
        '--token',
        default=os.environ.get('HIDREAM_AUTHORIZATION') or os.environ.get('HIDREAM_TOKEN'),
        help='API token (or use HIDREAM_AUTHORIZATION/HIDREAM_TOKEN; falls back to bundled Vivago login)'
    )
    
    parser.add_argument(
        '--storage-ak',
        default=os.environ.get('STORAGE_AK'),
        help='[Deprecated] Storage access key - no longer required'
    )
    
    parser.add_argument(
        '--storage-sk',
        default=os.environ.get('STORAGE_SK'),
        help='[Deprecated] Storage secret key - no longer required'
    )
    
    args = parser.parse_args()
    
    # Create client
    try:
        client = create_client(token=args.token)
    except MissingCredentialError as e:
        logger.error(f"Failed to create client: {e}")
        logger.error("Set HIDREAM_AUTHORIZATION/HIDREAM_TOKEN, use --token, or run: python scripts/vivago_login.py --env overseas-prod login")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        sys.exit(1)
    
    # Handle image input
    image_uuid = args.image
    if os.path.exists(args.image):
        logger.info(f"Uploading image: {args.image}")
        try:
            image_uuid = client.upload_image(args.image)
            logger.info(f"Image uploaded: {image_uuid}")
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            sys.exit(1)
    else:
        logger.info(f"Using existing image_uuid: {image_uuid}")
    
    # Generate video
    logger.info(f"Generating video from image: {image_uuid}")
    logger.info(f"Prompt: {args.prompt}")
    logger.info(f"Port: {args.port}, Duration: {args.duration}s, Mode: {args.mode}")
    
    results = client.image_to_video(
        prompt=args.prompt,
        image_uuid=image_uuid,
        port=args.port,
        wh_ratio=args.wh_ratio,
        duration=args.duration,
        mode=args.mode,
        fast_mode=args.fast_mode,
        motion_strength=args.motion_strength,
        negative_prompt=args.negative_prompt
    )
    
    if not results:
        logger.error("Video generation failed")
        sys.exit(1)
    
    # Save results
    output_data = {
        'prompt': args.prompt,
        'image_uuid': image_uuid,
        'parameters': {
            'wh_ratio': args.wh_ratio,
            'port': args.port,
            'duration': args.duration,
            'mode': args.mode,
            'fast_mode': args.fast_mode,
            'motion_strength': args.motion_strength
        },
        'results': results,
        'asset_urls': collect_asset_urls(results)
    }
    
    save_json(args.output, output_data)
    
    logger.info(f"Results saved to: {args.output}")
    
    # Print video URLs
    for i, result in enumerate(results):
        status = result.get('task_status')
        status_text = {1: '✓ Completed', 3: '✗ Failed', 4: '⊘ Rejected'}.get(status, '? Unknown')
        url = result.get('video') or result.get('image') or 'N/A'
        if isinstance(url, str) and url != 'N/A':
            url = video_url(url)
        
        print(f"\n[{i+1}] {status_text}")
        print(f"    URL: {url}")
        
        if result.get('task_completion'):
            print(f"    Progress: {result['task_completion']*100:.0f}%")


if __name__ == '__main__':
    main()
