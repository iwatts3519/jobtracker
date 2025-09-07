import PyPDF2
import os
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVProcessor:
    def __init__(self, upload_folder: str = 'static/uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'pdf', 'txt', 'doc', 'docx'}
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file, user_id: int = 1) -> Optional[Tuple[str, str]]:
        """
        Save uploaded CV file and return filepath and extracted text
        
        Args:
            file: Uploaded file object
            user_id: User ID for organizing files
            
        Returns:
            Tuple of (filepath, extracted_text) or None if failed
        """
        if not file or file.filename == '':
            return None
            
        if not self.allowed_file(file.filename):
            logger.error(f"File type not allowed: {file.filename}")
            return None
        
        try:
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"cv_{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            filepath = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(filepath)
            logger.info(f"CV file saved: {filepath}")
            
            # Extract text based on file type
            extracted_text = self.extract_text_from_file(filepath)
            
            return filepath, extracted_text
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            return None
    
    def extract_text_from_file(self, filepath: str) -> str:
        """
        Extract text content from various file types
        
        Args:
            filepath: Path to the file
            
        Returns:
            Extracted text content
        """
        file_extension = filepath.rsplit('.', 1)[1].lower()
        
        try:
            if file_extension == 'pdf':
                return self._extract_from_pdf(filepath)
            elif file_extension == 'txt':
                return self._extract_from_txt(filepath)
            elif file_extension in ['doc', 'docx']:
                return self._extract_from_docx(filepath)
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                return "Unsupported file type"
                
        except Exception as e:
            logger.error(f"Text extraction failed for {filepath}: {e}")
            return f"Text extraction failed: {str(e)}"
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return f"PDF extraction failed: {str(e)}"
    
    def _extract_from_txt(self, filepath: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Text file extraction failed: {e}")
                return f"Text file extraction failed: {str(e)}"
        except Exception as e:
            logger.error(f"Text file extraction failed: {e}")
            return f"Text file extraction failed: {str(e)}"
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file (requires python-docx)"""
        try:
            from docx import Document
            
            doc = Document(filepath)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            return "DOCX support requires python-docx library. Please install with: pip install python-docx"
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return f"DOCX extraction failed: {str(e)}"
    
    def save_customized_cv(self, cv_text: str, job_id: int, user_id: int = 1) -> Optional[str]:
        """
        Save customized CV text to a file
        
        Args:
            cv_text: Customized CV content
            job_id: Job ID this CV is customized for
            user_id: User ID
            
        Returns:
            Filepath of saved customized CV or None if failed
        """
        try:
            filename = f"custom_cv_{user_id}_{job_id}_{uuid.uuid4().hex[:8]}.txt"
            filepath = os.path.join(self.upload_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(cv_text)
            
            logger.info(f"Customized CV saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save customized CV: {e}")
            return None
    
    def save_cover_letter(self, cover_letter: str, job_id: int, user_id: int = 1) -> Optional[str]:
        """
        Save cover letter to a file
        
        Args:
            cover_letter: Cover letter content
            job_id: Job ID this cover letter is for
            user_id: User ID
            
        Returns:
            Filepath of saved cover letter or None if failed
        """
        try:
            filename = f"cover_letter_{user_id}_{job_id}_{uuid.uuid4().hex[:8]}.txt"
            filepath = os.path.join(self.upload_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(cover_letter)
            
            logger.info(f"Cover letter saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save cover letter: {e}")
            return None
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file safely
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath) and filepath.startswith(self.upload_folder):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {filepath}: {e}")
            return False
    
    def list_uploaded_cvs(self, user_id: int = 1) -> list:
        """
        List all uploaded CV files for a user
        
        Args:
            user_id: User ID to filter CVs
            
        Returns:
            List of dictionaries with CV file information
        """
        try:
            cv_files = []
            if not os.path.exists(self.upload_folder):
                return cv_files
            
            for filename in os.listdir(self.upload_folder):
                if filename.startswith(f'cv_{user_id}_') and not filename.startswith('custom_cv_'):
                    filepath = os.path.join(self.upload_folder, filename)
                    if os.path.isfile(filepath):
                        # Get file modification time
                        mod_time = os.path.getmtime(filepath)
                        
                        # Extract original extension
                        file_extension = filename.split('.')[-1]
                        
                        cv_files.append({
                            'filename': filename,
                            'filepath': filepath,
                            'display_name': f"CV ({file_extension.upper()}) - {datetime.fromtimestamp(mod_time).strftime('%m/%d/%Y %H:%M')}",
                            'modified_time': mod_time,
                            'extension': file_extension
                        })
            
            # Sort by modification time (newest first)
            cv_files.sort(key=lambda x: x['modified_time'], reverse=True)
            return cv_files
            
        except Exception as e:
            logger.error(f"Failed to list CV files: {e}")
            return []
    
    def get_cv_text_by_filename(self, filename: str) -> Optional[str]:
        """
        Get the text content of a CV file by filename
        
        Args:
            filename: Name of the CV file
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            filepath = os.path.join(self.upload_folder, filename)
            if os.path.exists(filepath):
                return self.extract_text_from_file(filepath)
            else:
                logger.error(f"CV file not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Failed to get CV text from {filename}: {e}")
            return None

# Global CV processor instance
cv_processor = CVProcessor()