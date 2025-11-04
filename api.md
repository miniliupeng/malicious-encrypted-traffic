# API 文档

## 伪装/混淆流量标签统计接口
**获取“伪装/混淆流量”分布**

### 请求方式
`GET /api/postgres/multilevel_flow_info/pcap_label_stats`

### 示例调用
```bash
curl -s http://localhost:5050/api/postgres/multilevel_flow_info/pcap_label_stats | jq .

```
### 调用结果
```json
{
  "data": [
    { "count": 350, "pcap_label": "meek" },
    { "count": 262, "pcap_label": "fte" },
    { "count": 222, "pcap_label": "obfs4" },
    { "count": 162, "pcap_label": "scramblesuit" },
    { "count": 159, "pcap_label": "obfs3" }
  ],
  "success": true
}

```

## 隧道行为流量标签统计接口  
**获取”隧道行为分布“**

### 请求方式  
`GET /api/postgres/behavior_flow_info/pcap_label_stats`

### 示例调用  
```bash
curl -s http://localhost:5050/api/postgres/behavior_flow_info/pcap_label_stats | jq .
```
### 调用结果
```json
{
  "data": [
    { "pcap_label": "Instant_Messaging", "count": 192 },
    { "pcap_label": "others",            "count": 168 },
    { "pcap_label": "Volp",              "count": 157 },
    { "pcap_label": "File_Transfer",     "count": 152 },
    { "pcap_label": "Mail_Communication","count": 119 },
    { "pcap_label": "Web_Browsing",      "count": 119 },
    { "pcap_label": "Video_Streaming",   "count": 117 }
  ],
  "success": true
}
```

## 隧道行为流量信息提取接口  
**获取”隧道行为总数“和“流量日志”**

### 请求方式  
`GET /api/postgres/behavior_flow_info/logs`

### 示例调用  
```bash
curl -s http://localhost:5050/api/postgres/behavior_flow_info/logs | jq .

```

### 调用结果
```json
{
  "data": [
    {
      "log_num": 1023,
      "log_time": "Tue, 14 Oct 2025 10:06:13 GMT",
      "src": "172.16.30.111",
      "sport": "30469",
      "dst": "172.16.30.153",
      "dport": "22",
      "protol": "tcp",
      "pcap_label": "Video_Streaming"
    }
    /* … 共 100 条，total=1024 … */
  ],
  "limit": 100,
  "page": 1,
  "total": 1024,
  "success": true
}
```

### 协议识别统计接口  

**用于获取各协议类比占比**
### 请求方式  
`GET /api/postgres/tunnel_flow_info/pcap_label_stats`

### 示例调用  
```bash
curl -s http://localhost:5050/api/postgres/tunnel_flow_info/pcap_label_stats | jq .
```
### 调用结果
```json
{
  "data": [
    { "pcap_label": "Modbus",    "count": 321 },
    { "pcap_label": "OPCUA",     "count": 320 },
    { "pcap_label": "L2TP",      "count": 314 },
    { "pcap_label": "DNP3",      "count": 252 },
    { "pcap_label": "PPTP",      "count": 203 },
    { "pcap_label": "IPv6",      "count": 198 },
    { "pcap_label": "SSH",       "count": 169 },
    { "pcap_label": "S7CommPlus","count": 152 },
    { "pcap_label": "IEC_104",   "count": 151 },
    { "pcap_label": "IPsec",     "count": 148 },
    { "pcap_label": "OpenVPN",   "count": 119 },
    { "pcap_label": "others",    "count": 110 },
    { "pcap_label": "Wireguard", "count": 105 }
  ],
  "success": true
}
```	

### 协议识别信息提取接口

**用于获取“协议总数” 和 “流量日志”**

### 请求方式
`GET /api/postgres/tunnel_flow_info/logs`

### 示例调用

```bash
curl -s http://localhost:5050/api/postgres/tunnel_flow_info/logs | jq .

```

### 调用结果

```json
{
  "data": [
    {
      "log_num": 2561,
      "log_time": "Tue, 14 Oct 2025 10:02:16 GMT",
      "src": "108.160.141.197",
      "sport": "{4500,51743}",
      "dst": "192.168.108.189",
      "dport": "{4500,51743}",
      "protol": "IPsec",
      "pcap_label": "IPsec"
    }
    /* … 共 100 条，total=2562 … */
  ],
  "limit": 100,
  "page": 1,
  "total": 2562,
  "success": true
}
```
