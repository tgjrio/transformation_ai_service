import json
import uuid
import logging
from configs import settings
from pydantic import BaseModel
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from services.gpt_service import GPTGenerator


app = FastAPI()

# Mock data class for request payload
class DataRequest(BaseModel):
    data: List[Dict[str, Any]]
    instructions: Dict[str, List[Dict[str, Any]]]

# Initialize the GPTGenerator instance with the mocked client (replace with actual client)
gpt_generator = GPTGenerator(client=settings.OPENAI_CLIENT)

@app.post("/process-data/")
async def process_data(request: DataRequest):
    try:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        
        # Convert the incoming data to the expected format (if needed)
        data = {"data": request.data}
        print(f"instructions: {request.instructions}")

        # Step 1: Process Field Transformations
        field_transformations = request.instructions.get('field_transformations', [])
        field_transformations = field_transformations[0:]
        if field_transformations:
            instructions_json = json.dumps({"field_transformations": field_transformations}, indent=4)
            result = gpt_generator.generate_response(
                session_id=session_id,
                instructions_object=field_transformations,
                instructions=f"Make the updates to the data using the given instructions for field_transformations: {instructions_json}. Your response should only be in JSON format; do not wrap in ```json markdown.",
                data=data
            )
            try:
                # Parse the result and update the data for the next step
                result_dict = json.loads(result)  # Convert to dict if JSON response
                if "data" in result_dict:
                    data = {"data": result_dict["data"]}
                else:
                    raise HTTPException(status_code=500, detail="Invalid response format for field transformations.")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON response from AI during field transformations.")

        # Step 2: Process Create New Field Instructions
        field_creations = request.instructions.get('field_creations', [])
        field_creations = field_creations[0:]
        if field_creations:
            instructions_json = json.dumps({"field_creations": field_creations}, indent=4)
            result = gpt_generator.generate_response(
                session_id=session_id,
                instructions_object=field_creations,
                instructions=f"Make the updates to the data using the given instructions for field_creations: {instructions_json}. Your response should only be in JSON format; do not wrap in ```json markdown.",
                data=data
            )
            try:
                # Parse the result for final output
                result_dict = json.loads(result)  # Convert to dict if JSON response
                return {"session_id": session_id, "modified_data": result_dict}
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON response from AI during field creations.")

        # If no transformations or creations were provided, return the original data
        return {"session_id": session_id, "modified_data": data["data"]}

    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
