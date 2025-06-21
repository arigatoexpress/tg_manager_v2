# 🔄 Redundancy & Failover Setup Guide

This guide will help you set up multiple DePIN providers for high availability, cost optimization, and automatic failover.

## 📋 Quick Start

1. **Run the setup script:**
   ```bash
   python setup_redundancy.py
   ```

2. **Follow the interactive prompts to:**
   - View setup instructions for each provider
   - Generate environment template
   - Test provider connectivity
   - Configure failover settings

## 🚀 Provider Configuration

### Primary Provider: Sui Compute

**Cost:** ~$0.001/hour ($0.72/month)
**Priority:** 1 (Primary)
**Setup Time:** 10-15 minutes

#### Setup Instructions:

1. **Install Sui CLI:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/MystenLabs/sui/main/docs/scripts/install-sui.sh | sh
   ```

2. **Create Wallet:**
   ```bash
   sui client new-address ed25519
   ```

3. **Get Testnet Tokens:**
   ```bash
   sui client faucet
   ```

4. **Configure Environment:**
   ```bash
   # Add to your .env file
   SUI_RPC_URL=https://fullnode.testnet.sui.io
   SUI_PRIVATE_KEY=your_private_key_here
   SUI_COMPUTE_PACKAGE_ID=your_package_id_here
   ```

### Secondary Provider: Nosana

**Cost:** ~$0.002/hour ($1.44/month)
**Priority:** 2 (Secondary)
**Setup Time:** 5 minutes

#### Setup Instructions:

1. **Visit Nosana:**
   - Go to [https://nosana.io](https://nosana.io)
   - Create account and get API key

2. **Configure Environment:**
   ```bash
   # Add to your .env file
   NOSANA_API_KEY=your_nosana_api_key_here
   ```

### Secondary Provider: Akash Network

**Cost:** ~$0.0015/hour ($1.08/month)
**Priority:** 3 (Secondary)
**Setup Time:** 15-20 minutes

#### Setup Instructions:

1. **Install Akash CLI:**
   ```bash
   curl -sSfL https://raw.githubusercontent.com/akash-network/node/master/install.sh | bash
   ```

2. **Create Wallet:**
   ```bash
   akash keys add default
   ```

3. **Get Testnet Tokens:**
   ```bash
   akash provider send-liquidity
   ```

4. **Configure Environment:**
   ```bash
   # Add to your .env file
   AKASH_WALLET_ADDRESS=your_akash_wallet_address
   AKASH_PRIVATE_KEY=your_akash_private_key
   ```

### Backup Provider: Flux Network

**Cost:** ~$0.003/hour ($2.16/month)
**Priority:** 4 (Backup)
**Setup Time:** 5 minutes

#### Setup Instructions:

1. **Visit Flux:**
   - Go to [https://runonflux.io](https://runonflux.io)
   - Create account and get API key

2. **Configure Environment:**
   ```bash
   # Add to your .env file
   FLUX_API_KEY=your_flux_api_key_here
   ```

## 🔧 Environment Configuration

### Complete .env Template

```bash
# REDUNDANCY CONFIGURATION
# Configure multiple providers for failover

# Sui Compute Configuration
# Tier: primary, Priority: 1
SUI_RPC_URL=https://fullnode.testnet.sui.io
SUI_PRIVATE_KEY=your_private_key_here
SUI_COMPUTE_PACKAGE_ID=your_package_id_here

# Nosana Configuration
# Tier: secondary, Priority: 2
NOSANA_API_KEY=your_nosana_api_key_here

# Akash Network Configuration
# Tier: secondary, Priority: 3
AKASH_WALLET_ADDRESS=your_akash_wallet_address
AKASH_PRIVATE_KEY=your_akash_private_key

# Flux Network Configuration
# Tier: backup, Priority: 4
FLUX_API_KEY=your_flux_api_key_here

