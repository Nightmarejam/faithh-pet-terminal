#!/usr/bin/env python3
"""
Universal Conversation Parser for FAITHH
Handles ChatGPT, Grok, and Claude conversation exports

Usage:
    from conversation_parsers import parse_chatgpt, parse_grok, parse_claude
    
    parse_chatgpt("chatgpt_export.json", "output_dir/")
    parse_grok("grok_export.json", "output_dir/")
    parse_claude("claude_export.json", "output_dir/")
"""

import json
import sys
from pathlib import Path  
from datetime import datetime
from typing import Optional, List, Dict, Any


class ConversationParser:
    """Base parser class with common utilities"""
    
    @staticmethod
    def sanitize_filename(title: str) -> str:
        """Convert title to safe filename"""
        safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        return safe.strip()[:100] or "untitled"
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format Unix timestamp to readable string"""
        if timestamp > 0:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return 'Unknown'
    
    @staticmethod
    def write_conversation(output_file: Path, title: str, messages: List[Dict], source: str = ''):
        """Write formatted conversation to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Messages: {len(messages)}\n")
            if source:
                f.write(f"Source: {source}\n")
            f.write("=" * 80 + "\n\n")
            
            for msg in messages:
                role = msg.get('role', msg.get('sender', 'unknown')).upper()
                timestamp = ConversationParser.format_timestamp(msg['timestamp'])
                f.write(f"[{role}] ({timestamp})\n")
                f.write(msg['text'])
                f.write("\n\n" + "-" * 80 + "\n\n")


