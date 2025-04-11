import asyncio
import os
import requests
import traceback
import tomllib # Requires Python 3.11+
from typing import Optional, Dict, List, Any
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from dotenv import load_dotenv

# Add project root for sibling imports
import sys
project_root_llm = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_llm not in sys.path:
    sys.path.insert(0, project_root_llm)

try:
    # Ensure logger is initialized from Day 3
    from engine.core.logger import logger_instance as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("LLM: Could not import custom logger, using basic logging.")

# --- Configuration Loading ---
CONFIG: Dict[str, Any] = {}
API_KEYS: Dict[str, Optional[str]] = {}

def load_configuration():
    """Loads config from TOML and secrets from .env."""
    global CONFIG, API_KEYS
    CONFIG = {} # Reset config on load
    API_KEYS = {} # Reset keys on load
    try:
        # Load TOML Configuration
        config_path = os.path.join(project_root_llm, 'data', 'config', 'config.dev.toml')
        logger.debug(f"Attempting to load config from: {config_path}")
        with open(config_path, 'rb') as f:
            CONFIG = tomllib.load(f)
        logger.info(f"Successfully loaded configuration from {config_path}")

        # Load Environment Variables (Secrets)
        dotenv_path = os.path.join(project_root_llm, 'data', 'config', '.env.development')
        logger.debug(f"Attempting to load .env file from: {dotenv_path}")
        if not load_dotenv(dotenv_path=dotenv_path):
             logger.warning(f"Could not load .env file from {dotenv_path}. API keys might be missing.")
        else:
             logger.info(f"Loaded environment variables from {dotenv_path}")

        # Populate API_KEYS dictionary based on config
        if 'ai' in CONFIG and 'providers' in CONFIG['ai']:
            for provider_name, provider_details in CONFIG['ai']['providers'].items():
                key_env_var = provider_details.get('api_key_env')
                if key_env_var:
                    api_key = os.getenv(key_env_var)
                    API_KEYS[key_env_var] = api_key # Store loaded key (or None)
                    if not api_key:
                        logger.warning(f"Environment variable '{key_env_var}' not found for provider '{provider_name}'.")
                    else:
                        logger.debug(f"Found API key for env var '{key_env_var}'.")

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}. LLM service may not function.")
    except tomllib.TOMLDecodeError as e:
         logger.error(f"Error decoding TOML configuration file: {e}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}\n{traceback.format_exc()}")

# Load configuration when the module is imported
load_configuration()

# --- LLM Class ---

