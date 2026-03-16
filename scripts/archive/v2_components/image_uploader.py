#!/usr/bin/env python3
"""
图片上传器 - 处理图片上传到Vivago存储
"""
import os
import uuid
import cv2
import numpy as np
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageUploader:
    """
    图片上传器
    
    职责：
    1. 图片压缩和调整大小
    2. 上传到Vivago存储
    3. 返回图片UUID
    """
    
    MAX_SIZE_MB = 5
    MAX_DIMENSION = 1024
    
    def __init__(self, s3_client, bucket: str = "hidreamai-image"):
        """
        初始化上传器
        
        Args:
            s3_client: boto3 S3客户端
            bucket: 存储桶名称
        """
        self.s3_client = s3_client
        self.bucket = bucket
    
    def upload(self, image_path: str) -> str:
        """
        上传图片到Vivago存储
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            图片UUID (如 j_xxxx)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # 检查文件大小
        size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if size_mb > self.MAX_SIZE_MB:
            logger.info(f"Image {size_mb:.1f}MB > {self.MAX_SIZE_MB}MB, will compress")
        
        # 处理图片
        processed_path = self._process_image(image_path)
        
        try:
            # 生成UUID
            image_uuid = f"j_{uuid.uuid4()}"
            s3_key = f"{image_uuid}.jpg"
            
            # 上传
            self.s3_client.upload_file(
                processed_path,
                self.bucket,
                s3_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            
            logger.info(f"Uploaded {image_path} -> {image_uuid}")
            return image_uuid
            
        finally:
            # 清理临时文件
            if processed_path != image_path and os.path.exists(processed_path):
                os.remove(processed_path)
    
    def _process_image(self, image_path: str) -> str:
        """
        处理图片（调整大小和压缩）
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            处理后的图片路径（可能是临时文件）
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        h, w = img.shape[:2]
        
        # 调整大小
        if max(h, w) > self.MAX_DIMENSION:
            scale = self.MAX_DIMENSION / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            logger.debug(f"Resized {w}x{h} -> {new_w}x{new_h}")
        
        # 保存到临时文件
        temp_path = f"/tmp/{uuid.uuid4()}.jpg"
        cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return temp_path
    
    def upload_multiple(self, image_paths: list) -> list:
        """
        批量上传图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            UUID列表
        """
        return [self.upload(path) for path in image_paths]
