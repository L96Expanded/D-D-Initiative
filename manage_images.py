import os
import shutil
import sys
import json
from pathlib import Path

def add_creature_image(image_path, creature_name=None):
    """Add a creature image to the local collection."""
    
    # Get the project directory
    project_dir = Path(__file__).parent
    database_images_dir = project_dir / "database_images"
    
    # Ensure database images directory exists
    database_images_dir.mkdir(exist_ok=True)
    
    # Get source image path
    source_path = Path(image_path)
    if not source_path.exists():
        print(f"❌ Error: Image file '{image_path}' not found")
        return False
    
    # Get creature name
    if not creature_name:
        creature_name = input("Enter creature name: ").strip()
    
    if not creature_name:
        print("❌ Error: Creature name is required")
        return False
    
    # Prepare filename
    clean_name = creature_name.lower().replace(' ', '_').replace('-', '_')
    file_extension = source_path.suffix.lower()
    
    # Validate file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if file_extension not in valid_extensions:
        print(f"❌ Error: Unsupported file format. Use: {', '.join(valid_extensions)}")
        return False
    
    destination_filename = f"{clean_name}{file_extension}"
    destination_path = database_images_dir / destination_filename
    
    # Check if file already exists
    if destination_path.exists():
        overwrite = input(f"File '{destination_filename}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled")
            return False
    
    # Copy the file
    try:
        shutil.copy2(source_path, destination_path)
        print(f"✅ Successfully added '{creature_name}' -> {destination_filename}")
        print(f"📁 Image saved to: {destination_path}")
        print(f"🔗 Will be available at: /local_images/{destination_filename}")
        return True
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False

def add_to_database(creature_name, image_url):
    """Add a creature mapping to the JSON database."""
    project_dir = Path(__file__).parent
    db_path = project_dir / "creature_database.json"
    
    try:
        # Load existing database
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {}
        
        # Add new entry
        creature_name_lower = creature_name.lower().strip()
        db[creature_name_lower] = image_url
        
        # Save database
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Added to database: '{creature_name_lower}' -> {image_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False

def list_creature_images():
    """List all creature images in the database collection and database."""
    
    project_dir = Path(__file__).parent
    database_images_dir = project_dir / "database_images"
    db_path = project_dir / "creature_database.json"
    
    print("🎨 D&D Creature Image Collection")
    print("=" * 50)
    
    # List database images
    if database_images_dir.exists():
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        
        for extension in image_extensions:
            image_files.extend(database_images_dir.glob(extension))
        
        if image_files:
            print(f"\n📁 Database Images ({len(image_files)} files):")
            for image_file in sorted(image_files):
                creature_name = image_file.stem.replace('_', ' ').title()
                file_size = image_file.stat().st_size / 1024  # KB
                print(f"  🐉 {creature_name}")
                print(f"     📄 File: {image_file.name} ({file_size:.1f} KB)")
                print(f"     🔗 URL: /database_images/{image_file.name}")
        else:
            print("\n📁 Local Images: None found")
    else:
        print("\n📁 Local Images: Directory doesn't exist")
    
    # List database entries
    if db_path.exists():
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            if db:
                print(f"\n📊 Database Entries ({len(db)} creatures):")
                for creature_name, image_url in sorted(db.items()):
                    print(f"  🎯 {creature_name.title()}")
                    print(f"     🔗 {image_url}")
            else:
                print("\n📊 Database Entries: Empty")
                
        except Exception as e:
            print(f"\n📊 Database Entries: Error reading - {e}")
    else:
        print("\n📊 Database Entries: File doesn't exist")

def test_api_connection():
    """Test connection to the local API."""
    import requests
    
    api_url = "http://127.0.0.1:8000/api/creature-images"
    
    try:
        # Test list endpoint
        response = requests.get(f"{api_url}/list_all_creatures", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection successful!")
            print(f"📊 Found {data.get('total', 0)} creatures in database")
            print(f"📁 {data.get('local_count', 0)} local images")
            print(f"📖 {data.get('database_count', 0)} database entries")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   cd backend && python -m uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main CLI interface."""
    
    if len(sys.argv) < 2:
        print("🐉 D&D Creature Image Manager (JSON-based)")
        print()
        print("Usage:")
        print("  python manage_images.py add <image_path> [creature_name]")
        print("  python manage_images.py add-db <creature_name> <image_url>")
        print("  python manage_images.py list")
        print("  python manage_images.py test")
        print()
        print("Examples:")
        print("  python manage_images.py add dragon.jpg \"Ancient Red Dragon\"")
        print("  python manage_images.py add orc_warrior.png")
        print("  python manage_images.py add-db \"Fire Dragon\" \"/local_images/fire_dragon.jpg\"")
        print("  python manage_images.py list")
        print("  python manage_images.py test")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ Error: Image path required")
            print("Usage: python manage_images.py add <image_path> [creature_name]")
            return
        
        image_path = sys.argv[2]
        creature_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        add_creature_image(image_path, creature_name)
        
    elif command == "add-db":
        if len(sys.argv) < 4:
            print("❌ Error: Creature name and image URL required")
            print("Usage: python manage_images.py add-db <creature_name> <image_url>")
            return
        
        creature_name = sys.argv[2]
        image_url = sys.argv[3]
        
        add_to_database(creature_name, image_url)
        
    elif command == "list":
        list_creature_images()
        
    elif command == "test":
        test_api_connection()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: add, add-db, list, test")

if __name__ == "__main__":
    main()