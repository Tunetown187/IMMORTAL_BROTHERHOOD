import os
import json
import shutil
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import browser_cookie3
import json
import base64
from cryptography.fernet import Fernet

class ResourceManager:
    def __init__(self):
        self.setup_logging()
        self.desktop_path = str(Path.home() / "Desktop")
        self.downloads_path = str(Path.home() / "Downloads")
        self.resource_cache = {}
        self.browser_profiles = {}
        
        # Create encryption key for sensitive data
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
        # Initialize resource database
        self.init_database()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        """Initialize SQLite database for resource tracking"""
        try:
            with sqlite3.connect('resources.db') as conn:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS resources (
                        id TEXT PRIMARY KEY,
                        type TEXT,
                        path TEXT,
                        metadata TEXT,
                        last_accessed TIMESTAMP,
                        is_encrypted INTEGER
                    )
                ''')
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")

    async def scan_local_resources(self):
        """Scan desktop and downloads for useful resources"""
        try:
            # Scan desktop
            desktop_resources = self._scan_directory(self.desktop_path)
            self._cache_resources("desktop", desktop_resources)
            
            # Scan downloads
            downloads_resources = self._scan_directory(self.downloads_path)
            self._cache_resources("downloads", downloads_resources)
            
            return {
                "desktop": desktop_resources,
                "downloads": downloads_resources
            }
        except Exception as e:
            self.logger.error(f"Error scanning local resources: {str(e)}")
            return {}

    def _scan_directory(self, directory: str) -> Dict:
        """Scan a directory for useful files"""
        resources = {
            "executables": [],
            "documents": [],
            "images": [],
            "code": [],
            "data": [],
            "other": []
        }
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    # Categorize file
                    if ext in ['.exe', '.msi', '.bat']:
                        resources["executables"].append(file_path)
                    elif ext in ['.pdf', '.doc', '.docx', '.txt']:
                        resources["documents"].append(file_path)
                    elif ext in ['.jpg', '.png', '.gif', '.bmp']:
                        resources["images"].append(file_path)
                    elif ext in ['.py', '.js', '.html', '.css', '.java']:
                        resources["code"].append(file_path)
                    elif ext in ['.csv', '.json', '.xml', '.db']:
                        resources["data"].append(file_path)
                    else:
                        resources["other"].append(file_path)
                        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {str(e)}")
            
        return resources

    def _cache_resources(self, location: str, resources: Dict):
        """Cache scanned resources"""
        try:
            # Encrypt sensitive data before caching
            encrypted_resources = self._encrypt_sensitive_data(resources)
            
            # Store in database
            with sqlite3.connect('resources.db') as conn:
                c = conn.cursor()
                for resource_type, paths in encrypted_resources.items():
                    for path in paths:
                        c.execute('''
                            INSERT OR REPLACE INTO resources
                            (id, type, path, metadata, last_accessed, is_encrypted)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                        ''', (
                            f"{location}_{resource_type}_{os.path.basename(path)}",
                            resource_type,
                            path,
                            json.dumps({"location": location}),
                            1 if self._is_sensitive(path) else 0
                        ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error caching resources: {str(e)}")

    def _encrypt_sensitive_data(self, data: Dict) -> Dict:
        """Encrypt sensitive data before storing"""
        encrypted_data = {}
        for key, values in data.items():
            encrypted_values = []
            for value in values:
                if self._is_sensitive(value):
                    encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
                    encrypted_values.append(encrypted_value)
                else:
                    encrypted_values.append(value)
            encrypted_data[key] = encrypted_values
        return encrypted_data

    def _is_sensitive(self, path: str) -> bool:
        """Check if file contains sensitive data"""
        sensitive_keywords = ['password', 'secret', 'key', 'credential', 'token']
        return any(keyword in path.lower() for keyword in sensitive_keywords)

    async def scan_browser_profiles(self):
        """Scan browser profiles for bookmarks and cookies"""
        try:
            # Chrome bookmarks
            chrome_bookmarks = self._get_chrome_bookmarks()
            self.browser_profiles["chrome"] = {
                "bookmarks": chrome_bookmarks,
                "cookies": self._get_chrome_cookies()
            }
            
            # Firefox bookmarks
            firefox_bookmarks = self._get_firefox_bookmarks()
            self.browser_profiles["firefox"] = {
                "bookmarks": firefox_bookmarks,
                "cookies": self._get_firefox_cookies()
            }
            
            # Edge bookmarks
            edge_bookmarks = self._get_edge_bookmarks()
            self.browser_profiles["edge"] = {
                "bookmarks": edge_bookmarks,
                "cookies": self._get_edge_cookies()
            }
            
            return self.browser_profiles
            
        except Exception as e:
            self.logger.error(f"Error scanning browser profiles: {str(e)}")
            return {}

    def _get_chrome_bookmarks(self) -> List[Dict]:
        """Get Chrome bookmarks"""
        bookmarks_path = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks')
        try:
            if os.path.exists(bookmarks_path):
                with open(bookmarks_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._parse_chrome_bookmarks(data['roots'])
        except Exception as e:
            self.logger.error(f"Error getting Chrome bookmarks: {str(e)}")
        return []

    def _parse_chrome_bookmarks(self, node: Dict) -> List[Dict]:
        """Parse Chrome bookmarks JSON"""
        bookmarks = []
        
        if isinstance(node, dict):
            if node.get('type') == 'url':
                bookmarks.append({
                    'title': node.get('name', ''),
                    'url': node.get('url', ''),
                    'date_added': node.get('date_added', '')
                })
            for child in node.values():
                if isinstance(child, dict):
                    bookmarks.extend(self._parse_chrome_bookmarks(child))
                
        return bookmarks

    def _get_chrome_cookies(self) -> List[Dict]:
        """Get Chrome cookies"""
        try:
            cookies = browser_cookie3.chrome()
            return [{'domain': c.domain, 'name': c.name} for c in cookies]
        except Exception as e:
            self.logger.error(f"Error getting Chrome cookies: {str(e)}")
            return []

    def _get_firefox_bookmarks(self) -> List[Dict]:
        """Get Firefox bookmarks"""
        # Implementation depends on Firefox profile location
        return []

    def _get_firefox_cookies(self) -> List[Dict]:
        """Get Firefox cookies"""
        try:
            cookies = browser_cookie3.firefox()
            return [{'domain': c.domain, 'name': c.name} for c in cookies]
        except Exception as e:
            self.logger.error(f"Error getting Firefox cookies: {str(e)}")
            return []

    def _get_edge_bookmarks(self) -> List[Dict]:
        """Get Edge bookmarks"""
        # Implementation depends on Edge profile location
        return []

    def _get_edge_cookies(self) -> List[Dict]:
        """Get Edge cookies"""
        try:
            cookies = browser_cookie3.edge()
            return [{'domain': c.domain, 'name': c.name} for c in cookies]
        except Exception as e:
            self.logger.error(f"Error getting Edge cookies: {str(e)}")
            return []

    async def get_resource(self, resource_id: str) -> Optional[str]:
        """Get a resource by ID"""
        try:
            with sqlite3.connect('resources.db') as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM resources WHERE id = ?', (resource_id,))
                resource = c.fetchone()
                
                if resource:
                    path = resource[2]  # path is the third column
                    if resource[5]:  # is_encrypted
                        path = self.cipher_suite.decrypt(path.encode()).decode()
                    return path
                    
        except Exception as e:
            self.logger.error(f"Error getting resource: {str(e)}")
            
        return None

    async def prepare_for_deployment(self):
        """Prepare resources for GitHub deployment"""
        try:
            # Create deployment directory
            deploy_dir = "deployment_resources"
            os.makedirs(deploy_dir, exist_ok=True)
            
            # Export resource database
            with sqlite3.connect('resources.db') as conn:
                with open(os.path.join(deploy_dir, 'resources.sql'), 'w') as f:
                    for line in conn.iterdump():
                        f.write(f'{line}\n')
            
            # Export browser profiles (bookmarks only)
            with open(os.path.join(deploy_dir, 'browser_profiles.json'), 'w') as f:
                sanitized_profiles = {
                    browser: {
                        'bookmarks': data['bookmarks']
                    } for browser, data in self.browser_profiles.items()
                }
                json.dump(sanitized_profiles, f)
            
            # Create resource manifest
            manifest = {
                "version": "1.0",
                "resources": {
                    "database": "resources.sql",
                    "browser_profiles": "browser_profiles.json",
                    "encryption_key": base64.b64encode(self.key).decode()
                }
            }
            
            with open(os.path.join(deploy_dir, 'manifest.json'), 'w') as f:
                json.dump(manifest, f)
                
            return deploy_dir
            
        except Exception as e:
            self.logger.error(f"Error preparing for deployment: {str(e)}")
            return None

    async def load_from_deployment(self, deploy_dir: str):
        """Load resources from deployment directory"""
        try:
            # Load manifest
            with open(os.path.join(deploy_dir, 'manifest.json'), 'r') as f:
                manifest = json.load(f)
            
            # Set encryption key
            self.key = base64.b64decode(manifest['resources']['encryption_key'])
            self.cipher_suite = Fernet(self.key)
            
            # Import resource database
            with sqlite3.connect('resources.db') as conn:
                with open(os.path.join(deploy_dir, manifest['resources']['database']), 'r') as f:
                    conn.executescript(f.read())
            
            # Import browser profiles
            with open(os.path.join(deploy_dir, manifest['resources']['browser_profiles']), 'r') as f:
                self.browser_profiles = json.load(f)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading from deployment: {str(e)}")
            return False
