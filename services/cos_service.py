import logging
from typing import BinaryIO, Optional
from storage import COSStorageService

logger = logging.getLogger("COSService")

class COSService(COSStorageService):
    """
    COSService is a wrapper around the core COSStorageService to maintain 
    consistency with the service-oriented architecture.
    """
    def __init__(self) -> None:
        super().__init__()
        logger.info("COS Service initialized.")
