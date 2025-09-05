"""
IPFS utility for document storage in the TrueCred application.
"""
import ipfshttpclient
import io
import hashlib
import json

class IPFSUtil:
    """
    Utility class for interacting with IPFS.
    """
    
    def __init__(self, ipfs_host='127.0.0.1', ipfs_port=5001):
        """
        Initialize the IPFS utility.
        
        Args:
            ipfs_host: IPFS daemon host
            ipfs_port: IPFS daemon port
        """
        self.client = None
        self.ipfs_host = ipfs_host
        self.ipfs_port = ipfs_port
    
    def connect(self):
        """
        Connect to the IPFS daemon.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            api_url = f'/ip4/{self.ipfs_host}/tcp/{self.ipfs_port}/http'
            self.client = ipfshttpclient.connect(api_url)
            return True
        except Exception as e:
            print(f"Error connecting to IPFS: {e}")
            return False
    
    def add_file(self, file_data, filename=None):
        """
        Add a file to IPFS.
        
        Args:
            file_data: File data (bytes or file-like object)
            filename: Name of the file (optional)
        
        Returns:
            IPFS hash of the added file
        """
        if not self.client:
            if not self.connect():
                raise Exception("Failed to connect to IPFS")
        
        try:
            # If file_data is bytes, wrap it in a BytesIO object
            if isinstance(file_data, bytes):
                file_data = io.BytesIO(file_data)
            
            # Add the file to IPFS
            result = self.client.add(file_data)
            return result['Hash']
        except Exception as e:
            print(f"Error adding file to IPFS: {e}")
            raise
    
    def add_json(self, json_data):
        """
        Add JSON data to IPFS.
        
        Args:
            json_data: Dictionary to store as JSON
        
        Returns:
            IPFS hash of the added JSON
        """
        if not self.client:
            if not self.connect():
                raise Exception("Failed to connect to IPFS")
        
        try:
            # Convert the JSON data to a string
            json_str = json.dumps(json_data)
            
            # Add the JSON data to IPFS
            result = self.client.add_json(json_data)
            return result
        except Exception as e:
            print(f"Error adding JSON to IPFS: {e}")
            raise
    
    def get_file(self, ipfs_hash):
        """
        Get a file from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the file to retrieve
        
        Returns:
            File data as bytes
        """
        if not self.client:
            if not self.connect():
                raise Exception("Failed to connect to IPFS")
        
        try:
            # Get the file from IPFS
            return self.client.cat(ipfs_hash)
        except Exception as e:
            print(f"Error getting file from IPFS: {e}")
            raise
    
    def get_json(self, ipfs_hash):
        """
        Get JSON data from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the JSON to retrieve
        
        Returns:
            JSON data as a dictionary
        """
        if not self.client:
            if not self.connect():
                raise Exception("Failed to connect to IPFS")
        
        try:
            # Get the JSON data from IPFS
            return self.client.get_json(ipfs_hash)
        except Exception as e:
            print(f"Error getting JSON from IPFS: {e}")
            raise
