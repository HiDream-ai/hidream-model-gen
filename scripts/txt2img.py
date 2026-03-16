#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text to Image Generator
Generate images from text prompts using Vivago AI.
"""

import argparse
import json
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vivago_client import create_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate images from text using Vivago AI'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='Text description of desired image'
    )
    
    parser.add_argument(
        '--negative-prompt', '-np',
        default='',
        help='What to avoid in generation'
    )
    
    parser.add_argument(
        '--wh-ratio', '-r',
        default='16:9',
        choices=['1:1', '4:3', '3:4', '16:9', '9:16'],
        help='Aspect ratio (default: 16:9)'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=1,
        help='Number of images to generate (1-4, default: 1)'
    )
    
    parser.add_argument(
        '--version', '-v',
        default='kling-image-o1',
        help='Model version (default: kling-image-o1)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='results.json',
        help='Output file for results (default: results.json)'
    )
    
    parser.add_argument(
        '--token',
        default=os.environ.get('HIDREAM_TOKEN'),
        help='API token (or set HIDREAM_TOKEN env var)'
    )
    
    # Advanced parameters
    parser.add_argument(
        '--guidance-scale',
        type=float,
        default=7.5,
        help='Guidance scale (default: 7.5)'
    )
    
    parser.add_argument(
        '--sample-steps',
        type=int,
        default=40,
        help='Sampling steps (default: 40)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=-1,
        help='Random seed (-1 for random, default: -1)'
    )
    
    parser.add_argument(
        '--enhance',
        default='1k',
        choices=['1k', '2k', '4k'],
        help='Enhancement level (default: 1k)'
    )
    
    args = parser.parse_args()
    
    # Validate batch size
    if not 1 <= args.batch_size <= 4:
        logger.error("Batch size must be between 1 and 4")
        sys.exit(1)
    
    # Create client
    try:
        client = create_client(token=args.token)
    except ValueError as e:
        logger.error(f"Failed to create client: {e}")
        sys.exit(1)
    
    # Generate images
    logger.info(f"Generating {args.batch_size} image(s) with prompt: {args.prompt}")
    logger.info(f"Aspect ratio: {args.wh_ratio}, Version: {args.version}")
    
    results = client.text_to_image(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        wh_ratio=args.wh_ratio,
        batch_size=args.batch_size,
        version=args.version,
        guidance_scale=args.guidance_scale,
        sample_steps=args.sample_steps,
        seed=args.seed,
        enhance=args.enhance
    )
    
    if not results:
        logger.error("Generation failed")
        sys.exit(1)
    
    # Save results
    output_data = {
        'prompt': args.prompt,
        'parameters': {
            'wh_ratio': args.wh_ratio,
            'batch_size': args.batch_size,
            'version': args.version,
            'guidance_scale': args.guidance_scale,
            'sample_steps': args.sample_steps,
            'seed': args.seed,
            'enhance': args.enhance
        },
        'results': results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"Results saved to: {args.output}")
    
    # Print image URLs
    if not results:
        logger.error("No results returned")
        sys.exit(1)
    
    if isinstance(results, dict):
        # Error response
        print(f"\nError: {results.get('message', 'Unknown error')}")
        sys.exit(1)
    
    for i, result in enumerate(results):
        if isinstance(result, str):
            print(f"\n[{i+1}] Error: {result}")
            continue
        status = result.get('task_status')
        status_text = {1: '✓ Completed', 3: '✗ Failed', 4: '⊘ Rejected'}.get(status, '? Unknown')
        image_url = result.get('image', 'N/A')
        
        print(f"\n[{i+1}] {status_text}")
        print(f"    URL: {image_url}")
        
        if result.get('task_completion'):
            print(f"    Progress: {result['task_completion']*100:.0f}%")


if __name__ == '__main__':
    main()
