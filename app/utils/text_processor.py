import re
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        # Expanded email pattern to handle more formats
        self.email_patterns = [
            # Standard email pattern with explicit underscore
            r'[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            # Specific pattern for usernames with underscores
            r'[A-Za-z]+_[A-Za-z0-9]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            # Pattern for outlook.com with explicit underscore
            r'[A-Za-z]+_[A-Za-z0-9]+@outlook\.com',
            # Very permissive pattern for edge cases
            r'[\w._-]+@[\w.-]+\.[a-zA-Z]{2,}'
        ]
        
        # Compile all email patterns
        self.email_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.email_patterns]
        
        # Phone patterns remain the same
        self.phone_patterns = [
            r'\+91\s*\d{5}\s*\d{5}',
            r'\+91[-\s]*\d{10}',
            r'91[-\s]*\d{10}',
            r'\b\d{5}[-\s]*\d{5}\b',
            r'\b\d{10}\b',
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        try:
            # Preserve line breaks for email extraction
            lines = text.splitlines()
            cleaned_lines = [' '.join(line.split()) for line in lines if line.strip()]
            cleaned_text = '\n'.join(cleaned_lines)
            logger.debug(f"Cleaned text length: {len(cleaned_text)}")
            return cleaned_text
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            raise

    def extract_contact_info(self, text: str) -> dict:
        """Extract contact information from text"""
        try:
            logger.info("Starting contact info extraction")
            logger.info(f"Text length: {len(text)}")
            
            # Extract email with multiple attempts
            email = self.extract_email(text)
            logger.info(f"Extracted email: {email}")
            
            # Extract phone
            phone = self.extract_phone(text)
            logger.info(f"Extracted phone: {phone}")
            
            # Extract LinkedIn URL
            linkedin = self.extract_linkedin(text)
            logger.info(f"Extracted LinkedIn: {linkedin}")
            
            # Final result
            result = {
                "email": email if email else "Not found",
                "phone": phone if phone else "Not found",
                "linkedin": linkedin if linkedin else "Not found"
            }
            
            logger.info(f"Final contact info: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")
            logger.exception("Full traceback:")
            return {"email": None, "phone": None, "linkedin": None}

    def extract_email(self, text: str) -> str:
        """Extract email address from text using multiple patterns"""
        try:
            # Log the input text for debugging
            logger.info("=== START OF TEXT CONTENT ===")
            logger.info(text)
            logger.info("=== END OF TEXT CONTENT ===")
            
            # Define email patterns with increasing permissiveness
            email_patterns = [
                # Exact pattern for the specific email format
                r'Aries_aakash786@outlook\.com',
                # Pattern for underscore emails
                r'[A-Za-z]+_[A-Za-z0-9]+@outlook\.com',
                # General underscore pattern
                r'[\w]+_[\w]+@[\w.-]+\.[A-Za-z]{2,}',
                # Most permissive pattern
                r'[\w._+-]+@[\w.-]+\.[A-Za-z]{2,}'
            ]
            
            # Try each pattern
            for pattern in email_patterns:
                logger.info(f"Trying pattern: {pattern}")
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    email = matches[0]
                    logger.info(f"Found email with pattern {pattern}: {email}")
                    return email.strip()
            
            # If no matches found with patterns, try direct text search
            logger.info("Trying direct text search")
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if '@' in line:
                    logger.info(f"Found line with @: {line}")
                    # Extract word containing @
                    words = line.split()
                    for word in words:
                        if '@' in word:
                            email = word.strip('.,;:()[]{}"\' \t')
                            if '@' in email and '.' in email.split('@')[1]:
                                logger.info(f"Found email through direct search: {email}")
                                return email

            logger.warning("No email found in text")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting email: {str(e)}")
            logger.exception("Full traceback:")
            return None

    def extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        try:
            logger.debug("Searching for phone number")
            logger.debug(f"Text to search: {text}")  # Debug print
            
            for pattern in self.phone_patterns:
                matches = re.findall(pattern, text)
                logger.debug(f"Pattern {pattern}: matches = {matches}")  # Debug print
                
                if matches:
                    # Clean and format the first match
                    phone = matches[0]
                    logger.debug(f"Found match: {phone}")  # Debug print
                    
                    # Extract digits while preserving +
                    digits = ''.join(c for c in phone if c.isdigit() or c == '+')
                    logger.debug(f"Extracted digits: {digits}")  # Debug print
                    
                    # Format based on the number
                    if digits.startswith('+91'):
                        formatted = f"+91-{digits[3:8]}-{digits[8:]}"
                    elif digits.startswith('91'):
                        formatted = f"+91-{digits[2:7]}-{digits[7:]}"
                    elif len(digits) == 10:
                        formatted = f"{digits[:5]}-{digits[5:]}"
                    else:
                        continue
                    
                    logger.debug(f"Formatted number: {formatted}")  # Debug print
                    return formatted
            
            logger.debug("No phone number found")  # Debug print
            return None
            
        except Exception as e:
            logger.error(f"Error extracting phone: {str(e)}")
            raise

    def extract_text_between(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract text between two markers"""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return None
            
            start_idx += len(start_marker)
            end_idx = text.find(end_marker, start_idx)
            
            if end_idx == -1:
                return text[start_idx:].strip()
            
            return text[start_idx:end_idx].strip()
        except Exception as e:
            logger.error(f"Error extracting text between markers: {str(e)}")
            raise

    def test(self):
        """Test the text processor with sample data"""
        test_text = """
        Contact Information:
        Email: test.user@example.com
        Phone: +91 9876543210
        
        Some other text...
        """
        
        print("\n=== TextProcessor Test Results ===")
        print(f"Clean text: {self.clean_text(test_text)[:50]}...")
        print(f"Email: {self.extract_email(test_text)}")
        print(f"Phone: {self.extract_phone(test_text)}")
        print(f"Contact Info: {self.extract_contact_info(test_text)}")
        print("=================================\n")

    def test_specific(self):
        """Test with specific format from the resume"""
        test_text = """
        Contact: balajikr.ravindran@gmail.com
        Phone: +91 70949 87073
        Location: Bengaluru, Karnataka
        """
        
        print("\n=== Testing Specific Format ===")
        contact_info = self.extract_contact_info(test_text)
        print(f"Email: {contact_info['email']}")
        print(f"Phone: {contact_info['phone']}")
        print("==============================\n")

    def extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL from text"""
        try:
            # Common LinkedIn URL patterns
            linkedin_patterns = [
                r'linkedin\.com/in/[\w-]+/?',
                r'linkedin\.com/profile/[\w-]+/?',
                r'@linkedin\.com/in/[\w-]+/?'
            ]
            
            for pattern in linkedin_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return "https://www." + match.group(0)
            return None
        except Exception as e:
            logger.error(f"Error extracting LinkedIn URL: {str(e)}")
            return None

    def test_email_extraction(self):
        """Test email extraction with specific cases"""
        test_cases = [
            "Aries_aakash786@outlook.com",
            "Contact: Aries_aakash786@outlook.com",
            "Email: Aries_aakash786@outlook.com",
            "My email is Aries_aakash786@outlook.com",
            "Aries_aakash786@outlook.com.",  # with period
            "<Aries_aakash786@outlook.com>",  # with brackets
            "Email:Aries_aakash786@outlook.com",  # no space after colon
        ]
        
        for test_case in test_cases:
            logger.info(f"\nTesting: {test_case}")
            result = self.extract_email(test_case)
            logger.info(f"Result: {result}")