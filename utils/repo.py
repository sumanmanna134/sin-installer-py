import requests
import shutil
import os
from pathlib import Path
import structlog

logger=structlog.get_logger()
class RepositoryDownloader:
    def download_repo(self, repo_url:str, dest_dir: Path):
        try:
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            dest_dir.mkdir(parents=True)

            repo_zip = dest_dir / "repo.zip"
            response = requests.get(f"{repo_url}/archive/refs/heads/main.zip", timeout=30)
            response.raise_for_status()
            with open(repo_zip, 'wb') as f:
                f.write(response.content)
            shutil.unpack_archive(repo_zip, dest_dir)
            extracted_dir = next(dest_dir.iterdir())
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(dest_dir/item.name))

            repo_zip.unlink()
            shutil.rmtree(extracted_dir)
        except Exception as e:
            logger.error("Failed to download repository", url=repo_url, error=str(e))
            raise RuntimeError(f"Failed to download repository: {str(e)}") 