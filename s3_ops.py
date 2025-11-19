import boto3
from boto3.s3.transfer import TransferConfig
import io

class Storage_Operations:
    def __init__(self, Bucket_Name):
        self.s3=boto3.client('s3')
        self.Bucket_Name=Bucket_Name
        self.transfer_config = TransferConfig(
            multipart_threshold=5 * 1024 * 1024,
            multipart_chunksize=5 * 1024 * 1024,
            max_concurrency=10,
            use_threads=True
        )

    def add_s3_objects(self):
        Count=1500
        for i in range(Count):
            Range='0-499' if i<500 else '500-999' if i<1000 else '1000-1499'
            Batch='batch-1' if i<500 else 'batch-2' if i<1000 else 'batch-3' 
            Nature='Even' if i%2==0 else 'Odd'

            body = f"This is file number {i}" * 400_000  
            metadata = {
                'number': str(i),
                'parity': Nature,
                'batch': Batch
            }
            tagging = f"Type=Number&Range={Range}&Nature={Nature}"

            body_stream = io.BytesIO(body.encode())

            self.s3.upload_fileobj(
                Fileobj=body_stream,
                Bucket=self.Bucket_Name,
                Key=f"{i}.txt",
                ExtraArgs={
                    "Metadata": metadata,
                    "Tagging": tagging
                },
                Config=self.transfer_config
            )


    def fetch_s3_objects_by_metadata(self,metadata):
        paginator=self.s3.get_paginator('list_objects')
        page_iterator=paginator.paginate(Bucket=self.Bucket_Name)
        objects=[]
        for page in page_iterator:
            for obj in page.get('Contents', []):
                key = obj['Key']
                head = self.s3.head_object(Bucket=self.Bucket_Name, Key=key)
                meta=head.get('Metadata')
                if all(meta.get(k) == v for k, v in metadata.items()):
                        objects.append(key)
                       
        return objects

    def fetch_s3_objects_by_tag(self, tag_filter):
        paginator=self.s3.get_paginator('list_objects')
        page_iterator=paginator.paginate(Bucket=self.Bucket_Name)
        objects=[]
        for page in page_iterator:
            for obj in page.get('Contents', []):
                key=obj['Key']
                tag_response = self.s3.get_object_tagging(Bucket=self.Bucket_Name, Key=key)
                tags = {t['Key']: t['Value'] for t in tag_response.get('TagSet', [])}

                if all(tags.get(k) == v for k, v in tag_filter.items()):
                    objects.append(key)

        return objects
    
    def delete_s3_objects_by_metadata(self,metadata):
        Objects=self.fetch_s3_objects_by_metadata(metadata)
        delete_payload = {'Objects': [{'Key': key} for key in Objects]}
        self.s3.delete_objects(Bucket=self.Bucket_Name, Delete=delete_payload)  
        return {'Deletion':'Complete','Deleted': len(Objects)}


    def delete_s3_objects_by_tags(self,tag_filter):
        Objects=self.fetch_s3_objects_by_tag(tag_filter)
        delete_payload = {'Objects': [{'Key': key} for key in Objects]}
        self.s3.delete_objects(Bucket=self.Bucket_Name, Delete=delete_payload) 
        return {'Deletion':'Complete','Deleted': len(Objects)}
        

def main():
    bucket_name = "assignment-2-s3-unit-test"

    s3 = boto3.client("s3")
    try:
        s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration={
        "LocationConstraint": "ap-south-1"
    })
        print(f"Bucket created: {bucket_name}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket already exists: {bucket_name}")

    ops = Storage_Operations(bucket_name)

    ops.add_s3_objects()
    print("Added 1500 objects with AUTO-MULTIPART upload!")

    print(ops.fetch_s3_objects_by_metadata({'batch': 'batch-1'}))
    print(ops.fetch_s3_objects_by_tag({'Nature': 'Odd'}))

    print(ops.delete_s3_objects_by_metadata({'batch': 'batch-1'}))
    print(ops.delete_s3_objects_by_tags({'Range': '500-999'}))


if __name__ == "__main__":
    main()