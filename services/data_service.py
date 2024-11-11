import logging
from google.cloud import storage

class GCSManager:
    """
    A class to manage uploads and downloads of files to and from Google Cloud Storage.
    This class provides methods to upload files to a specified bucket and retrieve files from the bucket.
    """

    def __init__(self, bucket_name: str):
        """
        Initialize the GCSManager with the necessary GCS configuration.
        Establish a connection to the GCS bucket.
        
        :param bucket_name: The name of the GCS bucket where files will be stored/retrieved.
        """
        self.bucket_name = bucket_name  # Store the bucket name as a string
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)  # Bucket object

    def upload_to_gcs(self, destination_blob_name: str, file_path: str):
        """
        Upload a file to GCS.

        :param destination_blob_name: The name of the blob (file) in the GCS bucket.
        :param file_path: The local path to the file that needs to be uploaded.
        """
        blob = self.bucket.blob(destination_blob_name)
        logging.info("Preparing file upload into GCS..")
        try:
            blob.upload_from_filename(file_path)
            logging.info(f"File {file_path} uploaded to {destination_blob_name}.")
        except Exception as e:
            logging.error(f"Failed to upload file {file_path} to {destination_blob_name}: {e}")