#!/usr/bin/env python3
"""
Elizao Agentic Framework for Telegram Manager
=============================================
An autonomous agent system for business development, lead management, and intelligent message processing.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

# Import our existing modules
from google_sheets_integration import GoogleSheetsManager, BusinessBrief, LeadData
from ollama_client import get_ollama_client
from atoma_client import get_atoma_client

class AgentState(Enum):
    """Agent states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    LEARNING = "learning"

class AgentRole(Enum):
    """Agent roles"""
    BUSINESS_ANALYST = "business_analyst"
    LEAD_MANAGER = "lead_manager"
    CONVERSION_SPECIALIST = "conversion_specialist"
    FOLLOW_UP_COORDINATOR = "follow_up_coordinator"
    INSIGHT_GENERATOR = "insight_generator"

@dataclass
class AgentMemory:
    """Agent memory for learning and context"""
    recent_actions: List[Dict[str, Any]]
    learned_patterns: Dict[str, Any]
    performance_metrics: Dict[str, float]
    context_window: List[Dict[str, Any]]
    last_updated: str

@dataclass
class AgentTask:
    """Task for agents to execute"""
    id: str
    type: str
    priority: int
    description: str
    data: Dict[str, Any]
    deadline: Optional[str]
    assigned_agent: Optional[str]
    status: str
    created_at: str

