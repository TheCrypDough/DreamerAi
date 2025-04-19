# C:\DreamerAI\engine\ai\llm.py (COMPLETE REPLACEMENT - Includes D38 Caching, D6 Updates)
import asyncio
import os
import requests
import traceback
import tomllib # Requires Python 3.11+
import json # Import json for serialization
import redis # For caching
import hashlib # For hashing prompt
import time # For test block timing
from typing import Optional, Dict, List, Any, Callable
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from dotenv import load_dotenv
from pathlib import Path # Added for Path object usage
import sys

def _add_project_root_to_path():
    """Adds the project root directory to sys.path if not already present."""
    try:
        # Correct project_root calculation for engine/ai/llm.py
        project_root_llm = Path(__file__).resolve().parent.parent.parent
        project_root_str = str(project_root_llm)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
            print(f"Added project root to sys.path: {project_root_str}") # Debug print
    except Exception as e:
        print(f"Error adding project root to path: {e}") # Debug print

_add_project_root_to_path() # Call the function to modify sys.path

try:
    # Ensure logger is initialized from Day 3
    from engine.core.logger import logger_instance as logger, log_rules_check as original_log_rules_check
    logger.info("DreamerLogger imported successfully.") # Add confirmation
except ImportError as e:
    print(f"LLM: ImportError for DreamerLogger: {e}. Using fallback logger.") # Debug print
    import logging
    logger = logging.getLogger(__name__)
    # Correct fallback signature (assuming original takes no args, just logs)
    def fallback_log_rules_check(message: str = "Fallback Rules Check Called"):
        logger.debug(f"[Fallback Logger] {message}")

# --- Configuration Loading ---
CONFIG: Dict[str, Any] = {}
API_KEYS: Dict[str, Optional[str]] = {}

def load_configuration(config_path="data/config/config.dev.toml", env_path="data/config/.env.development") -> Dict:
    """Loads LLM configuration from TOML and .env files."""
    global API_KEYS, CONFIG
    project_root_llm = Path(__file__).parent.parent.parent # C:\DreamerAI
    full_config_path = project_root_llm / config_path
    full_env_path = project_root_llm / env_path
    logger.debug(f"LLM: Attempting to load config from: {full_config_path}")
    try:
        with open(full_config_path, 'rb') as f:
             config = tomllib.load(f)
        CONFIG = config # Store loaded config globally as well if needed elsewhere
        # Correctly report providers from the nested structure in the log
        provider_keys = list(config.get('ai', {}).get('providers', {}).keys())
        logger.info(f"Config loaded from {full_config_path}. Providers found under [ai][providers]: {provider_keys}")
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {full_config_path}")
        CONFIG = {} # Reset global CONFIG on error
        return {}
    except tomllib.TOMLDecodeError as e: # Handle specific tomllib error
        logger.error(f"Error decoding TOML from {full_config_path}: {e}")
        CONFIG = {}
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration from {full_config_path}: {e}")
        CONFIG = {}
        return {}

    logger.debug(f"Attempting to load .env file from: {full_env_path}")
    # Add override=True to ensure .env file takes precedence
    loaded_env = load_dotenv(dotenv_path=full_env_path, override=True)
    # Add a check to see if load_dotenv reported success
    if loaded_env:
        logger.info(f"Successfully loaded environment variables from {full_env_path}.")
    else:
         logger.warning(f"Failed to load environment variables from {full_env_path}. Key might not be available.")

    # Load API keys specified in the config
    API_KEYS = {} # Clear previous keys
    # Access the nested providers correctly
    ai_config = config.get("ai", {})
    providers_config = ai_config.get("providers", {})
    
    if not isinstance(providers_config, dict):
         logger.error(f"Config Error: Expected [ai][providers] to be a table/dictionary in {full_config_path}, but found {type(providers_config)}.")
         # Handle error appropriately, maybe return config or raise exception depending on desired behavior
    else:     
        for provider_name, provider_config in providers_config.items():
            # Check if provider_config is a dictionary before proceeding
            if not isinstance(provider_config, dict):
                 logger.warning(f"Skipping provider '{provider_name}' in {full_config_path} because its configuration is not a dictionary/table. Found type: {type(provider_config)}.")
                 continue

            if provider_config.get("enabled", False):
                key_env_var = provider_config.get("api_key_env")
                if key_env_var:
                    # Explicitly check if the key exists AFTER load_dotenv
                    api_key = os.getenv(key_env_var)
                    if api_key:
                        API_KEYS[key_env_var] = api_key
                        key_preview = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 9 else api_key
                        logger.debug(f"Loaded API key for env var '{key_env_var}': {key_preview}")
                    else:
                        logger.warning(f"Environment variable '{key_env_var}' for provider '{provider_name}' not found in environment AFTER attempting to load {full_env_path}.")
                # Handle base_url env var if needed (similar pattern)

    return config