class LLM:
    """
    Manages interactions with multiple LLMs based on external configuration.
    Supports dynamic provider selection and fallback.
    """
    def __init__(self):
        self.clients: Dict[str, Any] = {} # Stores initialized clients (e.g., OpenAI)
        self.ollama_base_url: Optional[str] = None
        self.ollama_available: bool = False
        self._initialize_providers()

    def _get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Safely retrieves provider configuration from loaded CONFIG."""
        return CONFIG.get('ai', {}).get('providers', {}).get(provider_name)

    def _initialize_providers(self):
        """Initializes clients based on loaded configuration and API keys."""
        logger.info("Initializing LLM providers...")
        providers = CONFIG.get('ai', {}).get('providers', {})
        if not providers:
            logger.error("No providers found in configuration [ai.providers]. Cannot initialize clients.")
            return

        for name, config in providers.items():
            provider_type = config.get('type')
            api_key_env = config.get('api_key_env')
            base_url = config.get('base_url')
            # Retrieve the key value loaded earlier
            api_key = API_KEYS.get(api_key_env) if api_key_env else None

            if provider_type == "ollama":
                self.ollama_base_url = base_url
                if not base_url:
                     logger.warning(f"Ollama base_url not configured for provider '{name}'.")
                     continue
                # We don't store an ollama client, just the base URL
                self.ollama_available = self._check_ollama_status()
                if not self.ollama_available:
                    logger.warning(f"Ollama server not reachable at {self.ollama_base_url} for provider '{name}'.")
                else:
                    logger.info(f"Ollama provider '{name}' configured and server reachable at {self.ollama_base_url}.")

            elif provider_type == "openai_compatible":
                if not base_url:
                    logger.warning(f"base_url not configured for openai_compatible provider '{name}'.")
                    continue
                if not api_key:
                    logger.warning(f"API key not found (env var: '{api_key_env}') for openai_compatible provider '{name}'. Cannot initialize client.")
                    continue
                try:
                    client = OpenAI(base_url=base_url, api_key=api_key)
                    self.clients[name] = client
                    logger.info(f"Initialized OpenAI compatible client for provider '{name}' at {base_url}.")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI compatible client for '{name}': {e}")
            else:
                logger.warning(f"Unsupported provider type '{provider_type}' for provider '{name}'.")

    def _check_ollama_status(self) -> bool:
        """Checks if the configured Ollama server is running by hitting the root URL (e.g., http://localhost:11434/)."""
        if not self.ollama_base_url:
            logger.warning("Ollama base URL not configured.")
            return False
        try:
            # Always check the root of the Ollama server, regardless of the configured base_url path
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(self.ollama_base_url)
            # Build root URL: scheme://netloc/
            check_url = urlunparse((parsed.scheme, parsed.netloc, '/', '', '', ''))
            logger.debug(f"Attempting Ollama status check at: {check_url}")
            response = requests.get(check_url, timeout=1)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            logger.debug(f"Ollama server check successful at {check_url}")
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama server check failed for {check_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Ollama status check for {check_url}: {e}", exc_info=True)
            return False

    async def _generate_ollama(self, model: str, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.7) -> Optional[str]:
        """Generates text using a configured Ollama provider."""
        if not self.ollama_available or not self.ollama_base_url:
            logger.warning("Ollama provider unavailable, cannot generate.")
            return None
        
        ollama_api_url = f"{self.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False, # For simplicity, get the full response
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        try:
            logger.debug(f"Sending request to Ollama: {ollama_api_url} with model {model}")
            # Run the blocking requests call in a separate thread
            response = await asyncio.to_thread(
                requests.post, ollama_api_url, json=payload, timeout=60 # Increased timeout for generation
            )
            response.raise_for_status()
            data = response.json()
            content = data.get('message', {}).get('content')
            logger.debug(f"Received response from Ollama model {model}")
            return content
        except requests.exceptions.Timeout:
             logger.error(f"Ollama request timed out after 60s for model {model}.")
             return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed for model {model}: {e}")
            return None
        except Exception as e:
             logger.error(f"Unexpected error during Ollama generation for model {model}: {e}\n{traceback.format_exc()}")
             return None

    async def _generate_openai_compatible(self, client_name: str, model: str, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.7) -> Optional[str]:
        """Generates text using a configured OpenAI compatible provider."""
        client = self.clients.get(client_name)
        if not client:
            logger.error(f"OpenAI compatible client '{client_name}' not initialized or found.")
            return None
        
        try:
            logger.debug(f"Sending request to OpenAI compatible provider '{client_name}' with model {model}")
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                # stream=False, # Default
                timeout=60 # Default timeout
            )
            content = response.choices[0].message.content
            logger.debug(f"Received response from OpenAI compatible model {model}")
            return content
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error for '{client_name}' model {model}: {e}")
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded for '{client_name}' model {model}: {e}")
            # Implement retry logic here later if needed
        except APIStatusError as e:
             logger.error(f"OpenAI API status error for '{client_name}' model {model}: Status={e.status_code}, Response={e.response}")
        except Exception as e:
            logger.error(f"Unexpected error during OpenAI compatible generation for '{client_name}' model {model}: {e}\n{traceback.format_exc()}")
        return None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        agent_name: Optional[str] = None, # Agent requesting generation (for specific overrides)
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generates text using the configured providers based on preferences and availability."""
        
        ai_config = CONFIG.get('ai', {})
        providers_config = ai_config.get('providers', {})
        
        # Determine the provider sequence
        provider_sequence: List[str] = []
        if agent_name:
            agent_override_provider = ai_config.get(f"{agent_name}_model_provider")
            if agent_override_provider and agent_override_provider in providers_config:
                provider_sequence.append(agent_override_provider)
                logger.debug(f"Using agent-specific provider override for '{agent_name}': '{agent_override_provider}'")
            else:
                 logger.debug(f"No valid provider override found for agent '{agent_name}', using default preferences.")
        
        # Add default preferences if no override or if override fails
        default_preferences = ai_config.get('default_model_preference', [])
        for pref in default_preferences:
            if pref not in provider_sequence and pref in providers_config:
                provider_sequence.append(pref)
            elif pref not in providers_config:
                 logger.warning(f"Default provider preference '{pref}' not found in providers configuration.")
        
        if not provider_sequence:
            logger.error("No valid LLM providers configured or specified in preferences. Cannot generate.")
            return None
        
        logger.info(f"Attempting generation using provider sequence: {provider_sequence}")
        
        # Try providers in sequence
        for provider_name in provider_sequence:
            provider_config = self._get_provider_config(provider_name)
            if not provider_config:
                logger.warning(f"Skipping provider '{provider_name}': Configuration not found.")
                continue
                
            provider_type = provider_config.get('type')
            model_name = provider_config.get('model_name')
            if not model_name:
                logger.warning(f"Skipping provider '{provider_name}': 'model_name' not configured in config.dev.toml.")
                continue

            result: Optional[str] = None
            logger.info(f"Trying provider: '{provider_name}' (Type: {provider_type}, Model: {model_name})")
            
            if provider_type == "ollama":
                result = await self._generate_ollama(model_name, messages, max_tokens, temperature)
            elif provider_type == "openai_compatible":
                result = await self._generate_openai_compatible(provider_name, model_name, messages, max_tokens, temperature)
            else:
                logger.warning(f"Skipping provider '{provider_name}': Unsupported type '{provider_type}'.")
                continue
                
            if result is not None:
                logger.info(f"Successfully generated response using provider: '{provider_name}'")
                return result # Return the first successful response
            else:
                 logger.warning(f"Provider '{provider_name}' failed to generate response. Trying next provider.")
                 
        logger.error(f"All configured providers failed to generate a response: {provider_sequence}")
        return None

# --- Test Block ---
if __name__ == "__main__":
    import pprint
    print("=== LLM MODULE DIAGNOSTICS ===")
    print("sys.path:")
    pprint.pprint(sys.path)
    print("engine.ai.llm.__file__:", __file__)
    print("sys.executable:", sys.executable)
    print("project_root_llm:", project_root_llm)
    print("==============================")
    async def run_tests():
        logger.info("--- Running LLM Class Tests ---")
        if not CONFIG:
            logger.error("Configuration not loaded, cannot run tests.")
            return
        
        llm_instance = LLM()
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a short joke."}
        ]
        
        logger.info("--- Test 1: Default Provider Preference ---")
        response1 = await llm_instance.generate(test_messages)
        if response1:
            logger.info(f"Test 1 Response (Default):\n{response1[:100]}...") # Log truncated response
        else:
            logger.error("Test 1 Failed (Default)")
            
        logger.info("--- Test 2: Agent Override (Assuming 'jeff' prefers 'cloud_tier1' if configured) ---")
        response2 = await llm_instance.generate(test_messages, agent_name="jeff")
        if response2:
            logger.info(f"Test 2 Response (Jeff Override):\n{response2[:100]}...")
        else:
            logger.error("Test 2 Failed (Jeff Override - maybe override not configured or provider failed?)")
            
        logger.info("--- Test 3: Agent Override (Assuming 'ziggy' uses default) ---")
        response3 = await llm_instance.generate(test_messages, agent_name="ziggy")
        if response3:
            logger.info(f"Test 3 Response (Ziggy Default):\n{response3[:100]}...")
        else:
            logger.error("Test 3 Failed (Ziggy Default)")
            
        logger.info("--- LLM Class Tests Finished ---")

    asyncio.run(run_tests()) 