class LLMCallBudgetExceeded(Exception):
    """Raised when a single request exceeds it's allowed number of LLM calls."""
    pass

class CallBudget:
    """Tracks and enforces a hard limit on LLM calls within a single request/session """

    def __init__(self,max_calls: int):
        self.max_calls = max_calls
        self.calls_made = 0

    def record_call(self):
        self.calls_made += 1
        if self.calls_made > self.max_calls:
            raise LLMCallBudgetExceeded(
                f"exceed budget of {self.max_calls} LLM calls for this request"
                f"(attempted call {self.calls_made})"
            )   
    
    def remaining_calls(self):
        return self.max_calls - self.calls_made

if __name__ == "__main__":
    budget = CallBudget(max_calls=3)

    for i in range(5):
        try:
            budget.record_call()
            print(f"call {i+1}: allowed , {budget.remaining_calls()} remaining ")
        except LLMCallBudgetExceeded as e:
            print(f"call {i+1}: blocked - {e}")
            break

