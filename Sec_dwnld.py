import os
import time
import datetime
from collections import defaultdict
from azure.storage.blob import BlobServiceClient, BlobClient


def blob_download():
    print("Started download")

    # Azure Storage Connection String
    connect_str = "RandomString"  # Replace with your actual connection string

    # Container Name
    container_name = "projectx"

    try:
        # Create a BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()

        # Track the latest version of each file (A, B, C, D)
        latest_files = defaultdict(lambda: {"name": None, "last_modified": None})
        file_prefixes = ["08f-N_Results", "P_Results","N_Results"]  # Expected base file names

        # Identify the latest file version for each prefix
        for file in blob_list:
            file_name = file.name  # Full file name
            last_modified = file.last_modified

            for prefix in file_prefixes:
                if file_name.startswith(prefix) and file_name.endswith(".xlsx"):  # Match file prefix and extension
                    if (latest_files[prefix]["last_modified"] is None) or (last_modified > latest_files[prefix]["last_modified"]):
                        latest_files[prefix]["name"] = file_name
                        latest_files[prefix]["last_modified"] = last_modified

        # Current UTC time
        current_time = datetime.datetime.utcnow()
        time_threshold = current_time - datetime.timedelta(hours=6)  # 6-hour window
        
        # Create local directory
        local_dir = f"./{container_name}"
        os.makedirs(local_dir, exist_ok=True)

        # Download the latest version of each file (if last modified is within 6 hours)
        for prefix, file_info in latest_files.items():
            if file_info["name"]:
                last_modified = file_info["last_modified"]

                # Check if last modified time is within the last 6 hours
                if last_modified >= time_threshold:
                    print(f"✅ Downloading latest {prefix}: {file_info['name']} (Last Modified: {last_modified})")

                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_info["name"])
                    retry_count = 10
                    retry_delay = 10  # seconds
                    success = False

                    while retry_count > 0 and not success:
                        try:
                            file_path = os.path.join(local_dir, f"{prefix}.xlsx")  # Save as .xlsx
                            with open(file_path, "wb") as my_blob:
                                blob_data = blob_client.download_blob()
                                blob_data.readinto(my_blob)

                            success = True
                            print(f"🎉 Download completed: {file_info['name']} as {prefix}.xlsx")
                        except Exception as e:
                            print(f"⚠️ Error downloading {file_info['name']}: {e}")
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_count -= 1

                    if not success:
                        print(f"❌ Download failed after multiple retries: {file_info['name']}")
                else:
                    print(f"⏩ Skipping {prefix}: Latest file {file_info['name']} is older than 6 hours (Last Modified: {last_modified})")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
blob_download()

