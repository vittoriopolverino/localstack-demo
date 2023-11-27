import json
import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import urllib3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DockerAPIClient:
    docker_api_url: Optional[str] = field(default=os.environ.get('DOCKER_API_URL', None))

    def get_data_from_api(self) -> dict:
        try:
            http = urllib3.PoolManager()
            response = http.request('GET', self.docker_api_url)
            return json.loads(response.data.decode('utf-8'))
        except Exception as exception:
            logger.error(exception)
            raise
