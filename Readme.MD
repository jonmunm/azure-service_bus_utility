# Azure Event Hubs Uploader

A high-performance Python utility designed to benchmark and execute data uploads to Azure Event Hubs.

---

## 🚀 Features
* **Smart Sampling:** Randomly selects a subset of rows from a fake data file for stress testing.
* **Async Core:** Built on `asyncio` for maximum I/O throughput.

---

## 🛠 Prerequisites
* Python 3.11+
* Azure CLI (for `AzureCliCredential`)
* Active Azure Storage Account

---

## 📋 Usage

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Running the Uploader

The tool is invoked via utils.py using the following parameters:

* ```stream```: The target Azure Event Hubs namespace and hub. Format *namespace.hub*.
* ```samples```: Number of random files to pick from the fake data file.

```bash
python utils.py send --stream ehns.hub1 --samples 10 
```