import json
import logging
import tempfile
from . import data_service as ds
from typing import Any, Dict
from datetime import datetime
import configs.settings as settings


class GPTGenerator:
    def __init__(self, client: Any):
        self.client = client
        self.gcs_manager = ds.GCSManager(settings.GCS_BUCKET)

    def format_response_to_dict(self, instructions: str, response: Any, session_id: str, data: str) -> None:
        try:
            performance_data = {
                "session_id": session_id,
                "id": response.id,
                "created_at": response.created,
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
            message_data = {
                "session_id": session_id,
                "id": response.id,
                "instructions": instructions,
                "data": data
            }

            logging.info(f"Performance Data: {performance_data}")

            self.upload_token_usage(performance_data, session_id)
            self.upload_message_data(message_data, session_id)

            logging.info("Data loaded successfully!")
        except Exception as e:
            logging.error(f"Failed to format response to dict: {e}")

    def upload_token_usage(self, performance_data: Dict[str, Any], session_id: str) -> None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                json_data = json.dumps(performance_data, indent=4)
                temp_file.write(json_data.encode())
                temp_file.flush()
                temp_file_path = temp_file.name
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination_blob_name = f"token_usage/session_{session_id}_{timestamp}.json"
            self.gcs_manager.upload_to_gcs(destination_blob_name, temp_file_path)
        except Exception as e:
            logging.error(f"Failed to write analytics data to temp file or upload to GCS: {e}")

    def upload_message_data(self, message_data: Dict[str, Any], session_id: str) -> None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                json_data = json.dumps(message_data, indent=4)
                temp_file.write(json_data.encode())
                temp_file.flush()
                temp_file_path = temp_file.name

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination_blob_name = f"message_data/session_{session_id}_{timestamp}.json"
            self.gcs_manager.upload_to_gcs(destination_blob_name, temp_file_path)
        except Exception as e:
            logging.error(f"Failed to write message data to temp file or upload to GCS: {e}")

    def generate_response(self, session_id: str, instructions: str, instructions_object: dict,  data: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": instructions},
                    {"role": "user", "content": f"Here's the data: {data}"},
                ]
            )
            result = response.choices[0].message.content
            result_json = json.loads(result)
            clean_result = result_json['data']
    
            self.format_response_to_dict(instructions=instructions_object, response=response, session_id=session_id, data=clean_result)

            return result
        except Exception as e:
            logging.error(f"Failed to generate response: {e}")
            return ""