class BaseAgent(ABC):
    """Base agent class following Elizao principles"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.state = AgentState.IDLE
        self.memory = AgentMemory(
            recent_actions=[],
            learned_patterns={},
            performance_metrics={},
            context_window=[],
            last_updated=datetime.now().isoformat()
        )
        self.ai_client = None
        self.sheets_manager = None
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        self._initialize_dependencies()
    
    def _initialize_dependencies(self):
        """Initialize AI and sheets dependencies"""
        try:
            ai_backend = os.getenv("AI_BACKEND", "ollama").lower()
            if ai_backend == "atoma":
                self.ai_client = get_atoma_client()
            else:
                self.ai_client = get_ollama_client()
            
            self.sheets_manager = GoogleSheetsManager()
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
    
    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent thinking process"""
        pass
    
    @abstractmethod
    async def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Agent action process"""
        pass
    
    @abstractmethod
    async def observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Agent observation and learning"""
        pass
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a complete task cycle"""
        try:
            self.state = AgentState.THINKING
            self.logger.info(f"Agent {self.agent_id} thinking about task {task.id}")
            
            # Think phase
            thoughts = await self.think({
                'task': asdict(task),
                'memory': asdict(self.memory),
                'context': self.memory.context_window[-10:] if self.memory.context_window else []
            })
            
            self.state = AgentState.ACTING
            self.logger.info(f"Agent {self.agent_id} acting on task {task.id}")
            
            # Act phase
            result = await self.act(thoughts)
            
            self.state = AgentState.OBSERVING
            self.logger.info(f"Agent {self.agent_id} observing results of task {task.id}")
            
            # Observe and learn phase
            learning = await self.observe(result)
            
            # Update memory
            self._update_memory(task, thoughts, result, learning)
            
            self.state = AgentState.IDLE
            return {
                'task_id': task.id,
                'agent_id': self.agent_id,
                'thoughts': thoughts,
                'actions': result,
                'learning': learning,
                'success': result.get('success', False)
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.state = AgentState.IDLE
            return {'error': str(e), 'success': False}
    
    def _update_memory(self, task: AgentTask, thoughts: Dict, result: Dict, learning: Dict):
        """Update agent memory"""
        # Add to recent actions
        self.memory.recent_actions.append({
            'task_id': task.id,
            'thoughts': thoughts,
            'result': result,
            'learning': learning,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 actions
        if len(self.memory.recent_actions) > 50:
            self.memory.recent_actions = self.memory.recent_actions[-50:]
        
        # Update learned patterns
        if learning.get('patterns'):
            self.memory.learned_patterns.update(learning['patterns'])
        
        # Update performance metrics
        if learning.get('metrics'):
            self.memory.performance_metrics.update(learning['metrics'])
        
        # Update context window
        self.memory.context_window.append({
            'task': asdict(task),
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 context items
        if len(self.memory.context_window) > 20:
            self.memory.context_window = self.memory.context_window[-20:]
        
        self.memory.last_updated = datetime.now().isoformat()

class BusinessAnalystAgent(BaseAgent):
    """Agent specialized in business analysis and insights"""
    
    def __init__(self):
        super().__init__("business_analyst_001", AgentRole.BUSINESS_ANALYST)
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business context and generate insights"""
        try:
            task = context['task']
            messages = task['data'].get('messages', [])
            
            if not messages:
                return {'insights': [], 'recommendations': [], 'confidence': 0.0}
            
            # Prepare analysis prompt
            prompt = f"""
As a senior business analyst, analyze these messages for business opportunities, risks, and actionable insights.

Messages: {json.dumps(messages[:20], indent=2)}

Provide:
1. Key business insights (3-5 points)
2. Risk assessment
3. Opportunity identification
4. Strategic recommendations
5. Priority actions

Format as JSON with keys: insights, risks, opportunities, recommendations, priorities
"""
            
            response = self.ai_client.chat_completions_create(
                messages=[
                    {"role": "system", "content": "You are a senior business analyst providing strategic insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message["content"])
            return analysis
            
        except Exception as e:
            self.logger.error(f"Thinking failed: {e}")
            return {'error': str(e)}
    
    async def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Create business briefs and update sheets"""
        try:
            if 'error' in thoughts:
                return {'success': False, 'error': thoughts['error']}
            
            # Create business brief
            brief = BusinessBrief(
                chat_title=thoughts.get('chat_title', 'Unknown'),
                chat_type=thoughts.get('chat_type', 'Unknown'),
                date=datetime.now().isoformat(),
                executive_brief=thoughts.get('executive_summary', ''),
                key_insights=json.dumps(thoughts.get('insights', [])),
                conversion_opportunities=json.dumps(thoughts.get('opportunities', [])),
                actionable_recommendations=json.dumps(thoughts.get('recommendations', [])),
                next_steps=json.dumps(thoughts.get('priorities', [])),
                priority='High' if thoughts.get('confidence', 0) > 0.7 else 'Medium',
                status='Active'
            )
            
            # Add to sheets
            success = self.sheets_manager.add_business_brief(brief)
            
            return {
                'success': success,
                'brief_created': asdict(brief),
                'actions_taken': ['business_brief_created', 'sheets_updated']
            }
            
        except Exception as e:
            self.logger.error(f"Action failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from results and update patterns"""
        try:
            success = result.get('success', False)
            
            # Update performance metrics
            metrics = {
                'briefs_created': 1 if success else 0,
                'success_rate': 1.0 if success else 0.0,
                'last_action': datetime.now().isoformat()
            }
            
            # Learn patterns
            patterns = {
                'high_priority_indicators': ['urgent', 'deadline', 'opportunity'],
                'conversion_triggers': ['interested', 'proposal', 'meeting'],
                'risk_indicators': ['concern', 'issue', 'problem']
            }
            
            return {
                'metrics': metrics,
                'patterns': patterns,
                'learning': 'Business analysis completed successfully' if success else 'Analysis failed'
            }
            
        except Exception as e:
            self.logger.error(f"Observation failed: {e}")
            return {'error': str(e)}

class LeadManagerAgent(BaseAgent):
    """Agent specialized in lead management and follow-ups"""
    
    def __init__(self):
        super().__init__("lead_manager_001", AgentRole.LEAD_MANAGER)
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze lead data and determine follow-up actions"""
        try:
            # Get pending follow-ups
            pending_leads = self.sheets_manager.get_pending_follow_ups()
            
            if not pending_leads:
                return {'leads_to_follow_up': [], 'recommendations': []}
            
            # Analyze each lead
            analysis = []
            for lead in pending_leads:
                lead_analysis = {
                    'chat_title': lead.get('Chat Title', ''),
                    'contact_name': lead.get('Contact Name', ''),
                    'status': lead.get('Status', ''),
                    'priority': 'High' if 'urgent' in lead.get('Notes', '').lower() else 'Medium',
                    'recommended_action': self._determine_follow_up_action(lead)
                }
                analysis.append(lead_analysis)
            
            return {
                'leads_to_follow_up': analysis,
                'total_pending': len(pending_leads),
                'high_priority_count': len([l for l in analysis if l['priority'] == 'High'])
            }
            
        except Exception as e:
            self.logger.error(f"Lead analysis failed: {e}")
            return {'error': str(e)}
    
    def _determine_follow_up_action(self, lead: Dict[str, Any]) -> str:
        """Determine the best follow-up action for a lead"""
        status = lead.get('Status', '').lower()
        notes = lead.get('Notes', '').lower()
        
        if 'new' in status:
            return 'Initial outreach'
        elif 'contacted' in status:
            return 'Follow-up call'
        elif 'proposal' in notes:
            return 'Proposal follow-up'
        elif 'meeting' in notes:
            return 'Meeting scheduling'
        else:
            return 'General follow-up'
    
    async def act(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lead management actions"""
        try:
            if 'error' in thoughts:
                return {'success': False, 'error': thoughts['error']}
            
            actions_taken = []
            leads_processed = 0
            
            for lead in thoughts.get('leads_to_follow_up', []):
                # Update lead status
                success = self.sheets_manager.update_lead_status(
                    lead['chat_title'],
                    'Follow-up Scheduled',
                    f"Auto-scheduled {lead['recommended_action']} for {datetime.now().strftime('%Y-%m-%d')}"
                )
                
                if success:
                    leads_processed += 1
                    actions_taken.append(f"Updated {lead['contact_name']}")
            
            return {
                'success': True,
                'leads_processed': leads_processed,
                'actions_taken': actions_taken
            }
            
        except Exception as e:
            self.logger.error(f"Lead management action failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from lead management results"""
        try:
            success = result.get('success', False)
            leads_processed = result.get('leads_processed', 0)
            
            metrics = {
                'leads_processed': leads_processed,
                'success_rate': 1.0 if success else 0.0,
                'last_follow_up_batch': datetime.now().isoformat()
            }
            
            patterns = {
                'follow_up_frequency': 'daily',
                'high_priority_threshold': 0.7,
                'auto_scheduling_enabled': True
            }
            
            return {
                'metrics': metrics,
                'patterns': patterns,
                'learning': f'Processed {leads_processed} leads successfully' if success else 'Lead processing failed'
            }
            
        except Exception as e:
            self.logger.error(f"Lead observation failed: {e}")
            return {'error': str(e)}

class AgentOrchestrator:
    """Orchestrates multiple agents for complex tasks"""
    
    def __init__(self):
        self.agents = {
            AgentRole.BUSINESS_ANALYST: BusinessAnalystAgent(),
            AgentRole.LEAD_MANAGER: LeadManagerAgent()
        }
        self.task_queue = []
        self.logger = logging.getLogger("agent_orchestrator")
    
    async def add_task(self, task: AgentTask):
        """Add a task to the queue"""
        self.task_queue.append(task)
        self.logger.info(f"Added task {task.id} to queue")
    
    async def process_tasks(self):
        """Process all tasks in the queue"""
        while self.task_queue:
            task = self.task_queue.pop(0)
            
            # Determine which agent should handle the task
            agent = self._select_agent_for_task(task)
            
            if agent:
                result = await agent.execute_task(task)
                self.logger.info(f"Task {task.id} completed by {agent.agent_id}")
            else:
                self.logger.warning(f"No agent available for task {task.id}")
    
    def _select_agent_for_task(self, task: AgentTask) -> Optional[BaseAgent]:
        """Select the appropriate agent for a task"""
        task_type = task.type.lower()
        
        if 'analysis' in task_type or 'brief' in task_type:
            return self.agents[AgentRole.BUSINESS_ANALYST]
        elif 'lead' in task_type or 'follow' in task_type:
            return self.agents[AgentRole.LEAD_MANAGER]
        else:
            return self.agents[AgentRole.BUSINESS_ANALYST]  # Default
    
    async def run_continuous_cycle(self, interval_seconds: int = 300):
        """Run continuous agent cycles"""
        self.logger.info("Starting continuous agent cycle")
        
        while True:
            try:
                await self.process_tasks()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Agent cycle failed: {e}")
                await asyncio.sleep(60)  # Wait before retrying

def main():
    """Test the agentic framework"""
    logging.basicConfig(level=logging.INFO)
    
    async def test_agents():
        orchestrator = AgentOrchestrator()
        
        # Create test tasks
        test_task = AgentTask(
            id="test_001",
            type="business_analysis",
            priority=1,
            description="Analyze recent messages for business opportunities",
            data={'messages': [{'text': 'We need to discuss the proposal', 'sender': 'Client'}]},
            deadline=None,
            assigned_agent=None,
            status="pending",
            created_at=datetime.now().isoformat()
        )
        
        await orchestrator.add_task(test_task)
        await orchestrator.process_tasks()
    
    asyncio.run(test_agents())

if __name__ == "__main__":
    main() 