# Redundancy Settings
REDUNDANCY_ENABLED=true
FAILOVER_TIMEOUT=300
HEALTH_CHECK_INTERVAL=60
MAX_FAILOVER_ATTEMPTS=3
```

## 💰 Cost Comparison

| Provider | Tier | Hourly Cost | Monthly Cost | Yearly Cost | Priority |
|----------|------|-------------|--------------|-------------|----------|
| Sui Compute | Primary | $0.001 | $0.72 | $8.64 | 1 |
| Akash Network | Secondary | $0.0015 | $1.08 | $12.96 | 3 |
| Nosana | Secondary | $0.002 | $1.44 | $17.28 | 2 |
| Flux Network | Backup | $0.003 | $2.16 | $25.92 | 4 |

## 🔄 Failover Strategy

### Automatic Failover Logic

1. **Health Check:** Every 60 seconds
2. **Failover Trigger:** 
   - Primary provider down for 5 minutes
   - Response time > 30 seconds
   - Cost exceeds threshold

3. **Failover Sequence:**
   ```
   Primary (Sui) → Secondary (Nosana) → Secondary (Akash) → Backup (Flux)
   ```

4. **Recovery:**
   - Automatic return to primary when healthy
   - Manual override available

### Failover Configuration

```python
# In your deployment script
FAILOVER_CONFIG = {
    "enabled": True,
    "timeout": 300,  # 5 minutes
    "health_check_interval": 60,  # 1 minute
    "max_attempts": 3,
    "providers": [
        {"name": "sui_compute", "priority": 1, "cost_limit": 0.002},
        {"name": "nosana", "priority": 2, "cost_limit": 0.003},
        {"name": "akash", "priority": 3, "cost_limit": 0.0025},
        {"name": "flux", "priority": 4, "cost_limit": 0.004}
    ]
}
```

## 🛠️ Deployment Commands

### Deploy with Redundancy

```bash
# Deploy to best available provider
python deploy_to_depin.py --strategy=best

# Deploy to specific provider
python deploy_to_depin.py --provider=sui_compute

# Deploy with failover enabled
python deploy_to_depin.py --failover=true

# Deploy with cost optimization
python deploy_to_depin.py --optimize=cost
```

### Monitor Deployments

```bash
# Check all provider statuses
python deploy_to_depin.py --status

# Monitor costs
python deploy_to_depin.py --costs

# View failover history
python deploy_to_depin.py --history
```

## 🔍 Testing & Validation

### Test Provider Connectivity

```bash
# Test all providers
python setup_redundancy.py
# Select option 4: Test provider connectivity

# Test specific provider
python -c "
from depin_solutions import DePINManager
import asyncio

async def test():
    manager = DePINManager()
    result = await manager.deploy_to_provider('sui_compute', config)
    print(result)

asyncio.run(test())
"
```

### Validate Configuration

```bash
# Check environment variables
python -c "
import os
from setup_redundancy import RedundancyManager

manager = RedundancyManager()
for name, config in manager.providers.items():
    if config.enabled:
        print(f'{name}: {config.tier.value} (${config.cost_per_hour:.4f}/hour)')
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Provider Connection Failed:**
   ```bash
   # Check API keys and network connectivity
   python setup_redundancy.py --test-connectivity
   ```

2. **High Costs:**
   ```bash
   # Review cost limits and provider selection
   python deploy_to_depin.py --costs --detailed
   ```

3. **Failover Not Working:**
   ```bash
   # Check failover configuration
   python deploy_to_depin.py --check-failover
   ```

### Provider-Specific Issues

#### Sui Compute
- **Issue:** "Package not found"
- **Solution:** Verify `SUI_COMPUTE_PACKAGE_ID` in environment

#### Nosana
- **Issue:** "API key invalid"
- **Solution:** Regenerate API key from Nosana dashboard

#### Akash Network
- **Issue:** "Insufficient balance"
- **Solution:** Get testnet tokens: `akash provider send-liquidity`

#### Flux Network
- **Issue:** "Service unavailable"
- **Solution:** Check Flux network status at runonflux.io

## 📊 Monitoring & Analytics

### Health Dashboard

```bash
# Start monitoring dashboard
python deploy_to_depin.py --monitor

# Export metrics
python deploy_to_depin.py --export-metrics
```

### Cost Tracking

```bash
# Daily cost report
python deploy_to_depin.py --cost-report --period=daily

# Monthly cost analysis
python deploy_to_depin.py --cost-report --period=monthly
```

## 🔐 Security Best Practices

1. **API Key Management:**
   - Use environment variables only
   - Rotate keys regularly
   - Never commit keys to version control

2. **Network Security:**
   - Use HTTPS for all API calls
   - Validate SSL certificates
   - Implement rate limiting

3. **Access Control:**
   - Limit provider permissions
   - Use read-only keys where possible
   - Monitor access logs

## 📞 Support

For issues with specific providers:

- **Sui Compute:** [Sui Discord](https://discord.gg/sui)
- **Nosana:** [Nosana Support](https://nosana.io/support)
- **Akash Network:** [Akash Discord](https://discord.gg/akash)
- **Flux Network:** [Flux Support](https://runonflux.io/support)

---

**Next Steps:**
1. Run `python setup_redundancy.py`
2. Configure your preferred providers
3. Test connectivity
4. Deploy with failover enabled

Happy deploying! 🚀 