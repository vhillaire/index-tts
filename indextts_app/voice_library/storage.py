"""
Voice profile storage and library management

Manages voice profiles with metadata for voice cloning
"""

import json
import sqlite3
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib


@dataclass
class VoiceProfile:
    """Represents a stored voice profile"""
    id: str
    name: str
    audio_path: str
    created_at: str
    description: str = ""
    source_file: str = ""  # Original source (mp4, mp3, etc.)
    duration: float = 0.0  # Duration in seconds
    sample_rate: int = 24000
    language: str = "auto"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['tags'] = json.dumps(self.tags)
        data['metadata'] = json.dumps(self.metadata)
        return data


class VoiceLibrary:
    """SQLite-based voice library storage"""
    
    def __init__(self, db_path: Path):
        """
        Initialize voice library database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS voices (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                audio_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                description TEXT,
                source_file TEXT,
                duration REAL,
                sample_rate INTEGER DEFAULT 24000,
                language TEXT DEFAULT 'auto',
                tags TEXT,
                metadata TEXT
            )
            """)
            conn.commit()
    
    def add_voice(self, profile: VoiceProfile) -> bool:
        """Add a voice profile to library"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                data = profile.to_dict()
                conn.execute("""
                INSERT INTO voices 
                (id, name, audio_path, created_at, description, source_file, 
                 duration, sample_rate, language, tags, metadata)
                VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['name'], data['audio_path'],
                    data['created_at'], data['description'], data['source_file'],
                    data['duration'], data['sample_rate'], data['language'],
                    data['tags'], data['metadata']
                ))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_voice(self, voice_id: str) -> Optional[VoiceProfile]:
        """Retrieve a voice profile by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM voices WHERE id = ?",
                (voice_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_profile(row)
        return None
    
    def get_voice_by_name(self, name: str) -> Optional[VoiceProfile]:
        """Retrieve a voice profile by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM voices WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_profile(row)
        return None
    
    def list_voices(self) -> List[VoiceProfile]:
        """List all voices in library"""
        voices = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM voices ORDER BY created_at DESC")
            for row in cursor:
                voices.append(self._row_to_profile(row))
        return voices
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM voices WHERE id = ?", (voice_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_voice(self, profile: VoiceProfile) -> bool:
        """Update a voice profile"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                data = profile.to_dict()
                conn.execute("""
                UPDATE voices 
                SET name = ?, description = ?, tags = ?, metadata = ?, language = ?
                WHERE id = ?
                """, (
                    data['name'], data['description'], data['tags'],
                    data['metadata'], data['language'], data['id']
                ))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def _row_to_profile(row: tuple) -> VoiceProfile:
        """Convert database row to VoiceProfile"""
        return VoiceProfile(
            id=row[0],
            name=row[1],
            audio_path=row[2],
            created_at=row[3],
            description=row[4] or "",
            source_file=row[5] or "",
            duration=row[6] or 0.0,
            sample_rate=row[7] or 24000,
            language=row[8] or "auto",
            tags=json.loads(row[9]) if row[9] else [],
            metadata=json.loads(row[10]) if row[10] else {}
        )


class VoiceLibraryManager:
    """High-level voice library management"""
    
    def __init__(self, voice_dir: Path, db_path: Optional[Path] = None):
        """
        Initialize voice library manager
        
        Args:
            voice_dir: Directory to store voice audio files
            db_path: Path to SQLite database (defaults to voice_dir/voices.db)
        """
        self.voice_dir = Path(voice_dir)
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        
        if db_path is None:
            db_path = self.voice_dir / "voices.db"
        
        self.library = VoiceLibrary(db_path)
    
    def create_voice_id(self, name: str) -> str:
        """Generate unique voice ID from name"""
        timestamp = datetime.now().isoformat()
        data = f"{name}:{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:12]
    
    def add_voice_from_file(
        self,
        name: str,
        audio_path: Path,
        source_file: str = "",
        description: str = "",
        language: str = "auto",
        tags: Optional[List[str]] = None,
        **metadata
    ) -> Optional[VoiceProfile]:
        """
        Add a voice from an audio file
        
        Args:
            name: Display name for the voice
            audio_path: Path to audio file
            source_file: Original source file path
            description: Voice description
            language: Language of the voice
            tags: List of tags
            **metadata: Additional metadata
            
        Returns:
            VoiceProfile if successful, None otherwise
        """
        if not Path(audio_path).exists():
            return None
        
        voice_id = self.create_voice_id(name)
        
        # Copy audio file to voice directory
        dest_path = self.voice_dir / f"{voice_id}.wav"
        # In a real implementation, we'd copy and convert if needed
        # For now, store the path
        
        profile = VoiceProfile(
            id=voice_id,
            name=name,
            audio_path=str(audio_path),
            created_at=datetime.now().isoformat(),
            description=description,
            source_file=source_file,
            language=language,
            tags=tags or [],
            metadata=metadata
        )
        
        if self.library.add_voice(profile):
            return profile
        return None
    
    def get_voice(self, voice_id: str) -> Optional[VoiceProfile]:
        """Get voice by ID"""
        return self.library.get_voice(voice_id)
    
    def get_voice_by_name(self, name: str) -> Optional[VoiceProfile]:
        """Get voice by name"""
        return self.library.get_voice_by_name(name)
    
    def list_voices(self) -> List[VoiceProfile]:
        """List all voices"""
        return self.library.list_voices()
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice"""
        return self.library.delete_voice(voice_id)
    
    def update_voice(self, profile: VoiceProfile) -> bool:
        """Update a voice"""
        return self.library.update_voice(profile)
