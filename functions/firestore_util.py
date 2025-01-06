from google.cloud import firestore


def get_doc_ref():
    # Firestore client
    firestore_client = firestore.Client()
    return firestore_client.collection("questions").document("image_folder")


def get_processed_files() :
    # Firestore reference
    doc_ref = get_doc_ref()
    
    # Fetch existing data from Firestore
    existing_data = doc_ref.get().to_dict()
    
    return existing_data


def filter_files(new_files):
    # Prepare new file data
    new_file_data = [{"id": file["id"], "name": file["name"]} for file in new_files]


    # Fetch existing data from Firestore
    existing_data = get_processed_files()

    if existing_data and "processed_files" in existing_data:
        # Create a set of existing file IDs
        existing_file_ids = {file["id"] for file in existing_data["processed_files"]}

        # Filter out files that already exist
        filtered_new_files = [file for file in new_file_data if file["id"] not in existing_file_ids]

        # Merge the new files into the existing list
        updated_file_data = existing_data["processed_files"] + filtered_new_files
    else:
        # No existing data, use the new data directly
        filtered_new_files = new_file_data
        updated_file_data = filtered_new_files

    return updated_file_data, filtered_new_files


def save_new_files(doc_ref, updated_file_data):
    doc_ref.set({"processed_files": updated_file_data})