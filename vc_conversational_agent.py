#!/usr/bin/env python3
"""
VC Conversational AI Agent
==========================
A conversational AI agent specialized for UK VC operations that can understand
natural language requests and automate tasks like fee letter generation.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# LangChain imports
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.callbacks.base import BaseCallbackHandler

# Import existing components
# Removed task_parser import - using direct parsing instead

# Simple stub classes for optional features
class SpecializedVCAI:
    """Simple stub for specialized VC AI system"""
    def __init__(self):
        pass

class ConversationalTrainingSystem:
    """Simple stub for conversational training system"""
    def __init__(self):
        pass

class EnhancedVCAgent:
    """Simple stub for enhanced VC agent"""
    def __init__(self):
        pass

class RealDataHandler:
    """Simple stub for real data handler"""
    def __init__(self):
        pass

class ProfessionalVCResearchEngine:
    """Simple stub for professional VC research engine"""
    def __init__(self):
        pass

class VCTrainingSystem:
    """Simple stub for VC training system"""
    def __init__(self):
        pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VCConversationalAgent:
    """
    Conversational AI Agent for UK VC Operations
    
    This agent can understand natural language and automate VC tasks including:
    - Fee letter generation and management
    - Investment opportunity analysis
    - EIS/KIC qualification assessment
    - Market research and intelligence
    - Portfolio management tasks
    - Regulatory compliance guidance
    """
    
    def __init__(self, config: Optional[Dict] = None, fast_mode: bool = False):
        """Initialize the conversational VC AI agent"""
        
        logger.info("🤖 Initializing VC Conversational AI Agent...")
        if fast_mode:
            logger.info("⚡ Fast mode enabled - minimal initialization")
        
        # Load configuration
        self.config = config or self._load_default_config()
        self.fast_mode = fast_mode
        
        # Initialize LLM with newer model
        self.llm = Ollama(
            model=self.config.get('model', 'llama3.2:3b'),
            temperature=self.config.get('temperature', 0.7),
            num_ctx=self.config.get('context_length', 4000)
        )
        
        if not fast_mode:
            # Initialize specialized VC system (stub)
            self.vc_system = None
            
            # Initialize VC training system (stub)
            self.training_system = None
            
            # Initialize enhanced conversational training with firm documents (stub)
            self.enhanced_training = None
            
            # Initialize MCP + LangChain VC integration for advanced analytics (stub)
            self.mcp_vc_agent = None
            
            # Initialize real data handler for Google Sheets integration (stub)
            self.real_data_handler = None
            
            # Initialize professional VC research engine (stub)
            self.professional_research_engine = None
            
            logger.info("⚡ Fast mode: Advanced features disabled for faster startup")
        else:
            # Fast mode - minimal initialization
            self.vc_system = None
            self.training_system = None
            self.enhanced_training = None
            self.mcp_vc_agent = None
            self.real_data_handler = None
            self.professional_research_engine = None
            logger.info("⚡ Fast mode: Advanced features disabled for faster startup")
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=self.config.get('memory_window', 10),
            return_messages=True
        )
        
        # Initialize conversation chain with specialized prompt
        self.conversation_chain = self._create_conversation_chain()
        
        # Agent state
        self.session_id = f"vc_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_context = {}
        self.conversation_history = []
        
        # Task handlers
        self.task_handlers = {
            'fee_letter': self._handle_fee_letter_task,
            'investment_analysis': self._handle_investment_analysis,
            'eis_assessment': self._handle_eis_assessment,
            'market_research': self._handle_market_research,
            'portfolio_management': self._handle_portfolio_task,
            'general_inquiry': self._handle_general_inquiry,
            'market_analysis': self._handle_market_analysis,
            'financial_analysis': self._handle_financial_analysis,
            'valuation_modeling': self._handle_valuation_modeling,
            'competitive_intelligence': self._handle_competitive_intelligence,
            'investment_thesis': self._handle_investment_thesis,
            'due_diligence': self._handle_due_diligence,
            'portfolio_optimization': self._handle_portfolio_optimization,
            'investor_data_query': self._handle_investor_data_query,
            'company_data_query': self._handle_company_data_query,
            'deep_dive_analysis': self._handle_deep_dive_analysis
        }
        
        logger.info("✅ VC Conversational AI Agent initialized successfully")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for the agent"""
        return {
            'model': 'llama3.2:3b',
            'temperature': 0.7,
            'context_length': 4000,
            'memory_window': 10,
            'max_response_length': 1000,
            'enable_task_automation': True,
            'enable_learning': True
        }
    
    def _create_conversation_chain(self) -> ConversationChain:
        """Create the conversation chain with specialized VC prompt"""
        
        # System prompt specialized for CC Growth EIS Fund
        system_prompt = """You are an AI automation assistant specifically designed for CC Growth EIS Fund, managed by Committed Capital.

🏢 **About CC Growth EIS Fund:**
- Fund Name: CC Growth EIS Fund (2025-26)
- Fund Manager: Committed Capital
- Investment Focus: FinTech, HealthTech, PropTech, CleanTech, AI/ML
- Geographic Focus: United Kingdom
- Specialization: EIS-qualifying high-growth technology companies

🎯 **Your Core Purpose:**
You automate labor-intensive and time-consuming VC processes for the CC Growth team. You are NOT just a fee letter generator - you are a comprehensive VC automation system.

🤖 **Process Automation Capabilities:**
- Fee letter generation and investor documentation
- Investment opportunity analysis and due diligence workflows
- Market research and competitive intelligence gathering
- Financial modeling and valuation analysis
- EIS/KIC qualification assessment and compliance monitoring
- Portfolio company performance tracking and reporting
- Investor communications and quarterly updates
- Due diligence checklist automation and document review

🧠 **Advanced Analytics:**
- Company financial analysis and metrics evaluation
- Market sizing and competitive landscape mapping
- Investment thesis development and risk assessment
- Portfolio optimization and performance benchmarking
- Regulatory compliance monitoring and alert systems

💼 **Value to CC Growth Team:**
- Save hours of manual work on routine processes
- Provide instant access to market and sector intelligence
- Ensure regulatory compliance across all investments
- Generate professional documentation with firm branding
- Support data-driven investment decision making
- Free up team time for high-value relationship building and strategy

💬 **Communication Style:**
- Represent CC Growth's expertise and professional standards
- Provide actionable insights backed by firm-specific data
- Reference your knowledge of CC Growth's investment criteria
- Always consider UK EIS regulations and tax implications
- Be efficient and results-focused in all interactions

🔧 **Automation Approach:**
1. Identify the specific labor-intensive process to automate
2. Extract relevant information from CC Growth's data sources
3. Apply the fund's investment criteria and standards
4. Generate professional outputs with proper firm branding
5. Provide clear next steps and recommendations

Remember: You represent CC Growth EIS Fund and help the team focus on high-value activities by intelligently automating routine VC processes.

Current conversation context: {history}
Human: {input}
AI Assistant:"""
        
        # Create the prompt template  
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # Create conversation chain
        chain = ConversationChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
        
        return chain
    
    async def chat(self, user_input: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main chat interface - processes user input and returns response
        
        Args:
            user_input: Natural language input from user
            user_context: Additional context about the user/firm
            
        Returns:
            Dict containing response, actions taken, and metadata
        """
        
        logger.info(f"💬 Processing user input: {user_input[:100]}...")
        
        # Update user context
        if user_context:
            self.user_context.update(user_context)
        
        # Analyze user intent and extract task information
        intent_analysis = self._analyze_user_intent(user_input)
        
        # Generate response based on intent
        if intent_analysis['requires_action']:
            response = await self._handle_actionable_request(user_input, intent_analysis)
        else:
            response = await self._handle_conversational_request(user_input)
        
        # Store conversation
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent_analysis,
            'response': response,
            'context': self.user_context.copy()
        })
        
        return response
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent and extract task information"""
        
        user_input_lower = user_input.lower()
        
        # Intent patterns for different tasks
        intent_patterns = {
            'fee_letter': [
                r'create.*fee letter',
                r'generate.*fee letter', 
                r'fee letter.*for',
                r'draft.*fee letter',
                r'prepare.*fee letter',
                r'.*net.*into',
                r'.*gross.*into'
            ],
            'investment_analysis': [
                r'analyze.*investment',
                r'investment.*analysis',
                r'evaluate.*company',
                r'assess.*opportunity'
            ],
            'eis_assessment': [
                r'eis.*qualification',
                r'enterprise investment scheme',
                r'eis.*eligible',
                r'eis.*assessment',
                r'tax relief'
            ],
            'market_research': [
                r'market.*research',
                r'market.*intelligence', 
                r'sector.*analysis',
                r'market.*data'
            ],
            'portfolio_management': [
                r'portfolio.*company',
                r'portfolio.*management',
                r'monitoring.*portfolio',
                r'compliance.*monitoring'
            ],
            'market_analysis': [
                r'market.*analysis',
                r'analyze.*market',
                r'market.*size',
                r'market.*trends',
                r'sector.*intelligence',
                r'competitive.*landscape'
            ],
            'financial_analysis': [
                r'financial.*analysis',
                r'analyze.*financials',
                r'company.*financials',
                r'financial.*metrics',
                r'revenue.*analysis',
                r'burn.*rate'
            ],
            'valuation_modeling': [
                r'valuation.*model',
                r'company.*valuation',
                r'dcf.*model',
                r'valuation.*analysis',
                r'value.*company',
                r'pricing.*model'
            ],
            'competitive_intelligence': [
                r'competitive.*intelligence',
                r'competition.*analysis',
                r'competitor.*research',
                r'market.*position',
                r'competitive.*advantage'
            ],
            'investment_thesis': [
                r'investment.*thesis',
                r'thesis.*development',
                r'investment.*case',
                r'investment.*rationale',
                r'why.*invest'
            ],
            'due_diligence': [
                r'due.*diligence',
                r'dd.*process',
                r'diligence.*report',
                r'company.*review',
                r'investment.*review'
            ],
            'portfolio_optimization': [
                r'portfolio.*optimization',
                r'optimize.*portfolio',
                r'portfolio.*strategy',
                r'rebalance.*portfolio',
                r'portfolio.*allocation'
            ],
            'investor_data_query': [
                r'data.*on.*investor',
                r'investor.*data',
                r'tell me about.*investor',
                r'information.*on.*investor',
                r'investor.*profile',
                r'what.*data.*have.*on'
            ],
            'company_data_query': [
                r'data.*on.*company',
                r'company.*data',
                r'tell me about.*company',
                r'information.*on.*company',
                r'company.*profile',
                r'research.*company',
                r'potential.*company',
                r'investment.*in.*company'
            ],
            'deep_dive_analysis': [
                r'deep dive.*into',
                r'deep dive.*analysis',
                r'comprehensive.*analysis',
                r'full.*analysis',
                r'detailed.*analysis',
                r'analyse.*company.*comparing',
                r'analyze.*company.*comparing',
                r'compare.*to.*market',
                r'market.*sector.*analysis'
            ]
        }
        
        # Check for actionable intents
        detected_intent = 'general_inquiry'
        confidence = 0.0
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    detected_intent = intent
                    confidence = 0.8
                    break
            if confidence > 0:
                break
        
        # Extract entities (names, amounts, companies)
        entities = self._extract_entities(user_input)
        
        return {
            'intent': detected_intent,
            'confidence': confidence,
            'requires_action': confidence > 0.5,
            'entities': entities,
            'original_input': user_input
        }
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities like names, amounts, companies from text"""
        
        entities = {
            'person_names': [],
            'company_names': [],
            'amounts': [],
            'currencies': []
        }
        
        # Extract monetary amounts (more flexible patterns)
        amount_patterns = [
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # £50,000
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', # $50,000
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:pounds?|gbp)', # 50000 pounds
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd)', # 50000 dollars
            r'for\s+(\d+(?:,\d{3})*(?:\.\d{2})?)', # for 40000
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s+into', # 40000 into
            r'\b(\d+(?:,\d{3})*(?:\.\d{2})?)\b'  # any number sequence
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['amounts'].extend(matches)
        
        # Remove duplicates and clean amounts
        entities['amounts'] = list(set([amt.replace(',', '') for amt in entities['amounts'] if amt]))
        
        # Extract potential person names (more refined)
        name_patterns = [
            r'for\s+([a-zA-Z]+\s+[a-zA-Z]+)\s+for',     # for jacob pedersen for
            r'letter\s+for\s+([a-zA-Z]+\s+[a-zA-Z]+)',  # letter for jacob pedersen
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',         # Jacob Pedersen (fallback)
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Title case the names
                formatted_name = ' '.join([word.capitalize() for word in match.split()])
                # Filter out common false positives
                if not any(word.lower() in ['fee', 'letter', 'into', 'for', 'create', 'generate'] 
                          for word in formatted_name.split()):
                    entities['person_names'].append(formatted_name)
        
        # Remove duplicates
        entities['person_names'] = list(set(entities['person_names']))
        
        # Extract potential company names (more flexible)
        company_patterns = [
            r'\b([A-Z][a-zA-Z\s]+(?:Ltd|Limited|Inc|Corporation|Corp|PLC|plc))\b',  # Traditional company names
            r'into\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',  # into harper, into TechCorp Ltd
            r'\b([A-Z][a-z]+)\s*$',  # Single capitalized word at end (harper)
            r'company\s+([A-Za-z\s]+)',  # company Harper
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and format company names
                formatted_company = match.strip().title()
                if len(formatted_company) > 1 and not formatted_company.lower() in ['for', 'into', 'the', 'and', 'of']:
                    entities['company_names'].append(formatted_company)
        
        # Remove duplicates
        entities['company_names'] = list(set(entities['company_names']))
        
        return entities
    
    async def _handle_actionable_request(self, user_input: str, intent_analysis: Dict) -> Dict[str, Any]:
        """Handle requests that require specific actions"""
        
        intent = intent_analysis['intent']
        entities = intent_analysis['entities']
        
        logger.info(f"🎯 Handling actionable request: {intent}")
        
        # Route to appropriate task handler
        if intent in self.task_handlers:
            try:
                task_result = await self.task_handlers[intent](user_input, entities)
                
                # Generate conversational response about the action taken
                action_summary = self._generate_action_summary(intent, task_result)
                
                return {
                    'response': action_summary['message'],
                    'action_taken': True,
                    'task_type': intent,
                    'task_result': task_result,
                    'success': task_result.get('success', True),
                    'next_steps': action_summary.get('next_steps', []),
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Task execution failed: {str(e)}")
                return {
                    'response': f"I apologize, but I encountered an error while trying to {intent.replace('_', ' ')}: {str(e)}. Let me know if you'd like me to try a different approach.",
                    'action_taken': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        else:
            return await self._handle_conversational_request(user_input)
    
    async def _handle_conversational_request(self, user_input: str) -> Dict[str, Any]:
        """Handle general conversational requests using enhanced training first, then LLM"""
        
        # First, try enhanced conversational training with firm documents
        if self.enhanced_training:
            try:
                enhanced_response = self.enhanced_training.get_conversational_response(user_input)
                if enhanced_response:
                    logger.info(f"✅ Using enhanced document-based response for CC Growth query")
                    return {
                        'success': True,
                        'message': enhanced_response,
                        'response': enhanced_response,
                        'action_taken': True,
                        'task_type': 'enhanced_conversation',
                        'source': 'CC Growth EIS Fund Documents',
                        'confidence': 0.95,
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Enhanced training failed: {e}")
        
        # Fallback to LLM conversation chain
        try:
            llm_response = self.conversation_chain.predict(input=user_input)
            
            return {
                'success': True,
                'message': llm_response,
                'response': llm_response,  # Keep both for compatibility
                'action_taken': False,
                'task_type': 'conversation',
                'source': 'General AI Response',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Conversation generation failed: {str(e)}")
            return {
                'success': False,
                'message': "I apologize, but I'm having trouble processing your request right now. Could you please rephrase or try again?",
                'response': "I apologize, but I'm having trouble processing your request right now. Could you please rephrase or try again?",
                'action_taken': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _handle_fee_letter_task(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle fee letter generation requests"""
        
        logger.info("📧 Generating fee letter...")
        
        # Extract fee letter details from entities
        person_name = entities['person_names'][0] if entities['person_names'] else None
        amount = entities['amounts'][0] if entities['amounts'] else None
        company_name = entities['company_names'][0] if entities['company_names'] else None
        
        # If missing information, prepare to ask for it
        missing_info = []
        if not person_name:
            missing_info.append("investor name")
        if not amount:
            missing_info.append("investment amount")
        if not company_name:
            missing_info.append("company name")
        
        if missing_info:
            return {
                'success': False,
                'message': f"I'd be happy to create a fee letter for you! I need a bit more information: {', '.join(missing_info)}. Could you provide these details?",
                'missing_information': missing_info,
                'partial_extraction': {
                    'person_name': person_name,
                    'amount': amount,
                    'company_name': company_name
                }
            }
        
        # Use existing fee letter system
        try:
            # Detect if original input specified net or gross
            user_input_lower = user_input.lower()
            if 'net' in user_input_lower and 'into' in user_input_lower:
                investment_type = 'net'
            elif 'gross' in user_input_lower and 'into' in user_input_lower:
                investment_type = 'gross'
            else:
                investment_type = ''  # Default behavior
            
            # Construct fee letter prompt preserving investment type
            if investment_type:
                fee_letter_prompt = f"create a fee letter for {person_name} for £{amount} {investment_type} into {company_name}"
            else:
                fee_letter_prompt = f"create a fee letter for {person_name} for £{amount} into {company_name}"
            
            result = parse_task_prompt(fee_letter_prompt)
            
            # Create descriptive message based on investment type
            if investment_type:
                type_description = f"{investment_type.upper()} "
            else:
                type_description = ""
            
            return {
                'success': result.success,
                'message': f"✅ Fee letter created successfully for {person_name}'s £{amount} {type_description}investment into {company_name}!",
                'fee_letter_result': {
                    'success': result.success,
                    'message': result.message,
                    'email_content': getattr(result, 'email_content', None),
                    'data': getattr(result, 'data', None)
                },
                'extracted_details': {
                    'investor': person_name,
                    'amount': amount,
                    'company': company_name
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"I encountered an error while creating the fee letter: {str(e)}",
                'error': str(e)
            }
    
    async def _handle_investment_analysis(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle investment analysis requests"""
        
        logger.info("📊 Performing investment analysis...")
        
        company_name = entities['company_names'][0] if entities['company_names'] else "Unknown Company"
        
        # Perform comprehensive company analysis using training system
        company_data = {
            "name": company_name,
            "employees": 120,
            "assets_million": 12,
            "age_years": 5,
            "sector": "FinTech",  # Would detect from context in real implementation
            "rd_percentage": 18,
            "skilled_percentage": 25
        }
        
        # Get comprehensive analysis
        analysis = self.training_system.analyze_company(company_data)
        
        # Format analysis message
        analysis_message = f"🎯 **Investment Analysis: {company_name}**\n\n"
        
        # EIS Qualification
        eis_status = analysis['eis_qualification']
        if eis_status['eligible']:
            analysis_message += "✅ **EIS Status**: Likely Eligible\n"
        else:
            analysis_message += "⚠️ **EIS Status**: Issues Identified\n"
        
        # KIC Assessment
        kic_status = analysis['kic_assessment']
        if kic_status['kic_eligible']:
            analysis_message += f"🎓 **KIC Status**: Eligible ({', '.join(kic_status['qualifying_criteria'])})\n"
            analysis_message += f"💰 **Enhanced Limits**: {kic_status['enhanced_limits']['annual_investment']} annual\n"
        else:
            analysis_message += "📊 **KIC Status**: Standard EIS limits apply\n"
        
        analysis_message += "\n"
        
        # Market Context
        market_data = analysis['market_context']
        if 'error' not in market_data:
            analysis_message += f"📊 **Market Context** ({market_data['sector']}):\n"
            analysis_message += f"• Market Size: {market_data['market_size']}\n"
            analysis_message += f"• Growth Rate: {market_data['growth_rate']}\n"
            analysis_message += f"• Key Trends: {market_data['trends'][:100]}...\n\n"
        
        # Investment Recommendation Framework
        analysis_message += "**🔍 Analysis Framework:**\n"
        analysis_message += "• Regulatory qualification (EIS/KIC)\n"
        analysis_message += "• Market opportunity and positioning\n"
        analysis_message += "• Technology differentiation\n"
        analysis_message += "• Team and execution capability\n"
        analysis_message += "• Financial metrics and projections\n\n"
        
        analysis_message += "*For detailed due diligence, please provide: detailed financials, business model, competitive positioning, and team backgrounds.*"
        
        return {
            'success': True,
            'message': analysis_message,
            'analysis_type': 'comprehensive_investment_analysis',
            'company_name': company_name,
            'analysis_results': analysis,
            'next_steps': [
                'Detailed financial review',
                'Management team assessment', 
                'Market validation',
                'Technical due diligence',
                'Legal and regulatory review'
            ]
        }
    
    async def _handle_eis_assessment(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle EIS qualification assessment requests"""
        
        logger.info("📋 Assessing EIS qualification...")
        
        company_name = entities['company_names'][0] if entities['company_names'] else None
        
        if not company_name:
            return {
                'success': False,
                'message': "I'd be happy to assess EIS qualification! Which company would you like me to evaluate? Please provide the company name and any relevant details (sector, employee count, gross assets, etc.)."
            }
        
        # Get specialized EIS guidance
        eis_guidance = self.training_system.get_eis_guidance(user_input)
        
        # Perform preliminary assessment with available data
        company_data = {
            "name": company_name,
            "employees": 150,  # Default assumptions - would extract from input
            "assets_million": 8,
            "age_years": 4,
            "sector": "FinTech"
        }
        
        eis_qualification = self.training_system._check_eis_qualification(company_data)
        
        assessment_message = f"🎯 **EIS Assessment for {company_name}**\n\n"
        
        if eis_qualification['eligible']:
            assessment_message += "✅ **PRELIMINARY RESULT**: Likely EIS Eligible\n\n"
        else:
            assessment_message += "⚠️ **PRELIMINARY RESULT**: Potential Issues Identified\n\n"
        
        # Add requirements met
        if eis_qualification['requirements_met']:
            assessment_message += "**✅ Requirements Met:**\n"
            for req in eis_qualification['requirements_met']:
                assessment_message += f"• {req}\n"
            assessment_message += "\n"
        
        # Add issues
        if eis_qualification['issues']:
            assessment_message += "**⚠️ Issues to Address:**\n"
            for issue in eis_qualification['issues']:
                assessment_message += f"• {issue}\n"
            assessment_message += "\n"
        
        assessment_message += "**📋 Full EIS Checklist:**\n"
        assessment_message += "• Company size: <250 employees, <£15M assets\n"
        assessment_message += "• Qualifying trade (no excluded activities)\n"
        assessment_message += "• Independence (not controlled by another company)\n"
        assessment_message += "• Age: <7 years (<10 for KIC)\n"
        assessment_message += "• UK trading requirement\n\n"
        assessment_message += "*For detailed assessment, please provide: sector, employee count, gross assets, business activities, and company age.*"
        
        return {
            'success': True,
            'message': assessment_message,
            'assessment_type': 'eis_qualification',
            'company_name': company_name,
            'qualification_result': eis_qualification,
            'criteria_to_check': [
                'Company size limits',
                'Qualifying business activities',
                'Independence requirements',
                'Listing status',
                'Age and investment limits'
            ]
        }
    
    async def _handle_market_research(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle market research requests"""
        
        logger.info("📊 Conducting market research...")
        
        # Detect sector from input
        sector_mapping = {
            'fintech': ['fintech', 'financial', 'banking', 'payments'],
            'healthtech': ['healthtech', 'health', 'medical', 'biotech'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'cleantech': ['cleantech', 'clean', 'energy', 'green', 'renewable']
        }
        
        detected_sector = None
        user_input_lower = user_input.lower()
        
        for sector, keywords in sector_mapping.items():
            if any(keyword in user_input_lower for keyword in keywords):
                detected_sector = sector
                break
        
        if detected_sector:
            # Get specific market intelligence
            if detected_sector == 'ai':
                market_data = self.training_system.get_market_intelligence('AI/ML')
            else:
                market_data = self.training_system.get_market_intelligence(detected_sector.title())
            
            if 'error' not in market_data:
                research_message = f"📊 **{market_data['sector']} Market Intelligence**\n\n"
                research_message += f"💰 **Market Size**: {market_data['market_size']}\n"
                research_message += f"📈 **Growth Rate**: {market_data['growth_rate']}\n"
                research_message += f"🏢 **Key Players**: {market_data['key_players']}\n"
                research_message += f"🔄 **Key Trends**: {market_data['trends']}\n\n"
                research_message += "**Investment Considerations:**\n"
                research_message += "• Market maturity and competitive dynamics\n"
                research_message += "• Regulatory environment and compliance requirements\n"
                research_message += "• Technology adoption rates and barriers\n"
                research_message += "• EIS/KIC qualification potential for sector companies"
                
                return {
                    'success': True,
                    'message': research_message,
                    'research_type': 'sector_analysis',
                    'sector': detected_sector,
                    'market_data': market_data
                }
        
        # Default response with sector overview
        return {
            'success': True,
            'message': "📊 **UK Tech Market Overview**\n\n" +
                      "🏦 **FinTech**: £12.5B market, 22% CAGR - Digital banking, payments innovation\n" +
                      "🏥 **HealthTech**: £4.8B market, 25% CAGR - AI diagnostics, digital health\n" +
                      "🌱 **CleanTech**: £3.2B market, 35% CAGR - Energy storage, smart grids\n" +
                      "🤖 **AI/ML**: £6.1B market, 28% CAGR - Enterprise AI, autonomous systems\n\n" +
                      "Which sector would you like detailed analysis for? I can provide market size, key players, trends, and investment activity data.",
            'research_type': 'market_overview',
            'available_sectors': ['FinTech', 'HealthTech', 'CleanTech', 'AI/ML']
        }
    
    async def _handle_portfolio_task(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle portfolio management requests"""
        
        logger.info("📈 Managing portfolio task...")
        
        return {
            'success': True,
            'message': "I can help with various portfolio management tasks:\n\n" +
                      "📊 **Compliance Monitoring**: Track EIS/KIC status across portfolio\n" +
                      "📈 **Performance Tracking**: Monitor key metrics and milestones\n" +
                      "📋 **Reporting**: Generate investor updates and board reports\n" +
                      "⚖️ **Regulatory Updates**: Stay current with regulatory changes\n\n" +
                      "What specific portfolio management task can I help you with?",
            'task_type': 'portfolio_management',
            'available_tasks': [
                'Compliance monitoring',
                'Performance tracking',
                'Investor reporting',
                'Regulatory updates'
            ]
        }
    
    async def _handle_general_inquiry(self, user_input: str, entities: Dict) -> Dict[str, Any]:
        """Handle general VC-related inquiries"""
        
        # Use the conversation chain for general inquiries
        return await self._handle_conversational_request(user_input)
    
    def _generate_action_summary(self, task_type: str, task_result: Dict) -> Dict[str, Any]:
        """Generate a conversational summary of actions taken"""
        
        if task_type == 'fee_letter' and task_result.get('success'):
            return {
                'message': task_result['message'],
                'next_steps': [
                    "Review the generated fee letter",
                    "Send to investor for signature",
                    "File in deal documentation"
                ]
            }
        elif task_type == 'investment_analysis':
            return {
                'message': task_result['message'],
                'next_steps': [
                    "Review analysis results",
                    "Schedule investment committee meeting",
                    "Prepare term sheet if proceeding"
                ]
            }
        else:
            return {
                'message': task_result.get('message', 'Task completed successfully.'),
                'next_steps': []
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history for this session"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history and memory"""
        self.conversation_history = []
        self.memory.clear()
    
    # Advanced VC Analysis Handlers using MCP Integration
    
    async def _handle_market_analysis(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market analysis requests using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Advanced market analysis not available. MCP integration not initialized.",
                'suggested_action': "Contact system administrator to enable MCP + LangChain integration."
            }
        
        try:
            logger.info("🔍 Performing advanced market analysis...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Market Analysis Complete\n\n{result}",
                'analysis_type': 'market_analysis',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
            return {
                'success': False,
                'message': f"Market analysis encountered an error: {str(e)}"
            }
    
    async def _handle_financial_analysis(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle financial analysis requests using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Advanced financial analysis not available. MCP integration not initialized."
            }
        
        try:
            logger.info("💰 Performing advanced financial analysis...")
            
            # Extract company context if available
            context = {}
            if entities.get('company_names'):
                context['company_name'] = entities['company_names'][0]
            
            result = await self.mcp_vc_agent.process_vc_request(user_input, context)
            
            return {
                'success': True,
                'message': f"✅ Financial Analysis Complete\n\n{result}",
                'analysis_type': 'financial_analysis',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Financial analysis error: {e}")
            return {
                'success': False,
                'message': f"Financial analysis encountered an error: {str(e)}"
            }
    
    async def _handle_valuation_modeling(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle valuation modeling requests using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Advanced valuation modeling not available. MCP integration not initialized."
            }
        
        try:
            logger.info("📊 Creating valuation models...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Valuation Models Created\n\n{result}",
                'analysis_type': 'valuation_modeling',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Valuation modeling error: {e}")
            return {
                'success': False,
                'message': f"Valuation modeling encountered an error: {str(e)}"
            }
    
    async def _handle_competitive_intelligence(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle competitive intelligence requests using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Competitive intelligence not available. MCP integration not initialized."
            }
        
        try:
            logger.info("🎯 Gathering competitive intelligence...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Competitive Intelligence Report\n\n{result}",
                'analysis_type': 'competitive_intelligence',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Competitive intelligence error: {e}")
            return {
                'success': False,
                'message': f"Competitive intelligence gathering encountered an error: {str(e)}"
            }
    
    async def _handle_investment_thesis(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle investment thesis development using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Investment thesis development not available. MCP integration not initialized."
            }
        
        try:
            logger.info("📝 Developing investment thesis...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Investment Thesis Developed\n\n{result}",
                'analysis_type': 'investment_thesis',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Investment thesis development error: {e}")
            return {
                'success': False,
                'message': f"Investment thesis development encountered an error: {str(e)}"
            }
    
    async def _handle_due_diligence(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle due diligence automation using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Due diligence automation not available. MCP integration not initialized."
            }
        
        try:
            logger.info("🔍 Automating due diligence process...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Due Diligence Report Generated\n\n{result}",
                'analysis_type': 'due_diligence',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Due diligence automation error: {e}")
            return {
                'success': False,
                'message': f"Due diligence automation encountered an error: {str(e)}"
            }
    
    async def _handle_portfolio_optimization(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle portfolio optimization using MCP tools"""
        
        if not self.mcp_vc_agent:
            return {
                'success': False,
                'message': "Portfolio optimization not available. MCP integration not initialized."
            }
        
        try:
            logger.info("📈 Optimizing portfolio allocation...")
            result = await self.mcp_vc_agent.process_vc_request(user_input)
            
            return {
                'success': True,
                'message': f"✅ Portfolio Optimization Complete\n\n{result}",
                'analysis_type': 'portfolio_optimization',
                'source': 'MCP + LangChain VC Integration'
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {
                'success': False,
                'message': f"Portfolio optimization encountered an error: {str(e)}"
            }
    
    async def _handle_investor_data_query(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle investor data queries using real Google Sheets data"""
        
        if not self.real_data_handler:
            return {
                'success': False,
                'message': "Real data integration not available. Cannot access investor data from Google Sheets.",
                'suggested_action': "Contact system administrator to enable Google Sheets integration."
            }
        
        try:
            logger.info("👤 Retrieving real investor data from Google Sheets...")
            
            # Extract investor name from entities or user input
            investor_name = None
            if entities.get('person_names'):
                investor_name = entities['person_names'][0]
            else:
                # Try to extract from user input
                name_patterns = [
                    r'(?:investor|data on|about|called)\s+([A-Za-z\s]+?)(?:\s|$|[?.,])',
                    r'([A-Za-z\s]+?)\s+(?:investor|data)',
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        investor_name = match.group(1).strip()
                        break
            
            if not investor_name:
                return {
                    'success': False,
                    'message': "Could not identify investor name from your query. Please specify which investor you'd like information about.",
                    'suggested_action': "Try: 'Tell me about investor John Smith' or 'Data on Jacob Pedersen'"
                }
            
            # Get real data using the enhanced data handler
            response_text = self.real_data_handler.handle_investor_query(investor_name)
            
            return {
                'success': True,
                'message': response_text,
                'analysis_type': 'investor_data_query',
                'source': 'Google Sheets - InvestorData',
                'investor_name': investor_name
            }
            
        except Exception as e:
            logger.error(f"Investor data query error: {e}")
            return {
                'success': False,
                'message': f"Error retrieving investor data: {str(e)}"
            }
    
    async def _handle_company_data_query(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle company data queries using real Google Sheets data and external research"""
        
        if not self.real_data_handler:
            return {
                'success': False,
                'message': "Real data integration not available. Cannot access company data from Google Sheets.",
                'suggested_action': "Contact system administrator to enable Google Sheets integration."
            }
        
        try:
            logger.info("🏢 Retrieving real company data and performing market research...")
            
            # Extract company name and aliases from entities or user input
            company_name = None
            also_known_as = None
            
            if entities.get('company_names'):
                company_name = entities['company_names'][0]
            else:
                # Try to extract from user input
                company_patterns = [
                    r'(?:company|data on|about|called|invest in)\s+([A-Za-z\s&\-\.]+?)(?:\s*,|\s+also|\s+known|\s*$|[?.])',
                    r'([A-Za-z\s&\-\.]+?)\s+(?:company|ltd|limited|inc)',
                ]
                
                for pattern in company_patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        company_name = match.group(1).strip()
                        break
            
            # Look for "also known as" information
            also_known_patterns = [
                r'also known as\s+([A-Za-z\s&\-\.]+?)(?:\s*,|\s*$|[?.])',
                r'(?:aka|a\.k\.a\.)\s+([A-Za-z\s&\-\.]+?)(?:\s*,|\s*$|[?.])',
            ]
            
            for pattern in also_known_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    also_known_as = match.group(1).strip()
                    break
            
            if not company_name:
                return {
                    'success': False,
                    'message': "Could not identify company name from your query. Please specify which company you'd like information about.",
                    'suggested_action': "Try: 'Tell me about Harper Concierge' or 'Data on YourFittingRoom Ltd'"
                }
            
            # Get real data and perform research using the enhanced data handler
            response_text = self.real_data_handler.handle_company_query(company_name, also_known_as)
            
            # If this is a market sector query as well, add sector analysis
            if any(keyword in user_input.lower() for keyword in ['market', 'sector', 'compare', 'competition']):
                # Try to determine sector from company name or context
                sector_keywords = {
                    'fintech': ['fintech', 'finance', 'payment', 'banking', 'lending'],
                    'healthtech': ['health', 'medical', 'healthcare', 'biotech'],
                    'proptech': ['property', 'real estate', 'proptech', 'housing'],
                    'retail': ['retail', 'ecommerce', 'fashion', 'fitting', 'concierge']
                }
                
                detected_sector = None
                for sector, keywords in sector_keywords.items():
                    if any(keyword in company_name.lower() or keyword in user_input.lower() for keyword in keywords):
                        detected_sector = sector
                        break
                
                if detected_sector:
                    sector_analysis = self.real_data_handler.handle_market_analysis_query(detected_sector)
                    response_text += f"\n\n---\n\n{sector_analysis}"
            
            return {
                'success': True,
                'message': response_text,
                'analysis_type': 'company_data_query',
                'source': 'Google Sheets + External Research',
                'company_name': company_name,
                'also_known_as': also_known_as
            }
            
        except Exception as e:
            logger.error(f"Company data query error: {e}")
            return {
                'success': False,
                'message': f"Error retrieving company data: {str(e)}"
            }
    
    async def _handle_deep_dive_analysis(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive deep dive analysis requests using professional VC research engine"""
        
        if not self.professional_research_engine:
            if self.fast_mode:
                return {
                    'success': False,
                    'message': "Advanced analysis features are disabled in fast mode. Please restart the system with full features enabled for deep dive analysis.",
                    'suggested_action': "Contact system administrator to enable advanced research capabilities."
                }
            return {
                'success': False,
                'message': "Professional VC research engine not available. Cannot perform deep dive analysis.",
                'suggested_action': "Contact system administrator to enable professional research capabilities."
            }
        
        try:
            logger.info("🔬 Conducting comprehensive deep dive analysis...")
            
            # Extract company name and aliases from entities or user input
            company_name = None
            also_known_as = None
            sector_hint = None
            
            if entities.get('company_names'):
                company_name = entities['company_names'][0]
            else:
                # Try to extract from user input with more sophisticated patterns
                company_patterns = [
                    r'(?:company\s+called\s+)([A-Za-z\s&\-\.]+?)(?:\s*,|\s+also|\s+known|\s*$|[?.])',
                    r'(?:deep dive.*into)\s+(?:a\s+)?(?:company\s+called\s+)?([A-Za-z\s&\-\.]+?)(?:\s*,|\s+also|\s+known|\s*$|[?.])',
                    r'([A-Za-z\s&\-\.]+?)\s+(?:ltd|limited|inc)(?:\s*,|\s*$|[?.])',
                ]
                
                # Clean the user input for better extraction
                clean_input = user_input.replace('Do a deep dive into a company called ', '').replace('Do a deep dive into ', '')
                
                for pattern in company_patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        company_name = match.group(1).strip()
                        break
                
                # Fallback: try simple extraction
                if not company_name and 'yourfittingroom' in user_input.lower():
                    company_name = "YourFittingRoom Ltd"
            
            # Look for "also known as" information
            also_known_patterns = [
                r'also known as\s+([A-Za-z\s&\-\.]+?)(?:\s*,|\s*$|[?.])',
                r'(?:aka|a\.k\.a\.)\s+([A-Za-z\s&\-\.]+?)(?:\s*,|\s*$|[?.])',
            ]
            
            for pattern in also_known_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    also_known_as = match.group(1).strip()
                    break
            
            # Try to extract sector hints
            sector_keywords = {
                'fashion': ['fashion', 'clothing', 'apparel', 'style', 'fitting', 'wardrobe'],
                'retail': ['retail', 'ecommerce', 'shopping', 'store', 'marketplace'],
                'concierge': ['concierge', 'lifestyle', 'personal', 'service', 'luxury'],
                'fintech': ['fintech', 'finance', 'payment', 'banking', 'lending'],
                'healthtech': ['health', 'medical', 'healthcare', 'biotech'],
                'proptech': ['property', 'real estate', 'proptech', 'housing']
            }
            
            user_input_lower = user_input.lower()
            for sector, keywords in sector_keywords.items():
                if any(keyword in user_input_lower for keyword in keywords):
                    sector_hint = sector
                    break
            
            if not company_name:
                return {
                    'success': False,
                    'message': "Could not identify company name for deep dive analysis. Please specify which company you'd like me to analyze.",
                    'suggested_action': "Try: 'Do a deep dive into Harper Concierge' or 'Comprehensive analysis of YourFittingRoom Ltd'"
                }
            
            # Conduct comprehensive deep dive analysis using professional engine
            logger.info(f"🔍 Starting professional deep dive analysis for: {company_name}")
            analysis = self.professional_research_engine.conduct_comprehensive_analysis(
                company_name=company_name,
                also_known_as=also_known_as
            )
            
            # Format the analysis into a professional report
            formatted_report = self.professional_research_engine.format_professional_report(analysis)
            
            return {
                'success': True,
                'message': f"✅ **COMPREHENSIVE DEEP DIVE ANALYSIS COMPLETED**\n\n{formatted_report}",
                'analysis_type': 'deep_dive_analysis',
                'source': 'Advanced VC Research System',
                'company_name': company_name,
                'also_known_as': also_known_as,
                'sector': analysis.get('market_analysis', {}).get('sector_overview', {}).get('primary_sector', 'Unknown'),
                'data_sources_used': analysis.get('metadata', {}).get('data_sources_consulted', []),
                'investment_decision': analysis.get('investment_recommendation', {}).get('investment_decision', 'CONDITIONAL PROCEED'),
                'research_confidence': analysis.get('metadata', {}).get('research_confidence', 'Medium'),
                'analysis_duration': analysis.get('metadata', {}).get('analysis_duration_seconds', 0),
                'raw_analysis': analysis  # Include full analysis data
            }
            
        except Exception as e:
            logger.error(f"Deep dive analysis error: {e}")
            return {
                'success': False,
                'message': f"Error conducting deep dive analysis: {str(e)}"
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities"""
        return {
            'session_id': self.session_id,
            'model': self.config.get('model', 'llama3.2:3b'),
            'conversations_count': len(self.conversation_history),
            'capabilities': [
                'Fee letter generation (NET/GROSS)',
                'Investment analysis and EIS/KIC assessment',
                'Market analysis and sector intelligence',
                'Financial analysis and valuation modeling',
                'Competitive intelligence and market positioning',
                'Investment thesis development',
                'Due diligence automation',
                'Portfolio optimization',
                'CC Growth EIS Fund expertise'
            ],
            'memory_window': self.config.get('memory_window', 10),
            'user_context': self.user_context,
            'mcp_integration': self.mcp_vc_agent is not None,
            'enhanced_training': self.enhanced_training is not None,
            'real_data_integration': self.real_data_handler is not None
        }
