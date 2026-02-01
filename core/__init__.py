"""Core services package"""
from .notion_client import NotionWatchClient
from .openai_extractor import OpenAIExtractor
from .email_sender import EmailSender

__all__ = [
    'NotionWatchClient',
    'OpenAIExtractor',
    'EmailSender'
]
