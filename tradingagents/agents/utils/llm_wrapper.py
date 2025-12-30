
import time
import functools
from typing import Any

def wrap_llm_with_retry(llm: Any) -> Any:
    """
    Wraps an LLM instance to handle 429 Too Many Requests errors by pausing for an hour.
    """
    original_invoke = llm.invoke

    @functools.wraps(original_invoke)
    def safe_invoke(*args, **kwargs):
        while True:
            try:
                return original_invoke(*args, **kwargs)
            except Exception as e:
                # Check for explicit HTTP status code attributes on the exception object
                status_code = getattr(e, "status_code", None)
                code = getattr(e, "code", None) # explicit check for some libraries
                
                is_429 = (
                    status_code == 429 or 
                    code == 429 or 
                    "429" in str(e) or 
                    "Too Many Requests" in str(e) or 
                    "ResourceExhausted" in str(e)
                )
                
                # Also handle 500 errors from OpenAI/Ollama which might wrap 429s or malformed tool calls
                is_500 = (
                    status_code == 500 or
                    code == 500 or
                    "500" in str(e) or
                    "InternalServerError" in str(e)
                )

                if is_429:
                    print(f"Encountered 429/ResourceExhausted error. Pausing for 1 hour before retrying... Error: {e}")
                    time.sleep(3600)
                    print("Resuming after pause...")
                    continue
                
                # Retry on 500 errors too, often transient
                if is_500:
                    print(f"Encountered 500 error. Waiting 10 seconds before retrying... Error: {e}")
                    time.sleep(10)
                    continue
                    
                raise e

    # Monkey patch the invoke method
    # We bind the method to the instance to ensure 'self' is passed correctly if it wasn't already bound
    # However, Since we are replacing the bound method on the instance, we just need a function that takes args.
    # original_invoke is already bound to the instance (method)
    # safe_invoke closes over original_invoke
    
    # Use object.__setattr__ to bypass Pydantic's validation checks
    try:
        object.__setattr__(llm, "invoke", safe_invoke)
    except AttributeError:
        # Fallback for objects that might not allow direct setattr or behave differently
        llm.invoke = safe_invoke
        
    return llm
