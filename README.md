# AI-Driven Threat Intelligence and Incident Response System

## Real-Time RAG for Cybersecurity

A comprehensive Jupyter notebook implementing an intelligent cybersecurity threat detection and incident response system using Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), and real-time security log analysis.

## 🎯 Overview

This system combines cutting-edge AI technologies to provide:

- **Real-time Security Log Analysis**: Process and analyze security events as they occur
- **RAG-Based Threat Intelligence**: Retrieve relevant threat information from a comprehensive knowledge base
- **LLM-Powered Classification**: Intelligent threat categorization and severity assessment
- **Automated Incident Response**: AI-generated recommendations based on security best practices
- **Interactive Dashboards**: Visual monitoring and analytics
- **Comprehensive Reporting**: Automated incident response reports

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Log Sources                          │
│              (SIEM, Firewalls, IDS/IPS, EDR)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Log Ingestion & Parsing                         │
│              (SecurityLogGenerator + Parser)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Threat Analysis Engine                          │
│                                                                  │
│  ┌────────────────────┐         ┌─────────────────────┐        │
│  │  RAG Retrieval     │◄────────┤  Vector Database    │        │
│  │  (Top-K Search)    │         │  (ChromaDB)         │        │
│  └────────┬───────────┘         └─────────────────────┘        │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────┐                                         │
│  │  LLM Analysis      │                                         │
│  │  (GPT/Local Model) │                                         │
│  └────────┬───────────┘                                         │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Incident Response & Reporting                       │
│   (Alerts, Playbooks, Reports, Visualization)                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### 1. **Comprehensive Threat Intelligence Database**
- 15+ threat patterns based on MITRE ATT&CK framework
- CVE vulnerability information
- Threat actor profiles
- Incident response playbooks

### 2. **Real-Time Log Processing**
- Simulated security log generation (easily replaceable with real sources)
- Event types: brute force, SQL injection, ransomware, C2 communication, data exfiltration, and more
- Severity classification: CRITICAL, HIGH, MEDIUM, LOW

### 3. **RAG Implementation**
- Vector embeddings using Sentence Transformers or OpenAI
- ChromaDB for efficient similarity search
- Context-aware threat retrieval

### 4. **LLM-Based Analysis**
- OpenAI GPT integration (with local model fallback)
- Structured threat analysis reports
- Actionable incident response recommendations

### 5. **Visualization Dashboard**
- Threat distribution charts
- Severity analysis
- Timeline of critical events
- Source IP threat mapping
- Interactive Plotly visualizations

### 6. **Interactive Query System**
- Natural language threat intelligence queries
- Custom log analysis
- Real-time threat lookups

## 📋 Requirements

### Python Packages

```bash
pip install langchain langchain-community langchain-openai chromadb sentence-transformers openai python-dotenv pandas numpy matplotlib seaborn plotly
```

### Environment Variables

Create a `.env` file in the project directory:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: The system can work without OpenAI by using local HuggingFace models (free option).

## 🎓 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Option A: Using OpenAI (recommended for best results)
echo "OPENAI_API_KEY=your-key-here" > .env

# Option B: Use free local models (automatic fallback)
# No configuration needed!
```

### 3. Launch Jupyter Notebook

```bash
jupyter notebook realtime_rag_threat_intelligence.ipynb
```

### 4. Run All Cells

Execute the cells sequentially to:
1. Load threat intelligence data
2. Build the vector database
3. Initialize the analysis engine
4. Run real-time monitoring simulation
5. Generate visualizations and reports

## 💡 Usage Examples

### Query Threat Intelligence

```python
query_threat_intelligence("How do I respond to ransomware attacks?")
```

### Analyze Custom Security Log

```python
analyze_custom_log(
    event_type="suspicious_powershell",
    source_ip="192.168.1.50",
    dest_ip="192.168.1.10",
    description="PowerShell executed with -EncodedCommand downloading from external IP"
)
```

### Run Real-Time Monitoring

```python
# Monitor for 60 seconds, processing 5 logs per second
critical_incidents = security_monitor.process_log_stream(
    duration_seconds=60,
    logs_per_second=5
)
```

### Generate Incident Report

```python
report = security_monitor.generate_incident_report(critical_incidents)
print(report)
```

## 🔧 Customization

### Adding Custom Threat Intelligence

Edit the `THREAT_INTELLIGENCE_DATA` list in the notebook:

```python
THREAT_INTELLIGENCE_DATA.append({
    "id": "CUSTOM-001",
    "category": "Your Category",
    "technique": "Your Technique",
    "description": "Detailed description",
    "indicators": ["indicator1", "indicator2"],
    "severity": "CRITICAL",
    "response": "Response actions"
})
```

### Integrating Real Log Sources

Replace the `SecurityLogGenerator` with real log ingestion:

```python
# Example: Splunk integration
from splunklib import client

