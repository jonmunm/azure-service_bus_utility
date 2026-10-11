import time
import json
from datetime import datetime
from azure.identity.aio import AzureCliCredential
from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver

async def receive_worker(
        receiver: ServiceBusReceiver
    ):
    """
    Asynchronously receives and processes all messages continuously from an Azure Service Bus receiver 
    in batches using a while loop with a timeout until no more messages arrive.

    Args:
        receiver (ServiceBusReceiver): The initialized Service Bus receiver client.
    """
    start_time = time.perf_counter()
    start_str = datetime.now().strftime('%H:%M:%S')
    row_count = 0

    print("Listening for messages... (Will automatically stop if no messages arrive within 5 seconds)")

    while True:
        # Pull a batch of messages, waiting up to 5 seconds if none are immediately available
        received_msgs = await receiver.receive_messages(max_message_count=50, max_wait_time=5)
        
        # If no messages were returned after the wait time, we assume the queue/subscription is empty
        if not received_msgs:
            break
            
        for msg in received_msgs:
            row_count += 1
            body = b"".join(msg.body).decode("utf-8")
            record = json.loads(body)
            
            # Formatted JSON output
            formatted_json = json.dumps(record, indent=2)
            print(f"✔️ Received:\n{formatted_json}")
            
            # Complete the message to remove it from the Service Bus
            await receiver.complete_message(msg)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
        
    print(f"✅ Finished in {duration:.2f}s starting at {start_str} | {row_count:,} rows received")

async def command(
        namespace: str, 
        topic: str | None = None, 
        queue: str | None = None,
        subscription: str | None = None
    ):
    """
    Main command orchestrator to receive all available messages from a Service Bus topic subscription or queue.

    Args:
        namespace (str): The Azure Service Bus namespace.
        topic (str | None): Target topic name, if applicable.
        queue (str | None): Target queue name, if applicable.
        subscription (str | None): Target subscription name for the topic, if applicable.
    """
    credential = AzureCliCredential()
    fully_qualified_namespace = f"{namespace}.servicebus.windows.net"

    servicebus_client = ServiceBusClient(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=credential
    )
    
    target_name = topic if topic else queue
    target_type = "Topic" if topic else "Queue"
    
    print(f"Starting receiving all messages from {target_type} '{target_name}'...")
    
    async with servicebus_client:
        if topic and subscription:
            receiver = servicebus_client.get_subscription_receiver(topic_name=topic, subscription_name=subscription)
        elif queue:
            receiver = servicebus_client.get_queue_receiver(queue_name=queue)
        else:
            raise ValueError("You must specify either a queue, or a topic AND a subscription.")

        async with receiver:
            await receive_worker(receiver)

    await credential.close()
    
    print(f"Receiving from Service Bus finished")