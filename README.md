# 🔍 Maltese Minecraft Server Finder

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6+-green.svg)

A powerful Python tool that discovers Minecraft servers in Maltese IP ranges through automated network scanning.

<p align="center">
  <img src="https://img.shields.io/badge/Discovered_Servers-10+-success" alt="Servers Found">
  <img src="https://img.shields.io/badge/Scanning_Speed-High-blue" alt="Fast Scanning">
  <img src="https://img.shields.io/badge/Multi_Threaded-200+-orange" alt="Multi-threaded">
</p>

## ✨ Features

- 🇲🇹 Targets Maltese IP ranges from multiple ISPs (Melita, GO, Epic, etc.)
- 🚀 Multi-threaded scanning with up to 200 parallel connections
- 📊 Collects comprehensive server information (version, players, ping, etc.)
- 💾 Saves results in individual and summary JSON reports
- 🔄 Supports continuous scanning with configurable intervals
- 🔍 Optional nmap integration for enhanced scanning
- 🌈 Rich, colorful console output with progress visualization

## 📋 Requirements

- Python 3.6+
- Required packages:
  - python-nmap (optional)
  - mcstatus
  - ipaddress
  - tqdm
  - colorama

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ServerFinder.git
cd ServerFinder
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 📝 Configuration

The script can be configured by editing these parameters in `server_finder.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MALTA_IP_RANGES` | Multiple ranges | IP ranges associated with Maltese ISPs |
| `THREADS` | 200 | Number of parallel scanning threads |
| `TIMEOUT` | 1.5 | Connection timeout in seconds |
| `SCAN_LIMIT` | None | Limit IPs to scan (None = unlimited) |
| `CONTINUOUS_SCANNING` | True | Enable continuous scanning mode |
| `SCAN_INTERVAL` | 3600 | Seconds between scan cycles |
| `RANDOMIZE_IPS` | True | Shuffle IPs for each scan |
| `MAX_SCAN_COUNT` | None | Maximum number of scan cycles |
| `AGGRESSIVE_SCAN` | False | Check multiple ports on each IP |

## 💻 Usage

Run the script with:

```bash
python server_finder.py
```

The script will automatically:
1. Load all configured Maltese IP ranges
2. Scan for Minecraft servers on port 25565 (and optionally others)
3. Display real-time discovery information in the console
4. Save detailed reports of found servers

## 📊 Output

Server information is saved in two formats:

### Individual Server Files

Each discovered server gets its own JSON file with detailed information:
```
discovered_servers/minecraft_server_78.133.86.137_20250423_231059.json
```

### Summary Reports

After each scan cycle, a summary JSON is generated:
```
discovered_servers/scan_report_20250428_225723.json
```

Recent scans have discovered:
- Server types: Vanilla, Paper, Purpur
- Minecraft versions: 1.18.2 through 1.21.5
- Players online: Varies from 0-4 players

## 📈 Stats from Latest Scan

From recent scans, we have found:
- Total unique servers: 10+
- Most common version: 1.21.4/1.21.5
- Server software: Paper (40%), Vanilla (40%), Purpur (20%)
- Most active server: "All the Mods 9" with up to 4 players

## ⚠️ Important Notes

- ⚖️ Port scanning may be **illegal** without proper authorization
- 🎓 This tool is intended for **educational purposes only**
- 📝 Always ensure you have permission before scanning IP ranges
- 🔒 Some network providers actively block scanning activities
- 🚫 Use responsibly and ethically

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- mcstatus team for the Minecraft server API
- nmap developers for the powerful port scanning capabilities
- The Python community for the excellent libraries

---

<p align="center">
  Made with ❤️ for the Minecraft community
</p>