def ingest_from_splunk():
    service = client.connect(host='localhost', port=8089,
                            username='admin', password='password')
    # Query and parse logs
    # Return SecurityLog objects
```

### Fine-Tuning the LLM

```python
# Use your own fine-tuned model
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model_name="ft:gpt-3.5-turbo:your-org:model-name:id",
    temperature=0
)
```

## 📊 Key Components

### ThreatIntelligenceRAG
- Manages vector database of threat intelligence
- Performs similarity search for relevant threats
- Supports both OpenAI and local embeddings

### ThreatAnalysisEngine
- Analyzes security logs using RAG + LLM
- Generates structured threat assessments
- Provides incident response recommendations

### RealTimeSecurityMonitor
- Processes security logs in real-time
- Tracks statistics and trends
- Generates comprehensive reports

### SecurityLogGenerator
- Simulates realistic security events
- Supports 15+ event types
- Configurable IP ranges and user accounts

## 🎯 Real-World Deployment Roadmap

### Phase 1: Integration
- [ ] Connect to SIEM (Splunk, ELK, QRadar)
- [ ] Integrate threat feeds (MISP, AlienVault OTX)
- [ ] Add EDR/XDR platform integration
- [ ] Implement CVE database lookups

### Phase 2: Fine-Tuning
- [ ] Collect organization-specific security logs
- [ ] Fine-tune LLM on historical incidents
- [ ] Train on custom threat landscape
- [ ] Implement continuous learning pipeline

### Phase 3: Automation
- [ ] SOAR integration (Phantom, Demisto)
- [ ] Automated ticket creation (Jira, ServiceNow)
- [ ] Deploy response playbooks
- [ ] Enable automatic threat blocking

### Phase 4: Scaling
- [ ] Cloud deployment (AWS, Azure, GCP)
- [ ] Distributed processing (Kafka, Spark)
- [ ] Scale vector database (Pinecone, Weaviate)
- [ ] Implement caching and optimization

### Phase 5: Monitoring & Compliance
- [ ] Set up alerting (PagerDuty, Slack)
- [ ] Create executive dashboards
- [ ] Implement SLA tracking
- [ ] Ensure compliance (SOC2, ISO 27001)

## 🔒 Security Considerations

- **Data Encryption**: Encrypt sensitive log data at rest and in transit
- **Access Control**: Implement RBAC for system access
- **Audit Logging**: Track all system operations
- **API Security**: Secure API keys and credentials
- **Compliance**: Follow industry standards (NIST, CIS)

## 📈 Performance Metrics

The system tracks:
- **Detection Rate**: Percentage of threats identified
- **False Positive Rate**: Accuracy of threat classification
- **Response Time**: Time from detection to alert
- **Coverage**: Percentage of attack vectors monitored

## 🤝 Contributing

To extend this system:

1. Add new threat patterns to the knowledge base
2. Implement additional visualization types
3. Integrate new data sources
4. Enhance the LLM prompts for better analysis
5. Add machine learning models for anomaly detection

## 📚 References

- **MITRE ATT&CK**: https://attack.mitre.org/
- **CVE Database**: https://cve.mitre.org/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **LangChain Documentation**: https://python.langchain.com/
- **ChromaDB**: https://www.trychroma.com/

## 📝 License

This project is provided as-is for educational and research purposes.

## ⚠️ Disclaimer

This is a demonstration system for educational purposes. For production use:
- Implement proper authentication and authorization
- Use enterprise-grade vector databases
- Add comprehensive error handling
- Conduct security audits
- Follow your organization's security policies

## 🆘 Support

For issues or questions:
1. Check the notebook documentation
2. Review the code comments
3. Consult the LangChain and ChromaDB documentation
4. Test with sample data before production deployment

## 🎓 Learning Resources

- **Cybersecurity Fundamentals**: Study MITRE ATT&CK framework
- **RAG Systems**: Understand retrieval-augmented generation
- **LLM Fine-Tuning**: Learn prompt engineering and fine-tuning
- **Security Analytics**: Study SIEM and SOC operations

---

**Built with ❤️ for cybersecurity professionals**

*Empowering security teams with AI-driven threat intelligence and automated incident response*
