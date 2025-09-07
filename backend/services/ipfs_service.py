"""
IPFS service for the TrueCred application.

This service provides functionality to interact with IPFS (InterPlanetary File System)
for decentralized document storage and retrieval.
"""
import os
import io
import json
import logging
import base64
import ipfshttpclient
from datetime import datetime
from urllib.parse import urlparse
import requests
from typing import Union, Dict, Any, Optional, BinaryIO

# Set up logging
logger = logging.getLogger(__name__)

class IPFSService:
    """
    Service for interacting with IPFS for decentralized document storage.
    
    This service provides:
    - IPFS node connection management
    - Document storage and retrieval
    - Content addressing for documents
    - Metadata handling for stored documents
    """
    
    def __init__(self, api_url=None, gateway_url=None):
        """
        Initialize the IPFS service.
        
        Args:
            api_url (str, optional): URL of the IPFS API endpoint
            gateway_url (str, optional): URL of the IPFS HTTP gateway
        """
        # Load configuration
        self.api_url = api_url or os.getenv('IPFS_API_URL', 'http://localhost:5001')
        self.gateway_url = gateway_url or os.getenv('IPFS_GATEWAY_URL', 'http://localhost:8080')
        
        # Parse URLs to ensure they're properly formatted
        api_parsed = urlparse(self.api_url)
        if not api_parsed.scheme or not api_parsed.netloc:
            logger.warning(f"Invalid IPFS API URL: {self.api_url}. Using default.")
            self.api_url = 'http://localhost:5001'
        
        gateway_parsed = urlparse(self.gateway_url)
        if not gateway_parsed.scheme or not gateway_parsed.netloc:
            logger.warning(f"Invalid IPFS Gateway URL: {self.gateway_url}. Using default.")
            self.gateway_url = 'http://localhost:8080'
        
        # Remove trailing slashes
        self.api_url = self.api_url.rstrip('/')
        self.gateway_url = self.gateway_url.rstrip('/')
        
        # Initialize client to None, will connect on demand
        self.client = None
        logger.info(f"IPFS service initialized with API: {self.api_url}, Gateway: {self.gateway_url}")
    
    def connect(self) -> bool:
        """
        Connect to the IPFS node.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        if self.client:
            # Already connected
            return True
        
        try:
            # Connect to IPFS node
            self.client = ipfshttpclient.connect(self.api_url)
            logger.info(f"Connected to IPFS node at {self.api_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IPFS node: {str(e)}")
            self.client = None
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the IPFS node.
        """
        if self.client:
            try:
                self.client.close()
                logger.info("Disconnected from IPFS node")
            except Exception as e:
                logger.error(f"Error disconnecting from IPFS node: {str(e)}")
            finally:
                self.client = None
    
    def add_file(self, file_data: Union[bytes, BinaryIO, str], filename: str = None) -> Dict[str, Any]:
        """
        Add a file to IPFS.
        
        Args:
            file_data: File data as bytes, file object, or path to file
            filename: Name of the file (optional)
            
        Returns:
            dict: IPFS response with hash and other metadata
        """
        if not self.connect():
            logger.error("Cannot add file: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Handle different input types
            if isinstance(file_data, str) and os.path.isfile(file_data):
                # It's a file path
                ipfs_response = self.client.add(file_data)
            elif isinstance(file_data, bytes):
                # It's binary data
                with io.BytesIO(file_data) as file_obj:
                    ipfs_response = self.client.add(file_obj)
            elif hasattr(file_data, 'read'):
                # It's a file-like object
                ipfs_response = self.client.add(file_data)
            else:
                raise ValueError("Invalid file_data type. Expected bytes, file object, or file path.")
            
            # Add filename to response if provided
            if filename:
                ipfs_response['Name'] = filename
            
            logger.info(f"File added to IPFS with hash: {ipfs_response['Hash']}")
            return ipfs_response
        except Exception as e:
            logger.error(f"Error adding file to IPFS: {str(e)}")
            return {"error": str(e)}
    
    def add_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add JSON data to IPFS.
        
        Args:
            json_data: JSON serializable data
            
        Returns:
            dict: IPFS response with hash and other metadata
        """
        if not self.connect():
            logger.error("Cannot add JSON: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Convert JSON to string and then to bytes
            json_bytes = json.dumps(json_data, sort_keys=True, indent=2).encode('utf-8')
            
            # Add to IPFS
            ipfs_response = self.client.add_bytes(json_bytes)
            
            logger.info(f"JSON data added to IPFS with hash: {ipfs_response}")
            return {"Hash": ipfs_response, "Size": len(json_bytes), "Name": "data.json"}
        except Exception as e:
            logger.error(f"Error adding JSON to IPFS: {str(e)}")
            return {"error": str(e)}
    
    def get_file(self, ipfs_hash: str) -> bytes:
        """
        Get a file from IPFS by its hash.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            bytes: File data
        """
        if not self.connect():
            logger.error("Cannot get file: not connected to IPFS")
            return b''
        
        try:
            # Get file from IPFS
            file_data = self.client.cat(ipfs_hash)
            logger.info(f"Retrieved file from IPFS with hash: {ipfs_hash}")
            return file_data
        except Exception as e:
            logger.error(f"Error getting file from IPFS: {str(e)}")
            return b''
    
    def get_json(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Get JSON data from IPFS by its hash.
        
        Args:
            ipfs_hash: IPFS hash of the JSON data
            
        Returns:
            dict: Parsed JSON data
        """
        if not self.connect():
            logger.error("Cannot get JSON: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Get file from IPFS
            file_data = self.client.cat(ipfs_hash)
            
            # Parse JSON
            json_data = json.loads(file_data.decode('utf-8'))
            
            logger.info(f"Retrieved JSON from IPFS with hash: {ipfs_hash}")
            return json_data
        except json.JSONDecodeError:
            logger.error(f"Error parsing JSON from IPFS hash: {ipfs_hash}")
            return {"error": "Invalid JSON data"}
        except Exception as e:
            logger.error(f"Error getting JSON from IPFS: {str(e)}")
            return {"error": str(e)}
    
    def get_gateway_url(self, ipfs_hash: str) -> str:
        """
        Get the HTTP gateway URL for an IPFS hash.
        
        Args:
            ipfs_hash: IPFS hash
            
        Returns:
            str: HTTP URL to access the content
        """
        return f"{self.gateway_url}/ipfs/{ipfs_hash}"
    
    def pin_hash(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Pin a hash to keep it in the IPFS node storage.
        
        Args:
            ipfs_hash: IPFS hash to pin
            
        Returns:
            dict: IPFS response
        """
        if not self.connect():
            logger.error("Cannot pin hash: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Pin the hash
            pins = self.client.pin.add(ipfs_hash)
            logger.info(f"Pinned IPFS hash: {ipfs_hash}")
            return {"pinned": pins}
        except Exception as e:
            logger.error(f"Error pinning IPFS hash: {str(e)}")
            return {"error": str(e)}
    
    def unpin_hash(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Unpin a hash allowing it to be garbage collected.
        
        Args:
            ipfs_hash: IPFS hash to unpin
            
        Returns:
            dict: IPFS response
        """
        if not self.connect():
            logger.error("Cannot unpin hash: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Unpin the hash
            pins = self.client.pin.rm(ipfs_hash)
            logger.info(f"Unpinned IPFS hash: {ipfs_hash}")
            return {"unpinned": pins}
        except Exception as e:
            logger.error(f"Error unpinning IPFS hash: {str(e)}")
            return {"error": str(e)}
    
    def get_node_info(self) -> Dict[str, Any]:
        """
        Get information about the connected IPFS node.
        
        Returns:
            dict: Node information
        """
        if not self.connect():
            logger.error("Cannot get node info: not connected to IPFS")
            return {"error": "Not connected to IPFS"}
        
        try:
            # Get node ID info
            id_info = self.client.id()
            logger.info(f"Retrieved IPFS node info: {id_info['ID']}")
            return id_info
        except Exception as e:
            logger.error(f"Error getting IPFS node info: {str(e)}")
            return {"error": str(e)}
    
    def fallback_gateway_fetch(self, ipfs_hash: str) -> bytes:
        """
        Fallback method to fetch IPFS content via HTTP gateway when direct connection fails.
        
        Args:
            ipfs_hash: IPFS hash to fetch
            
        Returns:
            bytes: Content data
        """
        try:
            # Build gateway URL
            url = self.get_gateway_url(ipfs_hash)
            
            # Fetch content from gateway
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Retrieved file from IPFS gateway: {ipfs_hash}")
            return response.content
        except Exception as e:
            logger.error(f"Error fetching from IPFS gateway: {str(e)}")
            return b''
    
    def store_document(self, document_data: bytes, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Store a document in IPFS with metadata.
        
        Args:
            document_data: Document binary data
            metadata: Additional metadata about the document
            
        Returns:
            dict: Storage information including IPFS hash
        """
        if not metadata:
            metadata = {}
        
        # Add timestamp to metadata
        metadata['timestamp'] = datetime.utcnow().isoformat()
        
        try:
            # Add document to IPFS
            doc_response = self.add_file(document_data, metadata.get('filename', 'document'))
            
            if 'error' in doc_response:
                return doc_response
            
            # Add document hash to metadata
            metadata['document_hash'] = doc_response['Hash']
            metadata['document_size'] = doc_response['Size']
            
            # Add metadata to IPFS
            meta_response = self.add_json(metadata)
            
            if 'error' in meta_response:
                return {
                    'document_hash': doc_response['Hash'],
                    'metadata_error': meta_response['error'],
                    'document_gateway_url': self.get_gateway_url(doc_response['Hash']),
                }
            
            # Return combined response
            result = {
                'document_hash': doc_response['Hash'],
                'metadata_hash': meta_response['Hash'],
                'document_size': doc_response['Size'],
                'document_gateway_url': self.get_gateway_url(doc_response['Hash']),
                'metadata_gateway_url': self.get_gateway_url(meta_response['Hash']),
                'timestamp': metadata['timestamp']
            }
            
            # Pin both hashes for persistence
            self.pin_hash(doc_response['Hash'])
            self.pin_hash(meta_response['Hash'])
            
            logger.info(f"Document stored in IPFS: {result['document_hash']}, metadata: {result['metadata_hash']}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing document in IPFS: {str(e)}")
            return {"error": str(e)}
    
    def retrieve_document(self, document_hash: str, metadata_hash: str = None) -> Dict[str, Any]:
        """
        Retrieve a document and its metadata from IPFS.
        
        Args:
            document_hash: IPFS hash of the document
            metadata_hash: IPFS hash of the metadata (optional)
            
        Returns:
            dict: Document data and metadata
        """
        try:
            # Get document from IPFS
            document_data = self.get_file(document_hash)
            
            if not document_data:
                # Try fallback method
                document_data = self.fallback_gateway_fetch(document_hash)
                
                if not document_data:
                    return {"error": f"Could not retrieve document with hash: {document_hash}"}
            
            result = {
                'document_hash': document_hash,
                'document_data': base64.b64encode(document_data).decode('utf-8'),
                'document_size': len(document_data),
                'document_gateway_url': self.get_gateway_url(document_hash)
            }
            
            # Get metadata if provided
            if metadata_hash:
                metadata = self.get_json(metadata_hash)
                
                if 'error' not in metadata:
                    result['metadata'] = metadata
                    result['metadata_hash'] = metadata_hash
                    result['metadata_gateway_url'] = self.get_gateway_url(metadata_hash)
                else:
                    result['metadata_error'] = metadata['error']
            
            logger.info(f"Document retrieved from IPFS: {document_hash}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving document from IPFS: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def is_valid_ipfs_hash(ipfs_hash: str) -> bool:
        """
        Check if a string is a valid IPFS hash.
        
        Args:
            ipfs_hash: String to check
            
        Returns:
            bool: True if valid IPFS hash format, False otherwise
        """
        # Basic validation for IPFS hashes
        # Most IPFS hashes are multihash format, start with "Qm" and are 46 characters long
        if not ipfs_hash or not isinstance(ipfs_hash, str):
            return False
        
        # Check for CIDv0 (most common, starts with "Qm")
        if ipfs_hash.startswith('Qm') and len(ipfs_hash) == 46:
            return all(c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' for c in ipfs_hash)
        
        # Check for CIDv1
        if len(ipfs_hash) >= 48 and all(c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' for c in ipfs_hash):
            return True
        
        return False
