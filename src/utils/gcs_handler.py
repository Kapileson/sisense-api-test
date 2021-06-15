from google.cloud import storage


def get_test_data_from_gcs(bucket, file_path):
    gcs_client = storage.Client()
    bucket = gcs_client.get_bucket(bucket)
    blob = bucket.blob(file_path)
    return blob.download_as_string(client=None)
