# VPS Requirements for Agency Swarm Deployment

## Minimum System Requirements

### Basic Operations (Trading Bots & AI Agents)
- CPU: 8 cores (16 threads)
- RAM: 32GB
- Storage: 500GB SSD
- Bandwidth: Unmetered
- Operating System: Ubuntu 20.04 LTS or newer

### Node Operations
For running validator nodes on:
- Polygon (Port 8545)
- Arbitrum (Port 8546)
- Optimism (Port 8547)
- Avalanche (Port 8548)

Additional requirements for nodes:
- Extra 32GB RAM (64GB total)
- Extra 1TB SSD (1.5TB total)
- Static IP address
- Unmetered bandwidth with high speed (1Gbps recommended)

## Network Requirements
- Dedicated IP address
- Open ports:
  - 8545-8548 (Blockchain nodes)
  - 80/443 (Web interface)
  - 22 (SSH)
- No traffic restrictions
- Low latency connection (<100ms to major exchanges)

## Recommended VPS Providers
1. AWS EC2:
   - Instance Type: c5.4xlarge or better
   - Region: us-east-1 (closest to major exchanges)

2. Google Cloud:
   - Instance Type: c2-standard-16
   - Region: us-east4

3. DigitalOcean:
   - Premium Intel Droplet
   - 32GB RAM / 8 vCPUs minimum

4. Hetzner:
   - AX101 or better
   - Location: US or Finland

## Security Requirements
- UFW (Uncomplicated Firewall)
- Fail2ban
- SSH key authentication only
- Regular security updates
- DDoS protection

## Monitoring Requirements
- Prometheus metrics
- Grafana dashboards
- Log rotation
- Disk space monitoring
- Network traffic monitoring

## Backup Requirements
- Daily system snapshots
- Hourly data backups
- State backup every 5 minutes
- Off-site backup storage

## Cost Estimates
- Basic Setup (Trading & AI only): $200-400/month
- Full Setup (with Nodes): $500-1000/month
- Bandwidth costs: Included in above
- Backup storage: Additional $50-100/month

## Initial Setup Time
- Basic Setup: 2-3 hours
- Full Setup with Nodes: 4-6 hours
- Configuration & Testing: 2-3 hours

## Maintenance Requirements
- Daily health checks
- Weekly updates
- Monthly security audits
- Quarterly system optimization

## Emergency Procedures
- Automated failover
- 24/7 monitoring alerts
- Backup restoration protocols
- Node recovery procedures
