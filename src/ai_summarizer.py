"""
AI Summarizer using Google's Gemini API.

This module handles the integration with Gemini AI to generate
concise summaries of YouTube video transcripts.
"""

import logging
import time
from typing import Optional, Dict, Any

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

# Configuration constants
GEMINI_MODEL = 'gemini-1.5-flash-002'
MAX_SUMMARY_LENGTH = 300


class AISummarizer:
    """Handles AI-powered summarization using Gemini."""
    
    def __init__(self, api_key: str):
        """
        Initialize AI Summarizer with Gemini API.
        
        Args:
            api_key: Google AI Studio API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Safety settings to allow most content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        logger.info(f"AI Summarizer initialized with model: {GEMINI_MODEL}")
    
    def generate_summary(self, 
                        video_info: Dict[str, Any], 
                        transcript: str,
                        max_retries: int = 3) -> Optional[str]:
        """
        Generate a summary of the video transcript using AI.
        
        Args:
            video_info: Dictionary containing video metadata
            transcript: Full transcript text
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated summary or None if failed
        """
        if not transcript:
            logger.warning("No transcript provided for summarization")
            return None
        
        # Truncate transcript if too long (to stay within token limits)
        max_transcript_length = 50000  # Conservative limit
        if len(transcript) > max_transcript_length:
            logger.warning(f"Transcript too long ({len(transcript)} chars), truncating to {max_transcript_length}")
            transcript = transcript[:max_transcript_length] + "... [truncated]"
        
        # Prepare the prompt
        prompt = self._create_summary_prompt(video_info, transcript)
        
        # Try to generate summary with retries
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    safety_settings=self.safety_settings,
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 1024,
                    }
                )
                
                # Check if response was blocked
                if response.prompt_feedback.block_reason:
                    logger.warning(f"Prompt was blocked: {response.prompt_feedback.block_reason}")
                    return self._create_fallback_summary(video_info)
                
                # Extract summary text
                if response.text:
                    summary = response.text.strip()
                    logger.info(f"Successfully generated summary of {len(summary)} characters")
                    return summary
                else:
                    logger.warning("Empty response from Gemini")
                    
            except Exception as e:
                logger.error(f"Error generating summary (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
        
        # If all attempts failed, return fallback summary
        return self._create_fallback_summary(video_info)
    
    def _create_summary_prompt(self, video_info: Dict[str, Any], transcript: str) -> str:
        """
        Create the prompt for AI summarization.
        
        Args:
            video_info: Video metadata
            transcript: Video transcript
            
        Returns:
            Formatted prompt string
        """
        prompt_template = """
Please analyze the following YouTube video transcript and generate a concise summary:

Video Title: {title}
Video URL: {url}
Transcript: {transcript}

Requirements:
1. Extract 3-5 key points from the video
2. Summarize the main topic and conclusions
3. Keep the summary under {max_words} words
4. Use clear, bullet-point format
5. Focus on actionable insights and important information

Please provide the summary in the following format:
• Main Topic: [Brief description]
• Key Points:
  - [Point 1]
  - [Point 2]
  - [Point 3]
• Conclusion: [Brief conclusion or takeaway]
"""
        
        return prompt_template.format(
            title=video_info.get('title', 'Unknown'),
            url=video_info.get('url', ''),
            transcript=transcript,
            max_words=MAX_SUMMARY_LENGTH
        )
    
    def _create_fallback_summary(self, video_info: Dict[str, Any]) -> str:
        """
        Create a fallback summary when AI generation fails.
        
        Args:
            video_info: Video metadata
            
        Returns:
            Basic fallback summary
        """
        logger.info("Creating fallback summary")
        
        return f"""
• Main Topic: {video_info.get('title', 'Unknown')}
• Key Points:
  - Video published by {video_info.get('channel_title', 'Unknown Channel')}
  - Duration: {video_info.get('duration', 'Unknown')}
  - Unable to generate AI summary due to technical issues
• Note: Please watch the video directly for full content
"""
    
    def summarize_in_chunks(self, 
                           video_info: Dict[str, Any],
                           transcript: str,
                           chunk_size: int = 10000) -> Optional[str]:
        """
        Summarize long transcripts by processing in chunks.
        
        Args:
            video_info: Video metadata
            transcript: Full transcript text
            chunk_size: Size of each chunk in characters
            
        Returns:
            Combined summary or None
        """
        if len(transcript) <= chunk_size:
            # Short enough to process in one go
            return self.generate_summary(video_info, transcript)
        
        # Split transcript into chunks
        chunks = []
        for i in range(0, len(transcript), chunk_size):
            chunk = transcript[i:i + chunk_size]
            # Try to break at sentence boundary
            if i + chunk_size < len(transcript):
                last_period = chunk.rfind('. ')
                if last_period > chunk_size * 0.8:  # If period is in last 20%
                    chunk = chunk[:last_period + 1]
            chunks.append(chunk)
        
        logger.info(f"Processing transcript in {len(chunks)} chunks")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)}")
            
            chunk_prompt = f"""
Summarize this part {i + 1} of {len(chunks)} of the video transcript:

{chunk}

Provide a brief summary focusing on the main points discussed in this section.
"""
            
            try:
                response = self.model.generate_content(
                    chunk_prompt,
                    safety_settings=self.safety_settings
                )
                
                if response.text:
                    chunk_summaries.append(response.text.strip())
                    
            except Exception as e:
                logger.error(f"Error summarizing chunk {i + 1}: {e}")
        
        if not chunk_summaries:
            return self._create_fallback_summary(video_info)
        
        # Combine chunk summaries into final summary
        combined_summary_prompt = f"""
Based on these summaries of different parts of the video "{video_info.get('title', '')}":

{chr(10).join(f"Part {i+1}: {summary}" for i, summary in enumerate(chunk_summaries))}

Create a final, cohesive summary following this format:
• Main Topic: [Brief description]
• Key Points:
  - [Point 1]
  - [Point 2]
  - [Point 3]
• Conclusion: [Brief conclusion or takeaway]

Keep it under {max_words} words.
"""
        
        combined_summary_prompt = combined_summary_prompt.format(
            title=video_info.get('title', ''),
            max_words=MAX_SUMMARY_LENGTH
        )
        
        try:
            response = self.model.generate_content(
                combined_summary_prompt,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error creating final summary: {e}")
        
        # If final summary fails, join chunk summaries
        return "\n\n".join(chunk_summaries)
    
    def test_connection(self) -> bool:
        """
        Test connection to Gemini API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.model.generate_content(
                "Say 'API connection successful' in 5 words or less.",
                safety_settings=self.safety_settings
            )
            
            if response.text:
                logger.info(f"Gemini API test successful: {response.text.strip()}")
                return True
            else:
                logger.warning("Gemini API test returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"Gemini API test failed: {e}")
            return False