class ChatGPTParser(ConversationParser):
    """Parse ChatGPT conversation exports"""
    
    @staticmethod
    def extract_text_from_parts(parts):
        """Extract text from message parts"""
        if isinstance(parts, str):
            return parts
        
        text_parts = []
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict):
                    if 'text' in part:
                        text_parts.append(part['text'])
                    elif 'content' in part and isinstance(part['content'], str):
                        text_parts.append(part['content'])
                elif isinstance(part, str):
                    text_parts.append(part)
        elif isinstance(parts, dict):
            if 'text' in parts:
                text_parts.append(parts['text'])
            elif 'content' in parts and isinstance(parts['content'], str):
                text_parts.append(parts['content'])
        
        return '\n'.join(text_parts)
    
    def parse(self, input_file: Path, output_dir: Path) -> int:
        """Parse ChatGPT conversations"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = data if isinstance(data, list) else [data]
        print(f"📂 Found {len(conversations)} ChatGPT conversations")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir.absolute()}\n")
        
        success_count = 0
        for i, conv in enumerate(conversations, 1):
            if self._process_conversation(conv, output_dir, i):
                success_count += 1
        
        print(f"\n✅ Created {success_count} text files from ChatGPT")
        return success_count
    
    def _process_conversation(self, conv: Dict, output_dir: Path, index: int) -> Optional[Path]:
        """Process a single ChatGPT conversation"""
        try:
            title = conv.get('title', f'Conversation_{index}')
            mapping = conv.get('mapping', {})
            
            if not mapping:
                return None
            
            messages = []
            for node_id, node in mapping.items():
                message = node.get('message')
                if not message:
                    continue
                
                create_time = message.get('create_time', 0) or 0.0
                author_role = message.get('author', {}).get('role', 'unknown')
                
                content = message.get('content', {})
                parts = content.get('parts', []) if isinstance(content, dict) else content
                text = self.extract_text_from_parts(parts)
                
                if text and text.strip():
                    messages.append({
                        'timestamp': float(create_time),
                        'role': author_role,
                        'text': text.strip()
                    })
            
            if not messages:
                return None
            
            messages.sort(key=lambda x: x['timestamp'])
            
            safe_title = self.sanitize_filename(title)
            output_file = output_dir / f"{safe_title}.txt"
            
            counter = 1
            while output_file.exists():
                output_file = output_dir / f"{safe_title}_{counter}.txt"
                counter += 1
            
            self.write_conversation(output_file, title, messages, 'ChatGPT')
            return output_file
            
        except Exception as e:
            print(f"Error processing ChatGPT conversation {index}: {e}")
            return None


class GrokParser(ConversationParser):
    """Parse Grok conversation exports"""
    
    @staticmethod
    def parse_timestamp(ts) -> float:
        """Parse Grok's MongoDB-style timestamp"""
        if isinstance(ts, dict) and '$date' in ts:
            if isinstance(ts['$date'], dict) and '$numberLong' in ts['$date']:
                return int(ts['$date']['$numberLong']) / 1000
            elif isinstance(ts['$date'], str):
                return datetime.fromisoformat(ts['$date'].replace('Z', '+00:00')).timestamp()
        elif isinstance(ts, str):
            return datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
        return 0.0
    
    def parse(self, input_file: Path, output_dir: Path) -> int:
        """Parse Grok conversations"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = data.get('conversations', [])
        print(f"📂 Found {len(conversations)} Grok conversations")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir.absolute()}\n")
        
        success_count = 0
        for i, conv in enumerate(conversations, 1):
            if self._process_conversation(conv, output_dir, i):
                success_count += 1
        
        print(f"\n✅ Created {success_count} text files from Grok")
        return success_count
    
    def _process_conversation(self, conv_data: Dict, output_dir: Path, index: int) -> Optional[Path]:
        """Process a single Grok conversation"""
        try:
            conversation = conv_data.get('conversation', {})
            responses = conv_data.get('responses', [])
            
            if not responses:
                return None
            
            title = conversation.get('title', f'Grok_Conversation_{index}')
            
            messages = []
            for resp_item in responses:
                response = resp_item.get('response', {})
                message_text = response.get('message', '').strip()
                
                if not message_text:
                    continue
                
                sender = response.get('sender', 'unknown').lower()
                if sender == 'assistant':
                    sender = 'grok'
                
                timestamp = self.parse_timestamp(response.get('create_time', 0))
                
                messages.append({
                    'timestamp': timestamp,
                    'sender': sender,
                    'text': message_text
                })
            
            if not messages:
                return None
            
            messages.sort(key=lambda x: x['timestamp'])
            
            safe_title = self.sanitize_filename(title)
            output_file = output_dir / f"{safe_title}.txt"
            
            counter = 1
            while output_file.exists():
                output_file = output_dir / f"{safe_title}_{counter}.txt"
                counter += 1
            
            self.write_conversation(output_file, title, messages, 'Grok')
            return output_file
            
        except Exception as e:
            print(f"Error processing Grok conversation {index}: {e}")
            return None


class ClaudeParser(ConversationParser):
    """Parse Claude conversation exports"""
    
    def parse(self, input_file: Path, output_dir: Path) -> int:
        """Parse Claude conversations"""
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        print(f"📂 Found {len(conversations)} Claude conversations")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir.absolute()}\n")
        
        success_count = 0
        for i, conv in enumerate(conversations, 1):
            if self._process_conversation(conv, output_dir, i):
                success_count += 1
        
        print(f"\n✅ Created {success_count} text files from Claude")
        return success_count
    
    def _process_conversation(self, conv: Dict, output_dir: Path, index: int) -> Optional[Path]:
        """Process a single Claude conversation"""
        try:
            title = conv.get('name', f'Claude_Conversation_{index}')
            chat_messages = conv.get('chat_messages', [])
            
            if not chat_messages:
                return None
            
            messages = []
            for msg in chat_messages:
                text = msg.get('text', '').strip()
                if not text:
                    continue
                
                sender = msg.get('sender', 'unknown').lower()
                if sender == 'assistant':
                    sender = 'claude'
                
                created_at = msg.get('created_at', '')
                try:
                    timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                except:
                    timestamp = 0.0
                
                messages.append({
                    'timestamp': timestamp,
                    'sender': sender,
                    'text': text
                })
            
            if not messages:
                return None
            
            messages.sort(key=lambda x: x['timestamp'])
            
            safe_title = self.sanitize_filename(title)
            output_file = output_dir / f"{safe_title}.txt"
            
            counter = 1
            while output_file.exists():
                output_file = output_dir / f"{safe_title}_{counter}.txt"
                counter += 1
            
            self.write_conversation(output_file, title, messages, 'Claude')
            return output_file
            
        except Exception as e:
            print(f"Error processing Claude conversation {index}: {e}")
            return None


# ==================== CONVENIENCE FUNCTIONS ====================

def parse_chatgpt(input_file: str, output_dir: str) -> int:
    """Parse ChatGPT conversations
    
    Args:
        input_file: Path to conversations.json
        output_dir: Directory for output text files
        
    Returns:
        Number of conversations processed
    """
    return ChatGPTParser().parse(Path(input_file), Path(output_dir))


def parse_grok(input_file: str, output_dir: str) -> int:
    """Parse Grok conversations
    
    Args:
        input_file: Path to prod-grok-backend.json
        output_dir: Directory for output text files
        
    Returns:
        Number of conversations processed
    """
    return GrokParser().parse(Path(input_file), Path(output_dir))


def parse_claude(input_file: str, output_dir: str) -> int:
    """Parse Claude conversations
    
    Args:
        input_file: Path to conversations.json
        output_dir: Directory for output text files
        
    Returns:
        Number of conversations processed
    """
    return ClaudeParser().parse(Path(input_file), Path(output_dir))


# ==================== CLI INTERFACE ====================

def main():
    """CLI interface for parser"""
    if len(sys.argv) < 4:
        print("Usage: python conversation_parsers.py <parser> <input_json> <output_dir>")
        print("\nParsers: chatgpt, grok, claude")
        print("\nExamples:")
        print("  python conversation_parsers.py chatgpt conversations.json ./output")
        print("  python conversation_parsers.py grok prod-grok-backend.json ./output")
        print("  python conversation_parsers.py claude conversations.json ./output")
        sys.exit(1)
    
    parser_type = sys.argv[1].lower()
    input_file = sys.argv[2]
    output_dir = sys.argv[3]
    
    parsers = {
        'chatgpt': parse_chatgpt,
        'grok': parse_grok,
        'claude': parse_claude
    }
    
    if parser_type not in parsers:
        print(f"Unknown parser: {parser_type}")
        print(f"Available parsers: {', '.join(parsers.keys())}")
        sys.exit(1)
    
    count = parsers[parser_type](input_file, output_dir)
    
    print(f"\n\nNext steps:")
    print(f"  cd ~/ai-stack")
    print(f"  ./batch_embed.sh {Path(output_dir).absolute()}")


if __name__ == "__main__":
    main()
