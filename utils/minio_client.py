import asyncio
from minio import Minio
from minio.error import S3Error
import os


class MinIOClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str = "tasks", secure: bool = False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure
        self.client = None
        self._initialized = False
        try:
            self.client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            self._init_bucket()
            self._initialized = True
        except Exception as e:
            print(f"MinIO client initialization error: {e}")
    
    def _init_bucket(self):
        if not self.client:
            return
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"MinIO bucket init error: {e}")
        except Exception as e:
            print(f"MinIO bucket init error: {e}")
    
    async def upload_file(self, file_name: str, file_content: bytes, content_type: str = "application/octet-stream") -> str:
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    self.bucket_name,
                    file_name,
                    file_content,
                    len(file_content),
                    content_type=content_type
                )
            )
            
            protocol = "https" if self.secure else "http"
            file_url = f"{protocol}://{self.endpoint}/{self.bucket_name}/{file_name}"
            return file_url
        except S3Error as e:
            raise Exception(f"MinIO upload error: {e}")
    
    async def check_connection(self) -> bool:
        if not self.client:
            return False
        
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.bucket_exists(self.bucket_name)
            )
            return True
        except Exception:
            return False
