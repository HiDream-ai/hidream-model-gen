#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image to Image Generator
Transform one or more reference images using Vivago AI.
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vivago_client import create_client
from scripts.exceptions import MissingCredentialError
from scripts.cli_utils import collect_asset_urls, default_output, image_url, save_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate images from reference images using Vivago AI'
    )
    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='Text description of the desired image transformation'
    )
    parser.add_argument(
        '--image', '-i',
        action='append',
        required=True,
        help='Path to a source image or existing image_uuid. Repeat for multiple images.'
    )
    parser.add_argument(
        '--wh-ratio', '-r',
        default='16:9',
        choices=['1:1', '4:3', '3:4', '16:9', '9:16'],
        help='Aspect ratio (default: 16:9)'
    )
    parser.add_argument(
        '--port',
        default='kling-image',
        choices=['kling-image', 'nano-banana'],
        help='Model port (default: kling-image)'
    )
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=1,
        help='Number of images to generate (default: 1)'
    )
    parser.add_argument(
        '--strength',
        type=float,
        default=0.8,
        help='Transformation strength from 0.0 to 1.0 (default: 0.8)'
    )
    parser.add_argument(
        '--negative-prompt', '-np',
        default='',
        help='What to avoid in generation'
    )
    parser.add_argument(
        '--output', '-o',
        default=default_output('img2img_results.json'),
        help='Output JSON file (default: assets/img2img_results.json)'
    )
    parser.add_argument(
        '--token',
        default=os.environ.get('HIDREAM_AUTHORIZATION') or os.environ.get('HIDREAM_TOKEN'),
        help='API token (or use HIDREAM_AUTHORIZATION/HIDREAM_TOKEN; falls back to bundled Vivago login)'
    )

    args = parser.parse_args()

    try:
        client = create_client(token=args.token)
    except MissingCredentialError as e:
        logger.error(f"Failed to create client: {e}")
        logger.error("Set HIDREAM_AUTHORIZATION/HIDREAM_TOKEN, use --token, or run: python scripts/vivago_login.py --env overseas-prod login")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        sys.exit(1)

    image_uuids = []
    for image in args.image:
        if os.path.exists(image):
            logger.info(f"Uploading image: {image}")
            try:
                image_uuids.append(client.upload_image(image))
            except Exception as e:
                logger.error(f"Failed to upload image {image}: {e}")
                sys.exit(1)
        else:
            image_uuids.append(image)

    logger.info(f"Generating image from {len(image_uuids)} reference image(s)")
    results = client.image_to_image(
        prompt=args.prompt,
        image_uuids=image_uuids,
        port=args.port,
        wh_ratio=args.wh_ratio,
        strength=args.strength,
        negative_prompt=args.negative_prompt,
        batch_size=args.batch_size,
    )

    if not results:
        logger.error("Image generation failed")
        sys.exit(1)

    output_data = {
        'prompt': args.prompt,
        'image_uuids': image_uuids,
        'parameters': {
            'wh_ratio': args.wh_ratio,
            'port': args.port,
            'batch_size': args.batch_size,
            'strength': args.strength,
        },
        'results': results,
        'asset_urls': collect_asset_urls(results),
    }

    save_json(args.output, output_data)

    logger.info(f"Results saved to: {args.output}")
    for i, result in enumerate(results):
        if isinstance(result, str):
            print(f"\n[{i + 1}] Error: {result}")
            continue
        status = result.get('task_status')
        status_text = {1: 'Completed', 3: 'Failed', 4: 'Rejected'}.get(status, 'Unknown')
        url = result.get('image', 'N/A')
        if isinstance(url, str):
            url = image_url(url)
        print(f"\n[{i + 1}] {status_text}")
        print(f"    URL: {url}")


if __name__ == '__main__':
    main()
