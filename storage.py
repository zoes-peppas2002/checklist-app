import os
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Store map file constants
STORE_FILE_LOCAL = os.path.join("static", "store_map.json")
STORE_FILE_CLOUD = "store_map.json"

def load_store_map():
    """
    Load the store map from either local storage or Cloudinary
    """
    # First try to load from local file
    if os.path.exists(STORE_FILE_LOCAL):
        try:
            with open(STORE_FILE_LOCAL, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading local store map: {e}")
    
    # If local file doesn't exist or has issues, try to load from Cloudinary
    if 'RENDER' in os.environ:
        try:
            # Check if file exists in Cloudinary
            result = cloudinary.api.resources(type="raw")
            file_exists = any(resource['public_id'] == STORE_FILE_CLOUD for resource in result.get('resources', []))
            
            if file_exists:
                # Get the URL
                url = cloudinary.utils.cloudinary_url(STORE_FILE_CLOUD, resource_type="raw")[0]
                
                # Download the file
                import requests
                response = requests.get(url)
                if response.status_code == 200:
                    store_map = response.json()
                    
                    # Save to local file for caching
                    save_store_map_local(store_map)
                    
                    return store_map
        except Exception as e:
            print(f"Error loading store map from Cloudinary: {e}")
    
    # If all else fails, return empty map
    return {}

def save_store_map(store_map):
    """
    Save the store map to both local storage and Cloudinary
    """
    # Save locally
    save_store_map_local(store_map)
    
    # Save to Cloudinary if in production
    if 'RENDER' in os.environ:
        try:
            # Convert to JSON string
            json_data = json.dumps(store_map, ensure_ascii=False, indent=2)
            
            # Create a temporary file
            temp_file = "temp_store_map.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # Upload to Cloudinary
            cloudinary.uploader.upload(
                temp_file,
                public_id=STORE_FILE_CLOUD,
                resource_type="raw",
                overwrite=True
            )
            
            # Remove temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"Error saving store map to Cloudinary: {e}")

def save_store_map_local(store_map):
    """
    Save the store map to local storage
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STORE_FILE_LOCAL), exist_ok=True)
        
        # Save to file
        with open(STORE_FILE_LOCAL, 'w', encoding='utf-8') as f:
            json.dump(store_map, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving local store map: {e}")
