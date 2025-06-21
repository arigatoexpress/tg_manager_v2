#!/usr/bin/env python3
"""
Deploy Telegram Manager to DePIN Networks
=========================================
Comprehensive deployment script with Google Sheets integration and agentic framework.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from depin_solutions import DePINManager, create_telegram_bot_deployment, DePINProvider
from google_sheets_integration import GoogleSheetsManager
from elizao_agentic_framework import AgentOrchestrator

# Load environment variables
load_dotenv()

class TelegramManagerDeployer:
    """Comprehensive deployment manager for Telegram Manager"""
    
    def __init__(self):
        self.depin_manager = DePINManager()
        self.sheets_manager = None
        self.agent_orchestrator = None
        self.logger = logging.getLogger("deployer")
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, os.getenv("AGENT_LOG_LEVEL", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def initialize_services(self):
        """Initialize all services"""
        self.logger.info("🚀 Initializing Telegram Manager services...")
        
        # Initialize Google Sheets
        try:
            self.sheets_manager = GoogleSheetsManager()
            self.logger.info("✅ Google Sheets initialized")
        except Exception as e:
            self.logger.warning(f"⚠️  Google Sheets not available: {e}")
        
        # Initialize Agentic Framework
        try:
            if os.getenv("AGENT_ENABLED", "true").lower() == "true":
                self.agent_orchestrator = AgentOrchestrator()
                self.logger.info("✅ Agentic framework initialized")
            else:
                self.logger.info("ℹ️  Agentic framework disabled")
        except Exception as e:
            self.logger.warning(f"⚠️  Agentic framework not available: {e}")
        
        # Check DePIN providers
        available_providers = self.depin_manager.get_available_providers()
        if available_providers:
            self.logger.info(f"✅ DePIN providers available: {available_providers}")
        else:
            self.logger.warning("⚠️  No DePIN providers configured")
    
    async def deploy_to_depin(self, provider_name: str = None) -> dict:
        """Deploy to DePIN network"""
        self.logger.info("🌐 Deploying to DePIN network...")
        
        # Create deployment configuration
        config = create_telegram_bot_deployment()
        
        if provider_name:
            # Deploy to specific provider
            try:
                provider = DePINProvider(provider_name)
                result = await self.depin_manager.deploy_to_provider(provider, config)
            except ValueError:
                return {"success": False, "error": f"Unknown provider: {provider_name}"}
        else:
            # Deploy to best available provider
            result = await self.depin_manager.deploy_to_best_provider(config)
        
        if result.get("success"):
            self.logger.info(f"✅ Deployed to {result.get('provider')}")
            self.logger.info(f"💰 Estimated cost: ${result.get('estimated_cost_per_hour', 0):.4f}/hour")
            
            # Log deployment to Google Sheets if available
            if self.sheets_manager:
                await self._log_deployment_to_sheets(result)
        else:
            self.logger.error(f"❌ Deployment failed: {result.get('error')}")
        
        return result
    
    async def _log_deployment_to_sheets(self, deployment_result: dict):
        """Log deployment information to Google Sheets"""
        try:
            # Create deployment log entry
            deployment_data = {
                'date': datetime.now().isoformat(),
                'provider': deployment_result.get('provider', 'unknown'),
                'deployment_id': deployment_result.get('deployment_id', 'unknown'),
                'status': deployment_result.get('status', 'unknown'),
                'cost_per_hour': deployment_result.get('estimated_cost_per_hour', 0),
                'notes': f"Deployed via {deployment_result.get('provider')}",
                'last_updated': datetime.now().isoformat()
            }
            
            # Add to analytics sheet
            self.sheets_manager.export_message_analytics([deployment_data])
            self.logger.info("✅ Deployment logged to Google Sheets")
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to log deployment to sheets: {e}")
    
    async def start_agentic_framework(self):
        """Start the agentic framework"""
        if not self.agent_orchestrator:
            self.logger.warning("⚠️  Agentic framework not available")
            return
        
        self.logger.info("🤖 Starting agentic framework...")
        
        # Get cycle interval
        interval = int(os.getenv("AGENT_CYCLE_INTERVAL", "300"))
        
        # Start continuous cycle
        try:
            await self.agent_orchestrator.run_continuous_cycle(interval)
        except KeyboardInterrupt:
            self.logger.info("👋 Agentic framework stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Agentic framework failed: {e}")
    
    async def run_local_with_agents(self):
        """Run locally with agentic framework"""
        self.logger.info("🏠 Running locally with agentic framework...")
        
        if self.agent_orchestrator:
            # Start agents in background
            agent_task = asyncio.create_task(self.start_agentic_framework())
            
            # Start the main bot
            from telegram_manager_bot_unified import main as bot_main
            bot_task = asyncio.create_task(bot_main())
            
            # Wait for either to complete
            done, pending = await asyncio.wait(
                [agent_task, bot_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
        else:
            self.logger.warning("⚠️  Agentic framework not available, running bot only")
            from telegram_manager_bot_unified import main as bot_main
            await bot_main()
    
    def show_deployment_options(self):
        """Show available deployment options"""
        print("\n🚀 TELEGRAM MANAGER DEPLOYMENT OPTIONS")
        print("=" * 50)
        
        # DePIN providers
        available_providers = self.depin_manager.get_available_providers()
        costs = self.depin_manager.get_provider_costs()
        
        print("\n🌐 DePIN Providers:")
        if available_providers:
            for provider in available_providers:
                cost = costs.get(provider, 0)
                print(f"  • {provider.upper()}: ${cost:.4f}/hour")
        else:
            print("  ⚠️  No DePIN providers configured")
        
        print("\n📊 Available Services:")
        print("  • Google Sheets Integration: ✅" if self.sheets_manager else "  • Google Sheets Integration: ❌")
        print("  • Agentic Framework: ✅" if self.agent_orchestrator else "  • Agentic Framework: ❌")
        
        print("\n🎯 Deployment Options:")
        print("  1. Deploy to DePIN (24/7 cloud)")
        print("  2. Run locally with agents")
        print("  3. Run locally without agents")
        print("  4. Show provider costs")
        print("  5. Exit")

async def main():
    """Main deployment function"""
    deployer = TelegramManagerDeployer()
    
    # Initialize services
    await deployer.initialize_services()
    
    # Show options
    deployer.show_deployment_options()
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                # Deploy to DePIN
                provider = input("Enter provider name (or press Enter for best provider): ").strip()
                if not provider:
                    provider = None
                
                result = await deployer.deploy_to_depin(provider)
                if result.get("success"):
                    print(f"\n🎉 Successfully deployed to {result.get('provider')}!")
                    print(f"💰 Cost: ${result.get('estimated_cost_per_hour', 0):.4f}/hour")
                    print(f"🆔 Deployment ID: {result.get('deployment_id')}")
                else:
                    print(f"\n❌ Deployment failed: {result.get('error')}")
            
            elif choice == "2":
                # Run locally with agents
                print("\n🏠 Starting local deployment with agents...")
                await deployer.run_local_with_agents()
                break
            
            elif choice == "3":
                # Run locally without agents
                print("\n🏠 Starting local deployment...")
                from telegram_manager_bot_unified import main as bot_main
                await bot_main()
                break
            
            elif choice == "4":
                # Show costs
                costs = deployer.depin_manager.get_provider_costs()
                print("\n💰 Provider Costs (per hour):")
                for provider, cost in costs.items():
                    print(f"  • {provider.upper()}: ${cost:.4f}")
                print(f"\n📅 Monthly estimates (24/7):")
                for provider, cost in costs.items():
                    monthly = cost * 24 * 30
                    print(f"  • {provider.upper()}: ${monthly:.2f}")
            
            elif choice == "5":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 Deployment interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 