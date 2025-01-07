from google.cloud import firestore

from questions import questions_to_dict 


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
    
    
def save_new_questions(questions):
    
    docref = get_phyq_doc_ref()
    
    #check if document already exists otherwise create it
    snapshot = docref.get()
    if snapshot.exists:
        data = snapshot.to_dict()
        if 'questionlist' in data:
            # Append new values to an array field
            docref.update({
                "questionlist" : firestore.ArrayUnion(questions_to_dict(questions))
            })
        else:
            # Create the array field with the new object
            docref.update({
                "questionlist" : questions_to_dict(questions)
            })
    else:
        # Handle the case where the document does not exist
        # For example, create the document with the array field
        docref.set({
            'questionlist': questions_to_dict(questions)
        })
    
    print("physics questions updated")

def get_phyq_doc_ref():
    # Firestore client
    firestore_client = firestore.Client()
    docref=  firestore_client.collection("questions").document("phy_questions")
    return docref


def get_phy_questions():
    doc_ref = get_phyq_doc_ref()
    
    return doc_ref.get().to_dict()