# Azure Service Bus Utility

A high-performance Python utility designed to benchmark, execute data uploads in parallel batches, and stream/read messages from Azure Service Bus Queues and Topics.

---

## 🚀 Features
* **Parallel Batching (`send`):** Sends multiple record batches concurrently using `asyncio` and random batch sizing for realistic stress testing to either a Queue or a Topic.
* **Continuous Consumption (`receive`):** Reads and displays JSON messages continuously from a Queue or a Topic Subscription, with automatic completion and a smart timeout window to stop when idle.
* **Async Core:** Built on `asyncio` for maximum I/O throughput.

---

## 🛠 Prerequisites
* Python 3.11+
* Azure CLI (for `AzureCliCredential`)
* Active Azure Service Bus Namespace (Queues, Topics & Subscriptions)

---

## 📋 Usage

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Running the Commands

The tool is invoked via `utils.py` using two main commands supporting either `--topic` or `--queue`:

#### A. Send Events in Parallel Batches (`send`)
Sends multiple batches of mock records in parallel to a Service Bus Topic or Queue, randomizing the size of each batch and displaying execution metrics upon completion.

* `--topic` / `--queue`: Target entity specification. Format *namespace.topic* or *namespace.queue*.
* `--batches`: Number of concurrent batches to send.

```bash
python utils.py send --topic sbn002.topic002 --batches 5
```

```text
Starting uploading 5 batches in parallel to Topic 'topic002'...
✅ [Batch #1] Finished in 0.82s at 22:30:10 | 12 rows sent
✅ [Batch #3] Finished in 0.85s at 22:30:10 | 7 rows sent
✅ [Batch #2] Finished in 0.88s at 22:30:10 | 15 rows sent
✅ [Batch #5] Finished in 0.91s at 22:30:10 | 11 rows sent
✅ [Batch #4] Finished in 0.94s at 22:30:10 | 9 rows sent
All batch uploads to Service Bus finished successfully.
```

#### B. Receive and Read Events (`receive`)
Listens to a Service Bus Queue or a Topic Subscription continuously, prints formatted JSON payloads, completes messages automatically, and stops when no new messages arrive.

* `--topic` / `--queue`: Target entity specification. Format *namespace.topic.subscription* for topic subscriptions, or *namespace.queue* for queues.

```bash
python utils.py receive --topic sbn002.topic002.subs002
```

```text
Starting receiving all messages from Topic 'topic002'...
Listening for messages... (Will automatically stop if no messages arrive within 5 seconds)
✔️ Received:
{
  "id": 800,
  "name": "John Martinez",
  "username": "johmar33",
  "email": "john.martinez@gmail.com",
  "address": {
    "street": "Joseph Light",
    "suite": "Apt. 784",
    "city": "Smithborough",
    "zipcode": "80230-2865",
    "geo": {
      "lat": "-30.8257",
      "lng": "-121.8251"
    }
  },
  "phone": "1-652-207-7621 x41958",
  "website": "martinez14.org",
  "company": {
    "name": "Martinez-Martin",
    "catchPhrase": "Visionary maximizing middleware",
    "bs": "deploy open-source paradigms"
  }
}
...
✅ Finished in 5.21s starting at 22:31:00 | 54 rows received
Receiving from Service Bus finished