# 📊 SDN-Based Traffic Classification using Mininet and Ryu Controller

## 📌 Problem Statement

Traditional networks lack visibility into traffic types and require manual analysis to understand network behavior.
This project implements a **Software-Defined Networking (SDN) based traffic classification system** using **Mininet** and the **Ryu OpenFlow controller**.

The controller dynamically analyzes incoming packets and classifies them into **TCP, UDP, ICMP, and OTHER** categories, demonstrating centralized and intelligent network monitoring.

---

## 🎯 Objectives

* Implement traffic classification using OpenFlow controller
* Identify packet types (TCP, UDP, ICMP, OTHER)
* Maintain real-time traffic statistics (packets & bytes)
* Dynamically install flow rules for efficient forwarding
* Display periodic traffic reports
* Understand protocol distribution in a network

---

## 🌐 Network Topology

```
        h1 (10.0.0.1)
             |
        h2 (10.0.0.2)
             |
        s1 (OpenFlow Switch)  <------>  Ryu Controller
          /      |       \
     h3 (10.0.0.3)  h4 (10.0.0.4)
```

* 4 hosts connected to 1 switch
* Remote Ryu controller manages traffic classification
* All packets are analyzed at the controller

---

## ⚙️ Setup & Installation

### ✅ Prerequisites

* Ubuntu 20.04 / 22.04
* Mininet
* Ryu Controller
* Python 3

---

### 🔹 Step 1 — Install Mininet

```bash
sudo apt update
sudo apt install mininet -y
```

---

### 🔹 Step 2 — Install Ryu Controller

```bash
pip install ryu
```

---

### 🔹 Step 3 — Clone Repository

```bash
git clone https://github.com/your-username/traffic-classifier.git
cd traffic-classifier
```

---

## ▶️ Execution Steps

### 🖥️ Terminal 1 — Start Ryu Controller

```bash
ryu-manager traffic_classifier.py
```

✅ Expected Output:

```
Switch connected
[CLASSIFIED: TCP/UDP/ICMP] logs appearing
```

---

### 🖥️ Terminal 2 — Start Mininet Topology

```bash
sudo python3 topology.py
```

👉 Topology info from your file :

* 4 hosts (h1–h4) connected to switch s1
* Remote controller is used

---

## 🧪 Test Scenarios

### ✅ Test 1 — Ping (ICMP Traffic)

```bash
mininet> h1 ping h2 -c 4
```

👉 Classified as: **ICMP**

---

### ✅ Test 2 — TCP Traffic

```bash
mininet> h1 iperf -c 10.0.0.2
```

👉 Classified as: **TCP**

---

### ✅ Test 3 — UDP Traffic

```bash
mininet> h1 iperf -c 10.0.0.2 -u
```

👉 Classified as: **UDP**

---

### 🔍 Test 4 — Observe Classification Logs

Controller output (from your code ):

```
[CLASSIFIED: TCP] src=xx dst=xx
[CLASSIFIED: UDP] src=xx dst=xx
[CLASSIFIED: ICMP] src=xx dst=xx
```

---

### 📊 Test 5 — Traffic Report (Auto Generated)

Every 10 seconds:

```
========= Traffic Classification Report =========
Protocol     Packets        Bytes     Share
---------------------------------------------
TCP              xx           xx       xx%
UDP              xx           xx       xx%
ICMP             xx           xx       xx%
OTHER            xx           xx       xx%
=================================================
```

---

## 📈 Expected Results

| Test        | Result                    |
| ----------- | ------------------------- |
| Ping        | ICMP packets classified   |
| iperf (TCP) | TCP traffic detected      |
| iperf (UDP) | UDP traffic detected      |
| Logs        | Real-time classification  |
| Report      | Periodic statistics shown |

---

## 🧠 How It Works

* Switch sends packets to controller (Packet-In)
* Controller inspects packet headers
* Identifies protocol using:

  * TCP → port-based detection
  * UDP → port-based detection
  * ICMP → ping packets
* Updates statistics (count & bytes)
* Installs flow rules to optimize forwarding
* Periodically prints traffic report

---

## 🚀 Future Improvements

* Add graphical dashboard for visualization
* Integrate AI-based traffic analysis
* Support multiple switches
* Store logs in database
* Real-time web monitoring

---

## 🔗 GitHub

https://github.com/sankgit14

---

## 🤝 Contributing

Feel free to fork this project and enhance it.
Pull requests are welcome!

