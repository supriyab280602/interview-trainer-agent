import logging
import io
import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pypdf import PdfReader
from services.cloudant_service import CloudantService
from services.cos_service import COSService
from services.granite_service import GraniteService
from prompts.resume_prompt import RESUME_PROMPT
from models.resume import Resume

logger = logging.getLogger("ResumeService")

class ResumeService:
    """
    ResumeService handles PDF parsing, text cleaning, entity extraction using 
    IBM Granite reasoning, uploading files to COS, and saving metadata records in Cloudant.
    """
    
    def __init__(self, db_service: CloudantService, cos_service: COSService, granite_service: GraniteService) -> None:
        self.db = db_service
        self.cos = cos_service
        self.granite = granite_service

    def _extract_raw_text(self, file_bytes: bytes) -> str:
        """
        Extract text from raw PDF bytes using pypdf.
        """
        try:
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}", exc_info=True)
            raise ValueError("Corrupted or unreadable PDF document structure.") from e

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean up formatting from PDF text before feeding to the LLM.
        """
        # Replace duplicate spacing and keep ASCII chars primarily
        cleaned = re.sub(r'[ \t]+', ' ', text)
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
        return cleaned.strip()[:6000] # Cap text length to prevent context limit errors

    async def parse_and_save_resume(self, user_id: str, file_bytes: bytes, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Process the uploaded resume:
        1. Extract and clean text.
        2. Call Granite to parse structured details into JSON.
        3. Upload PDF to COS.
        4. Save metadata record to Cloudant.
        """
        try:
            logger.info(f"Starting resume process for user '{user_id}' with file '{file_name}'...")
            
            # 1. Extract text
            raw_text = self._extract_raw_text(file_bytes)
            cleaned_text = self._clean_extracted_text(raw_text)
            if not cleaned_text:
                raise ValueError("No text could be extracted from the uploaded PDF resume.")

            # 2. Extract entities using Granite
            prompt = RESUME_PROMPT.format(resume_text=cleaned_text)
            logger.info("Requesting Granite analysis of resume text...")
            granite_response = self.granite.generate(prompt)
            
            # Clean response JSON string in case the model added markdown blocks or commentary
            json_str = granite_response.strip()
            # If wrapped in markdown json block, extract it
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Fix common escape mistakes if any
            try:
                parsed_details = json.loads(json_str)
            except json.JSONDecodeError as je:
                logger.warning(f"Granite did not return a clean JSON string: {json_str}. Trying parsing regex fallback...")
                # Attempt regex search for first open brace
                match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if match:
                    try:
                        parsed_details = json.loads(match.group(0))
                    except Exception:
                        raise ValueError("Failed to parse Granite output as JSON.") from je
                else:
                    raise ValueError("Failed to parse Granite output as JSON.") from je

            # Generate unique Resume ID
            resume_id = f"resume_{uuid.uuid4().hex}"
            object_name = f"{user_id}/{resume_id}.pdf"
            
            # 3. Upload file to IBM COS
            # Reset file pointer
            file_stream = io.BytesIO(file_bytes)
            cos_url = self.cos.upload_file(file_stream, object_name)
            if not cos_url:
                logger.error("COS upload failed. Resorting to local metadata-only flow.")
                cos_url = f"local_storage://{object_name}"

            # 4. Save metadata record to Cloudant
            resume_meta = Resume(
                _id=resume_id,
                user_id=user_id,
                resume_name=file_name,
                cloud_storage_url=cos_url,
                candidate_name=parsed_details.get("candidate_name", "Unknown"),
                skills=parsed_details.get("skills", []),
                programming_languages=parsed_details.get("programming_languages", []),
                frameworks=parsed_details.get("frameworks", []),
                projects=parsed_details.get("projects", []),
                work_experience=parsed_details.get("work_experience", []),
                education=parsed_details.get("education", []),
                certifications=parsed_details.get("certifications", []),
                achievements=parsed_details.get("achievements", []),
                tools=parsed_details.get("tools", []),
                technologies=parsed_details.get("technologies", []),
                soft_skills=parsed_details.get("soft_skills", [])
            )

            # Store in Cloudant
            success = await self.db.create_document("resumes", resume_id, resume_meta.model_dump(by_alias=True))
            if success:
                logger.info(f"Resume metadata saved in Cloudant. ID: {resume_id}")
                return resume_meta.model_dump(by_alias=True)
            return None
        except Exception as e:
            logger.error(f"Error parsing and saving resume: {str(e)}", exc_info=True)
            return None

    async def get_resume_by_id(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch resume metadata from Cloudant.
        """
        try:
            return await self.db.get_document("resumes", resume_id)
        except Exception as e:
            logger.error(f"Error fetching resume: {str(e)}")
            return None

    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """
        Deletes the resume metadata from Cloudant and binary file from COS.
        """
        try:
            resume_doc = await self.get_resume_by_id(resume_id)
            if not resume_doc:
                return True
                
            # Security check
            if resume_doc["user_id"] != user_id:
                logger.warning(f"Delete permission denied: User '{user_id}' trying to delete resume of user '{resume_doc['user_id']}'.")
                return False

            # Delete file from COS
            object_name = f"{user_id}/{resume_id}.pdf"
            await self.db.delete_document("resumes", resume_id)
            self.cos.delete_file(object_name)
            
            logger.info(f"Deleted resume record: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting resume '{resume_id}': {str(e)}")
            return False