# Load configuration when the module is imported
CONFIG = load_configuration() # Assign the result to the global CONFIG

# --- Constants ---
DEFAULT_LLM_CACHE_TTL = 3600 # 1 hour TTL (from Day 38)

# --- LLM Class ---
class LLM:
    """ V2: Manages interactions with OpenRouter/Ollama based on config, with Redis caching. """
    def __init__(self):
        self.config: Dict[str, Any] = CONFIG # Assign the loaded global config to the instance
        self.providers: Dict[str, Any] = {}
        self.openai_clients: Dict[str, OpenAI] = {} # Explicitly type hint
        self.ollama_config: Dict = {} # Store ollama provider config
        self.ollama_available: bool = False
        self.redis_client: Optional[redis.Redis] = None
        self.cache_enabled: bool = False

        self._initialize_redis() # Init Redis (D38)
        self._initialize_providers() # Init LLM Providers

    def _initialize_redis(self): # Keep D38 Logic
        """Initializes connection to the Redis server for caching."""
        redis_host = os.getenv("REDIS_HOST", "localhost") # Use localhost if not in compose/env
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        logger.info(f"Attempting Redis connection to {redis_host}:{redis_port}...")
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, socket_timeout=5, decode_responses=False)
            self.redis_client.ping()
            self.cache_enabled = True; logger.info("Redis cache connected successfully.")
        except redis.exceptions.ConnectionError as e: logger.error(f"Redis connection failed: {e}. Caching disabled."); self.redis_client = None
        except Exception as e: logger.error(f"Redis init error: {e}. Caching disabled."); self.redis_client = None

    def _get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves the configuration for a specific provider."""
        return CONFIG.get('ai', {}).get('providers', {}).get(provider_name)

    def _initialize_providers(self):
        """Initializes clients for enabled providers based on config."""
        logger.info("Initializing LLM providers (OpenRouter/Ollama)...")
        # Reset instance variables here before the loop
        self.providers = {}
        self.openai_clients = {}

        # Access the config stored in the instance, navigating to the correct nested structure
        ai_config = self.config.get("ai", {}) # Get the [ai] table first
        providers_config = ai_config.get("providers", {}) # Then get the nested [providers]

        # Check if providers_config is actually a dictionary
        if not isinstance(providers_config, dict):
            logger.error(f"Expected 'providers' to be a dictionary/table within [ai] in config, but got {type(providers_config)}. Check config.dev.toml structure.")
            return

        for provider_name, config in providers_config.items():
            if not isinstance(config, dict):
                 logger.warning(f"Skipping provider '{provider_name}' because its configuration is not a dictionary/table. Found type: {type(config)}.")
                 continue # Skip if the provider's config isn't a table
            
            if not config.get("enabled", False):
                logger.debug(f"Provider '{provider_name}' is disabled in config, skipping initialization.")
                continue

            provider_type = config.get("type")
            if provider_type == "ollama":
                # Ensure ollama_config is correctly populated before checking status
                self.ollama_config = config # Store the specific Ollama config needed by _check_ollama_status
                ollama_base_url = config.get("base_url", "http://localhost:11434/api/generate") # Use generate URL here for consistency?
                # Derive root URL for status check
                try:
                    ollama_root_url = '/'.join(ollama_base_url.split('/')[:3])
                except Exception:
                     ollama_root_url = "http://localhost:11434" # Fallback root
                     logger.warning(f"Could not derive root from Ollama base_url '{ollama_base_url}', falling back to {ollama_root_url} for status check.")
                
                # Call the status check synchronously
                ollama_available = self._check_ollama_status(ollama_root_url) 
                
                provider_info = {"name": provider_name, "status": "Available" if ollama_available else "Unavailable", **config}
                self.providers[provider_name] = provider_info # Store unified provider info
                logger.info(f"Ollama provider '{config.get('model_name')}' @ {ollama_base_url} configured. Status: {provider_info['status']}")

            elif provider_type == "openai_compatible":
                api_key_env = config.get("api_key_env")
                api_key = API_KEYS.get(api_key_env) if api_key_env else None
                base_url = config.get("base_url")

                if not api_key:
                    logger.warning(f"API key env var '{api_key_env}' not found for OpenAI-compatible provider '{provider_name}'. Disabling.")
                    continue
                if not base_url:
                     logger.warning(f"Base URL not configured for OpenAI-compatible provider '{provider_name}'. Disabling.")
                     continue

                try:
                    client = OpenAI(
                        base_url=base_url,
                        api_key=api_key,
                        # Temporarily remove default headers for debugging
                        # default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "DreamerAI"} # Example headers
                    )
                    self.openai_clients[provider_name] = client
                    self.providers[provider_name] = {"name": provider_name, "status": "Available", **config}
                    logger.info(f"Initialized OpenAI-compatible client for provider: '{provider_name}' @ {base_url}")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client for '{provider_name}': {e}")
                    self.providers[provider_name] = {"name": provider_name, "status": "Error", **config}

            else:
                logger.warning(f"Unsupported provider type '{provider_type}' for provider '{provider_name}'.")

    def _check_ollama_status(self, root_url: str) -> bool:
        """ Checks if the Ollama server root is responding synchronously. """
        if not root_url:
             logger.warning("Ollama root_url missing for status check.")
             return False
        
        logger.debug(f"Checking Ollama status synchronously at root: {root_url}...")
        try:
            # Use the root URL for the status check - standard requests call
            response = requests.get(root_url, timeout=3) # Slightly longer timeout
            # Ollama root typically responds with "Ollama is running" text
            if response.status_code == 200 and "Ollama is running" in response.text:
                 logger.info(f"Ollama server check PASSED at {root_url}.")
                 return True
            else:
                 logger.warning(f"Ollama server check FAILED at {root_url}. Status: {response.status_code}, Response: {response.text[:100]}")
                 return False
        except requests.exceptions.Timeout: logger.warning(f"Ollama status check timed out at {root_url}."); return False
        except requests.exceptions.RequestException as e: logger.warning(f"Ollama connection error at {root_url}: {e}"); return False
        except Exception as e: logger.error(f"Error checking Ollama status at {root_url}: {e}"); return False

    # --- Caching Helpers (Keep from Day 38/V1) ---
    def _get_cache_key(self, prompt: str, agent_name: Optional[str], max_tokens: int) -> str: # Keep D38 logic
         """Generates a SHA256 hash key for caching based on prompt and config."""
         identifier = f"{agent_name or 'default'}|{max_tokens}|{prompt}"; 
         return f"llm_cache:{hashlib.sha256(identifier.encode('utf-8')).hexdigest()}"

    def _get_from_cache(self, key: str) -> Optional[str]:
        """Retrieves response from Redis cache; returns None if miss or error."""
        if not self.cache_enabled or not self.redis_client: return None
        try:
            cached_bytes = self.redis_client.get(key)
            if cached_bytes:
                logger.info(f"LLM Cache HIT for key suffix: ...{key[-10:]}")
                # Add type check before decoding
                if isinstance(cached_bytes, bytes):
                    return cached_bytes.decode('utf-8') 
                else:
                    logger.warning(f"LLM: Redis returned non-bytes type for key {key[-10:]}: {type(cached_bytes)}")
                    return None # Or handle differently if necessary
            else:
                logger.debug(f"LLM Cache MISS for key suffix: ...{key[-10:]}")
                return None
        except redis.RedisError as e: logger.error(f"LLM: Redis GET error for key {key[-10:]}: {e}"); return None
        except Exception as e: logger.error(f"LLM: Cache decode/GET error for key {key[-10:]}: {e}"); return None

    def _set_cache(self, key: str, value: str, ttl: int = DEFAULT_LLM_CACHE_TTL): # Keep D38 logic
        """Stores a response in Redis cache with a TTL, handling potential errors."""
        if not self.cache_enabled or not self.redis_client: return
        try: 
            value_bytes = value.encode('utf-8'); # Encode to bytes
            self.redis_client.setex(key, ttl, value_bytes); 
            logger.info(f"LLM Cache SET for key: {key} with TTL: {ttl}s")
        except redis.RedisError as e: logger.error(f"Redis SETEX error for key {key}: {e}")
        except Exception as e: logger.error(f"Cache encode/SET error for key {key}: {e}") # Catch potential encode errors


    # --- Generation Methods (Implement Day 6/38 logic) ---
    async def _generate_ollama(self, config: Dict, prompt: str, max_tokens: int) -> Optional[str]: # Implement Day 6/38 logic
        """Generates text using the configured Ollama provider via requests."""
        url = config.get('base_url')
        model_name = config.get('model_name')
        if not url or not model_name: 
            logger.error("Ollama URL or model name missing in config.")
            return None
        
        headers = {'Content-Type': 'application/json'}
        # Basic payload structure for Ollama /api/generate
        # Note: max_tokens might be handled via num_predict option if supported, or implicitly
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False, # Get full response at once
            "options": {
                "num_predict": max_tokens # Attempt to control max tokens
            }
        }
        logger.info(f"Calling Ollama provider '{model_name}' at {url}...")
        try:
            # Use asyncio.to_thread for the blocking requests call
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload, timeout=120 # Longer timeout for generation
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            response_data = response.json()
            generated_text = response_data.get('response')
            if generated_text:
                logger.debug(f"Ollama '{model_name}' generated response successfully.")
                return generated_text.strip()
            else:
                logger.warning(f"Ollama '{model_name}' response missing 'response' field: {response_data}")
                return None
        except requests.exceptions.Timeout: logger.error(f"Ollama '{model_name}' request timed out."); return None
        except requests.exceptions.RequestException as e: logger.error(f"Ollama '{model_name}' request failed: {e}"); return None
        except json.JSONDecodeError as e: logger.error(f"Ollama '{model_name}' response JSON decode error: {e}"); return None
        except Exception as e: logger.error(f"Error generating with Ollama '{model_name}': {e}"); traceback.print_exc(); return None


    async def _generate_openai_compatible(self, client: OpenAI, config: Dict, provider_name: str, prompt: str, max_tokens: int) -> Optional[str]: # Implement Day 6/38 logic
        """Generates text using an OpenAI-compatible client (like OpenRouter)."""
        model_name = config.get('model_name')
        if not model_name:
             logger.error(f"Model name missing for OpenAI-compatible provider '{provider_name}'.")
             return None
        
        logger.info(f"Calling OpenAI-compatible provider '{provider_name}' model '{model_name}'...")
        try:
            # Wrap the blocking call in a lambda for asyncio.to_thread
            completion = await asyncio.to_thread(
                lambda: client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=config.get('temperature', 0.7), # Use config or default
                    # Add other parameters like top_p if needed from config
                )
            )
            
            # --- Start Change ---
            response_text = None
            if completion and completion.choices and len(completion.choices) > 0:
                choice = completion.choices[0]
                if choice and choice.message and choice.message.content is not None:
                     response_text = choice.message.content
                elif choice and choice.message and hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                     # Handle potential tool calls if that's an expected response format
                     logger.warning(f"OpenAI-compatible '{provider_name}' responded with tool calls, not direct text content.")
                     # Decide how to handle tool calls - for now, treat as non-text response
                     response_text = None # Or potentially serialize tool calls if needed elsewhere
                else:
                     logger.warning(f"OpenAI-compatible '{provider_name}' choice or message content missing structure: {choice}")
            else:
                 logger.warning(f"OpenAI-compatible '{provider_name}' response missing choices structure: {completion}")
            # --- End Change ---

            if response_text is not None: # Check explicitly for None now
                logger.debug(f"OpenAI-compatible '{provider_name}' model '{model_name}' generated response successfully.")
                return response_text.strip()
            else:
                logger.warning(f"OpenAI-compatible '{provider_name}' response was empty or structured unexpectedly (e.g., tool calls).")
                return None
        # Handle specific OpenAI errors
        except APIConnectionError as e: logger.error(f"OpenAI API Connection Error for '{provider_name}': {e}"); return None
        except RateLimitError as e: logger.error(f"OpenAI Rate Limit Error for '{provider_name}': {e}"); return None
        except APIStatusError as e: logger.error(f"OpenAI API Status Error for '{provider_name}': Status={e.status_code}, Response={e.response}"); return None
        except Exception as e: logger.error(f"Error generating with OpenAI-compatible '{provider_name}': {e}"); traceback.print_exc(); return None


    # --- Main Generate Method (Integrates Cache + Fallback) ---
    async def generate( self, prompt: str, agent_name: Optional[str] = None, max_tokens: int = 1500 ) -> str: # Keep D38 Logic
        """
        Generates text using configured LLM providers, with caching and fallback.
        1. Checks cache.
        2. Determines provider order based on agent config or default.
        3. Attempts generation with preferred provider(s).
        4. Falls back to secondary provider(s) if primary fails.
        5. Caches successful response.
        Returns generated text or an error message.
        """
        # Directly call the function imported at the top
        original_log_rules_check(f"LLM generate called by: {agent_name or 'Unknown Agent'}") 
             
        cache_key = self._get_cache_key(prompt, agent_name, max_tokens)
        
        # 1. Check Cache
        cached_response = self._get_from_cache(cache_key)
        if cached_response is not None: # Check explicitly for None, as empty string might be cached
            return cached_response # Return from cache if hit

        # 2. Determine Provider Preference (Cache Miss)
        logger.info(f"LLM Cache MISS for agent '{agent_name}'. Determining provider preference...")
        agent_config = self.config.get('ai', {}).get('agent_settings', {}).get(agent_name, {})
        default_preference = self.config.get('ai', {}).get('default_model_preference', [])
        
        # Use agent-specific preference if defined, otherwise use default
        provider_preference = agent_config.get('model_preference', default_preference)
        
        if not provider_preference: 
             logger.error(f"LLM provider preference list is empty for agent '{agent_name}' and no default is set.")
             return "ERROR: LLM provider preference not configured."
        
        logger.info(f"Provider preference order for agent '{agent_name}': {provider_preference}")

        # 3. Attempt Generation with Fallback
        fresh_response: Optional[str] = None
        for provider_name in provider_preference: 
            provider_info = self.providers.get(provider_name) 
            if not provider_info or provider_info.get('status') == "Error" or not provider_info.get('enabled', False):
                logger.warning(f"Provider '{provider_name}' not available, disabled, or errored during init. Skipping.")
                continue

            logger.debug(f"Attempting generation with provider: '{provider_name}'...")
            provider_type = provider_info.get('type')

            if provider_type == "ollama":
                 if provider_info.get('status') == "Available":
                     fresh_response = await self._generate_ollama(provider_info, prompt, max_tokens)
                 else:
                     logger.warning(f"Skipping unavailable Ollama provider '{provider_name}'.")
            elif provider_type == "openai_compatible": # OpenRouter etc.
                 client = self.openai_clients.get(provider_name)
                 if client and provider_info.get('status') == "Available":
                     fresh_response = await self._generate_openai_compatible(client, provider_info, provider_name, prompt, max_tokens)
                 else:
                     logger.warning(f"Client for OpenAI-compatible provider '{provider_name}' not initialized or provider unavailable. Skipping.")
            else:
                 logger.warning(f"Unknown provider type '{provider_type}' for '{provider_name}'. Skipping.")

            # Break loop if successful generation
            if fresh_response is not None: # Check for None, allow empty string response
                logger.info(f"Successfully generated response via provider '{provider_name}'.")
                break
            else: 
                logger.warning(f"Provider '{provider_name}' failed to generate response. Trying next provider.")

        # 4. Cache Successful Response & Return
        if fresh_response is not None: 
            self._set_cache(cache_key, fresh_response)
            return fresh_response
        else: 
            logger.error(f"LLM Cache MISS & All attempted providers ({provider_preference}) failed for agent '{agent_name}'.")
            return "ERROR: AI service unavailable after attempting all configured providers."

# --- Test Block (Keep from Day 38/V1, adjusted for asyncio) ---
async def test_llm_config_generation(): # Keep D38 Test Logic
    """Tests the LLM class functionality including config loading, provider init, and caching."""
    print("--- LLM Initialization & Config ---")
    # Access config via the global CONFIG dictionary after initial load
    # Log message fixed in load_configuration, but print check here is still valid
    print(f"Loaded Config Providers (from global CONFIG): {list(CONFIG.get('ai', {}).get('providers', {}).keys())}") 
    print(f"Default Preference: {CONFIG.get('ai', {}).get('default_model_preference')}")
    print(f"API Keys Loaded: { {k: ('Present' if v else 'Missing') for k, v in API_KEYS.items()} }")
    
    # LLM() init is now synchronous because _initialize_providers is sync
    llm = LLM() # Instantiate after printing initial load info 
    # Access initialized status from the instance
    print(f"Initialized Providers & Status: { {name: data.get('status', 'Unknown') for name, data in llm.providers.items()} }")
    print(f"OpenAI Clients Initialized: {list(llm.openai_clients.keys())}")
    print(f"Redis Cache Enabled: {llm.cache_enabled}")
    
    is_any_provider_available = any(p.get('status') == 'Available' for p in llm.providers.values())
    
    if not is_any_provider_available:
        print("ERROR: No LLM providers available. Cannot run generation test.")
        return
        
    test_prompt = "Explain the concept of a hybrid LLM architecture with caching in exactly three concise sentences."
    
    # Run 1 (MISS)
    print("--- Run 1 (Expect Cache MISS) ---")
    start_time_1 = time.time()
    result1 = await llm.generate(test_prompt, agent_name="TestAgent") # Specify agent for potential preference test
    end_time_1 = time.time()
    print(f"Time Taken: {end_time_1 - start_time_1:.2f}s")
    print(f"Result 1: {result1}")
    
    await asyncio.sleep(1) # Small delay to ensure distinct timestamps if needed

    # Run 2 (HIT)
    print("--- Run 2 (Expect Cache HIT) ---")
    start_time_2 = time.time()
    result2 = await llm.generate(test_prompt, agent_name="TestAgent") # Use same prompt/agent
    end_time_2 = time.time()
    print(f"Time Taken: {end_time_2 - start_time_2:.2f}s")
    print(f"Result 2: {result2}")
    
    print("--- CACHE TEST VERIFICATION ---")
    if end_time_2 - start_time_2 < 0.1 and end_time_1 - start_time_1 > 0.5: # Crude check for significant speedup
         print("PASSED: Run 2 was significantly faster, indicating potential cache hit.")
    else:
         print("NOTE: Run 2 time difference wasn't drastically smaller. Check logs carefully for 'LLM Cache HIT' message on Run 2 and absence of provider call logs.")
    if result1 == result2 and "ERROR:" not in result1:
        print("PASSED: Results from Run 1 and Run 2 are identical.")
    else:
        print("FAILED: Results from Run 1 and Run 2 differ OR an error occurred.")

if __name__ == "__main__":
    print("Starting LLM Test Block...")
    # Ensure event loop is managed correctly for async execution
    # Requires: OpenRouter Key in .env, Ollama server running (gemma3:12b pulled), Redis running (e.g., docker compose)
    try:
        asyncio.run(test_llm_config_generation())
    except Exception as e:
        # Simplified error print for linter
        print("\nAn error occurred during the test execution:")
        print(e)
        traceback.print_exc()
    print("\nLLM Test Block Finished.") # Ensured quotes and parens match
 