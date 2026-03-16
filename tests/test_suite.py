#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vivago AI Skill Test Suite
Standardized testing framework with version control and report generation.
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vivago_client import create_client, VivagoClient


class TestResult:
    """Test result container"""
    
    def __init__(self, test_name: str, test_id: str):
        self.test_name = test_name
        self.test_id = test_id
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = "NOT_STARTED"  # NOT_STARTED, RUNNING, PASSED, FAILED, SKIPPED
        self.error_message: Optional[str] = None
        self.response_data: Optional[Any] = None
        self.duration_ms: int = 0
        
    def start(self):
        """Mark test as started"""
        self.start_time = datetime.now()
        self.status = "RUNNING"
        
    def end(self, status: str, error: str = None, data: Any = None):
        """Mark test as ended"""
        self.end_time = datetime.now()
        self.status = status
        self.error_message = error
        self.response_data = data
        if self.start_time:
            self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "test_name": self.test_name,
            "test_id": self.test_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "response_data": self.response_data
        }


class TestSuite:
    """Test suite runner"""
    
    def __init__(self, config_path: str = "tests/test_config.json"):
        self.config = self._load_config(config_path)
        self.results: List[TestResult] = []
        self.client: Optional[VivagoClient] = None
        self.suite_id = str(uuid.uuid4())[:8]
        self.suite_start_time = datetime.now()
        
    def _load_config(self, path: str) -> Dict:
        """Load test configuration"""
        full_path = os.path.join(os.path.dirname(__file__), '..', path)
        with open(full_path, 'r') as f:
            return json.load(f)
    
    def setup(self) -> bool:
        """Setup test environment"""
        logger.info("=" * 60)
        logger.info(f"Test Suite ID: {self.suite_id}")
        logger.info(f"Version: {self.config['version']}")
        logger.info(f"Start Time: {self.suite_start_time.isoformat()}")
        logger.info("=" * 60)
        
        try:
            self.client = create_client()
            logger.info("✓ Client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize client: {e}")
            return False
    
    def run_test(self, test_name: str, test_func, **kwargs) -> TestResult:
        """Run a single test"""
        test_id = f"{self.suite_id}_{test_name}_{int(time.time())}"
        result = TestResult(test_name, test_id)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Running Test: {test_name}")
        logger.info(f"Test ID: {test_id}")
        logger.info('='*60)
        
        result.start()
        
        try:
            test_func(result, **kwargs)
            if result.status == "RUNNING":
                result.end("PASSED")
                logger.info(f"✓ Test {test_name} PASSED")
        except Exception as e:
            result.end("FAILED", str(e))
            logger.error(f"✗ Test {test_name} FAILED: {e}")
        
        logger.info(f"Duration: {result.duration_ms}ms")
        self.results.append(result)
        return result
    
    # ==================== Test Cases ====================
    
    def test_txt2img_basic(self, result: TestResult):
        """Test basic text-to-image generation"""
        logger.info("Testing basic text-to-image generation...")
        
        response = self.client.text_to_image(
            prompt="a simple red circle on white background",
            wh_ratio="1:1",
            batch_size=1,
            version="kling-image-o1"
        )
        
        result.response_data = response
        
        if response is None:
            raise Exception("API returned None")
        
        if isinstance(response, dict) and response.get('code') != 0:
            raise Exception(f"API Error: {response.get('message')}")
        
        if isinstance(response, list) and len(response) > 0:
            task_status = response[0].get('task_status')
            if task_status == 1:
                logger.info(f"✓ Image generated: {response[0].get('image')}")
            elif task_status == 3:
                raise Exception("Task failed")
            elif task_status == 4:
                raise Exception("Task rejected (content review)")
            else:
                logger.info(f"Task status: {task_status} (may still be processing)")
    
    def test_txt2img_batch(self, result: TestResult):
        """Test batch generation"""
        logger.info("Testing batch text-to-image generation...")
        
        response = self.client.text_to_image(
            prompt="a blue square",
            wh_ratio="1:1",
            batch_size=2,
            version="kling-image-o1"
        )
        
        result.response_data = response
        
        if response is None:
            raise Exception("API returned None")
        
        if isinstance(response, list):
            logger.info(f"✓ Generated {len(response)} images")
            for i, r in enumerate(response):
                logger.info(f"  [{i+1}] Status: {r.get('task_status')}")
    
    def test_txt2img_ratios(self, result: TestResult):
        """Test different aspect ratios"""
        logger.info("Testing different aspect ratios...")
        
        ratios = ["1:1", "16:9"]
        results_by_ratio = {}
        
        for ratio in ratios:
            logger.info(f"  Testing ratio: {ratio}")
            response = self.client.text_to_image(
                prompt="a green triangle",
                wh_ratio=ratio,
                batch_size=1,
                version="kling-image-o1"
            )
            results_by_ratio[ratio] = response
            
            if isinstance(response, list) and response:
                logger.info(f"  ✓ Ratio {ratio}: status={response[0].get('task_status')}")
        
        result.response_data = results_by_ratio
    
    def test_api_error_handling(self, result: TestResult):
        """Test API error handling"""
        logger.info("Testing API error handling...")
        
        # Test with empty prompt (should fail)
        try:
            response = self.client.text_to_image(
                prompt="",
                wh_ratio="1:1",
                batch_size=1
            )
            result.response_data = {"empty_prompt_response": response}
            logger.info(f"  Empty prompt response: {response}")
        except Exception as e:
            logger.info(f"  ✓ Empty prompt rejected: {e}")
            result.response_data = {"empty_prompt_error": str(e)}
    
    # ==================== Suite Runner ====================
    
    def run_all(self):
        """Run all enabled tests"""
        if not self.setup():
            logger.error("Setup failed, aborting tests")
            return False
        
        test_cases = self.config.get('test_cases', {})
        
        # Run enabled tests
        for test_name, test_config in test_cases.items():
            if not test_config.get('enabled', False):
                logger.info(f"\nSkipping {test_name} (disabled)")
                continue
            
            test_method = getattr(self, f'test_{test_name}', None)
            if test_method:
                self.run_test(test_name, test_method)
            else:
                logger.warning(f"No test method found for {test_name}")
        
        # Generate report
        self.generate_report()
        return True
    
    def generate_report(self):
        """Generate test report"""
        suite_end_time = datetime.now()
        total_duration = int((suite_end_time - self.suite_start_time).total_seconds() * 1000)
        
        report = {
            "suite_id": self.suite_id,
            "version": self.config['version'],
            "start_time": self.suite_start_time.isoformat(),
            "end_time": suite_end_time.isoformat(),
            "total_duration_ms": total_duration,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.status == "PASSED"),
                "failed": sum(1 for r in self.results if r.status == "FAILED"),
                "skipped": sum(1 for r in self.results if r.status == "SKIPPED")
            },
            "environment": self.config['environment'],
            "api_config": {
                "base_url": self.config['api_config']['base_url'],
                "timeout": self.config['api_config']['timeout']
            },
            "results": [r.to_dict() for r in self.results]
        }
        
        # Save report
        report_filename = f"test_report_{self.suite_id}_{self.suite_start_time.strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), '..', 'test_reports', report_filename)
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("TEST SUITE COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Suite ID: {self.suite_id}")
        logger.info(f"Total Tests: {report['summary']['total']}")
        logger.info(f"Passed: {report['summary']['passed']}")
        logger.info(f"Failed: {report['summary']['failed']}")
        logger.info(f"Skipped: {report['summary']['skipped']}")
        logger.info(f"Total Duration: {total_duration}ms")
        logger.info(f"Report saved to: {report_path}")
        logger.info(f"{'='*60}")
        
        return report


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vivago AI Skill Test Suite')
    parser.add_argument('--config', '-c', default='tests/test_config.json',
                       help='Test configuration file')
    parser.add_argument('--test', '-t', help='Run specific test only')
    
    args = parser.parse_args()
    
    suite = TestSuite(args.config)
    
    if args.test:
        # Run single test
        if not suite.setup():
            sys.exit(1)
        
        test_method = getattr(suite, f'test_{args.test}', None)
        if test_method:
            suite.run_test(args.test, test_method)
            suite.generate_report()
        else:
            logger.error(f"Unknown test: {args.test}")
            sys.exit(1)
    else:
        # Run all tests
        suite.run_all()


if __name__ == '__main__':
    main()
