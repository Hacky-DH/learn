import boto3
import os
from pathlib import Path
from tqdm import tqdm
from urllib.parse import quote
import sys

ENDPOINT = ""
ACCESS_KEY = ""
SECRET_KEY = ""
BUCKET = ""
BATCH_SIZE = 10 * 1024 * 1024  # 10MB
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 10))


class OSS:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            use_ssl=False,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            endpoint_url=ENDPOINT,
        )

    def close(self):
        self.client.close()

    def upload(self, path, key):
        abs_path = Path(path).expanduser().absolute()
        if not abs_path.exists():
            print(f"文件不存在 {path}")
            return
        file_size = abs_path.stat().st_size
        if file_size <= BATCH_SIZE:
            self.client.upload_file(str(abs_path), BUCKET, key)
            print(f"成功上传 {path}，\n下载url {self.url(key)}")
            return
        print(f"分块上传 {path} 到 {key}")
        # self._upload_multipart(abs_path, key)
        self._upload_multipart_multi_thread(abs_path, key)
        print(f"成功上传 {path}，\n下载url {self.url(key)}")

    def _upload_multipart(self, path: Path, key: str):
        file_size = path.stat().st_size
        total_parts = (file_size + BATCH_SIZE - 1) // BATCH_SIZE
        mpu = self.client.create_multipart_upload(
            Bucket=BUCKET, Key=key, StorageClass="STANDARD"
        )
        upload_id = mpu["UploadId"]
        part_info = {"Parts": []}
        progress_bar = tqdm(
            total=file_size, unit="B", unit_scale=True, desc=f"上传 {path.name}"
        )
        # 读取并上传文件块
        part_number = 1
        uploaded_bytes = 0
        try:
            with open(str(path), "rb") as file:
                while True:
                    data = file.read(BATCH_SIZE)
                    if not data:
                        break
                    # 上传分块
                    response = self.client.upload_part(
                        Bucket=BUCKET,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data,
                    )
                    # 记录分块信息
                    part_info["Parts"].append(
                        {"PartNumber": part_number, "ETag": response["ETag"]}
                    )
                    # 更新进度
                    uploaded_bytes += len(data)
                    part_number += 1
                    progress_bar.update(len(data))
                    # 打印当前进度
                    if part_number % 10 == 0:  # 每10块打印一次详细信息
                        print(
                            f"  已上传 {part_number - 1}/{total_parts} 块 "
                            f"({self._format_size(uploaded_bytes)}/{self._format_size(file_size)})"
                        )

            progress_bar.close()
            # 完成上传
            self.client.complete_multipart_upload(
                Bucket=BUCKET, Key=key, UploadId=upload_id, MultipartUpload=part_info
            )
        except Exception as e:
            print(f"上传失败: {str(e)}")
            try:
                self.client.abort_multipart_upload(
                    Bucket=BUCKET, Key=key, UploadId=upload_id
                )
            except Exception:
                pass
            raise

    def _upload_multipart_multi_thread(self, path, key):
        import threading
        from concurrent.futures import ThreadPoolExecutor, wait

        file_size = path.stat().st_size
        # 初始化分块上传
        mpu = self.client.create_multipart_upload(
            Bucket=BUCKET, Key=key, StorageClass="STANDARD"
        )
        upload_id = mpu["UploadId"]
        try:
            progress_bar = tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=f"多线程上传 {path.name}",
            )
            uploaded_bytes = 0
            lock = threading.Lock()
            part_info_list = []

            def upload_part(part_num, data):
                """上传单个分块的函数"""
                response = self.client.upload_part(
                    Bucket=BUCKET,
                    Key=key,
                    PartNumber=part_num,
                    UploadId=upload_id,
                    Body=data,
                )

                with lock:
                    nonlocal uploaded_bytes
                    uploaded_bytes += len(data)
                    progress_bar.update(len(data))
                    part_info_list.append(
                        {"PartNumber": part_num, "ETag": response["ETag"]}
                    )

            # 读取文件并创建上传任务
            with (
                open(str(path), "rb") as file,
                ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor,
            ):
                futures = []
                part_number = 1
                while True:
                    data = file.read(BATCH_SIZE)
                    if not data:
                        break
                    # 提交上传任务到线程池
                    future = executor.submit(upload_part, part_number, data)
                    futures.append(future)
                    part_number += 1

            # 等待所有任务完成
            wait(futures)
            progress_bar.close()
            # 按PartNumber排序
            part_info_list.sort(key=lambda x: x["PartNumber"])
            part_info = {"Parts": part_info_list}
            # 完成上传
            self.client.complete_multipart_upload(
                Bucket=BUCKET, Key=key, UploadId=upload_id, MultipartUpload=part_info
            )
        except Exception as e:
            print(f"上传失败: {str(e)}")
            try:
                self.client.abort_multipart_upload(
                    Bucket=BUCKET, Key=key, UploadId=upload_id
                )
            except Exception:
                pass
            raise

    def _format_size(self, size_bytes):
        """格式化文件大小显示"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def download(self, key):
        name = Path(key).name
        response = self.client.get_object(Bucket=BUCKET, Key=key)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            body = response["Body"].read()
            with open(name, "wb") as f:
                f.write(body)
            print(f"成功下载 {key} 到 {name}")
        else:
            print("下载文件不存在")

    def delete(self, key):
        response = self.client.delete_object(Bucket=BUCKET, Key=key)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
            print(f"成功删除 {key}")
        else:
            print(f"删除文件失败 {response}")

    def url(self, key, internal=True):
        key = quote(key)
        if not internal:
            return f"https:///{key}"
        return f"https:///{key}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:  <file path>")
        exit()
    path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        key = sys.argv[2]
    else:
        key = path.name
    s3 = OSS()
    s3.upload(path, key)
    # s3.download(key)
    # s3.delete(key)
    s3.close()
