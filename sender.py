import time
import json
import random
import asyncio
from datetime import datetime
from azure.identity.aio import AzureCliCredential
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender
from azure.servicebus import ServiceBusMessage
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
fake_user_file = f"{BASE_DIR}/users_fake_data.json"

async def send_worker(
        sender: ServiceBusSender, 
        batch_id: int,
        all_records: list
    ):
    """
    Asynchronously creates and sends a single batch of randomly selected mock records 
    to an Azure Service Bus queue or topic.

    Args:
        sender (ServiceBusSender): The initialized Service Bus sender client.
        batch_id (int): Identifier number for the current batch.
        all_records (list): The complete list of source records loaded from the mock file.
    """
    start_time = time.perf_counter()
    start_str = datetime.now().strftime('%H:%M:%S')

    # Define a random batch size (e.g., between 5 and 15 records per batch)
    # Ensuring we do not exceed the total records available in the file
    max_limit = min(15, len(all_records))
    min_limit = min(5, max_limit)
    batch_size = random.randint(min_limit, max_limit) if max_limit >= min_limit else len(all_records)
    
    # Select a random subset of records for this batch
    chunk = random.sample(all_records, batch_size)
    row_count = len(chunk)
    
    batch_message = await sender.create_message_batch()
    
    for record in chunk:
        batch_message.add_message(ServiceBusMessage(json.dumps(record)))
        
    await sender.send_messages(batch_message)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
        
    print(f"✅ [Batch #{batch_id}] Finished in {duration:.2f}s at {start_str} | {row_count:,} rows sent")


async def command(
        namespace: str,
        batches: int, 
        topic: str | None = None, 
        queue: str | None = None
    ):
    """
    Main command orchestrator to upload multiple batches of mock data in parallel 
    to a Service Bus topic or queue.

    Args:
        namespace (str): The Azure Service Bus namespace.
        batches (int): Total number of concurrent batches to send.
        topic (str | None): Target topic name, if applicable.
        queue (str | None): Target queue name, if applicable.
    """
    credential = AzureCliCredential()
    fully_qualified_namespace = f"{namespace}.servicebus.windows.net"

    servicebus_client = ServiceBusClient(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=credential
    )
    
    target_name = topic if topic else queue
    target_type = "Topic" if topic else "Queue"
    
    # Load base records only once
    with open(fake_user_file, "r", encoding="utf-8") as archivo:
        records = json.load(archivo)

    print(f"Starting uploading {batches} batches in parallel to {target_type} '{target_name}'...")
    
    async with servicebus_client:
        if topic:
            sender = servicebus_client.get_topic_sender(topic_name=topic)
        elif queue:
            sender = servicebus_client.get_queue_sender(queue_name=queue)
        else:
            raise ValueError("You must specify either a topic or a queue.")

        async with sender:
            # Create concurrent tasks for each requested batch
            tasks = [
                send_worker(sender, i + 1, records) 
                for i in range(batches)
            ]
            # Execute all batches in parallel
            await asyncio.gather(*tasks)

    await credential.close()
    
    print(f"All batch uploads to Service Bus finished successfully.")